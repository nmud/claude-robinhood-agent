#!/usr/bin/env bash
# Daily framework self-iteration. Cron (after US close, before evening testing):
#   47 21 * * *  /path/to/claude-robinhood-agent/scripts/iterate_run.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs

claude -p "$(cat prompts/iterate.md)" \
  --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "WebSearch" "WebFetch" \
    "Bash(git *)" "Bash(python3 eval/*)" \
  >> "logs/iterate_$(date +%F).log" 2>&1
