---
name: app-capture
description: Screenshots and screen recordings of the ReUseX app (app.reuse-x.com) for the website, pitch deck, LinkedIn and the promo video — read-only, repeatable from recipes. Use whenever someone wants new or updated product screenshots, a product video/clip/GIF, "show the app on the site", "refresh the images after the new release", a 3D viewport orbit, or any picture of the real product; also when app.reuse-x.com is unreachable from this machine (office web filter) and captures need the Tailscale proxy.
---

# App capture — real product imagery from app.reuse-x.com

Every app image on the site comes from a **recipe** in `media/app.toml`, so
after a new app release one command re-shoots everything. Masters go to the
media library (`$REUSEX_MEDIA`, see the `media-library` skill); the site gets
web derivatives via `derive.py`.

## Before the first capture

1. **Network.** The office web filter blocks app.reuse-x.com ("high-risk"). Use
   the private proxy — a second, userspace tailscaled whose exit node is
   beagle; the system tailscale and its exit node are never changed:
   ```bash
   bash .claude/skills/app-capture/scripts/capture-proxy.sh up      # status | down
   ```
   First time it prints a login URL: the owner approves node
   `<host>-capture` once. Elsewhere (no filter) pass `--no-proxy`.
2. **Login.** The app session cookie value lives in
   `~/.config/reusex-capture/session` (0600, never in the repo) — or
   `$REUSEX_SESSION`. When captures land on the login page, ask the owner for
   a fresh `__Host-ruxd_session_8080` value (browser dev tools → cookies).
3. **Shell.** Dev shell (`nix develop`): Playwright + Chromium + ffmpeg.

## Run

```bash
S=.claude/skills/app-capture/scripts
python3 $S/capture.py --list                      # every recipe
python3 $S/capture.py                             # everything (both themes)
python3 $S/capture.py viewport --theme light      # ids by prefix
python3 $S/capture.py --try "/sager/{case}/rapport" --out /tmp   # look around
python3 $S/capture.py --frames 30 orbit           # preview a clip quickly
```

Then **look at every PNG/poster** (Read tool), and contact-sheet clips:
`ffmpeg -i clip.mp4 -vf "select='not(mod(n\,48))',scale=480:-2,tile=3x3" -frames:v 1 sheet.jpg`.

## Writing a recipe (`media/app.toml`)

`[[shot]]` = still, `[[clip]]` = video. Keys: `id`, `title`, `alt` (real alt
text — it becomes the site's), `path` (`{case}` = defaults.case), optional
`viewport`, `scale`, `themes`, `selector` (crop to one element, e.g.
`canvas`), `actions`, `full`.

Actions (setup, run in order): `click`, `check`/`uncheck`, `select`+`option`,
`hover`, `press`, `wait` (ms), `wait_for` (selector visible), `gone`
(selector absent — e.g. streaming progress), `idle` (network idle + ms),
`scroll`, `drag` (`from`, `by`, `steps`), `wheel` (`dy`, `steps`), `hide`
(overlay chrome), `eval`, `use` (a named list in `[preludes]`).

3D camera (viewport): a capture-only hook turns the OrbitControls damping
off and exposes `window.__ruxCam`, so camera moves are numeric and exactly
repeatable — never orbit by mouse drags in recordings (damping makes them
depend on frame timing). The hook also disables three.js frustum culling
(the viewport's bounding spheres go stale while streaming, so walls vanished
at some angles — product bead d8u). Actions: `camera = { azimuth, elevation, distance }`
(degrees around the target; distance multiplies) and `frame = { fill, x, y }`
(measure where the model is on screen, robust to stray points, centre it and
size it to `fill` of the larger canvas extent).

Clips add `timeline` — segments, each one eased step per frame, then a
screenshot, so motion is smooth regardless of GPU speed: `turn`
(`deg`, optional `el`, `dolly` — numeric orbit; 360° linear loops
seamlessly), `hold`, `orbit`/`pan`/`zoom` (mouse — UI demos only),
`scroll`, `cursor` (drawn pointer; set `cursor = true`), `do` (actions
mid-clip), each with `seconds` and optional `ease = "linear"`.
`frame_wait` = a selector that must be gone before each frame is shot.
Clip default: 1920×1080-ish canvas, 30 fps, H.264 master CRF 12 + poster.

**Passes** (shots and clips): `passes = { rgb = {}, labels = { query =
"labels=labels" }, … }` records the same item once per pass — the camera is
measured in the first pass and restored exactly in the others, so
`rgb.png`/`labels.png` line up pixel for pixel (before/after sliders) and
`rgb.mp4`/`labels.mp4`/… can be cut or cross-faded in an editor. Set the
viewport's label source with the URL parameter (`query`), not by clicking
the colour controls — clicked state did not survive a full turn. A clip with
`composite = [[pass, fade-in start s], …]` + `fade` also gets
`composite.mp4`. Re-record one pass with `capture.py orbit --pass labels` (the
camera is saved in meta.json, the composite is rebuilt). `frame_check = 0.7`
re-shoots any frame that draws far less than the recent ones — the viewport
sometimes drops points for a moment (bead d8u).

## House rules

- **Read-only.** The browser aborts every non-GET `/api` request. Never write
  a recipe that clicks "Generér", "Send", "Upload", "Kør" … — capture the
  state that is there; if the case needs better data, ask the owner.
- **Masks** (defaults.mask): the account e-mail → `demo@reuse-x.com`;
  "SAM3" is not cleared for public use (bead l2c) → removed. Add masks, never
  edit screenshots by hand.
- **People/privacy:** look at every frame for faces, names, addresses of
  private persons. The demo case is the LINK Arkitektur office (public
  address; owner's own name as author is fine).
- **GPU:** Chromium runs with ANGLE on EGL (NVIDIA). If WebGL comes up as
  SwiftShader, 3D shots time out — check `nvidia-smi` and the `--use-angle`
  flag.
- **The UI is Danish**; site copy is English — say what a screenshot shows in
  the caption/alt, don't translate the UI.
- Known product gap: the app header wordmark renders "REUSEX" in uppercase
  (bead 1g0) — crop the header out of hero shots.

After capturing: `derive.py` (media-library skill), then place on the site
with the design-studio loop. Update the bead you're working.
