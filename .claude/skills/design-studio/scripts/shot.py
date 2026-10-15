#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Screenshot pages of the LIVE `hugo server` — the "look at it" step of the
design-studio loop. No build: it reads whatever the running server (serve.sh)
renders right now, so an edit is visible on the next shot (~1-3 s per page).

One Chromium is launched for the whole run. Every shot:
  - forces the theme via localStorage *before* the page's own theme script
    runs (data-theme="light"|"dark") and matches prefers-color-scheme,
  - waits for `load` and web fonts (not networkidle: video streams never go
    idle),
  - forces every lazy image to load and decode (headless Chromium skips
    off-screen images), disables animations/transitions, emulates
    reduced motion (silent video clips therefore show controls),
  - runs QA checks and prints them as CHECK lines; exit status 3 if any fail:
      * console errors / page errors / failed requests / HTTP >= 400
      * Hugo error overlay (template error) present in the page
      * horizontal overflow (document wider than the viewport; the deepest
        offending elements are named)
      * broken <img> and broken internal links (#broken-link/… markers)

Usage:
  shot.py [PATH ...] [options]
    PATH            site path relative to the site root, e.g. "" (home),
                    "people/", "pitchdeck/". Default: "" (home).
    --all           top-level pages from sitemap.xml (home + each section);
                    skips the per-section fragment pages Hugo also publishes
    --everything    literally every sitemap.xml entry (fragments, pilots, …)
    --theme T       light | dark | both            (default: both)
    --vp V          desktop | tablet | mobile | all (default: desktop,mobile)
                    comma-separated is fine: --vp desktop,tablet
    --full          full-page screenshot (default: first viewport only)
    --selector CSS  screenshot just the FIRST match, e.g. "footer"; in the
                    components gallery the rendered element is the sibling
                    after the snippet: "#example-faq + .faq"
    --each CSS      screenshot EVERY match separately (-01, -02, …), e.g.
                    "main > section" — the way to review a long page on
                    mobile; a --full mobile shot gets shrunk to illegibility
    --scroll-to CSS scroll the element into view before a viewport shot
    --js CODE       evaluate JS in the page before the shot, e.g. open every
                    <details>: "document.querySelectorAll('details')
                    .forEach(d => d.open = true)", or a slide: "goToSlide(4)"
                    (deep links work too: shot.py "pitchdeck/#slide-4")
    --keys KEYS     press real keys before the shot, space-separated
                    Playwright key names, e.g. "Tab Tab Enter" — the way to
                    check :focus-visible rings and keyboard behaviour
    --out DIR       output directory (default: .screenshots/ in the repo)
    --base URL      server URL (default: ask serve.sh, starting it if needed;
                    use with PORT=… serve.sh for a second server)
    --no-checks     skip the QA checks
    --probe CSS     print measurements for every match instead of guessing:
                    size (tap targets), font-size, colour, effective
                    background and WCAG contrast ratio

Output: <out>/<slug>-<theme>-<vp>.png, one path per line on stdout; CHECK
lines and timings on stderr.

Examples:
  shot.py                               # home, both themes, desktop + mobile
  shot.py people/ --theme light --full  # one page, full length
  shot.py "" --selector footer --vp all # just the footer at every width
  shot.py --all --vp desktop --theme dark
  shot.py people/ --vp mobile --each "main > section"
  shot.py people/ --probe "a[aria-label], .people-card p" --theme dark
"""
import argparse
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # outside the dev shell: re-run inside it (~5 s extra)
    import os
    if os.environ.get("SHOT_PY_REEXEC"):
        sys.exit("shot.py: playwright missing even in `nix develop` — check flake.nix")
    os.environ["SHOT_PY_REEXEC"] = "1"
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()
    os.execvp("nix", ["nix", "develop", root, "-c", "python3", *sys.argv])

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900, "scale": 1, "mobile": False},
    "tablet": {"width": 820, "height": 1180, "scale": 2, "mobile": True},
    "mobile": {"width": 390, "height": 844, "scale": 2, "mobile": True},
}

NO_MOTION_CSS = """
*, *::before, *::after {
  animation: none !important;
  transition: none !important;
  scroll-behavior: auto !important;
}
"""

# The Play CDN appends a <style> with its generated utilities once it has run.
TAILWIND_READY_JS = """
() => !window.tailwind || [...document.querySelectorAll('style')]
  .some(s => s.textContent.includes('--tw-'))
"""

LOAD_ALL_IMAGES_JS = """
async () => {
  const imgs = [...document.images];
  imgs.forEach(i => { i.loading = 'eager'; });
  await Promise.all(imgs.map(i => i.complete ? null : new Promise(r => {
    i.addEventListener('load', r, { once: true });
    i.addEventListener('error', r, { once: true });
    setTimeout(r, 8000);
  })));
  // Headless Chromium skips decoding off-screen images; force it so
  // full-page and element shots never show empty frames.
  await Promise.all(imgs.map(i => i.decode ? i.decode().catch(() => null) : null));
}
"""

QA_JS = """
() => {
  const doc = document.documentElement;
  const overflow = doc.scrollWidth - doc.clientWidth;
  const offenders = [];
  if (overflow > 1) {
    const wide = [...document.querySelectorAll('body *')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.right > doc.clientWidth + 1 && r.width > 0;
    });
    // Only the deepest: an ancestor is wide *because of* its child.
    for (const el of wide.filter(e => !wide.some(o => o !== e && e.contains(o))).slice(0, 5)) {
      const id = el.id ? '#' + el.id : '';
      const cls = (typeof el.className === 'string' && el.className.trim())
        ? '.' + el.className.trim().split(/\\s+/).slice(0, 3).join('.') : '';
      const text = (el.innerText || '').trim().slice(0, 40);
      offenders.push(el.tagName.toLowerCase() + id + cls + (text ? ` "${text}"` : ''));
    }
  }
  const brokenImgs = [...document.images]
    .filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src'))
    .map(i => i.getAttribute('src'));
  const hugoError = !!document.querySelector('.hugo-error, #hugo-error, [data-hugo-error]')
    || /Failed to render|execute of template failed/.test(document.body ? document.body.innerText : '');
  const brokenLinks = [...document.querySelectorAll('a[href^="#broken-link"]')]
    .map(a => a.getAttribute('href').replace('#broken-link/', ''));
  return { overflow, offenders, brokenImgs, brokenLinks, hugoError,
           theme: doc.getAttribute('data-theme') };
}
"""


PROBE_JS = """
(sel) => {
  const parse = c => (c.match(/[\\d.]+/g) || []).map(Number);
  const lum = ([r, g, b]) => {
    const f = v => (v /= 255) <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const bgOf = el => {
    for (let e = el; e; e = e.parentElement) {
      const c = parse(getComputedStyle(e).backgroundColor);
      if (c.length >= 3 && (c.length < 4 || c[3] > 0.5)) return c.slice(0, 3);
    }
    return [255, 255, 255];
  };
  return [...document.querySelectorAll(sel)].slice(0, 20).map(el => {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    let fg = parse(cs.color);
    const bg = bgOf(el);
    if (fg.length === 4) fg = fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3]));
    const op = parseFloat(cs.opacity);
    if (op < 1) fg = fg.map((v, i) => v * op + bg[i] * (1 - op));
    const [a, b] = [lum(fg), lum(bg)].sort((x, y) => y - x);
    return {
      el: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
      text: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 30),
      size: `${Math.round(r.width)}x${Math.round(r.height)}`,
      font: cs.fontSize + '/' + cs.fontWeight,
      fg: 'rgb(' + fg.map(Math.round) + ')', bg: 'rgb(' + bg + ')',
      contrast: ((a + 0.05) / (b + 0.05)).toFixed(2),
    };
  });
}
"""


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True)
    return Path(out.stdout.strip())


def server_url() -> str:
    serve = Path(__file__).with_name("serve.sh")
    out = subprocess.run(["bash", str(serve), "start"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        sys.exit("shot.py: could not start hugo server (serve.sh)")
    return out.stdout.strip().splitlines()[-1]


def sitemap_paths(base: str, everything: bool) -> list[str]:
    with urlopen(urljoin(base, "sitemap.xml"), timeout=10) as r:
        tree = ET.fromstring(r.read())
    base_path = urlparse(base).path
    paths = []
    for loc in tree.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        p = urlparse(loc.text.strip()).path
        if p.startswith(base_path):
            p = p[len(base_path):]
        # Section "sub-pages" (e.g. people/01-people/) are fragments rendered
        # into their list page; --all keeps only home + section pages.
        if everything or p.strip("/").count("/") == 0:
            paths.append(p)
    return sorted(set(paths))


def slug(path: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-")
    return s or "home"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--everything", action="store_true")
    ap.add_argument("--theme", default="both", choices=["light", "dark", "both"])
    ap.add_argument("--vp", default="desktop,mobile")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--selector")
    ap.add_argument("--each")
    ap.add_argument("--probe")
    ap.add_argument("--scroll-to")
    ap.add_argument("--js")
    ap.add_argument("--keys")
    ap.add_argument("--out")
    ap.add_argument("--base")
    ap.add_argument("--no-checks", action="store_true")
    a = ap.parse_args()

    t0 = time.monotonic()
    base = a.base or server_url()
    if not base.endswith("/"):
        base += "/"
    out = Path(a.out) if a.out else repo_root() / ".screenshots"
    out.mkdir(parents=True, exist_ok=True)

    if a.all or a.everything:
        paths = sitemap_paths(base, a.everything)
    else:
        paths = a.paths or [""]
    themes = ["light", "dark"] if a.theme == "both" else [a.theme]
    vps = list(VIEWPORTS) if a.vp == "all" else [v.strip() for v in a.vp.split(",")]
    for v in vps:
        if v not in VIEWPORTS:
            sys.exit(f"shot.py: unknown viewport {v!r} (desktop|tablet|mobile|all)")

    failures = 0
    with sync_playwright() as pw:
        # channel="chromium": the full Nix-provided Chromium in new headless
        # mode (the dev shell ships browsers-chromium, no headless-shell build).
        browser = pw.chromium.launch(channel="chromium")
        t_launch = time.monotonic()
        for theme in themes:
            for vp in vps:
                spec = VIEWPORTS[vp]
                ctx = browser.new_context(
                    viewport={"width": spec["width"], "height": spec["height"]},
                    device_scale_factor=spec["scale"],
                    is_mobile=spec["mobile"],
                    has_touch=spec["mobile"],
                    color_scheme=theme,
                    reduced_motion="reduce",
                )
                # reusex-theme = the product/new-site key; theme = the old site's key.
                ctx.add_init_script(f"try {{ localStorage.setItem('reusex-theme', '{theme}'); "
                                    f"localStorage.setItem('theme', '{theme}'); }} catch (e) {{}}")
                for path in paths:
                    page = ctx.new_page()
                    problems: list[str] = []
                    page.on("console", lambda m, p=problems: m.type == "error" and p.append(f"console: {m.text[:200]}"))
                    page.on("pageerror", lambda e, p=problems: p.append(f"pageerror: {str(e)[:200]}"))
                    # Media is aborted by design (range requests, no H.264 in
                    # open-source Chromium): only real failures count.
                    page.on("requestfailed", lambda r, p=problems: r.failure != "net::ERR_ABORTED"
                            and p.append(f"requestfailed: {r.url} ({r.failure})"))
                    page.on("response", lambda r, p=problems: r.status >= 400 and p.append(f"HTTP {r.status}: {r.url}"))

                    url = urljoin(base, path.lstrip("/"))
                    try:
                        page.goto(url, wait_until="load", timeout=30000)
                        page.evaluate("document.fonts.ready")
                        page.wait_for_function(TAILWIND_READY_JS, timeout=10000)
                    except Exception as e:  # noqa: BLE001 - report, keep going
                        problems.append(f"goto: {e}")
                    page.add_style_tag(content=NO_MOTION_CSS)
                    # Lazy images: force them all to load, so full-page and element
                    # shots never show empty frames.
                    page.evaluate(LOAD_ALL_IMAGES_JS)
                    if a.js:
                        try:
                            page.evaluate(a.js)
                            page.wait_for_timeout(300)
                        except Exception as e:  # noqa: BLE001
                            problems.append(f"--js failed: {str(e)[:200]}")
                    if a.keys:
                        for key in a.keys.split():
                            page.keyboard.press(key)
                        page.wait_for_timeout(100)
                    if a.scroll_to:
                        if page.locator(a.scroll_to).count():
                            page.locator(a.scroll_to).first.scroll_into_view_if_needed()
                        else:
                            problems.append(f"--scroll-to {a.scroll_to!r}: no such element")
                    page.wait_for_timeout(100)

                    png = out / f"{slug(path)}-{theme}-{vp}.png"
                    shots = [png]
                    sel = a.selector or a.each
                    if a.probe:
                        for row in page.evaluate(PROBE_JS, a.probe):
                            print(f"PROBE {slug(path)} {theme} {vp}: " + "  ".join(f"{k}={v}" for k, v in row.items()))
                        shots = []
                    elif sel and not page.locator(sel).count():
                        problems.append(f"selector {sel!r}: no such element")
                        shots = []
                    elif a.selector:
                        png = shots[0] = out / f"{slug(path)}-{slug(sel)}-{theme}-{vp}.png"
                        page.locator(sel).first.scroll_into_view_if_needed()
                        page.wait_for_timeout(50)
                        page.locator(sel).first.screenshot(path=str(png))
                    elif a.each:
                        loc = page.locator(sel)
                        shots = []
                        for i in range(loc.count()):
                            el = loc.nth(i)
                            if not el.is_visible() or (el.bounding_box() or {}).get("height", 0) < 2:
                                continue  # hidden or empty: nothing to look at
                            p = out / f"{slug(path)}-{slug(sel)}-{i + 1:02d}-{theme}-{vp}.png"
                            el.scroll_into_view_if_needed()
                            page.wait_for_timeout(50)
                            el.screenshot(path=str(p), timeout=10000)
                            shots.append(p)
                    else:
                        page.screenshot(path=str(png), full_page=a.full)

                    if not a.no_checks:
                        qa = page.evaluate(QA_JS)
                        if qa["theme"] != theme:
                            problems.append(f"theme is {qa['theme']!r}, expected {theme!r}")
                        if qa["hugoError"]:
                            problems.append("Hugo template error rendered in page (see serve.sh log)")
                        if qa["overflow"] > 1:
                            problems.append(f"horizontal overflow {qa['overflow']}px: {', '.join(qa['offenders'])}")
                        for href in qa["brokenLinks"]:
                            problems.append(f"broken link (page does not exist): {href}")
                        for src in qa["brokenImgs"]:
                            problems.append(f"broken img: {src}")
                    # The Tailwind Play CDN always warns about production use; not ours to fix here.
                    # "Failed to load resource" console lines carry no URL; every real
                    # 4xx/5xx is already reported with its URL by the response
                    # handler, and the rest is the favicon (bead reusex-page-k4m).
                    problems = [p for p in problems if "cdn.tailwindcss.com should not be used" not in p
                                and "Failed to load resource" not in p]
                    if a.no_checks:
                        problems = []
                    for p in problems:
                        print(f"CHECK FAIL {png.name}: {p}", file=sys.stderr)
                    failures += bool(problems)
                    for p in shots:
                        print(p)
                    page.close()
                ctx.close()
        browser.close()
    t_end = time.monotonic()
    print(f"shot.py: browser {t_launch - t0:.2f}s, shots {t_end - t_launch:.2f}s, "
          f"{failures} shot(s) with CHECK failures", file=sys.stderr)
    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
