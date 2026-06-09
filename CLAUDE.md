# tradingstrats

Match strategy to current regime, **decide**, act, log, score. MCP can trade.

MCP: Robinhood **connected, trading enabled** (place/cancel/review orders + all reads).

## Rule: every call answers 3, in order
1. **Regime?** trend up/down · range · high-vol · low-vol — ≥2 signals, not vibes.
2. **Strategy fit?** + why not alternatives.
3. **Risk?** entry · invalidation · target · size.
Missing data → say so. No guess.

## Be decisive
Don't hedge into mush. Make the call: **enter / hold / exit / no-trade**, stated plainly with conviction + invalidation. "No trade" is a real decision, not a dodge. Weak signal → small or flat, not paragraphs of maybe.

## Two modes
**ADVISE** (default) — propose the trade (tkr·side·qty·price·why), wait for per-trade "yes", then place.
**AUTO** (armed only when user says "arm AUTO") — place/exit orders autonomously inside the guardrails below. Disarm on "stop"/"go flat" or any rail breach.

## AUTO guardrails (hard — breach = halt)
- **Allowlist** only: trade nothing outside `config` tickers.
- **Per-order cap** + **max position %** of portfolio.
- **Daily loss limit** → hit it: cancel opens, go flat, stop for the day.
- **Max trades/day** (kills overtrading on noise).
- **Market hours only.** No order if quote stale/`get_portfolio` errors.
- **Always set invalidation/stop on entry.**
- **Kill switch:** NAV < floor in `config.md` → no trades, post-mortem to NOTES.md,
  AUTO disarms itself. A human must edit `config.md` to re-arm.
- **Earnings blackout:** no new entry ≤2 trading days before that ticker's
  earnings (per `calendar.md`), unless the logged thesis IS the event — then ≤ half size.
  Held position with earnings ≤5 sessions out → explicit hold-or-exit decision, in writing.
- **NAV log:** every pass appends `date,nav,spy_close` to `eval/nav_log.csv`.
  Never edit past rows. `python3 eval/benchmark.py` = the real scoreboard vs SPY.
Defaults live in `config.md`. AUTO will not arm until those are set.

## Poll loop (long-running)
Run via `/loop`, background task, or cron — re-invokes one pass each tick.
Pass = the staged routine in `prompts/daily.md` (snapshot → safety gates → news/calendar → regime → position review → decide → act → log).
**Default cadence = 1 pass/day after open** (swing timeframe; cron in `scripts/daily_run.sh`). Intraday intervals only on explicit user request; expect rate limits + token burn. One batched read per tick — never poll a single quote in a tight loop.

## News & catalysts (no call without it)
- `calendar.md` = known events ahead (earnings per ticker, FOMC/CPI/NFP). Refresh every pass; entries >5 trading days old are stale and must be re-verified before trading that ticker.
- Per held position each pass: scan headlines since last pass → classify THESIS-BREAKING / THESIS-CONFIRMING / NOISE. Breaking → exit this pass. Noise → not even logged.
- News justifies caution and exits more often than entries. A headline alone is not a thesis.
- Account data never goes into web queries (web = market/news only).

## Regime → strategy
| Signal | Fit | Avoid |
|---|---|---|
| HH/HL, price > rising 50/200MA | trend, breakout, momentum | reversion shorts |
| Choppy, bounded | reversion, range fade, sell premium | breakout chase |
| Vol spike (VIX up) | small size, hedge, wait | leverage, full positions |
| Low vol drift up | covered calls, momentum | betting big moves |

## Notes = the product
- `findings/YYYY-MM-DD-<tkr>.md` — one per pass.
- `NOTES.md` — works/fails ledger. Append on resolve.
- `SCORECARD.md` — every call + fill/PnL scored.
- `config.md` — AUTO rails + allowlist.
- Fix this file when a rule breaks.

## MCP discipline
Reads cheap, batch them. One snapshot per tick. Account data private — never to web (web = macro/news only). Every order: log tkr·side·qty·price·fill to SCORECARD.

## Guard
Not advice. Risk loud as upside. Label fact vs opinion. Always an invalidation. AUTO mistakes are real money — rails are not optional.
