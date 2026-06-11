#!/usr/bin/env bash
# start.sh — launch watcher.py as a background daemon that survives an ssh drop.
# Issue #3: the watcher must NOT depend on your terminal/ssh session. setsid puts
# it in its own session so SIGHUP on disconnect can't kill it. watcher.py owns
# watcher.pid (single-instance guard). Reattach later with scripts/resume.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs

PY="${WATCHER_PY:-python3}"
PIDFILE="watcher.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "watcher already running (pid $(cat "$PIDFILE")). scripts/status.sh for state."
  exit 0
fi

# setsid + nohup + redirect + </dev/null = fully detached, survives logout.
setsid nohup "$PY" watcher.py >> logs/watcher.log 2>&1 < /dev/null &

# watcher.py writes its own pid; give it a moment, then report.
for _ in 1 2 3 4 5; do
  [ -f "$PIDFILE" ] && break
  sleep 0.5
done

if [ -f "$PIDFILE" ]; then
  echo "watcher started (pid $(cat "$PIDFILE")) -> logs/watcher.log"
  echo "follow it: scripts/resume.sh   stop it: scripts/stop.sh"
else
  echo "watcher did not write a pidfile — check logs/watcher.log"
  tail -n 20 logs/watcher.log || true
  exit 1
fi
