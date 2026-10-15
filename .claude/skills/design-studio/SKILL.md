---
name: design-studio
description: The design and content workflow for the ReUseX marketing site (reuse-x.com; Hugo with the custom theme themes/reuse-x, product design tokens vendored from rux-frontend, content as Markdown + content elements/shortcodes). Use this whenever you design, build, restyle, clean up or "make it look better" for any page (home, Solution, How it works, Vision, Roadmap, People, Contact, Research, pilots, the pitch deck); whenever you add or change a content element (shortcode), a layout, theme CSS/JS, tokens, menus in hugo.toml, data/*.yaml or a page under content/; whenever a page looks wrong in light or dark mode or on mobile; and whenever you work a design, content or restructure bead for the site.
---

# Design Studio — the ReUseX website

Claude Code writes good HTML/CSS. What this skill adds is *process* and the
site's *house rules*: content and design stay separated, everything visual
is a token, you edit against a **live** server (no builds), you **look** at
the result in both themes and at phone width, and iterate. The one step
never to skip is §5 — never call a page done that you haven't seen.

`references/site-map.md` has the directory map, the content model, how the
layout grid works, the checklist for writing a new element, the naming rule
and every recorded gotcha. Read it before your first change.

## The loop

Brief → Locate → Serve → Edit → Screenshot → Critique & fix → Hand off

**Review only** (an audit, "what's wrong with X"): do §3 → §5 → §6's
critique, no edits; report findings with file:line and file a bead per
defect (`bd create … -l design`).

### 1. Pin down the brief

If the request is vague, ask up to 3 short questions whose answers change
the design. If the user wants speed, state assumptions in one line and go.
Check `bd ready` / `bd list` for an existing bead first. Plans and progress
go in beads — never in spec/plan Markdown files (see CLAUDE.md).

### 2. Locate the work — content or design?

- **Copy, order of blocks, which element is used** → the page's Markdown in
  `content/en/<page>/`. Front matter stays ≤ 10 lines (`title`,
  `description`, optional `layout`, `draft`, `date`, `aliases`).
- **Lists of things** (people, partners, contact details, socials) →
  `data/*.yaml`. **Menus** → `hugo.toml`.
- **How anything looks** → `themes/reuse-x/` only. An element's look,
  spacing, colour, columns and band background are never parameters.
- **Reuse before inventing:** check the elements in
  `themes/reuse-x/layouts/_shortcodes/` (doc comment at the top of each) and
  the `/components/` gallery. A new element follows the checklist in the
  site map.
- **Colours and sizes come from tokens only.** Product tokens
  (`assets/css/tokens.css`) are vendored and never edited — refresh with
  `scripts/sync-tokens.sh`. Site-only tokens go in `site-tokens.css`, built
  on product tokens. Dark mode is the product's `[data-theme='dark']`.

### 3. Serve (once per session)

```bash
bash .claude/skills/design-studio/scripts/serve.sh            # prints the URL
DRAFTS=1 bash .claude/skills/design-studio/scripts/serve.sh restart   # + drafts, /components/
```

Idempotent; one `hugo server` in memory with live reload, bound to this
machine's **Tailscale** address so the user can watch from their own device
(give them the URL). Drafts are off by default, like production. Edits are
live in < 1 s. **Never run `hugo` to check a change** and never restart for
an edit — only `serve.sh restart` after a crash, a config change, or to pick
up new aliases; `serve.sh log` shows template errors (they also appear as an
overlay in the page).

### 4. Edit

- **Real copy**, specific to building reuse / LiDAR / circularity — no
  lorem ipsum. Missing content (copy, images, video) → file a content bead,
  don't invent it.
- **Quality floor:** body contrast ≥ 4.5:1 in *both* themes, visible focus,
  tap targets ≥ 44 px, no horizontal scroll at 390 px, nothing clipped.
- **Naming rule:** never let the product name render as one uppercase word
  ("REUSEX" reads "reu-SEX") — headings go through `brand-text`.

### 5. Look at it (mandatory) — both themes, desktop and mobile

```bash
python3 .claude/skills/design-studio/scripts/shot.py people/                  # one page
python3 .claude/skills/design-studio/scripts/shot.py people/ --vp mobile --each ".landing > *"
python3 .claude/skills/design-studio/scripts/shot.py "pitchdeck/#slide-4"     # a slide
python3 .claude/skills/design-studio/scripts/shot.py --all                    # every page
python3 .claude/skills/design-studio/scripts/shot.py people/ --probe ".person__link"
```

Default: light + dark × desktop (1440) + mobile (390), first viewport.
`--selector` for one element, `--each` for every match as its own image,
`--scroll-to`, `--js` to drive the page first. **On mobile use `--each`,
not `--full`** (a full-length phone shot is shrunk to illegibility).
`--probe` measures size, font, colours and contrast instead of guessing.
Then **open every PNG with the Read tool and actually look.** `CHECK FAIL`
lines (exit 3) — console errors, 404s, template errors, horizontal overflow,
broken images, broken internal links — are defects.

### 6. Critique and fix

Review against `references/critique-checklist.md`; fix the 3–5 biggest
problems, re-shoot; 2–3 rounds. Before finishing, all of these must pass:

```bash
python3 .claude/skills/design-studio/scripts/content_lint.py   # content model
python3 .claude/skills/design-studio/scripts/token_lint.py     # tokens only
bash .claude/skills/design-studio/scripts/check_old_urls.sh    # old URLs resolve
```

### 7. Hand off

A few lines: what changed and where, which tokens/elements it depends on,
known gaps (a bead each), the live URL and the screenshot paths. Close or
update the beads you worked.

## Iterating on feedback

Find the exact element, change it, re-shoot, confirm. A comment that implies
a *system* change ("the accent is too loud", "cards need more air") is a
token or element-CSS change — make it once in the theme and re-shoot every
page that uses it (`shot.py --all`), never patch one page's content.
