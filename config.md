# config — AUTO rails

Sized for a ~$1,000 agentic account. Edit, then say "arm AUTO".

- Allowlist tickers: SPY, QQQ, AAPL, MSFT, NVDA
- Per-order cap ($): 100
- Max position (% portfolio): 10
- Min cash (% portfolio): 10
- Daily loss limit (% portfolio): 2
- Max trades/day: 3
- Kill-switch NAV floor ($): 850
- Cadence: 1 pass/day after open (cron: scripts/daily_run.sh)
- Hours: regular only (yes)
- Instruments: stocks/ETFs only — no options, no margin

Kill: "stop" = disarm. "go flat" = close all + disarm.
Kill-switch breach: AUTO disarms itself; re-arm requires a human editing this file.
