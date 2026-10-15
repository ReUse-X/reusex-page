# Site map — where things live and what bites

## Stack

- **Hugo** from the flake (dev shell and CI use the same version; CI builds
  with `nix develop .#ci`). Theme `themes/reuse-x`, new template system
  (`layouts/_partials`, `_shortcodes`, `_markup`).
- **Tailwind v4, built ourselves — no Node/npm/CDN.** The standalone
  Tailwind CLI (dev shell `tailwindcss_4`) compiles `assets/css/main.css`
  (the Tailwind entry) into `assets/css/generated/site.css` (gitignored),
  which `head.html` loads. `serve.sh` runs `tailwindcss --watch=always`
  next to `hugo server`; CI runs `tailwindcss --minify` before `hugo`.
  Hugo's own `css.TailwindCSS` is not used (it needs the npm package).
- **Theme = product tokens.** `scripts/tailwind-theme.py` (run by
  `sync-tokens.sh`) generates `tailwind-theme.css`: `@theme reference`
  registers the product token names, so `bg-accent`, `text-on-chrome`,
  `border-border`, `rounded-md`, `shadow-md`, `font-display` compile to
  `var(--color-accent)` … and the values stay in `tokens.css` (per theme).
  Tailwind's default palette/radii/shadows/fonts are off — `bg-gray-500`
  doesn't exist. Site sizes map via `@theme inline`: `text-hero/h1–h4/lead/body`,
  `max-w-site`, `max-w-site-prose`, `px-gutter`, `py-section`, `size-tap`,
  `min-h-header`. Use `page-width` for the centred content width;
  `dark:` = `[data-theme=dark]`.
- **Which utilities exist:** whatever `assets/css/tailwind-theme.css`
  registers, plus Tailwind's own spacing/layout/border-width defaults
  (`p-5`, `mt-0.5`, `gap-4`, `max-w-3xl`, `border-l-4`, `grid-cols-*` …).
  Switched off: Tailwind's colours, radii, shadows, fonts, text sizes and
  leading — `text-sm`, `rounded-md`, `leading-tight` are the *product's*
  values. Colour names are the token names minus `--color-`, so the body
  text colour is `text-text`, muted `text-text-muted`, borders
  `border-border`. Tokens outside the registered families (e.g.
  `--tone-*`, `--circ-*`, `--label-*`) have no utility — use
  `bg-(--tone-good-bg)`.
- **JS:** vanilla modules bundled by `js.Build` from `assets/js/main.js`.
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
| CSS | Utilities in the templates. Small layers only where utilities can't reach: `base/` (fonts, reset, typography), `layouts/` (flow grid, landing bands, article, deck), `components/` (`markdown.css` = `.md` for Markdown inside elements, media side alternation, checklist ticks, before/after clip, gallery panel) |
| Shared template pieces | `_partials/button.html` (all button variants — templates pass `variant`, never classes), `frame.html` (picture frames by `kind`), `heading-split.html` (title from the first Markdown heading) |
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

## Adding a new page

1. Section-type page (has its own URL and may get children, e.g. `/faq/`):
   `content/en/<name>/_index.md` → `landing` layout by default. Single
   article (a pilot, a news item): a leaf bundle `content/en/<section>/<slug>/index.md`
   → `article` layout. Start from `hugo new content/en/<name>/_index.md`
   (the archetype follows the content model).
2. Navigation is a separate decision: add it to `[menus.main]` (top bar,
   keep it short) or as a child of a `[menus.footer]` column in
   `hugo.toml` — or nowhere, if it is only linked from other pages. Menu
   labels come from the menu entry's `name`, not the page title.
3. Renamed/moved page → `aliases: [/old/path/]`, then `serve.sh restart`
   (aliases, like menu and other `hugo.toml` changes, are only picked up
   reliably after a restart) and `check_old_urls.sh`.

## Writing a new element (checklist)

1. `layouts/_shortcodes/<name>.html`, starting with the short header every
   element has: one line of purpose, one usage example written the way
   content should be written (tags and content on separate lines), and a
   compact parameter table. Then the validate line, then indented HTML.
2. First line of logic: `partial "validate.html" (dict "ctx" . "named" … "required" … "enums" … "inner" …)`.
   Never accept design params (colour, tone, columns, size …) — validate
   rejects them.
3. Inner Markdown: `partial "markdown.html" (dict "page" .Page "inner" .Inner)`
   — pass `.Inner` explicitly (Hugo only treats a shortcode as taking inner
   content if its own template mentions `.Inner`).
4. Output must contain **no blank lines** (they break the parent's HTML
   block when elements nest) — use `{{- -}}` trimming.
