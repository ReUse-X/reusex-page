#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Keep ONE live `hugo server` (per PORT) + ONE `tailwindcss --watch` (per
# checkout — a git worktree gets its own) running for the design loop and
# print the URL. Tailwind (standalone CLI, no npm) compiles
# themes/reuse-x/assets/css/main.css → assets/css/generated/site.css; Hugo
# picks the file up and live-reloads.
#
# Idempotent: if the server is already answering on the port it just prints
# the URL and exits 0, so call it at the start of every round without worrying.
# The server renders to memory and live-reloads: template, CSS, content and
# hugo.toml edits are picked up in well under a second — never run `hugo`
# (a full build into public/) to look at a change.
#
# Usage: serve.sh [start|stop|status|log|restart]   (default: start)
#   PORT=1313 serve.sh          another port (e.g. a second worktree)
#   DRAFTS=1 serve.sh restart   also render `draft: true` content (default:
#                               off, like the production build — what you see
#                               is what visitors see)
#   HOST=127.0.0.1 serve.sh     bind elsewhere (default: this machine's Tailscale
#                               address, so the user can watch from any device
#                               on the tailnet; 127.0.0.1 if Tailscale is down)
#
# Only the Tailscale interface is bound, never 0.0.0.0 — the office LAN must
# not see the dev server. Screenshots (shot.py) use the same URL this prints.
#
# Log: .screenshots/hugo-server.log (gitignored). Template errors show up there
# AND as an error overlay in the browser/screenshot.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
PORT="${PORT:-1313}"
tailscale_ip() {
  ip -4 -o addr show dev tailscale0 2>/dev/null | awk '{ split($4, a, "/"); print a[1]; exit }'
}
HOST="${HOST:-$(tailscale_ip)}"
HOST="${HOST:-127.0.0.1}"
OUT="$ROOT/.screenshots"
LOG="$OUT/hugo-server.log"
mkdir -p "$OUT"

# Path prefix from baseURL (empty for https://reuse-x.com/).
url() {
  local path
  path="$(sed -nE "s|^baseURL *= *['\"]https?://[^/]+(/[^'\"]*)['\"].*|\1|p" "$ROOT/hugo.toml")"
  echo "http://$HOST:$PORT${path:-/}"
}

up() { curl -fs -o /dev/null --max-time 2 "$(url)"; }

in_dev() {
  if [[ -n "${IN_NIX_SHELL:-}" ]]; then "$@"; else nix develop "$ROOT" -c "$@"; fi
}

# Match the hugo process itself by its port (the PID of `nix develop -c …`
# is a wrapper; killing it leaves hugo running). Anchored with ^ so it never
# matches a shell whose command line merely mentions hugo.
pids() { pgrep -f "^hugo server --bind [^ ]+ --port $PORT " || true; }
THEME_CSS="$ROOT/themes/reuse-x/assets/css"
TW_ARGS=(-i "$THEME_CSS/main.css" -o "$THEME_CSS/generated/site.css")
TW_LOG="$OUT/tailwind.log"
checkout_hugo_pids() {
  local p
  for p in $(pgrep -f '^hugo server ' || true); do
    [[ "$(readlink "/proc/$p/cwd" 2>/dev/null)" == "$ROOT" ]] && echo "$p"
  done
  return 0
}
tw_pids() { pgrep -f "^[^ ]*tailwindcss -i $THEME_CSS/main.css" || true; }
tw_start() {
  [[ -n "$(tw_pids)" ]] && return 0
  mkdir -p "$THEME_CSS/generated"
  in_dev tailwindcss "${TW_ARGS[@]}" >"$TW_LOG" 2>&1 || { cat "$TW_LOG" >&2; return 1; }
  in_dev tailwindcss "${TW_ARGS[@]}" --watch=always >>"$TW_LOG" 2>&1 &
}
drafts_on() { pgrep -af "^hugo server --bind [^ ]+ --port $PORT " | grep -q -- --buildDrafts; }

stop() {
  local p
  p="$(pids)"
  if [[ -n "$p" ]]; then
    # shellcheck disable=SC2086 # one PID per word
    kill $p
    echo "serve.sh: stopped hugo server on :$PORT"
  fi
  # One Tailwind watcher per checkout (worktrees get their own, keyed on the
  # path); stop it once this checkout has no hugo server left on any port.
  if [[ -z "$(checkout_hugo_pids)" && -n "$(tw_pids)" ]]; then
    # shellcheck disable=SC2046
    kill $(tw_pids); echo "serve.sh: stopped tailwind watcher"
  fi
}

start() {
  tw_start
  if up; then url; return 0; fi
  # Bound to another address (e.g. Tailscale came up since): restart cleanly.
  if [[ -n "$(pids)" ]]; then stop; sleep 0.5; fi
  cd "$ROOT"
  # --renderToMemory: nothing written to public/, fastest rebuilds.
  # --disableFastRender is NOT used: fast render re-renders visited pages first,
  # which is exactly what a screenshot or an open browser tab is.
  in_dev hugo server \
    --bind "$HOST" --port "$PORT" --baseURL "http://$HOST$(url | sed -E 's|^https?://[^/]+||')" \
    --renderToMemory --navigateToChanged \
    ${DRAFTS:+--buildDrafts} --printPathWarnings \
    >"$LOG" 2>&1 &
  local wrapper=$!
  for _ in $(seq 1 120); do
    if up; then url; return 0; fi
    if ! kill -0 "$wrapper" 2>/dev/null; then
      tail -30 "$LOG" >&2
      echo "serve.sh: hugo server exited (log: $LOG)" >&2
      return 1
    fi
    sleep 0.5
  done
  tail -30 "$LOG" >&2
  echo "serve.sh: hugo server did not answer on :$PORT within 60 s (log: $LOG)" >&2
  return 1
}

case "${1:-start}" in
  start) start ;;
  stop) stop ;;
  restart) stop; sleep 0.5; start ;;
  status)
    if up; then echo "up $(url)$(drafts_on && echo ' (with drafts)')"; else echo "down"; exit 1; fi ;;
  log) tail -n "${LINES:-40}" "$LOG"; echo "--- tailwind"; tail -n 5 "$TW_LOG" ;;
  -h|--help) sed -n '2,/^set -euo/p' "$0" | sed 's/^# \{0,1\}//; /^set -euo/d' ;;
  *) echo "serve.sh: unknown command $1" >&2; exit 2 ;;
esac
