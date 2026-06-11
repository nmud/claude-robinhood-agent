#!/usr/bin/env bash
# stop.sh — stop the watcher daemon (issue #3). Sends SIGTERM so it finishes the
# current pass, reaps child agents, and removes its own pidfile cleanly.
set -euo pipefail
cd "$(dirname "$0")/.."
PIDFILE="watcher.pid"

if [ ! -f "$PIDFILE" ]; then
  echo "not running (no $PIDFILE)"
  exit 0
fi

PID="$(cat "$PIDFILE")"
if ! kill -0 "$PID" 2>/dev/null; then
  echo "stale pidfile (pid $PID gone) — removing"
  rm -f "$PIDFILE"
  exit 0
fi

kill -TERM "$PID"
echo "sent SIGTERM to watcher (pid $PID); waiting for clean exit..."
for _ in $(seq 1 20); do
  kill -0 "$PID" 2>/dev/null || { echo "stopped."; exit 0; }
  sleep 0.5
done

echo "still alive after 10s — sending SIGKILL"
kill -KILL "$PID" 2>/dev/null || true
rm -f "$PIDFILE"
echo "killed."
