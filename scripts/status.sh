#!/usr/bin/env bash
# status.sh — is the watcher alive? show pid, running agents, recent activity.
set -euo pipefail
cd "$(dirname "$0")/.."
PIDFILE="watcher.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "watcher: RUNNING (pid $(cat "$PIDFILE"))"
else
  echo "watcher: stopped"
fi

# in-flight 1:1 agents (issue #1) leave per-ticker logs while running
if ls logs/agent_*.log >/dev/null 2>&1; then
  echo "--- recent agent logs ---"
  ls -1t logs/agent_*.log 2>/dev/null | head -n 5
fi

echo "--- last 15 watcher lines ---"
tail -n 15 logs/watcher.log 2>/dev/null || echo "(no logs/watcher.log yet)"
