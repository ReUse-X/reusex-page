# Site map — where things live and what bites

## Stack

- **Hugo** (dev shell: nixpkgs `hugo`, currently 0.16x extended). CI
  (`.github/workflows/deploy-hugo.yml`) pins **0.146.0** — don't use template
  functions newer than that without bumping the workflow too.
- **Tailwind Play CDN** (`<script src="https://cdn.tailwindcss.com">` in
  `themes/reusex/layouts/partials/head.html`): classes are compiled in the
  browser at run time. No Tailwind build step, no purge. (`tailwindcss_4` is
  in the dev shell but nothing uses it yet.)
- **Fonts**: Inter + Space Grotesk from Google Fonts. Body uses
  `var(--font-display)` = Inter.
- **JS**: `themes/reusex/assets/js/main.js` via `js.Build` (theme toggle,
  mobile menu, fade-in on scroll, before/after slider). The pitch deck has its
  own inline script in `layouts/pitchdeck/list.html` (`goToSlide(n)`,
  1-based; `nextSlide()`, arrow keys).
- **Deploy**: push to `main` → GitHub Pages at
  `https://linkarkitektur.github.io/reusex-page/` — note the **/reusex-page/
  path prefix**. Use `relURL`/`.RelPermalink`/`partials/smart-url.html`,
  never a root-absolute `/foo` (it breaks on Pages).

## Template lookup (root overrides theme)

| What | File |
|---|---|
| Page shell (head/header/footer) | `themes/reusex/layouts/baseof.html` — the 8 `layouts/*/baseof.html` copies are byte-identical duplicates |
| Head, CSS/JS includes, theme pre-paint script | `themes/reusex/layouts/partials/head.html` (the `head/css.html`, `head/js.html` partials are unused) |
| Header / menu / footer | `themes/reusex/layouts/partials/{header,menu,footer}.html`; menu items in `hugo.toml [menus]`, footer in `[params.footer]` |
| Home page | `themes/reusex/layouts/home.html`, content from `content/sections/*.md` (hero, challenges, solution, stats, testimonial, cta, logos, blog) via `site.GetPage "sections/x"` |
| Section pages (Vision, Solution, How it Works, Roadmap, People, Contact, Research) | `layouts/<section>/list.html` ranging over `content/<section>/NN-*.md` ordered by `order` |
| Pitch deck | `layouts/pitchdeck/list.html` (829 lines: own `<style>` + script), slides `content/pitchdeck/NN-*.md` |
| Pilots / posts | `layouts/pilots/single.html`, `layouts/post/single.html` |
| Shared partials | `layouts/partials/icon.html` (named SVG icons), `layouts/partials/timeline.html` |

## Content model (section sub-pages)

Each `content/<section>/NN-name.md` is one band of its section page:

- `order:` — position on the page.
- `colorScheme: 1 | 2 | 3` — which section theme the band uses (default 2).
  The list templates branch on it (`if eq $colorScheme 1 … else if …`), so
  a band's look is often defined three times — change all branches.
- `layout:` — variant within a section (e.g. `cards`, `research-card`).
- Variant-specific params: `cards:` (people), `steps:` (timeline), `points:`
  (pitch deck), `desktopColumns:` …

Hugo also **publishes each sub-page standalone** (`/people/01-people/` etc.,
in sitemap.xml) — they are fragments, not real pages. `shot.py --all` skips
them; `--everything` includes them.

## Tokens (`themes/reusex/assets/css/main.css`)

Three blocks define values:

