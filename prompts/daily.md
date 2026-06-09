Run the daily pass. Stages in order — do not skip, do not reorder.

## 1. Snapshot + reconcile (one batched read)
Portfolio, positions, buying power, OPEN ORDERS, quotes for held + allowlist
tickers (get_portfolio, get_equity_positions, get_equity_quotes). MCP error or
stale quote → log it, place no trades, stop.
Broker truth vs journal mismatch (position we didn't log, fill we missed,
manual trade) → reconcile in writing first; no new trades this pass.

## 2. Safety gates
- Kill switch: NAV below floor in config.md → no trades, post-mortem to NOTES.md, stop.
- Daily loss limit / max trades — check before any order, not after.

## 3. Calendar + news sweep (WebSearch — account data never goes into queries)
- Refresh `calendar.md`: earnings dates for held + allowlist tickers; macro
  events (FOMC, CPI, NFP) in the next 2 weeks.
- Per held position: scan headlines since the last pass. Classify each hit:
  THESIS-BREAKING / THESIS-CONFIRMING / NOISE. Only the first two go in the finding.
- People & policy sweep per `strategy/people.md`: Tier-1 statements (President,
  Fed, regulators) affecting held/allowlist names or the whole tape; Tier-2/3
  (congressional disclosures, 13Fs, short reports) as ENTRY-RELEVANT ideas only —
  disclosure lag means idea, never copy-trade.
- Macro: one-line regime-relevant summary (rates, vol, sector rotation). No essays.

## 4. Memory load
Read `strategy/lessons.md`. ACTIVE lessons bind today's decisions; contradicting
one requires written justification in the finding.
First trading day of the month → run the S0 core-sleeve check (playbook).

## 5. Regime (per CLAUDE.md: ≥2 signals, not vibes)

## 6. Position review (ledger = positions.md, not memory)
Each row in positions.md: check against its invalidation, its time stop
(15 sessions, playbook), AND today's news class. Invalidation hit or
THESIS-BREAKING news → exit this pass. Earnings within 5 sessions → explicit
hold-through-or-exit decision, in writing. Any change → update positions.md
same pass (intent-then-confirm for orders).

## 7. New ideas (max 1–2, allowlist only, playbook setups only)
Entry checklist: named setup + thesis + catalyst/timeframe + invalidation +
risk-based size + calendar check (no entry ≤2 days before earnings unless the
thesis IS the event, half size).

## 8. Act
SIM: paper order to SCORECARD [SIM]. ADVISE: propose and wait. AUTO: place within rails.

## 9. Log + learn
- `findings/YYYY-MM-DD-<tkr>.md` per call (include Catalysts + setup name).
- Every trade RESOLVED today (exit or invalidation): SCORECARD row + NOTES.md
  lesson line + lessons.md update — add/strengthen a CANDIDATE, promote to
  ACTIVE only at ≥3 observations, demote an ACTIVE lesson it contradicts.
- Append `date,nav,spy_close` to `eval/nav_log.csv` (SPY close via quote or web).

Be terse. Numbers over narrative. "No trade" is a complete, respectable output.
