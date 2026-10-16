#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared helpers for the media skills (app-capture, infographics, media-library).

The media library has two halves:

- **masters** — full-resolution stills (PNG) and high-bitrate video (MP4) in
  $REUSEX_MEDIA (default ~/Videos/reusex-media), outside git. These are what a
  promo-video edit or a print layout starts from. Every master directory has a
  meta.json saying where it came from.
- **recipes** — media/*.toml in the repo: how to (re)make every master and
  which web derivative (assets/media/…) each one feeds. Masters are
  disposable: the recipes regenerate them.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, check=True, cwd=Path(__file__).parent).stdout.strip())
RECIPES = ROOT / "media"
WEB = ROOT / "assets" / "media"
MEDIA = Path(os.environ.get("REUSEX_MEDIA", Path.home() / "Videos" / "reusex-media")).expanduser()


def load(name: str) -> dict:
    """Load media/<name>.toml."""
    with open(RECIPES / f"{name}.toml", "rb") as f:
        return tomllib.load(f)


def master_dir(group: str, ident: str) -> Path:
    d = MEDIA / group / ident
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_meta(d: Path, **meta) -> None:
    meta.setdefault("made", _dt.datetime.now().isoformat(timespec="seconds"))
    (d / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def read_meta(d: Path) -> dict:
    p = d / "meta.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _clean_env() -> dict:
    # Some shells export an LD_LIBRARY_PATH built against another glibc,
    # which breaks Nix binaries (ffmpeg: "GLIBC_2.43 not found").
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)
    return env


def ffmpeg_bin(name: str = "ffmpeg") -> str:
    exe = shutil.which(name)
    if not exe:
        sys.exit(f"{name} not found — enter the dev shell (nix develop; flake has ffmpeg-headless)")
    return exe


def ffmpeg(*args: str) -> None:
    cmd = [ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y", *args]
    subprocess.run(cmd, check=True, env=_clean_env())


def probe(path: Path) -> dict:
    out = subprocess.run([ffmpeg_bin("ffprobe"), "-v", "error", "-print_format", "json",
                          "-show_format", "-show_streams", str(path)],
                         capture_output=True, text=True, check=True, env=_clean_env()).stdout
    return json.loads(out)


def encode_master(frames_glob: str, fps: int, out: Path) -> None:
    """PNG frame sequence → visually lossless H.264 master (edit-friendly)."""
    ffmpeg("-framerate", str(fps), "-pattern_type", "glob", "-i", frames_glob,
           "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
           "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-movflags", "+faststart", str(out))


def web_video(src: Path, out: Path, width: int = 1280, crf: int = 27,
              start: float | None = None, duration: float | None = None) -> None:
    """Master → small silent H.264 for the site (plays everywhere, loops well)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    trim = []
    if start is not None:
        trim += ["-ss", str(start)]
    if duration is not None:
        trim += ["-t", str(duration)]
    ffmpeg(*trim, "-i", str(src), "-an", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-vf", f"scale='min({width},iw)':-2:flags=lanczos", "-movflags", "+faststart", str(out))


def web_still(src: Path, out: Path, width: int = 2400, quality: int = 88,
              at: float | None = None) -> None:
    """Master PNG (or a video frame at `at` seconds) → webp for assets/.
    Hugo then makes the responsive srcset from it."""
    out.parent.mkdir(parents=True, exist_ok=True)
    pre = ["-ss", str(at)] if at is not None else []
    ffmpeg(*pre, "-i", str(src), "-frames:v", "1",
           "-vf", f"scale='min({width},iw)':-2:flags=lanczos",
           "-c:v", "libwebp", "-quality", str(quality), str(out))


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p).replace(str(Path.home()), "~")
