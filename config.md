# config — AUTO rails

Sized for a ~$1,000 agentic account. Edit, then say "arm AUTO".

- Mode: SIM            # SIM | ADVISE | AUTO — see CLAUDE.md "Three modes"
- Allowlist tickers: SPY, QQQ, AAPL, MSFT, NVDA
- Per-order cap ($): 100   # tactical (S1-S4) orders only; S0 core-sleeve orders exempt
- Max position (% portfolio): 10
- Min cash (% portfolio): 10
- Risk per trade (% NAV): 0.75
- Daily loss limit (% portfolio): 2   # measured vs previous close NAV (last nav_log row)
- Drawdown tier-1 floor ($): 925   # below: half size, 1 trade/day, no new names
- Max correlated-bucket exposure (% NAV, satellite): 20   # mega-tech bucket: AAPL MSFT NVDA QQQ
- Max trades/day: 3
- Kill-switch NAV floor ($): 850
- Cadence: 1 daily pass after open (cron: scripts/daily_run.sh) + loop ticks
- Loop interval: 15m (prompts/tick.md)
- Escalation move threshold (%): 1.5
- Hours: regular only (yes)
- Instruments: stocks/ETFs only — no options, no margin

Kill: "stop" = disarm. "go flat" = close all + disarm.
Kill-switch breach: AUTO disarms itself; re-arm requires a human editing this file.
