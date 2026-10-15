#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Vendor the product's design tokens (rux-frontend src/tokens.css) into the
# site theme. The file is copied verbatim and never edited here: the token
# names belong to rux-frontend, the values to the Claude Design project
# "ReUseX GUI". Site-only tokens live in site-tokens.css, built on these.
#
# Usage:
#   scripts/sync-tokens.sh                                  # ../rux-frontend/src/tokens.css
#   scripts/sync-tokens.sh <path-to-tokens.css>
#   scripts/sync-tokens.sh <https://… raw tokens.css URL>
#
# After syncing, run the token lint: a renamed or removed token that the site
# still uses is reported as unknown-token.
set -euo pipefail

ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
DEST="$ROOT/themes/reuse-x/assets/css/tokens.css"
SRC="${1:-$ROOT/../rux-frontend/src/tokens.css}"

case "$SRC" in
  -h|--help) sed -n '2,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//; /^set -euo/d'; exit 0 ;;
  http://*|https://*) curl -fsSL "$SRC" -o "$DEST.tmp" && mv "$DEST.tmp" "$DEST" ;;
  *) [[ -f "$SRC" ]] || { echo "sync-tokens.sh: no such file: $SRC" >&2; exit 1; }
     cp "$SRC" "$DEST" ;;
esac
echo "sync-tokens.sh: $SRC -> ${DEST#"$ROOT/"}"
python3 "$ROOT/.claude/skills/design-studio/scripts/token_lint.py" --summary
