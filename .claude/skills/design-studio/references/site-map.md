# Site map — where things live and what bites

## Stack

- **Hugo** from the flake (dev shell and CI use the same version; CI builds
  with `nix develop .#ci`). Theme `themes/reuse-x`, new template system
  (`layouts/_partials`, `_shortcodes`, `_markup`).
- **No Node/npm/CDN.** CSS: plain modern CSS (native nesting) bundled by
  `css.Build` from `assets/css/main.css` (an `@import` list). JS: vanilla
  modules bundled by `js.Build` from `assets/js/main.js`.
- **Fonts:** Oswald + Archivo, self-hosted in `themes/reuse-x/static/fonts/`
  (OFL, licences next to them); `css.Build` treats `/fonts/*` as external.
- **Hosting:** GitHub Pages at `https://reuse-x.com/` (root, no path
  prefix), `static/CNAME`. The app is `https://app.reuse-x.com/`
  (`params.app_url`).
- **Languages:** English in `content/en/`; Danish configured in `hugo.toml`
  but disabled until `content/da/` exists. UI strings in
  `themes/reuse-x/i18n/en.yaml`.

## Content model — content says WHAT, templates decide HOW

| Concern | Lives in |
|---|---|
| Page copy | `content/en/<page>/_index.md` (section pages) or `…/index.md` (leaf bundles, e.g. each pilot) |
| Front matter | ≤ 10 lines: `title`, `description`, `layout` (landing \| article \| deck), `draft`, `date`, `aliases`, `weight` |
| Navigation | `hugo.toml` `[menus]` (main + footer with parent columns) — never in pages |
| Lists of things | `data/people.yaml` (team/board, `draft: true` hides), `partners.yaml`, `contact.yaml`, `socials.yaml` |
| Images / video | `assets/images/`, `assets/videos/`, `assets/people/`, `assets/partners/` (or next to a page in its bundle) — referenced as `image="images/x.jpg"`; the image partial resizes them |
| Design | `themes/reuse-x/` only |

Layout defaults: home and section pages → `landing`; leaf pages →
`article`; `layout: deck` → the pitch deck.

Content lint (`scripts/content_lint.py`) enforces front matter keys/length,
valid layouts, known element names and **no hand-written HTML** (Goldmark
`unsafe = true` is on only so elements can nest).

## Theme map (`themes/reuse-x/`)

| What | File |
|---|---|
| Shell | `layouts/baseof.html`; `_partials/head.html` (meta, theme pre-paint, CSS/JS), `header.html`, `footer.html`, `wordmark.html` |
| Page layouts | `layouts/{home,section,landing,page,article,deck}.html` → `_partials/layout/{landing,article,deck}.html` |
| Elements | `layouts/_shortcodes/*.html` — each starts with a doc comment (params, inner, example) |
| Element plumbing | `_partials/validate.html` (param checks → `errorf` with file:line), `markdown.html` (nesting-safe inner Markdown), `link.html` (pages / `app:` / external / mailto), `image.html` (webp srcset, w/h, required alt), `actions.html` (button pairs), `icon.html` (the one icon registry), `brand-text.html` (naming rule), `frontmatter-check.html` |
| Markdown headings | `_markup/render-heading.html` (anchors + naming rule) |
| Tokens | `assets/css/tokens.css` (vendored from rux-frontend, never edit; `scripts/sync-tokens.sh`), `assets/css/site-tokens.css` (display type, widths, bands, deck canvas — all colours alias product tokens) |
| CSS | `assets/css/base/` (fonts, reset, typography), `layouts/` (site frame, flow, landing, article, deck), `components/` (one file per element) |
| JS | `assets/js/{theme,menu,before-after,video,deck}.js` |

## How layout works (the "flow" grid)

`.flow` is a breakout grid: children sit in the content column; anything
that is not `.element` or `.band` is held to the prose measure; `.band`
spans the full width. Landing pages are a `.flow`; each band (section,
hero, cta) is itself a `.flow`. Consequences:

- A new element's root **must** carry `class="element element--<name>"`
  (or be a `band …` + `flow` if it is a full-width band), otherwise it is
  squeezed to the prose width.
- Band backgrounds alternate automatically (`.band--plain` nth-child);
  `hero` (navy), `cta` (accent) and canvas-type media own their look.

## Writing a new element (checklist)

1. `layouts/_shortcodes/<name>.html`, starting with the doc comment
   (purpose, params, inner, example).
2. First line of logic: `partial "validate.html" (dict "ctx" . "named" … "required" … "enums" … "inner" …)`.
   Never accept design params (colour, tone, columns, size …) — validate
   rejects them.
3. Inner Markdown: `partial "markdown.html" (dict "page" .Page "inner" .Inner)`
   — pass `.Inner` explicitly (Hugo only treats a shortcode as taking inner
   content if its own template mentions `.Inner`).
4. Output must contain **no blank lines** (they break the parent's HTML
   block when elements nest) — use `{{- -}}` trimming.
5. Links via `link.html`, images via `image.html`, icons via `icon.html`.
6. CSS in `assets/css/components/<name>.css`, imported in `main.css`;
   tokens only (`token_lint.py`).
7. Add a snippet `content/en/components/examples/<name>.txt` and an
   `{{< example "<name>" >}}` line on the gallery page.

## Naming rule (product name)

Headings are uppercase (Oswald); "REUSEX" reads "reu-SEX". The
`brand-text` partial wraps any "ReUseX"/"reusex"/"reuse-x" in headings and
titles in `<span class="brand">` (exempt from `text-transform`). The text
wordmark sets ReUse and X apart. Never uppercase the name as one word in a
template.

## Gotchas (recorded)

- **Mixed params:** Hugo can't mix positional and named shortcode params —
  `card`/`step` take `title="…"`; only `stat "40 %"` is positional.
- **Self-closing:** an element whose template mentions `.Inner` must be
  closed or self-closed (`{{< media … />}}`) when used without content.
- **Broken internal links** don't stop the build: the link partial warns
  and renders `#broken-link/<path>`; shot.py reports them as CHECK FAIL.
- **Aliases** of pages added while the server runs only appear after
  `serve.sh restart`.
- **`zoom`** scales the deck canvas (it also scales layout, so centring
  works); the canvas is 1000×562.5 (`--deck-canvas-*`).
- **Theme key:** `localStorage['reusex-theme']` = light | dark | system,
  same as the app; light is the default.
- **Headless screenshots:** shot.py forces lazy images to load and decode
  (headless Chromium skips off-screen images) and runs with reduced
  motion, so silent video clips show controls instead of autoplaying.
- **Old URLs:** `references/old-urls.txt` + `scripts/check_old_urls.sh`;
  renamed or retired pages need `aliases:`.
