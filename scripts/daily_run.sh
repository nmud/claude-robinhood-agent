#!/usr/bin/env bash
# Headless daily pass. Cron (9:45am ET = 13:45 UTC during DST):
#   45 13 * * 1-5  /home/ec2-user/claude-robinhood-agent/scripts/daily_run.sh
# Authenticate the MCP interactively once (claude -> /mcp) before using cron.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs

claude -p "$(cat prompts/daily.md)" \
  --allowedTools "mcp__robinhood-trading__*" "Read" "Write" "Edit" "Glob" "Grep" "WebSearch" "WebFetch" \
  >> "logs/run_$(date +%F).log" 2>&1

git add -A && git commit -q -m "daily pass $(date +%F)" || true
