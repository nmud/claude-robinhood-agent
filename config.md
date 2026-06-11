# config — AUTO rails + posture

Account: agentic cash acct ••••2663. Value ~$264. Mode: **AUTO — LIVE** (user armed 2026-06-09; investor profile completed, trading unblocked). Acts on confirmed triggers within rails below, no per-trade ask. Kill: "stop"=disarm, "go flat"=close all+disarm. 1 trade used today (SG); 2 left.
Posture: **HYBRID** — disciplined core + ring-fenced lotto sleeve. Set 2026-06-09.

## Capital split
- **Core ~$214** — stocks + fractional shares only. Disciplined risk. This is the real account.
- **Lotto sleeve $50 (hard cap)** — ring-fenced for asymmetric bets. **DORMANT until options enabled** (`option_level` empty — apply: applink.robinhood.com/upgrade_options?account_number=925632663). Max $50 total exposure, ever. Losing the whole sleeve = within plan. Losing more = rail breach.

## Core rails  (AGGRESSIVE-LEAN, set 2026-06-09)
- Allowlist (expanded consciously 2026-06-11 for the short-via-inverse objective): **SPY, QQQ, SH, PSQ, SDS, SQQQ, SPXU**.
  - SPY / QQQ — index longs only (hedge · exit · go-flat · the only up-regime expression).
  - SH (−1x S&P), PSQ (−1x Nasdaq) — calm-regime shorts; need a real ~2–3% index drop to hit target (slow).
  - SDS (−2x S&P) — middle gear; index −1.5% ≈ +3%.
  - SQQQ (−3x Nasdaq), SPXU (−3x S&P) — the scalp workhorses; index −1% ≈ +3% intraday. **Leveraged decay + whipsaw → tight stop mandatory, intraday only.**
  - AAPL & SG = **watch-only** (no clean single-name inverse in a long-only cash acct). Single-name shorts only via puts once the sleeve is armed.
- Per-order cap ($): 130
- Max position (% portfolio): 50  — NOTE: forced concentration at this size; can't diversify $214. Accept it consciously.
- Risk per trade: 3% of total (~$8). Stop placed so max loss ≈ $8. (was 2%/$5)
- Daily loss limit (% portfolio): 4% (~$10) → cancel opens, go flat, stop for the day. UNCHANGED — the floor stays.
- Max trades/day: 3 (cash settlement caps velocity anyway; curbs overtrading)
- Poll interval: 1m (user override; swing default 15m)
- Hours: regular only (yes)

### Aggressive SG trigger (loosened from strict 3/3)
Enter on momentum, not a full macro all-clear. Need ALL of:
- SG breaking session range / new HOD (strength leading), AND
- SPY reclaiming/holding >729 and rising (regime improving, not waiting for >730 confirmed), AND
- VIXY FALLING intraday (cooling — drop the hard <24 wall).
Still ADVISE: propose + wait for yes. Always a stop. Aggression = earlier entry + bigger risk, NOT skipping the stop.

## Sleeve rails (apply once options enabled)
- Total sleeve exposure cap ($): 50
- Per-ticket cap ($): 25 (≥2 swings, not one all-in)
- Allowlist: TBD when armed (liquid optionable names)
- Always define max loss = premium paid. No naked/undefined risk.

## Watcher (event-driven runtime — issues #1/#2/#3)
Token-free monitor (`watcher.py`) polls quotes from a FREE no-key API (Yahoo v8
chart) and wakes a **single-ticker** agent only when a name actually moves —
no LLM tokens spent idling. Each trigger = one `claude -p` scoped to one ticker
(1:1 agent-to-stock). Run it as a daemon: `scripts/start.sh` (survives ssh drop),
`stop.sh`, `status.sh`, `resume.sh`. See WATCHER.md.

Tunables below are machine-read by `watcher.py` (`key: value`, edit freely):
- watch_tickers: SPY, QQQ, IWM, AAPL, SG   # what the watcher POLLS (signal source, not the trade gate). IWM = small-cap risk-off tell. A drop here wakes the agent, which trades the matching inverse from the allowlist.
- poll_seconds: 15
- move_trigger_pct: 0.6                # |move| from anchor that wakes the agent
- take_profit_pct: 2.5                 # objective: short, bank +2–3% per CLAUDE.md
- cooldown_seconds: 600                # min gap between triggers on the same name
- max_concurrent_agents: 2
- market_hours_only: true
- stale_seconds: 300                   # quote older than this during RTH = no trigger
- short_via: inverse_etf               # cash acct is long-only; "short" = inverse ETF (SPY→SH/SPXU, QQQ→PSQ/SQQQ), or puts once sleeve armed

## Kill
"stop" = disarm AUTO. "go flat" = close all + disarm. Any rail breach = halt for the day.
Watcher: `scripts/stop.sh` halts the daemon (does not flatten positions).
