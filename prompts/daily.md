Run the daily pass. Stages in order — do not skip, do not reorder.

## 1. Snapshot (one batched read)
Portfolio, positions, buying power, quotes for held + allowlist tickers
(get_portfolio, get_equity_positions, get_equity_quotes). MCP error or stale
quote → log it, place no trades, stop.

## 2. Safety gates
- Kill switch: NAV below floor in config.md → no trades, post-mortem to NOTES.md, stop.
- Daily loss limit / max trades — check before any order, not after.

## 3. Calendar + news sweep (WebSearch — account data never goes into queries)
- Refresh `calendar.md`: earnings dates for held + allowlist tickers; macro
  events (FOMC, CPI, NFP) in the next 2 weeks.
- Per held position: scan headlines since the last pass. Classify each hit:
  THESIS-BREAKING / THESIS-CONFIRMING / NOISE. Only the first two go in the finding.
- Macro: one-line regime-relevant summary (rates, vol, sector rotation). No essays.

## 4. Regime (per CLAUDE.md: ≥2 signals, not vibes)

## 5. Position review
Each held position: check against its logged invalidation AND today's news class.
Invalidation hit or THESIS-BREAKING news → exit this pass. Earnings within 5
sessions → explicit hold-through-or-exit decision, in writing.

## 6. New ideas (max 1–2, allowlist only)
Entry checklist: thesis + catalyst/timeframe + invalidation + calendar check
(no entry ≤2 days before earnings unless the thesis IS the event, half size).

## 7. Act
ADVISE mode: propose and wait. AUTO mode: place within config.md rails.

## 8. Log
- `findings/YYYY-MM-DD-<tkr>.md` per call (include a Catalysts line).
- Resolved calls → SCORECARD.md row + NOTES.md lesson.
- Append `date,nav,spy_close` to `eval/nav_log.csv` (SPY close via quote or web).

Be terse. Numbers over narrative. "No trade" is a complete, respectable output.