| Block | Seen when |
|---|---|
| `[data-theme="light"]` | light mode — off-white, black text/borders |
| `[data-theme="dark"]` | dark mode — dark grey (#343634 family). **This is what dark-mode visitors see.** |
| `:root` | base values ("Nordic Deep-Tech" navy) — only visible with JS disabled, because the pre-paint script in head.html always sets `data-theme` to `light` or `dark` |

Main groups: global (`--surface-bg`, `--border`, `--heading-text`,
`--body-text`, `--muted-text`, `--link`, `--highlight`, `--primary-teal` …),
per-band `--section1-*` (teal/hero band), `--section2-*` (main content),
`--section3-*` (anchor/footer band), `--header-bg`, `--footer-bg`,
`--cta-bg/-text`, `--pitchdeck-accent(-text)`, `--icon-color`,
`--timeline-*`. Older docs: `README-Color-Scheme.md`,
`README-Light-Theme-Presentation.md` (partly out of date — trust main.css).

`token_lint.py` treats any `--x:` defined in main.css **or** in a template
(component-local props like timeline.html's `--gap`, content-driven ones like
home.html's `--hero-bg-light`) as known.

## Theme switching

`localStorage.theme` → else `prefers-color-scheme` → sets
`<html data-theme>` before paint (head.html), toggled by the header button
(main.js). `shot.py` forces it by seeding localStorage, so the screenshot is
the real switched theme, not a CSS emulation.

## Gotchas (recorded)

- **Tailwind's CSS wins ties.** The Play CDN injects its `<style>` after
  main.css, so a main.css rule with the same specificity as a utility on the
  element loses (people `desktopColumns` vs `md:grid-cols-2`). Raise the
  main.css selector's specificity or drop the utility — don't add
  `!important`.
- **Section schemes 2 and 3 are the same colour** in both themes
  (`--section2-bg` = `--section3-bg`), so bands don't visually alternate yet.
- **Missing images vanish silently.** Templates use
  `Resources.GetMatch`/`with`, so a wrong filename in front matter (e.g.
  `.jpg` vs `.svg`) just drops the `<img>`; shot.py's broken-image check
  can't see it. Check the content path exists.
- **Section anchors**: Roadmap bands get ids from `urlize` of the title;
  People/most others have none — use `--each "main > section"` or a
  `:nth-of-type` selector rather than guessing `#id`.
- **Drafts**: several sub-pages are `draft: true` (e.g. people intro and
  board). The production build omits them; serve.sh does too unless
  `DRAFTS=1`.

- **Tailwind palette classes ignore the theme.** `bg-white`, `text-gray-600`
  … look the same in both themes. main.css has a few light-mode patches
  (`[data-theme="light"] .text-white { … }`) — a symptom, not a pattern to
  extend. Use tokens.
- **Hero background in dark mode**: `[data-theme="dark"] .hero-section` also
  uses `--hero-bg-light` (set from `content/sections/hero.md heroBg`), so the
  hero is light grey in dark mode.
- **No `<link rel="icon">`**: browsers request `/favicon.ico` at the domain
  root → 404 on every page (it exists at `/reusex-page/favicon.ico`).
  shot.py reports it as `console: Failed to load resource … 404`.
- **Fade-in on scroll** (main.js IntersectionObserver adds
  `animate-fadeInUp`) — shot.py disables animations; a user's browser won't.
- **Hero video** (`static/video/*.mp4`) streams: never wait for network idle.
  Open-source Chromium can't play H.264, so the video frame is blank in
  screenshots; check it in a real browser if it matters.
- **`hugo.toml` deprecations** under Hugo ≥0.158 (`languageCode`,
  `.Language.LanguageCode/LanguageDirection`) — harmless warnings in the
  server log, but CI's 0.146 doesn't know the replacements yet.
- **Big binaries**: `static/` is ~46 MB (video 27 MB). Don't add more
  without asking; compress images before committing.
- **Dead head partials**: `head.html` inlines the CSS/JS includes;
  `partials/head/css.html` and `head/js.html` hold the same code but nothing
  calls them. Edit `head.html`.

## Server & tooling

- `scripts/serve.sh` — one `hugo server` (in-memory, live reload,
  `--buildDrafts`), bound to the Tailscale IP (`HOST=` to override, `PORT=`
  for a second worktree). Log: `.screenshots/hugo-server.log`.
- `scripts/shot.py` — Playwright/Chromium from the dev shell
  (`PLAYWRIGHT_BROWSERS_PATH` is set by flake.nix); re-execs itself under
  `nix develop` if run outside it. Prefer `--probe`/`--js` over a one-off
  script; if you must write one: `pw.chromium.launch(channel="chromium")`
  (the dev shell has no headless-shell build) and don't run it with
  `python3 -I` (that hides the dev shell's site-packages).
- `scripts/token_lint.py` — colour-literal / unknown-token lint.
- `.screenshots/` is gitignored.
