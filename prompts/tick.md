Run ONE loop tick. Light by default — escalate only when news or price warrants.

## 0. Mode, hours, reconcile
- Read `Mode` from config.md: SIM / ADVISE / AUTO.
- Market closed (incl. pre/after-hours)? → NEWS-ONLY tick: run stages 1–2,
  log, stop. No orders in any mode; SIM logs a "plan for next open" instead.
- Market open → one batched snapshot: positions, cash, OPEN ORDERS, quotes.
  Broker state vs our journal mismatch → log discrepancy, NO trades this tick.

## 1. News sweep (the core of every tick)
- "Last tick" = the latest timestamp in today's `news/YYYY-MM-DD.md`
  (first tick of the day: the last timestamp in yesterday's file). That
  timestamp is the single source of truth for "since when".
- WebSearch headlines for held + allowlist tickers published since the last tick.
- Dedupe: check today's `news/YYYY-MM-DD.md` (and yesterday's on the first tick).
  Already-logged items are skipped silently.
- Classify each NEW item:
  - THESIS-BREAKING — contradicts a held position's logged thesis
  - THESIS-CONFIRMING — supports a held thesis
  - ENTRY-RELEVANT — could justify a new allowlist entry (catalyst-grade only)
  - NOISE — everything else (do not log)
- Append non-noise items to `news/YYYY-MM-DD.md`:
  `HH:MM | TKR | class | one-line summary | source domain`
- People & policy sweep (`strategy/people.md`): Tier-1 (President/Fed/regulators)
  EVERY tick — a statement naming a held ticker or its sector is a
  THESIS-BREAKING-candidate, reviewed this tick. Tiers 2–3 (congressional
  disclosures, 13Fs, short reports) on the first tick of the day only.
- First tick of the day only: macro sweep (rates, VIX, today's data releases)
  + refresh `calendar.md`.
- Account data NEVER goes into web queries.

## 2. Escalation gate
Run the full decision stage ONLY if at least one is true:
- any THESIS-BREAKING or ENTRY-RELEVANT item this tick
- an allowlist/held ticker moved more than the threshold in config.md since last tick
- a held position is within 1% of its logged invalidation
- it's the first tick of the trading day (full pass per prompts/daily.md)
Otherwise append one line to `news/YYYY-MM-DD.md`: `HH:MM | tick | no escalation`
and STOP. A quiet tick is the normal outcome.

## 3. Decision (only if escalated)
Per CLAUDE.md: regime (≥2 signals) → playbook setup (strategy/playbook.md — name
it, or NO-TRADE) → risk (entry·invalidation·target·risk-based size). All rails
apply: allowlist, caps, earnings blackout, drawdown tier, kill switch,
daily loss limit, max trades/day.

## 4. Act — by mode
- SIM: no real orders ever. Log the paper order to SCORECARD.md tagged [SIM]
  with tkr·side·qty·ref price·time. Market closed → log as [SIM-PLAN] for open.
- ADVISE: propose (tkr·side·qty·price·why·invalidation), wait for "yes".
- AUTO: place within config.md rails. Log fill to SCORECARD immediately.

## 5. Log
- Escalated tick → `findings/YYYY-MM-DD-<tkr>.md` (include Catalysts line).
- Once per day (first escalated tick or last tick): append `date,nav,spy_close` —
  real modes → `eval/nav_log.csv`; SIM → `eval/nav_log_sim.csv` (paper NAV =
  cash + marked paper positions). NEVER write paper NAV to the real log.

Be terse. One batched quote read per tick. No essays on quiet ticks.
