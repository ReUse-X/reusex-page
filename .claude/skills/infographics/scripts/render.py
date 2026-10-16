#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render animated infographics (media/infographics/<id>.html) to video,
deterministically, from the recipes in media/infographics.toml.

  render.py                    every infographic, every theme
  render.py pipeline           ids (prefix match)
  render.py --still 4.5 id     one frame at t = 4.5 s (scratch PNG) to look at
  render.py --list

How: the page is loaded paused; for each frame every animation is seeked to
t (document.getAnimations(): CSS animations, transitions and WAAPI) and
window.renderAt(t) is called if the page defines one (counters, SVG paths
driven from JS). Then a screenshot. So the output never stutters, whatever
the machine, and loops are exact: make the animation's state at t = duration
equal to t = 0.

Masters → $REUSEX_MEDIA/infographics/<id>/<theme>.mp4 (+ -poster.png, and
-final.png = the last frame, a complete still for print/LinkedIn).
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "media-library" / "scripts"))
import medialib as ml  # noqa: E402

from playwright.sync_api import sync_playwright  # noqa: E402

SEEK = """t => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  if (window.renderAt) window.renderAt(t);
}"""


_SERVER = None


def base_url() -> str:
    """Serve the repo over local HTTP: browsers refuse ES-module imports from
    file://, and the wrappers import the site's own infographic modules."""
    global _SERVER
    if _SERVER is None:
        import functools
        import http.server
        import threading
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        handler = functools.partial(Quiet, directory=str(ml.ROOT))
        _SERVER = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=_SERVER.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_SERVER.server_address[1]}"


def page_for(browser, item: dict, theme: str, scale: float, layout: str = "wide"):
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=scale,
                              color_scheme="dark" if theme == "dark" else "light")
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(f"{base_url()}/media/infographics/{item['id']}.html?theme={theme}&layout={layout}&render=1",
              wait_until="load")
    page.wait_for_function("document.documentElement.dataset.ready === '1'", timeout=20000)
    page.evaluate("document.fonts.ready")
    info = page.evaluate("window.infographic")
    page.set_viewport_size({"width": info["w"], "height": info["h"]})
    item.setdefault("_info", {})[layout] = info
    page.evaluate(SEEK, 0)
    return ctx, page, errors


def frame(page, t: float, path: Path) -> None:
    page.evaluate(SEEK, t)
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    page.screenshot(path=str(path), animations="allow")


def render(browser, item: dict, theme: str, layout: str = "wide") -> None:
    t0 = time.time()
    fps = int(item.get("fps", 30))
    dur = float(item["duration"])
    scale = float(item.get("scale", 1))
    ctx, page, errors = page_for(browser, item, theme, scale, layout)
    d = ml.master_dir("infographics", item["id"])
    name = theme if layout == "wide" else f"{theme}-{layout}"
    frames = Path(tempfile.mkdtemp(prefix="frames-", dir=d))
    try:
        n = round(dur * fps)
        for i in range(n):
            frame(page, i / fps, frames / f"f{i:05d}.png")
        ml.encode_master(str(frames / "f*.png"), fps, d / f"{name}.mp4")
        poster_t = float(item.get("poster", dur * 0.5))
        frame(page, poster_t, d / f"{name}-poster.png")
        frame(page, float(item.get("final", dur - 1 / fps)), d / f"{name}-final.png")
    finally:
        shutil.rmtree(frames, ignore_errors=True)
    meta = ml.read_meta(d)
    meta.update({"id": item["id"], "kind": "infographic", "title": item.get("title", ""),
                 "alt": item.get("alt", ""), "source": f"media/infographics/{item['id']}.html",
                 "duration": dur, "fps": fps, "size": [item["_info"][layout]["w"], item["_info"][layout]["h"]],
                 "source_module": f"themes/reuse-x/assets/js/infographics/{item['id']}.js",
                 "recipe": "media/infographics.toml"})
    meta.setdefault("themes", {})[name] = ml.rel(d / f"{name}.mp4")
    ml.write_meta(d, **meta)
    ctx.close()
    note = f"  ⚠ page errors: {errors[:2]}" if errors else ""
    print(f"  {item['id']:<24} {theme:<5} → {ml.rel(d / f'{name}.mp4')}  ({time.time() - t0:.0f}s){note}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--theme", choices=["light", "dark"])
    ap.add_argument("--still", type=float, metavar="T")
    ap.add_argument("--layout", choices=["wide", "tall"])
    ap.add_argument("--out", default=tempfile.gettempdir())
    args = ap.parse_args()
    cfg = ml.load("infographics")
    items = cfg.get("infographic", [])
    if args.list:
        for it in items:
            print(f"{it['id']:<24} {it['duration']:>5}s  {it.get('title', '')}")
        return
    chosen = [it for it in items if not args.ids or any(it["id"].startswith(i) for i in args.ids)]
    if not chosen:
        sys.exit(f"no infographic matches {args.ids} (see --list)")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chromium", args=["--use-angle=gl-egl", "--ignore-gpu-blocklist"])
        for it in chosen:
            themes = [args.theme] if args.theme else it.get("themes", ["light", "dark"])
            for th, lay in [(t, l) for t in themes for l in ([args.layout] if args.layout else it.get("layouts", ["wide"]))]:
                if args.still is not None:
                    ctx, page, errors = page_for(browser, it, th, 1, lay)
                    out = Path(args.out) / f"{it['id']}-{th}-{lay}-{args.still:g}.png"
                    frame(page, args.still, out)
                    print(out, *(f"⚠ {e}" for e in errors))
                    ctx.close()
                else:
                    render(browser, it, th, lay)
        browser.close()


if __name__ == "__main__":
    main()
