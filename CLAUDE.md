# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:1105d646 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->


## Build & Test

Everything runs in the Nix dev shell (`nix develop`, or direnv via `.envrc`):
hugo, beads (`bd`), Python + Playwright with a Nix-provided Chromium.

```bash
bash .claude/skills/design-studio/scripts/serve.sh        # live hugo server (Tailscale IP, live reload)
python3 .claude/skills/design-studio/scripts/shot.py --all   # screenshots, both themes, desktop + mobile
python3 .claude/skills/design-studio/scripts/token_lint.py   # colour literals / unknown tokens
```

Don't run `hugo` (full build into public/) to check a change — the live
server re-renders in under a second. CI (`.github/workflows/deploy-hugo.yml`)
builds with Hugo 0.146.0 and deploys `main` to GitHub Pages under
`/reusex-page/`.

## Architecture Overview

Hugo site, theme `themes/reusex/`; root `layouts/` overrides it per section.
Section pages are `layouts/<section>/list.html` ranging over
`content/<section>/NN-*.md` bands (`order`, `colorScheme`, `layout` front
matter). Colours are CSS custom properties in
`themes/reusex/assets/css/main.css` (light/dark via `data-theme` on `<html>`);
layout uses the Tailwind Play CDN.

## Conventions & Patterns

Any visual or template work: use the `design-studio` skill
(`.claude/skills/design-studio/`) — it has the site map, house rules and the
screenshot loop.

## Planning & tracking: beads only

We use the superpowers skills (brainstorming, writing-plans, executing-plans,
…) for their *process*, but **never write spec or plan Markdown files** — no
`docs/superpowers/specs/`, no `docs/superpowers/plans/`, no design docs.
Wherever a skill says "write the spec/plan to a file", put it in **beads**
instead:

- the agreed design → the description of an epic (`bd create -t epic`)
- plan steps → child issues (`--parent <epic>`) with dependencies
  (`bd dep add`), acceptance criteria in each issue
- progress, decisions, findings → `bd update` / `bd comment` on the issue

A skill's "user reviews the written spec" gate becomes "user reviews the epic
and its issues (`bd show <epic>`)".
