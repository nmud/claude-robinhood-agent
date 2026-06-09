#!/usr/bin/env bash
# Weekly review (Friday after close). Cron:
#   30 21 * * 5  /home/ec2-user/claude-robinhood-agent/scripts/weekly_run.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
claude -p "$(cat prompts/weekly.md)" \
  --allowedTools "mcp__robinhood-trading__*" "Read" "Write" "Edit" "Glob" "Grep" "Bash(python3 eval/*)" "WebSearch" "WebFetch" \
  >> "logs/weekly_$(date +%F).log" 2>&1
git add -A && git commit -q -m "weekly review $(date +%F)" || true
