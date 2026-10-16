#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Copy external material into the media library with provenance
(media/imports.toml → $REUSEX_MEDIA/imports/<id>/master.<ext> + meta.json).

  import.py            every entry (skips ones already imported and unchanged)
  import.py scan-ipad  only these ids
  import.py --list     ids, clearance, source
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import medialib as ml  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    for e in ml.load("imports").get("import", []):
        if args.ids and e["id"] not in args.ids:
            continue
        src = Path(e["source"]).expanduser()
        if args.list:
            print(f"{e['id']:<26} {e.get('clearance', '?'):<12} {e['source']}")
            continue
        if not src.exists():
            print(f"  ✗ {e['id']}: source missing {e['source']}")
            continue
        d = ml.master_dir("imports", e["id"])
        dst = d / f"master{src.suffix.lower()}"
        if not dst.exists() or dst.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dst)
        info = ml.probe(dst)
        v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
        ml.write_meta(d, id=e["id"], kind="import", title=e.get("title", ""), source=e["source"],
                      notes=e.get("notes", ""), clearance=e.get("clearance", "owner-check"),
                      size=[v.get("width"), v.get("height")],
                      duration=float(info["format"].get("duration", 0) or 0),
                      recipe="media/imports.toml")
        print(f"  ✓ {e['id']:<26} {ml.rel(dst)}  [{e.get('clearance')}]")


if __name__ == "__main__":
    main()
