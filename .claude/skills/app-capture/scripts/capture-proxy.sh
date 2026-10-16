#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Povl Filip Sonne-Frederiksen
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# A private SOCKS5 proxy into the tailnet, for the capture browser only.
#
# Some networks (the office web filter) block app.reuse-x.com. This runs a
# second, userspace tailscaled — its own node "<host>-capture", its own state
# — whose exit node is $CAPTURE_EXIT_NODE (default beagle), and exposes it as
# SOCKS5 on 127.0.0.1:1055. The system tailscale, its exit node and LAN
# access are never touched.
#
#   capture-proxy.sh up       start (first time: prints a login URL to approve)
#   capture-proxy.sh status   node + exit node + does app.reuse-x.com answer
#   capture-proxy.sh down     stop (state is kept; next `up` needs no login)
set -euo pipefail

STATE="${CAPTURE_TS_STATE:-$HOME/.local/state/reusex-capture-ts}"
SOCK="$STATE/tailscaled.sock"
SOCKS="${CAPTURE_SOCKS:-127.0.0.1:1055}"
EXIT_NODE="${CAPTURE_EXIT_NODE:-beagle}"
APP="${CAPTURE_APP_URL:-https://app.reuse-x.com/}"
ts() { tailscale --socket="$SOCK" "$@"; }


case "${1:-status}" in
  up)
    mkdir -p "$STATE"
    if ! pgrep -f "tailscaled .*--socket=$SOCK" >/dev/null; then
      nohup tailscaled --tun=userspace-networking --socket="$SOCK" --statedir="$STATE" \
        --port=0 --socks5-server="$SOCKS" >"$STATE/tailscaled.log" 2>&1 &
      for _ in $(seq 20); do [ -S "$SOCK" ] && break; sleep 0.5; done
    fi
    # Resolve the exit node's tailnet IP from the *system* client's peer list.
    exit_ip="$(tailscale status --json | python3 -c "import json,sys
d=json.load(sys.stdin)
print(next((p['TailscaleIPs'][0] for p in d['Peer'].values() if p['HostName']=='$EXIT_NODE'),''))")"
    [ -n "$exit_ip" ] || { echo "exit node '$EXIT_NODE' not found in the tailnet" >&2; exit 1; }
    timeout 20 tailscale --socket="$SOCK" up --hostname="$(hostname)-capture" \
      --exit-node="$exit_ip" --exit-node-allow-lan-access=false --accept-dns=false >/dev/null 2>&1 || true
    if ts status 2>&1 | grep -q "Logged out\|NeedsLogin"; then
      echo "Approve this node once: $(grep -o 'https://login.tailscale.com/a/[a-z0-9]*' "$STATE/tailscaled.log" | tail -1)"
      exit 2
    fi
    "$0" status
    ;;
  status)
    if ! pgrep -f "tailscaled .*--socket=$SOCK" >/dev/null; then echo "proxy: down"; exit 1; fi
    ts status 2>/dev/null | grep -E "capture|exit node" | sed 's/^/  /'
    code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 -x "socks5h://$SOCKS" "$APP" || true)"
    echo "proxy: socks5://$SOCKS → $EXIT_NODE · $APP → HTTP $code"
    [ "$code" = 200 ]
    ;;
  down)
    pkill -f "tailscaled .*--socket=$SOCK" && echo "proxy: stopped" || echo "proxy: was not running"
    ;;
  *) echo "usage: $0 up|status|down" >&2; exit 64 ;;
esac
