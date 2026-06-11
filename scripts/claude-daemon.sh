#!/usr/bin/env bash
# claude-daemon.sh — run an interactive Claude TUI as a detached tmux session you
# can attach to, drive, and stop independently of your ssh/terminal.
#
# Why this exists: watcher.py (scripts/start.sh) is the TOKEN-FREE trigger daemon
# that spawns headless one-shot `claude -p` agents on a price move. THIS is the
# other half: a single persistent, INTERACTIVE Claude you attach to (live TUI),
# type actions into anytime, and that begins trading the moment the market opens.
#
# tmux gives us everything asked for:
#   - process not dictated by the terminal: detached session survives ssh drop.
#   - stoppable: `stop` kills the session (optionally flattens first).
#   - resumed/watched again: `attach` re-enters the live TUI; Ctrl-b d detaches.
#   - actions sent whenever: `send "<prompt>"` injects into the live prompt.
#   - 24/7: `start` arms a kickoff that waits for market open, then begins.
#
# Requires on the linux box: tmux, claude (authed), this repo cloned, the
# robinhood MCP configured. Run `attach` once on first setup to clear any
# trust/auth prompt before relying on unattended kickoff.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$SCRIPT_DIR/daemon.env" ] && . "$SCRIPT_DIR/daemon.env"

# ---- config (override in scripts/daemon.env) ----------------------------------
: "${SESSION:=claude-trader}"
: "${WORKDIR:=$(cd "$SCRIPT_DIR/.." && pwd)}"
: "${CLAUDE_CMD:=claude --continue || claude}"   # resume convo if one exists, else fresh
: "${MARKET_TZ:=America/New_York}"
: "${MARKET_OPEN:=0930}"                          # HHMM, regular session
: "${MARKET_CLOSE:=1600}"
: "${HALFDAY_CLOSE:=1300}"                        # close on early-close days
: "${POLL:=5}"                                    # seconds between open-checks while armed
: "${KICKOFF:=ADVISE mode. Run one trading pass per CLAUDE.md (regime -> strategy -> risk), then /loop every 5m until I say stop.}"
HOLIDAYS="$SCRIPT_DIR/market-holidays.txt"
HALFDAYS="$SCRIPT_DIR/market-halfdays.txt"

CWIN="$SESSION:claude"     # the Claude TUI window
KWIN="$SESSION:kickoff"    # the kickoff-waiter window (self-closes when done)

# ---- helpers ------------------------------------------------------------------
have_session() { tmux has-session -t "$SESSION" 2>/dev/null; }

effective_close() {
  local d; d=$(TZ="$MARKET_TZ" date +%F)
  if [ -f "$HALFDAYS" ] && grep -qx "$d" "$HALFDAYS"; then echo "$HALFDAY_CLOSE"; else echo "$MARKET_CLOSE"; fi
}

# verify the timezone actually resolves (needs OS zoneinfo). If it doesn't, `date`
# silently falls back to UTC and the gate would fire at the wrong hours — so we
# fail CLOSED instead of risking real-money trades off a bad clock.
tz_ok() {
  case "$(TZ="$MARKET_TZ" date +%Z)" in EST|EDT) return 0;; *) return 1;; esac
}

