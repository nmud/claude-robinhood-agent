#!/usr/bin/env bash
# resume.sh — "tap back into the main running process" (issue #3). The watcher is
# a detached daemon, so resuming = following its live log. Ctrl-C here just stops
# watching the log; it does NOT stop the watcher (use scripts/stop.sh for that).
set -euo pipefail
cd "$(dirname "$0")/.."
PIDFILE="watcher.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "attached to watcher (pid $(cat "$PIDFILE")). Ctrl-C detaches (watcher keeps running)."
else
  echo "watcher is NOT running. Start it: scripts/start.sh"
fi
echo "----------------------------------------------------------------"
exec tail -n 40 -f logs/watcher.log
