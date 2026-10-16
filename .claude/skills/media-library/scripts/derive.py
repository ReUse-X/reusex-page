#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Masters ($REUSEX_MEDIA) → web files (assets/media/) and other outputs,
from the [[out]] entries in media/web.toml.

  derive.py               every output whose master is newer (or missing output)
  derive.py --force       rebuild all
  derive.py hero          only outputs whose `to` contains "hero"
  derive.py --check       report missing masters / stale outputs, change nothing
  derive.py --profile linkedin   only that profile (default: site)

An [[out]] entry:
  from     master path inside $REUSEX_MEDIA (app/<id>/light.png, …)
  to       output path; profile "site" → inside assets/, others → inside
           $REUSEX_MEDIA/out/<profile>/
  width    max width in px (stills default 2400, video 1280)
  crop     optional [w, h] aspect crop, centred (e.g. [1200, 627] LinkedIn)
  pad      optional [w, h] aspect letterbox instead (pad_color, default black)
  poster   (video) also write this still (first frame, or `poster_at` s)
  start, duration   (video) trim
Imports (media/imports.toml) are masters too: imports/<id>/<file>.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import medialib as ml  # noqa: E402

VIDEO = {".mp4", ".mov", ".mkv", ".webm"}


def target(entry: dict, profile: str) -> Path:
    if profile == "site":
        return ml.ROOT / "assets" / entry["to"]
    return ml.MEDIA / "out" / profile / entry["to"]


def crop_filter(entry: dict) -> str:
    if "pad" in entry:
        # Letterbox to an aspect instead of cropping (black bars — invisible
        # on scan footage, whose background is black).
        w, h = entry["pad"]
        return (f"pad='max(iw,ceil(ih*{w}/{h}/2)*2)':'max(ih,ceil(iw*{h}/{w}/2)*2)':"
                f"(ow-iw)/2:(oh-ih)/2:{entry.get('pad_color', 'black')},")
    if "crop" not in entry:
        return ""
    w, h = entry["crop"]
    return f"crop='min(iw,ih*{w}/{h})':'min(ih,iw*{h}/{w})',"


def build(entry: dict, src: Path, out: Path, poster: Path | None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cf = crop_filter(entry)
    if src.suffix.lower() in VIDEO and out.suffix.lower() in VIDEO:
        width = int(entry.get("width", 1280))
        ml.ffmpeg(*(["-ss", str(entry["start"])] if "start" in entry else []),
                  *(["-t", str(entry["duration"])] if "duration" in entry else []),
                  "-i", str(src), "-an", "-c:v", "libx264", "-preset", "slow",
                  "-crf", str(entry.get("crf", 27)), "-profile:v", "high", "-pix_fmt", "yuv420p",
                  "-vf", f"{cf}scale='min({width},iw)':-2:flags=lanczos", "-movflags", "+faststart", str(out))
        if "poster" in entry:
            ml.ffmpeg("-ss", str(float(entry.get("poster_at", 0)) + float(entry.get("start", 0))), "-i", str(src), "-frames:v", "1",
                      "-vf", f"{cf}scale='min({width * 2},iw)':-2:flags=lanczos",
                      "-c:v", "libwebp", "-quality", "85", str(poster))
    else:
        width = int(entry.get("width", 2400))
        at = ["-ss", str(entry["at"])] if "at" in entry else []
        codec = ["-c:v", "libwebp", "-quality", str(entry.get("quality", 88))] if out.suffix == ".webp" else (
            ["-q:v", "2"] if out.suffix in (".jpg", ".jpeg") else [])
        ml.ffmpeg(*at, "-i", str(src), "-frames:v", "1",
                  "-vf", f"{cf}scale='min({width},iw)':-2:flags=lanczos", *codec, str(out))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filter", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--profile", default="site")
    args = ap.parse_args()
    entries = [e for e in ml.load("web").get("out", []) if e.get("profile", "site") == args.profile]
    bad = 0
    for e in entries:
        if args.filter and not any(f in e["to"] for f in args.filter):
            continue
        src = ml.MEDIA / e["from"]
        out = target(e, args.profile)
        if not src.exists():
            print(f"  ✗ missing master {ml.rel(src)}  (for {e['to']})")
            bad += 1
            continue
        stale = args.force or not out.exists() or out.stat().st_mtime < src.stat().st_mtime
        if args.check:
            print(f"  {'stale' if stale else 'ok   '} {ml.rel(out)}")
            continue
        if stale:
            build(e, src, out, target({**e, 'to': e['poster']}, args.profile) if 'poster' in e else None)
            print(f"  ✓ {ml.rel(out)}  ({out.stat().st_size // 1024} KB)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
