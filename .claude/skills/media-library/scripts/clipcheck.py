#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Find flicker in a clip: single frames whose brightness or content jumps
against their neighbours (e.g. a 3D viewport that dropped points for a frame).

  clipcheck.py FILE.mp4 [...]     report, exit 1 if any spike
  clipcheck.py --sheet OUT.jpg FILE.mp4   also save the worst frame ±1 side by side

A spike = a frame that differs from BOTH neighbours much more than they
differ from each other (motion is smooth, a dropout is not).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import medialib as ml  # noqa: E402


def yavg(path: Path) -> list[float]:
    out = subprocess.run([ml.ffmpeg_bin(), "-nostats", "-i", str(path), "-vf",
                          "scale=320:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
                          "-f", "null", "-"], capture_output=True, text=True, env=ml._clean_env()).stdout
    return [float(l.split("=")[1]) for l in out.splitlines() if "YAVG=" in l]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--sheet", type=Path)
    ap.add_argument("--threshold", type=float, default=0.8, help="brightness spike (0–255 scale)")
    args = ap.parse_args()
    bad = 0
    for f in args.files:
        y = yavg(f)
        spikes = []
        for i in range(1, len(y) - 1):
            a, b, c = y[i - 1], y[i], y[i + 1]
            jump = min(abs(b - a), abs(b - c))
            if jump > args.threshold and abs(c - a) < jump / 2:
                spikes.append((jump, i))
        spikes.sort(reverse=True)
        print(f"{ml.rel(f)}: {len(y)} frames, {len(spikes)} spike(s)"
              + (f" — worst at frame {spikes[0][1]} ({spikes[0][0]:.2f}): {[i for _, i in spikes[:10]]}" if spikes else ""))
        if spikes and args.sheet:
            n = spikes[0][1]
            ml.ffmpeg("-i", str(f), "-vf", f"select='between(n\\,{n - 1}\\,{n + 1})',scale=640:-2,tile=3x1",
                      "-frames:v", "1", str(args.sheet))
        bad += bool(spikes)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
