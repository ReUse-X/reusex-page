---
name: infographics
description: Make animated infographics and explainer diagrams for ReUseX — live, native HTML elements on the website (sharp at any size, theme-aware, responsive) that are also rendered frame-exact to MP4 loops and stills for the pitch deck, LinkedIn and the promo video. Use whenever someone asks for an infographic, an animated diagram, an explainer animation, a chart or figure "that moves", a visual for a stat or a process (scan → AI → inventory, timelines, before/after), or a still graphic for a post or slide.
---

# Infographics — one source, live on the site and rendered to video

Each infographic is **one ES module** in the theme:
`themes/reuse-x/assets/js/infographics/<id>.js`. It is used

- **on the site** by the `infographic` element
  (`{{< infographic name="<id>" alt="…" caption="…" >}}`) — drawn natively in
  the page by `assets/js/infographic.js`: scaled to its box (text and canvas
  stay sharp), tall layout below 640 px, plays while in view, redraws on a
  theme switch, complete still for reduced motion, poster image without JS;
- **for video** by `render.py`, through the thin wrapper
  `media/infographics/<id>.html` (recipe in `media/infographics.toml`).

## The module contract (see `lib.js`)

```js
export const duration = 12;          // loop length (s); state at duration == state at 0
export const still = 10.5;           // most complete frame: reduced motion, posters
export const layouts = { wide: { w: 1920, h: 1080 }, tall: { w: 640, h: 1300 } };
export function mount(stage, layout) { /* build DOM in stage px */ return renderAt; }
// renderAt(t): a pure function of t — seeded randomness only, no timers.
```

- Lay out in **stage px** (absolute positions per layout); the runtime
  scales the stage. Canvas: draw with `ctx.setTransform(k…)`,
  `k = canvas.width / cssWidth` — the runtime sizes canvases to real pixels.
- **Tall layout** for phones: 640 px wide stage, text ≥ 22 px (≈ 12 px on a
  390 px screen). Reflow (vertical timeline, list under the picture) rather
  than shrinking the wide one.
- **Colours: tokens only** (`var(--color-…)`, component hues
  `var(--viz-floor)` … in `site-tokens.css`). Read token values with
  `token(stage, '--x')` when drawing on canvas, and re-read when
  `stage.dataset.themeStale` is set (theme switch). Scan imagery sits on
  `--color-canvas` (dark in both themes); page-surface pieces follow the theme.
- Use only **cleared** content (site, public deck, documented figures). No
  invented numbers — illustrative quantities are bars. Brand name via `brand`
  from `lib.js` (never "REUSEX").
- New module: register it in `assets/js/infographic.js` (REGISTRY) and in the
  `infographic` element's `name` enum, add a wrapper html (copy one) and a
  recipe.

## Look, then render

```bash
python3 .claude/skills/design-studio/scripts/shot.py / --each "[data-infographic]"   # live element, both themes, desktop + mobile
S=.claude/skills/infographics/scripts
python3 $S/render.py --still 5.5 --layout tall --out /tmp pipeline   # one frame
python3 $S/render.py pipeline                                          # all themes × layouts → video
```

render.py serves the repo on a local HTTP port (module imports don't work
from file://), seeks `renderAt(t)` frame by frame → `$REUSEX_MEDIA/
infographics/<id>/<theme>[-tall].mp4`, `-poster.png`, `-final.png`. The
site's no-JS fallback is `assets/media/<id>-poster.webp` (derive.py).
