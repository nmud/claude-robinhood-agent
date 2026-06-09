# TESTING — evening loop test (markets closed)

Config is already `Mode: SIM`. After hours, every tick should run NEWS-ONLY:
sweep → classify → log; paper plans instead of orders; nothing real placed.

## Run it

```
cd ~/claude-robinhood-agent
claude
/mcp                       # confirm robinhood-trading is connected
/loop 15m Run one tick per prompts/tick.md
```

(Or a single manual tick first: just say "Run one tick per prompts/tick.md".)

Stop with: "stop the loop" / Esc.

## What to verify, tick by tick

1. **Tick 1:** creates `news/YYYY-MM-DD.md`; macro sweep + `calendar.md` refreshed
   (earnings dates for all 5 allowlist tickers present, with Verified-on date).
2. **Tick 2 (the dedupe test):** same headlines are NOT re-logged. A quiet tick
   appends exactly one `no escalation` line. If it re-classifies tick 1's items,
   the dedupe instruction is failing — that's a bug to fix in prompts/tick.md.
3. **No real orders:** zero `place_order`-type MCP calls in any tick (SIM +
   market closed = doubly impossible; if one ever appears it's a sev-0 prompt bug).
4. **Escalation gate honesty:** evening price moves are stale/AH — ticks should
   mostly NOT escalate. If every tick escalates, the gate is too loose.
5. **[SIM-PLAN] rows** (if any ENTRY-RELEVANT news lands): logged to SCORECARD
   with qty within the $100 per-order cap and a written invalidation.
6. **No account data in web queries** — skim the tick transcripts for leaks.

## Pass criteria for graduating SIM → ADVISE
- ≥1 full simulated trading day (loop during market hours) with: clean dedupe,
  mostly-quiet ticks, every [SIM] order inside the rails, NAV row appended once.
- Then a few days in ADVISE approving by hand. Only then "arm AUTO"
  (and keep Robinhood's app-side trade review on for the first AUTO week).
