---
name: media-library
description: The ReUseX media library — where screenshots, recordings, infographics and imported footage live as full-quality masters (reusable for the promo video, deck, LinkedIn, print) and how web files are derived from them for the site. Use whenever you add, find, reuse, convert, trim or resize an image or video; import material from ~/Videos or other repos; prepare assets for a promo video, LinkedIn, or a slide; or need to know which picture on the site came from where and whether it is cleared for public use.
---

# Media library — masters outside git, recipes inside

```
$REUSEX_MEDIA (default ~/Videos/reusex-media)      ← NOT in git, large files
  app/<id>/            light.png dark.png  <theme>.mp4 -poster.png  meta.json
                       (passes: <pass>.png / <pass>.mp4 + composite.mp4)
  infographics/<id>/   <theme>.mp4 -poster.png -final.png           meta.json
  imports/<id>/        master.<ext>                                 meta.json
  out/<profile>/…      non-site outputs (linkedin, deck, promo)
repo
  media/app.toml           capture recipes        (app-capture skill)
  media/infographics.toml  + media/infographics/*.html (infographics skill)
  media/imports.toml       external material + clearance
  media/web.toml           which master → which output file
  assets/media/…           web derivatives the site uses (small, in git)
```

Masters are **disposable and reproducible**: recipes rebuild them. Every
master folder has `meta.json` (source, recipe, app version, date, alt,
clearance). A promo-video editor (kdenlive) can point straight at
`$REUSEX_MEDIA` — clips are 1920×1080 H.264 CRF 12, stills 2× PNG.

## Commands (dev shell)

```bash
S=.claude/skills/media-library/scripts
python3 $S/import.py --list        # external material + clearance
python3 $S/import.py               # copy into imports/ with provenance
python3 $S/derive.py --check       # missing masters / stale outputs
python3 $S/derive.py               # build what is stale (→ assets/media/)
python3 $S/derive.py --profile linkedin
python3 $S/clipcheck.py ~/Videos/reusex-media/app/orbit/*.mp4   # single-frame flicker (exit 1)
```

## `media/web.toml` entries

```toml
[[out]]
from = "app/hero/labels.png"             # inside $REUSEX_MEDIA
to = "media/hero-labels.webp"            # inside assets/ (profile site)
width = 2400                             # Hugo makes the srcset from this

[[out]]
from = "app/orbit/composite.mp4"
to = "media/orbit.mp4"                   # small silent H.264 for <video>
poster = "media/orbit-poster.webp"
width = 1280                             # crf 27 default; start/duration trim
```
`crop = [1200, 627]` crops to an aspect (centred), `pad = [9, 19.5]` letterboxes
instead (black — invisible on scan footage) — LinkedIn and Open Graph
images (profile `linkedin`, bead 9b8; OG images, bead yzn).

## Rules

- **Clearance.** `owner-check` imports never go on the public site until the
  owner says so (update `clearance` in imports.toml, note it in the bead).
  Nothing from the confidential pitch material, ever.
- **Web budgets:** a still ≤ ~400 KB webp at 2400 px; a loop ≤ ~3 MB
  (1280 px, ≤ 15 s). Web media in `assets/media/` is stored in Git LFS
  (`.gitattributes`); masters stay out of git entirely.
- **One theme per web image** unless the element supports both: product
  screenshots in the app's light theme, 3D/scan imagery on the dark canvas.
- Don't hand-edit derivatives: change the master/recipe and re-derive.
- New material type or tool? Extend these scripts and this file.