# returns 0 if the US equities regular session is open right now
is_market_open() {
  local dow date hm o c n
  if ! tz_ok; then
    echo "WARN: '$MARKET_TZ' not resolving (zoneinfo missing?) — gate fail-CLOSED" >&2
    return 1
  fi
  dow=$(TZ="$MARKET_TZ" date +%u)     # 1=Mon .. 7=Sun
  date=$(TZ="$MARKET_TZ" date +%F)
  hm=$(TZ="$MARKET_TZ" date +%H%M)
  [ "$dow" -ge 6 ] && return 1                                    # weekend
  [ -f "$HOLIDAYS" ] && grep -qx "$date" "$HOLIDAYS" && return 1  # holiday
  o=$((10#$MARKET_OPEN)); c=$((10#$(effective_close))); n=$((10#$hm))
  [ "$n" -ge "$o" ] && [ "$n" -lt "$c" ]
}

# type text into the live Claude prompt, then submit
send_keys() {
  have_session || { echo "no session '$SESSION'."; return 1; }
  tmux send-keys -t "$CWIN" -l -- "$*"
  tmux send-keys -t "$CWIN" Enter
}

ensure_session() {
  if have_session; then return 0; fi
  tmux new-session -d -s "$SESSION" -n claude -c "$WORKDIR" "$CLAUDE_CMD"
  echo "session '$SESSION' started — claude booting in $WORKDIR"
}

# ---- subcommands --------------------------------------------------------------
cmd="${1:-help}"; shift 2>/dev/null || true

case "$cmd" in
  start)
    mode="${1:-at-open}"   # at-open | now | idle
    ensure_session
    # clear any prior kickoff waiter
    tmux kill-window -t "$KWIN" 2>/dev/null || true
    case "$mode" in
      now)
        tmux new-window -t "$SESSION" -n kickoff -c "$WORKDIR" \
          "bash '$SCRIPT_DIR/claude-daemon.sh' _kick now"
        echo "kickoff: sending now (once claude is up)";;
      at-open|"")
        tmux new-window -t "$SESSION" -n kickoff -c "$WORKDIR" \
          "bash '$SCRIPT_DIR/claude-daemon.sh' _kick wait"
        if is_market_open; then echo "kickoff: market OPEN — beginning now"
        else echo "kickoff: armed — will begin at market open ($MARKET_OPEN $MARKET_TZ)"; fi;;
      idle)
        echo "session up, no kickoff. drive it: $0 send \"...\"";;
      *) echo "unknown start mode '$mode' (use: at-open | now | idle)"; exit 2;;
    esac
    echo "watch it: $0 attach   |   stop it: $0 stop"
    ;;

  _kick)   # internal: runs inside the kickoff tmux window
    sleep 4                                      # let claude finish booting
    [ "${1:-wait}" = "wait" ] && while ! is_market_open; do sleep "$POLL"; done
    send_keys "$KICKOFF"
    ;;       # window self-closes on exit

  send)
    [ "$#" -ge 1 ] || { echo "usage: $0 send \"<prompt>\""; exit 2; }
    send_keys "$*" && echo "sent."
    ;;

  attach)
    have_session || { echo "no session '$SESSION'. start it: $0 start"; exit 1; }
    exec tmux attach -t "$CWIN"
    ;;

  stop)
    have_session || { echo "not running."; exit 0; }
    if [ "${1:-}" = "--flat" ]; then
      echo "asking Claude to cancel opens + go flat; waiting 30s..."
      send_keys "STOP. Cancel all open orders and go flat now, then confirm." || true
      sleep 30
      echo "NOTE: this script cannot confirm fills — verify FLAT in the Robinhood app."
    fi
    tmux kill-session -t "$SESSION"
    echo "stopped '$SESSION'. WARNING: killing the daemon does NOT close open positions."
    ;;

  status)
    if have_session; then
      echo "session: UP ($SESSION)"; tmux list-windows -t "$SESSION"
    else echo "session: DOWN"; fi
    tz_ok || echo "TZ WARN: '$MARKET_TZ' not resolving here — gate fail-CLOSED (fine on the linux box; broken under git-bash)"
    if is_market_open 2>/dev/null; then echo "market: OPEN"
    else echo "market: CLOSED (gate: $MARKET_OPEN-$(effective_close) $MARKET_TZ, weekdays, minus holidays)"; fi
    ;;

  *)
    cat <<EOF
claude-daemon.sh — detached, attachable Claude trading TUI (tmux)

  start [at-open|now|idle]   create session; arm kickoff (default at-open:
                             waits for market open, then begins immediately)
  attach                     enter the live TUI (Ctrl-b d to detach, leaves it running)
  send "<prompt>"            inject an action into the live prompt anytime
  stop [--flat]              kill the session; --flat asks Claude to go flat first
  status                     session + market state

  session=$SESSION  workdir=$WORKDIR
  hours=$MARKET_OPEN-$MARKET_CLOSE $MARKET_TZ (config: scripts/daemon.env)
EOF
    ;;
esac
