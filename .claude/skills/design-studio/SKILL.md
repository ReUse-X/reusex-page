---
name: design-studio
description: The design workflow for the ReUseX website (Hugo site with theme "reusex", Tailwind Play CDN, light/dark tokens in themes/reusex/assets/css/main.css, deployed to GitHub Pages). Use this whenever you design, build, restyle, redesign, clean up or "make it look better/more polished" for any page or section of the site (home, Vision, Solution, How it Works, Roadmap, People, Contact, Research, pilots, the pitch deck); whenever you touch a template in layouts/ or themes/reusex/layouts/, main.css, main.js, hugo.toml menus/footer, or a content file's layout/colorScheme front matter; whenever a page looks wrong in light or dark mode or on mobile; and whenever you work a design or cleanup bead for the site.
---

# Design Studio — the ReUseX website

Claude Code writes good HTML/CSS. What this skill adds is *process* and the
site's *house rules*: work inside the token system that exists, edit against
a **live** server (no builds), **look** at the result in both themes and at
phone width, and iterate. The one step never to skip is §5 — never call a
page done that you haven't seen.

Directory map, how templates override the theme, the content/front-matter
model, the token list and every recorded gotcha: `references/site-map.md`.
Read it before your first change.

## The loop

Brief → Locate in the system → Serve → Edit → Screenshot → Critique & fix → Hand off

**Review only** (an audit, "what's wrong with X", planning a cleanup): do
§3 → §5 → §6's critique, no edits; report findings with file:line and file
a bead per defect (`bd create … -l design`).

### 1. Pin down the brief

If the request is vague, ask up to 3 short questions whose answers change
the design: which page/section, which theme(s) it must work in, whether the
copy is final. If the user wants speed, state assumptions in one line and go.
Check `bd ready` / `bd list` for an existing bead before starting from scratch.

### 2. Locate the work in the existing system

- **Find where the markup actually lives.** Root `layouts/` overrides
  `themes/reusex/layouts/` file-for-file; most section pages are
  `layouts/<section>/list.html` ranging over `content/<section>/NN-*.md`
  sub-pages. The home page is `themes/reusex/layouts/home.html` reading
  `content/sections/*.md`. Copy is in content front matter, not templates.
- **Colours come from tokens only.** `themes/reusex/assets/css/main.css`
  defines them in three blocks: `[data-theme="light"]`, `[data-theme="dark"]`
  (what dark-mode visitors see) and `:root` (base/fallback — only visible
  with JS off). Details: `references/site-map.md` §Tokens.
  Use `style="color: var(--heading-text)"` or a class in main.css — never a
  hex, `rgb()`, or a Tailwind palette class (`bg-white`, `text-gray-600`):
  those don't flip with the theme. Need a colour that doesn't exist? Add a
  token to the light **and** dark blocks (and `:root`), then use it.
- **Section themes:** every band uses exactly one of section 1/2/3 tokens
  (`--sectionN-*`), chosen by the sub-page's `colorScheme` front matter.
- **Reuse before inventing**: icons via `partials/icon.html`, the timeline
  via `partials/timeline.html`, links via `partials/smart-url.html`.

### 3. Serve (once per session)

```bash
bash .claude/skills/design-studio/scripts/serve.sh      # prints the URL
```

Idempotent; starts `hugo server` in memory with live reload, bound to this
machine's **Tailscale** address so the user can watch from their own device
(the URL it prints — give it to the user). Drafts are **off**, like the
production build; `DRAFTS=1 serve.sh restart` to see `draft: true` content
(and remember visitors don't). Edits to templates, CSS, content or hugo.toml
are live in <1 s. **Never run `hugo` (a full build) to check a
change**, and never restart the server for an edit — only `serve.sh restart`
after a crash or `serve.sh log` to read a template error.

### 4. Edit

- **Real copy**, specific to building reuse / LiDAR / circularity — no
  "Feature one", no lorem ipsum.
- **Quality floor:** body contrast ≥ 4.5:1 in *both* themes, visible focus,
  tap targets ≥ 44 px, no horizontal scroll at 390 px, nothing clipped.
- The Tailwind **Play CDN** compiles classes in the browser: any standard
  utility works with no build, arbitrary values (`w-[37rem]`) too. Layout
  and spacing utilities are fine; colour utilities are not (§2).

### 5. Look at it (mandatory) — both themes, desktop and mobile

```bash
python3 .claude/skills/design-studio/scripts/shot.py people/            # one page
python3 .claude/skills/design-studio/scripts/shot.py "" --selector footer --vp all
python3 .claude/skills/design-studio/scripts/shot.py --all              # every section
```

Default: light + dark × desktop (1440) + mobile (390), first viewport;
`--selector` for one element, `--each "main > section"` for every band as
its own image, `--scroll-to` for a viewport further down, `--js` to drive
the page first (pitch deck: `--js "goToSlide(4)"`). **On mobile use
`--each`, not `--full`**: a full-length phone shot is shrunk to ~200 px wide
when you Read it and clipping becomes invisible. `--full` is for a desktop
overview only.

Don't eyeball numbers — measure them:
`shot.py PAGE --probe "CSS"` prints size (tap targets), font size, colours,
effective background and contrast ratio for each match, per theme. ~1 s per shot against the live server, PNGs in
`.screenshots/`. Then **open every PNG with the Read tool and actually look.**
It prints `CHECK FAIL` lines (exit 3) for console errors, 404s, a Hugo
template error, horizontal overflow (with the offending elements) and broken
images — treat each as a defect. `--help` for the rest.

### 6. Critique and fix

Review the shots against `references/critique-checklist.md`. Write down the
3–5 biggest problems, fix them, re-shoot. Expect 2–3 rounds; stop when what's
left is taste, not defects. Before finishing:

- `python3 .claude/skills/design-studio/scripts/token_lint.py <files you touched>`
  — fix every finding in lines you wrote or edited. (The site has a backlog
  of older findings; run without arguments / `--summary` to see it. Don't
  widen a cleanup task into fixing all of them unless asked.)
- Remove one decorative element that isn't earning its place.

### 7. Hand off

A few lines: what changed and where, which tokens it depends on, known gaps
(file a bead for each: `bd create`), the live URL, and the screenshot paths.

## Iterating on feedback

Find the exact element, change it, re-shoot, confirm. A comment that implies
a *system* change ("the teal is too loud", "dark mode cards are muddy") is a
token change in main.css — change the token in the right theme block, then
re-shoot **every** page that uses it (`shot.py --all`), not just the one in
the comment.