5. Links via `link.html`, images via `image.html`, icons via `icon.html`,
   buttons via `button.html`, picture frames via `frame.html`.
6. Style with Tailwind utilities (token colours only — `token_lint.py`
   rejects literal colours and palette classes). Panels use
   `bg-(--panel-bg)` so they contrast on alternating bands. Wrap rendered
   Markdown in `class="md"`. Only add a CSS file (in a layer, imported in
   `main.css`) for what utilities can't do; say why in its header.
   Every partial that returns HTML must end with `-}}` (a trailing newline
   becomes a blank line that breaks nested elements; shot.py flags it).
7. An item with a title (card, step, question) takes it from the first
   Markdown heading: `partial "heading-split.html"`. Never add `title=`.
8. Add a snippet `content/en/components/examples/<name>.txt` and an
   `{{< example "<name>" >}}` line on the gallery page (a draft page: run
   the server with `DRAFTS=1`). The source panel is `#example-<name>` and
   the rendered element is its next sibling: shoot it with
   `--selector "#example-<name> + *"`.
   An element meant to sit *inside prose* (callout, checklist) also takes
   `max-w-site-prose` — `.element` alone spans the full content width.
9. Container + item elements (cards/card, steps/step, stats/stat,
   faq/question): only the container carries `element`; each item checks
   its parent with the guard copied from `card.html`
   (`with .Parent … ne .Name "cards" … errorf`).
10. Icons: add new ones to the registry in `_partials/icon.html` (24×24,
   stroke `currentColor`, same 1.75 stroke weight); an unknown name errors
   and lists the known ones.
11. Interactive states: shoot them with `--js` (e.g. open every
    `<details>`, `goToSlide(4)`) and real keyboard focus with
    `--keys "Tab Tab Enter"`; check the focus ring is visible on every band
    (dark bands override `--site-focus-ring`).

## Naming rule (product name)

Headings are uppercase (Oswald); "REUSEX" reads "reu-SEX". The
`brand-text` partial wraps any "ReUseX"/"reusex"/"reuse-x" in headings and
titles in `<span class="brand">` (exempt from `text-transform`). The text
wordmark sets ReUse and X apart. Never uppercase the name as one word in a
template.

## Gotchas (recorded)

- **Readable content:** an element's content never shares a line with its
  tags; titles are `###` headings inside card/step/question; long tags put
  one group of params per line; a blank line between sibling items.
  content_lint enforces the one-line rule.
- **Mixed params:** Hugo can't mix positional and named shortcode params;
  every element uses named parameters only.
- **Utilities vs layers:** Tailwind utilities beat the CSS layers; to
  change an element inside a context (slides) use variants like
  `in-[.slide]:hidden`, not a layered override.
- **Self-closing:** an element whose template mentions `.Inner` must be
  closed or self-closed (`{{< media … />}}`) when used without content.
- **Broken internal links** don't stop the build: the link partial warns
  and renders `#broken-link/<path>`; shot.py reports them as CHECK FAIL.
- **Aliases** of pages added while the server runs only appear after
  `serve.sh restart`.
- **Watcher:** if a new class has no effect, grep it in
  `themes/reuse-x/assets/css/generated/site.css`; if it's missing, see
  `serve.sh log` (Tailwind section). The watcher scans
  `themes/reuse-x/layouts` and `assets/js`; classes built from strings must
  appear literally there. Each checkout/worktree has its own `generated/`
  and its own watcher (started and stopped by its `serve.sh`).
- **Deck overflow:** a slide with more content than the canvas is shrunk
  to fit (down to 75 %, `js/deck.js`); below that the console warns —
  split the slide instead of cutting copy.
- **`zoom`** scales the deck canvas (it also scales layout, so centring
  works); the canvas is 1000×562.5 (`--deck-canvas-*`).
- **Theme key:** `localStorage['reusex-theme']` = light | dark | system,
  same as the app; light is the default.
- **Headless screenshots:** shot.py forces lazy images to load and decode
  (headless Chromium skips off-screen images) and runs with reduced
  motion, so silent video clips show controls instead of autoplaying.
- **Old URLs:** `references/old-urls.txt` + `scripts/check_old_urls.sh`;
  renamed or retired pages need `aliases:`.
- **Second server / worktrees:** `PORT=1315 serve.sh` runs another server;
  pass its URL to `shot.py --base …` and `check_old_urls.sh <url>`. Run the
  scripts *inside* the dev shell: run outside it they re-enter
  `nix develop`, and from a git **worktree** the git-hooks shellHook then
  rewrites the shared `core.hooksPath` — repair with
  `git config core.hooksPath .beads/hooks`.
