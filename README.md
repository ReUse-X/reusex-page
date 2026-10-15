<!--
SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen

SPDX-License-Identifier: GPL-3.0-or-later
-->

# reuse-x.com

The marketing site for [ReUseX](https://reuse-x.com/) — AI-powered resource
mapping of existing buildings. The product itself lives at
[app.reuse-x.com](https://app.reuse-x.com/).

Built with [Hugo](https://gohugo.io/) and a custom theme (`themes/reuse-x`)
that uses the product's own design tokens. No Node, no npm, no CDN: plain CSS
and JS bundled by Hugo, self-hosted fonts.

## Develop

```bash
nix develop            # or direnv: hugo, bd, Python + Playwright
bash .claude/skills/design-studio/scripts/serve.sh            # live server
DRAFTS=1 bash .claude/skills/design-studio/scripts/serve.sh restart   # incl. /components/
```

The server live-reloads on every edit; there is no build step during
development.

## Where things live

| What | Where |
|---|---|
| Pages (Markdown + content elements) | `content/en/` (Danish later in `content/da/`) |
| Lists of things: people, partners, contact, socials | `data/*.yaml` |
| Images, portraits, logos, videos | `assets/` (resized by Hugo) |
| Menus, site settings, app URL | `hugo.toml` |
| All design: layouts, elements, CSS, JS | `themes/reuse-x/` |
| Product design tokens (vendored, never edit) | `themes/reuse-x/assets/css/tokens.css` — refresh with `scripts/sync-tokens.sh` |

A page has at most ten lines of front matter (`title`, `description`,
optionally `layout: landing | article | deck`, `draft`, `date`, `aliases`).
Everything else is Markdown plus content elements like
`{{< hero >}}`, `{{< steps >}}` or `{{< people group="team" >}}`. Every
element documents its parameters at the top of its file in
`themes/reuse-x/layouts/_shortcodes/`, and the draft page `/components/`
shows each one with the snippet that produces it.

## Checks (also run in CI)

```bash
python3 .claude/skills/design-studio/scripts/content_lint.py   # content model
python3 .claude/skills/design-studio/scripts/token_lint.py     # no colour literals
python3 .claude/skills/design-studio/scripts/shot.py --all     # screenshots + QA
bash .claude/skills/design-studio/scripts/check_old_urls.sh    # old URLs still resolve
```

Pushes to `main` build with the flake's Hugo and deploy to GitHub Pages
(`.github/workflows/deploy-hugo.yml`). Work is tracked with
[beads](https://github.com/gastownhall/beads): `bd ready`.
