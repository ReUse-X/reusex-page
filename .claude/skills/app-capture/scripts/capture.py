#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Capture screenshots and recordings of the ReUseX app from the recipes in
media/app.toml. READ-ONLY by construction: every non-GET request to /api is
aborted, so no recipe can change a case.

  capture.py                      every shot and clip in media/app.toml
  capture.py viewport-labels      only these ids (prefix match: "viewport")
  capture.py --list               ids, kinds and titles
  capture.py --try /sager/{case}/rapport [--theme dark]   ad-hoc look (scratch PNG)
  capture.py --frames 30 clip-id  a clip, but stop after 30 frames (preview)

Masters land in $REUSEX_MEDIA/app/<id>/ (light.png, dark.png, <theme>.mp4,
meta.json). Then `derive.py` makes the web files.

Login: the app session cookie, from ~/.config/reusex-capture/session (or
$REUSEX_SESSION). Network: socks5 127.0.0.1:1055 by default
(capture-proxy.sh up), or --no-proxy where the app is reachable directly.
GPU: headless Chromium is started with ANGLE on EGL so the WebGL viewport
renders on the NVIDIA card (SwiftShader is far too slow for 7 M points).
"""
from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "media-library" / "scripts"))
import medialib as ml  # noqa: E402

from playwright.sync_api import Page, sync_playwright  # noqa: E402

COOKIE_FILE = Path.home() / ".config" / "reusex-capture" / "session"


# --------------------------------------------------------------------------- setup

def session_token() -> str:
    tok = os.environ.get("REUSEX_SESSION") or (COOKIE_FILE.read_text().strip() if COOKIE_FILE.exists() else "")
    if not tok:
        sys.exit(f"no session: put the app's session cookie value in {COOKIE_FILE} (chmod 600)")
    return tok


def open_browser(p, cfg: dict, use_proxy: bool):
    args = ["--use-angle=gl-egl", "--ignore-gpu-blocklist", "--enable-gpu-rasterization"]
    kw = {"channel": "chromium", "args": args}
    if use_proxy:
        kw["proxy"] = {"server": cfg.get("proxy", "socks5://127.0.0.1:1055")}
    return p.chromium.launch(**kw)


def new_context(browser, cfg: dict, theme: str, viewport, scale: float):
    ctx = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]},
                              device_scale_factor=scale, locale="da-DK",
                              color_scheme="dark" if theme == "dark" else "light",
                              reduced_motion="reduce")
    base = cfg["base"]
    ctx.add_cookies([{"name": cfg.get("cookie", "__Host-ruxd_session_8080"), "value": session_token(),
                      "url": base, "secure": True, "httpOnly": True, "sameSite": "Lax"}])
    ctx.add_init_script(f"try{{localStorage.setItem('reusex-theme','{theme}')}}catch(e){{}}")
    ctx.add_init_script(CAMERA_HOOK)

    blocked = []

    def guard(route):
        req = route.request
        if req.method not in ("GET", "HEAD", "OPTIONS"):
            blocked.append(f"{req.method} {req.url}")
            return route.abort()
        return route.continue_()

    ctx.route(re.compile(r".*/api/.*"), guard)
    ctx.blocked = blocked  # type: ignore[attr-defined]
    return ctx


# Capture-only hook: the viewport's three.js OrbitControls damp the camera,
# so a mouse-driven move depends on frame timing. This registers every
# controls object (window.__ruxControls) and turns damping off; then
# __ruxCam moves the camera numerically — identical path on every run, which
# is what lets several passes (RGB, labels, instances …) be cross-faded.
CAMERA_HOOK = r"""
(() => {
  const keep = Symbol('df');
  Object.defineProperty(Object.prototype, 'dampingFactor', { configurable: true,
    get() { return this[keep] ?? 0.05; },
    set(v) { this[keep] = v; const l = (window.__ruxControls ||= []); if (!l.includes(this)) l.push(this); } });
  Object.defineProperty(Object.prototype, 'enableDamping', { configurable: true, get() { return false; }, set(v) {} });
  // three.js culls a Points object by its geometry's bounding sphere; the
  // viewport computes it before all pages have streamed in, so at some angles
  // whole walls vanish. Capture-only: never cull.
  Object.defineProperty(Object.prototype, 'frustumCulled', { configurable: true, get() { return false; }, set(v) {} });
  const ctl = () => (window.__ruxControls || []).find(c => c.object && c.target && c.object.position);
  // Spherical coordinates around the target, up = camera.up (Z in the app).
  const sph = c => { const p = c.object.position, t = c.target, u = c.object.up;
    const dx = p.x - t.x, dy = p.y - t.y, dz = p.z - t.z, r = Math.hypot(dx, dy, dz);
    if (u.z === 1) return { r, az: Math.atan2(dy, dx), el: Math.asin(dz / r), up: 'z' };
    return { r, az: Math.atan2(dx, dz), el: Math.asin(dy / r), up: 'y' }; };
  const put = (c, { r, az, el, up }) => { const t = c.target, ce = Math.cos(el);
    if (up === 'z') c.object.position.set(t.x + r * ce * Math.cos(az), t.y + r * ce * Math.sin(az), t.z + r * Math.sin(el));
    else c.object.position.set(t.x + r * ce * Math.sin(az), t.y + r * Math.sin(el), t.z + r * ce * Math.cos(az));
    c.object.lookAt(t.x, t.y, t.z); c.update(); };
  window.__ruxCam = (op, a) => { const c = ctl(); if (!c) return 'no-controls'; const s = sph(c);
    if (op === 'get') return { ...s, az: s.az * 180 / Math.PI, el: s.el * 180 / Math.PI };
    if (op === 'set') { if (a.azimuth != null) s.az = a.azimuth * Math.PI / 180; if (a.elevation != null) s.el = a.elevation * Math.PI / 180;
                        if (a.distance != null) s.r *= a.distance; put(c, s); return 'ok'; }
    if (op === 'state') return { p: c.object.position.toArray(), t: c.target.toArray() };
    if (op === 'restore') { c.object.position.fromArray(a.p); c.target.fromArray(a.t);
                            c.object.lookAt(c.target.x, c.target.y, c.target.z); c.update(); return 'ok'; }
    if (op === 'pan') { // move camera + target in the screen plane; a.dx/a.dy in CSS px (y down)
      const el = c.domElement || document.querySelector('canvas'), h = el.clientHeight;
      const per = 2 * s.r * Math.tan((c.object.fov || 50) * Math.PI / 360) / h;
      c.object.updateMatrixWorld(); const m = c.object.matrixWorld.elements;
      const off = [0, 1, 2].map(i => -a.dx * per * m[i] + a.dy * per * m[4 + i]);
      // Content should move by (dx, dy) on screen → the camera moves the other way.
      c.object.position.set(c.object.position.x + off[0], c.object.position.y + off[1], c.object.position.z + off[2]);
      c.target.set(c.target.x + off[0], c.target.y + off[1], c.target.z + off[2]);
      c.update(); return 'ok'; }
    if (op === 'turn') { s.az += a.deg * Math.PI / 180; if (a.el) s.el += a.el * Math.PI / 180; if (a.dolly) s.r *= a.dolly; put(c, s); return 'ok'; }
  };
})();
"""


MASK_JS = r"""
(rules) => {
  const apply = () => {
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      let t = n.nodeValue, o = t;
      for (const [pat, rep] of rules) t = t.replace(new RegExp(pat, 'g'), rep);
      if (t !== o) n.nodeValue = t;
    }
    for (const el of document.querySelectorAll('[title],[aria-label]')) {
      for (const a of ['title', 'aria-label']) {
        const v = el.getAttribute(a); if (!v) continue;
        let t = v; for (const [pat, rep] of rules) t = t.replace(new RegExp(pat, 'g'), rep);
        if (t !== v) el.setAttribute(a, t);
      }
    }
  };
  apply();
  if (!window.__ruxMask) {
    window.__ruxMask = new MutationObserver(apply);
    window.__ruxMask.observe(document.body, {subtree: true, childList: true, characterData: true});
  }
}
"""


def masks(page: Page, cfg: dict) -> None:
    rules = [[m["find"], m["replace"]] for m in cfg.get("mask", [])]
    if rules:
        page.evaluate(MASK_JS, rules)
    css = cfg.get("css", "")
    if css:
        page.add_style_tag(content=css)


def settle(page: Page, extra_ms: int) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=25000)
    except Exception:
        pass
    page.wait_for_timeout(extra_ms)


def two_frames(page: Page) -> None:
    page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")


# --------------------------------------------------------------------------- actions

def point(page: Page, at) -> tuple[float, float]:
    """[x, y] in CSS px, or a selector → its centre, or [selector, fx, fy]."""
    if isinstance(at, str):
        at = [at, 0.5, 0.5]
    if isinstance(at[0], str):
        box = page.locator(at[0]).first.bounding_box()
        if not box:
            raise RuntimeError(f"not visible: {at[0]}")
        return box["x"] + box["width"] * at[1], box["y"] + box["height"] * at[2]
    return float(at[0]), float(at[1])


def expand(cfg: dict, actions: list) -> list:
    """`{ use = "name" }` → the action list [preludes.name] from app.toml."""
    out = []
    for a in actions:
        if "use" in a:
            out += expand(cfg, cfg.get("preludes", {})[a["use"]])
        else:
            out.append(a)
    return out


def act(page: Page, a: dict) -> None:
    """One setup action. Never anything that writes: the API guard aborts
    POST/PUT/PATCH/DELETE anyway, but recipes should not even try."""
    if "click" in a:
        page.locator(a["click"]).first.click()
    elif "check" in a:
        loc = page.locator(a["check"]).first
        if not loc.is_checked():
            loc.click()
    elif "uncheck" in a:
        loc = page.locator(a["uncheck"]).first
        if loc.is_checked():
            loc.click()
    elif "select" in a:
        page.locator(a["select"]).first.select_option(label=a["option"])
    elif "hide" in a:
        # Visually remove overlay chrome (a floating button over the canvas).
        for el in page.locator(a["hide"]).all():
            el.evaluate("e => e.style.setProperty('visibility', 'hidden', 'important')")
    elif "hover" in a:
        page.locator(a["hover"]).first.hover()
    elif "press" in a:
        page.keyboard.press(a["press"])
    elif "wait" in a:
        page.wait_for_timeout(int(a["wait"]))
    elif "wait_for" in a:
        page.locator(a["wait_for"]).first.wait_for(state="visible", timeout=int(a.get("timeout", 60000)))
    elif "camera" in a:
        # { camera = { azimuth = 225, elevation = 35, distance = 0.8 } } —
        # degrees around the target (after "Frame all"); distance multiplies.
        r = page.evaluate("a => window.__ruxCam('set', a)", a["camera"])
        if r != "ok":
            raise RuntimeError(f"camera: {r} (is this the 3D viewport?)")
        two_frames(page)
    elif "frame" in a:
        # { frame = { fill = 0.7, x = 0.5, y = 0.5 } } — measure where the
        # content is on screen (robust to stray points), pan it to (x, y) and
        # dolly until it spans `fill` of the canvas. Deterministic for a given
        # starting camera; a pass-clip measures once and reuses the state.
        autoframe(page, a["frame"])
    elif "gone" in a:
        # Wait until nothing matches (e.g. a streaming progress bar).
        page.wait_for_function("s => !document.querySelector(s)", arg=a["gone"],
                               timeout=int(a.get("timeout", 180000)), polling=500)
    elif "idle" in a:
        settle(page, int(a["idle"]))
    elif "scroll" in a:
        sel = a["scroll"]
        page.evaluate("([s, y]) => { const e = s ? document.querySelector(s) : document.scrollingElement; e.scrollTop += y }",
                      [sel or None, a.get("by", 0)])
    elif "drag" in a:
        x, y = point(page, a["from"])
        dx, dy = a.get("by", [0, 0])
        steps = int(a.get("steps", 20))
        page.mouse.move(x, y)
        page.mouse.down(button=a.get("button", "left"))
        for i in range(1, steps + 1):
            page.mouse.move(x + dx * i / steps, y + dy * i / steps)
            two_frames(page)
        page.mouse.up(button=a.get("button", "left"))
    elif "wheel" in a:
        x, y = point(page, a["wheel"])
        page.mouse.move(x, y)
        for _ in range(int(a.get("steps", 1))):
            page.mouse.wheel(0, a.get("dy", 100))
            two_frames(page)
    elif "eval" in a:
        page.evaluate(a["eval"])
    elif "goto" in a:
        page.goto(a["goto"], wait_until="load")
    else:
        raise ValueError(f"unknown action {a}")


MEASURE_JS = r"""
async ([png, thr]) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + png; await img.decode();
  const c = new OffscreenCanvas(img.width, img.height), g = c.getContext('2d'); g.drawImage(img, 0, 0);
  const d = g.getImageData(0, 0, img.width, img.height).data, W = img.width, H = img.height;
  const bg = [d[0], d[1], d[2]], xs = new Uint32Array(W), ys = new Uint32Array(H); let n = 0;
  for (let y = 0; y < H; y += 2) for (let x = 0; x < W; x += 2) { const i = (y * W + x) * 4;
    if (Math.abs(d[i] - bg[0]) + Math.abs(d[i + 1] - bg[1]) + Math.abs(d[i + 2] - bg[2]) > thr) { xs[x]++; ys[y]++; n++; } }
  const q = (h, f) => { let acc = 0; const want = n * f; for (let i = 0; i < h.length; i++) { acc += h[i]; if (acc >= want) return i; } return h.length - 1; };
  return { n, W, H, x0: q(xs, .02) / W, x1: q(xs, .98) / W, y0: q(ys, .02) / H, y1: q(ys, .98) / H };
}
"""


# Mean absolute difference between this frame and the last accepted one
# (both downscaled ×4). Between two orbit frames only a 0.5° turn changes, so a
# frame that differs much more than usual has a rendering dropout.
DIFF_JS = r"""
async ([png, keep]) => {
  const img = new Image(); img.src = 'data:image/png;base64,' + png; await img.decode();
  const w = Math.max(1, img.width >> 2), h = Math.max(1, img.height >> 2);
  const c = new OffscreenCanvas(w, h), g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h);
  const d = g.getImageData(0, 0, w, h).data, prev = window.__ruxPrev;
  let sum = 0;
  if (prev && prev.length === d.length) for (let i = 0; i < d.length; i += 4)
    sum += Math.abs(d[i] - prev[i]) + Math.abs(d[i + 1] - prev[i + 1]) + Math.abs(d[i + 2] - prev[i + 2]);
  if (keep) window.__ruxPrev = d;
  window.__ruxCand = d;
  return prev ? sum / (w * h) : -1;
}
"""


def autoframe(page: Page, spec: dict) -> None:
    import base64
    canvas = page.locator(spec.get("in", "canvas")).first
    box = canvas.bounding_box()
    fill, tx, ty = float(spec.get("fill", 0.7)), float(spec.get("x", 0.5)), float(spec.get("y", 0.5))
    for _ in range(int(spec.get("iterations", 4))):
        png = base64.b64encode(canvas.screenshot(animations="disabled")).decode()
        m = page.evaluate(MEASURE_JS, [png, int(spec.get("threshold", 60))])
        if not m["n"]:
            raise RuntimeError("frame: nothing drawn on the canvas")
        cx, cy = (m["x0"] + m["x1"]) / 2, (m["y0"] + m["y1"]) / 2
        span = max(m["x1"] - m["x0"], m["y1"] - m["y0"])   # fraction of the larger extent
        page.evaluate("a => window.__ruxCam('pan', a)",
                      {"dx": (tx - cx) * box["width"], "dy": (ty - cy) * box["height"]})
        page.evaluate("a => window.__ruxCam('set', a)", {"distance": max(0.5, min(2.0, span / fill))})
        two_frames(page)
        if item_wait := spec.get("wait_gone"):
            page.wait_for_function("s => !document.querySelector(s)", arg=item_wait, timeout=120000, polling=200)
        page.wait_for_timeout(300)


def ease(t: float, kind: str) -> float:
    if kind == "linear":
        return t
    return 0.5 - 0.5 * math.cos(math.pi * t)  # ease-in-out (sine)


class Timeline:
    """Clip segments → one small, eased input step per frame. Because every
    frame is a screenshot taken after the step has rendered, the result is
    smooth at any resolution regardless of how slow the GPU readback is."""

    def __init__(self, page: Page, fps: int, cfg: dict):
        self.page, self.fps, self.cfg = page, fps, cfg
        self.held = None  # (button) when a drag spans frames

    def frames(self, seg: dict):
        """Yield once per frame after applying that frame's step."""
        page = self.page
        n = max(1, round(float(seg.get("seconds", 1)) * self.fps))
        kind = seg.get("ease", "inout")
        if "hold" in seg or seg.get("type") == "hold":
            for _ in range(n):
                yield
            return
        if "orbit" in seg or "pan" in seg:
            spec = seg.get("orbit") or seg.get("pan")
            x, y = point(page, spec.get("at", ["canvas", 0.5, 0.5]))
            dx, dy = spec.get("by", [0, 0])
            button = "right" if "pan" in seg else spec.get("button", "left")
            page.mouse.move(x, y)
            page.mouse.down(button=button)
            for i in range(1, n + 1):
                f = ease(i / n, kind)
                page.mouse.move(x + dx * f, y + dy * f)
                yield
            page.mouse.up(button=button)
            return
        if "turn" in seg:
            # Numeric orbit: `deg` of azimuth (optionally `el` degrees of
            # elevation and a `dolly` distance factor) over the segment.
            spec = seg["turn"]
            deg, el, dolly = float(spec.get("deg", 90)), float(spec.get("el", 0)), float(spec.get("dolly", 1))
            prev = 0.0
            for i in range(1, n + 1):
                f = ease(i / n, kind)
                step = {"deg": deg * (f - prev), "el": el * (f - prev), "dolly": dolly ** (f - prev)}
                page.evaluate("a => window.__ruxCam('turn', a)", step)
                prev = f
                yield
            return
        if "zoom" in seg:
            spec = seg["zoom"]
            x, y = point(page, spec.get("at", ["canvas", 0.5, 0.5]))
            total = float(spec.get("dy", -600))
            page.mouse.move(x, y)
            done = 0.0
            for i in range(1, n + 1):
                target = total * ease(i / n, kind)
                page.mouse.wheel(0, target - done)
                done = target
                yield
            return
        if "scroll" in seg:
            spec = seg["scroll"]
            sel, total = spec.get("in"), float(spec.get("by", 600))
            done = 0.0
            for i in range(1, n + 1):
                target = total * ease(i / n, kind)
                page.evaluate("([s, y]) => { const e = s ? document.querySelector(s) : document.scrollingElement; e.scrollTop += y }",
                              [sel, target - done])
                done = target
                yield
            return
        if "cursor" in seg:
            # Move the (drawn) pointer to a target, e.g. before a click.
            spec = seg["cursor"]
            x0, y0 = getattr(self, "pos", point(page, ["body", 0.5, 0.5]))
            x1, y1 = point(page, spec["to"])
            for i in range(1, n + 1):
                f = ease(i / n, kind)
                self.pos = (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
                page.mouse.move(*self.pos)
                page.evaluate("([x,y]) => window.__ruxCursor && window.__ruxCursor(x,y)", list(self.pos))
                yield
            return
        if "do" in seg:
            # A discrete setup action mid-clip (click a toggle, open a tab),
            # then hold for the segment's length while it renders.
            for a in expand(self.cfg, seg["do"]):
                act(page, a)
            for _ in range(n):
                yield
            return
        raise ValueError(f"unknown segment {seg}")


CURSOR_JS = r"""
() => {
  if (window.__ruxCursor) return;
  const c = document.createElement('div');
  c.style.cssText = 'position:fixed;left:0;top:0;width:22px;height:22px;z-index:2147483647;pointer-events:none;' +
    'transform:translate(-3px,-2px);background:no-repeat center/contain url("data:image/svg+xml,' +
    encodeURIComponent('<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\"><path d=\"M3 2l7 19 2.6-7.4L20 11z\" fill=\"#fff\" stroke=\"#1d2d3d\" stroke-width=\"1.6\" stroke-linejoin=\"round\"/></svg>') + '")';
  document.documentElement.appendChild(c);
  window.__ruxCursor = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; };
}
"""


# --------------------------------------------------------------------------- run

def url_for(cfg: dict, path: str) -> str:
    return cfg["base"].rstrip("/") + path.replace("{case}", cfg.get("case", ""))


def prepare(page: Page, cfg: dict, item: dict) -> None:
    page.goto(url_for(cfg, item["path"]), wait_until="load", timeout=90000)
    masks(page, cfg)
    settle(page, int(item.get("wait", cfg.get("wait", 2500))))
    for a in expand(cfg, item.get("actions", [])):
        act(page, a)
    masks(page, cfg)
    settle(page, int(item.get("settle", cfg.get("settle", 1500))))


def shoot_still(page: Page, item: dict, out: Path) -> None:
    sel = item.get("selector")
    if sel:
        page.locator(sel).first.screenshot(path=str(out), animations="disabled")
    else:
        page.screenshot(path=str(out), full_page=bool(item.get("full")), animations="disabled")


def record(page: Page, cfg: dict, item: dict, d: Path, name: str, max_frames: int | None) -> Path:
    """Run the clip timeline, one screenshot per frame → d/<name>.mp4 (+ poster)."""
    fps = int(item.get("fps", cfg.get("fps", 30)))
    if item.get("cursor"):
        page.evaluate(CURSOR_JS)
    tl = Timeline(page, fps, cfg)
    frames = Path(tempfile.mkdtemp(prefix=f"frames-{name}-", dir=d))
    sel = item.get("selector")
    target = page.locator(sel).first if sel else page
    n = 0
    recent: list[int] = []
    diffs: list[float] = []
    page.evaluate("() => { window.__ruxPrev = null; }")
    try:
        for seg in item["timeline"]:
            for _ in tl.frames(seg):
                two_frames(page)
                if item.get("frame_wait"):
                    # e.g. the viewport re-streams points as the camera moves:
                    # don't shoot a frame until it has finished.
                    page.wait_for_function("s => !document.querySelector(s)", arg=item["frame_wait"],
                                           timeout=120000, polling=100)
                    two_frames(page)
                if seg.get("settle"):
                    page.wait_for_timeout(int(seg["settle"]))
                shot_path = frames / f"f{n:05d}.png"
                target.screenshot(path=str(shot_path), animations="disabled")
                if item.get("frame_check"):
                    # Guard against frames where the viewport has momentarily
                    # dropped points (bead d8u): if far less is drawn than in
                    # the recent frames, wait and shoot the frame again.
                    import base64
                    for attempt in range(int(item.get("frame_retries", 20))):
                        drawn = page.evaluate(MEASURE_JS, [base64.b64encode(shot_path.read_bytes()).decode(), 60])["n"]
                        ref = sorted(recent)[len(recent) // 2] if len(recent) >= 5 else 0
                        if drawn >= float(item["frame_check"]) * ref:
                            break
                        page.wait_for_timeout(500)
                        two_frames(page)
                        target.screenshot(path=str(shot_path), animations="disabled")
                    else:
                        print(f"    ⚠ frame {n}: still {drawn} vs {ref} drawn after retries")
                    recent.append(drawn)
                    del recent[:-15]
                    # Second test: change against the previous accepted frame.
                    for attempt in range(int(item.get("frame_retries", 20))):
                        diff = page.evaluate(DIFF_JS, [base64.b64encode(shot_path.read_bytes()).decode(), False])
                        dref = sorted(diffs)[len(diffs) // 2] if len(diffs) >= 5 else None
                        if diff < 0 or dref is None or diff <= 2.5 * dref + 1.0:
                            break
                        page.wait_for_timeout(500)
                        two_frames(page)
                        target.screenshot(path=str(shot_path), animations="disabled")
                    else:
                        print(f"    ⚠ frame {n}: changes {diff:.1f} vs usual {dref:.1f} after retries")
                    page.evaluate("() => { window.__ruxPrev = window.__ruxCand; }")
                    if diff >= 0:
                        diffs.append(diff)
                        del diffs[:-15]
                n += 1
                if max_frames and n >= max_frames:
                    break
            if max_frames and n >= max_frames:
                break
        out = d / f"{name}.mp4"
        ml.encode_master(str(frames / "f*.png"), fps, out)
        pf = min(int(item.get("poster_frame", 0)), n - 1)
        shutil.copy(frames / f"f{pf:05d}.png", d / f"{name}-poster.png")
    finally:
        shutil.rmtree(frames, ignore_errors=True)
    return out


def composite(item: dict, d: Path) -> Path:
    """Cross-fade time-aligned passes: composite = [[pass, fade-in start s], …].
    Every pass has the identical camera path, so a fade only changes the look."""
    seq = item["composite"]
    fade = float(item.get("fade", 1.0))
    args, chain = [], []
    for name, _ in seq:
        args += ["-i", str(d / f"{name}.mp4")]
    prev = "[0:v]"
    for i, (_, st) in enumerate(seq[1:], start=1):
        chain.append(f"[{i}:v]format=yuva420p,fade=t=in:st={st}:d={fade}:alpha=1[f{i}]")
        chain.append(f"{prev}[f{i}]overlay=shortest=1:format=auto[o{i}]")
        prev = f"[o{i}]"
    out = d / "composite.mp4"
    ml.ffmpeg(*args, "-filter_complex", ";".join(chain), "-map", prev, "-c:v", "libx264", "-preset", "slow",
              "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out))
    return out


def run_item(browser, cfg: dict, item: dict, theme: str, max_frames: int | None,
             only: list[str] | None = None) -> Path:
    clip = item["_kind"] == "clip"
    vp = item.get("viewport", cfg.get("clip_viewport" if clip else "viewport", [1600, 1000]))
    scale = float(item.get("scale", cfg.get("clip_scale" if clip else "scale", 2)))
    d = ml.master_dir("app", item["id"])
    # A clip with `passes` is recorded once per pass (same camera path, a
    # different look each), then cross-faded per `composite`.
    passes = item.get("passes")
    runs = list(passes.items()) if passes else [(theme, [])]
    outs, blocked, errors, version = [], [], [], None
    cam_state = None
    if only and passes:
        # Re-record some passes only: reuse the camera of the full run.
        cam_state = ml.read_meta(d).get("camera")
        first = runs[0]
        runs = [r for r in runs if r[0] in only]
        if not cam_state:
            # Older run without a saved camera: measure it again from the first
            # pass's setup (deterministic for the same data) — check alignment.
            print(f"  {item['id']}: no saved camera — re-measuring from pass {first[0]!r}")
            ctx = new_context(browser, cfg, theme, vp, scale)
            page = ctx.new_page()
            fp = item["path"] + (("&" if "?" in item["path"] else "?") + first[1]["query"]
                                 if isinstance(first[1], dict) and first[1].get("query") else "")
            prepare(page, cfg, {**item, "path": fp})
            cam_state = page.evaluate("() => window.__ruxCam('state')")
            ctx.close()
    t0 = time.time()
    for name, extra in runs:
        ctx = new_context(browser, cfg, theme, vp, scale)
        page = ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)[:200]))
        # A pass is a list of extra actions, or { query = "labels=labels",
        # actions = [...] } — a URL parameter is the most reliable way to set
        # app state (e.g. the viewport's label source) for a whole recording.
        path, extra_actions = item["path"], extra
        if isinstance(extra, dict):
            if extra.get("query"):
                path += ("&" if "?" in path else "?") + extra["query"]
            extra_actions = extra.get("actions", [])
        prepare(page, cfg, {**item, "path": path, "actions": item.get("actions", []) + list(extra_actions)})
        if passes:
            # Same camera for every pass: the first pass's (auto-framed)
            # state is restored exactly in the others.
            if cam_state is None:
                cam_state = page.evaluate("() => window.__ruxCam('state')")
            else:
                page.evaluate("s => window.__ruxCam('restore', s)", cam_state)
                settle(page, 1500)
                if item.get("frame_wait"):
                    page.wait_for_function("s => !document.querySelector(s)", arg=item["frame_wait"],
                                           timeout=120000, polling=200)
        version = page.evaluate("() => { const m = document.body.innerText.match(/ruxd\\s+(\\d+\\.\\d+\\.\\d+)/); return m ? m[1] : null }")
        if not clip:
            out = d / (f"{name}.png" if passes else f"{theme}.png")
            shoot_still(page, item, out)
        else:
            out = record(page, cfg, item, d, name, max_frames)
        outs.append(out)
        blocked += ctx.blocked  # type: ignore[attr-defined]
        ctx.close()
        if passes:
            print(f"    pass {name:<12} → {ml.rel(out)}")
    if clip and passes and only:
        # The other passes are on disk already; rebuild the composite.
        pass
    if clip and passes and item.get("composite"):
        outs.append(composite(item, d))
    meta = ml.read_meta(d)
    meta.update({"id": item["id"], "kind": item["_kind"], "title": item.get("title", ""),
                 "alt": item.get("alt", ""), "source": "app", "url": url_for(cfg, item["path"]),
                 "app_version": version, "viewport": vp, "scale": scale,
                 "recipe": "media/app.toml"})
    if passes:
        meta["camera"] = cam_state
        meta["passes"] = {n: ml.rel(d / f"{n}.{'mp4' if clip else 'png'}") for n, _ in runs}
        meta["composite"] = item.get("composite")
    meta.setdefault("themes", {})[theme] = ml.rel(outs[-1])
    ml.write_meta(d, **meta)
    note = f"  ⚠ blocked writes: {blocked}" if blocked else ""
    note += f"  ⚠ page errors: {errors[:2]}" if errors else ""
    print(f"  {item['id']:<28} {theme:<5} → {ml.rel(outs[-1])}  ({time.time() - t0:.0f}s){note}")
    return outs[-1]


def items(cfg: dict) -> list[dict]:
    out = []
    for kind in ("shot", "clip"):
        for it in cfg.get(kind, []):
            out.append({**it, "_kind": kind})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--theme", choices=["light", "dark", "both"])
    ap.add_argument("--try", dest="try_path", metavar="PATH")
    ap.add_argument("--frames", type=int, help="stop clips after N frames (preview)")
    ap.add_argument("--pass", dest="only", action="append", metavar="NAME",
                    help="re-record only this pass (repeatable), with the saved camera")
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--out", default=None, help="--try: where to write the PNG")
    args = ap.parse_args()
    cfg = ml.load("app")
    defaults = cfg.get("defaults", {})
    cfg = {**defaults, **cfg}
    all_items = items(cfg)
    if args.list:
        for it in all_items:
            print(f"{it['id']:<28} {it['_kind']:<5} {it.get('title', '')}")
        return
    with sync_playwright() as p:
        browser = open_browser(p, cfg, not args.no_proxy)
        if args.try_path:
            theme = args.theme if args.theme in ("light", "dark") else "light"
            ctx = new_context(browser, cfg, theme, cfg.get("viewport", [1600, 1000]), 1)
            page = ctx.new_page()
            prepare(page, cfg, {"path": args.try_path})
            out = Path(args.out or tempfile.gettempdir()) / "capture-try.png"
            if out.is_dir():
                out = out / "capture-try.png"
            page.screenshot(path=str(out))
            print(out)
            print(page.inner_text("body")[:1200])
            return
        chosen = [it for it in all_items if not args.ids or any(it["id"].startswith(i) for i in args.ids)]
        if not chosen:
            sys.exit(f"no recipe matches {args.ids} (see --list)")
        for it in chosen:
            themes = it.get("themes", cfg.get("themes", ["light", "dark"]))
            if args.theme in ("light", "dark"):
                themes = [args.theme]
            for th in themes:
                run_item(browser, cfg, it, th, args.frames, args.only)
        browser.close()


if __name__ == "__main__":
    main()
