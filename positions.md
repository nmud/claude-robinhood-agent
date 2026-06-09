# positions — current state (the ONLY authoritative open-position ledger)

Updated in the SAME pass as any entry, exit, or stop adjustment — never later.
Reconciled against broker truth every pass (mismatch = no trades, see CLAUDE.md).
History lives in findings/ and SCORECARD; this file is now-state only.

| Ticker | Opened | Setup | Entry | Inval | Target | Shares | Thesis (one line) | Finding |
|---|---|---|---|---|---|---|---|---|
| (none) | | | | | | | | |

Cash: $— · Core sleeve (S0): not yet established · Mode: SIM
Pending orders: none
Last updated: 2026-06-09 (initialized, pre-funding)

## Order intent log (crash safety — see CLAUDE.md Execution discipline)
Before placing any order: append `INTENT | time | tkr side qty @ limit | reason`.
After fill/cancel: append `CONFIRM | time | fill price` or `CANCELLED | time`.
An INTENT without CONFIRM at next pass = check broker open orders/fills FIRST.
(empty)
