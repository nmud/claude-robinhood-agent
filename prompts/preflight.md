Run the preflight check. NO ORDERS of any kind in this pass — read-only.
Write results to findings/preflight-YYYY-MM-DD.md as PASS/FAIL per item.

## 1. Tool inventory
List every robinhood-trading MCP tool with a one-line description (from the
tool schemas — do not call destructive ones). Flag which are reads vs orders.

## 2. Historical data check (critical — regime calls depend on it)
The playbook needs: 200d MA, 50d MA, recent ranges, volume context.
- Test on SPY: can any MCP tool return historical candles/closes?
- If NOT: establish the web fallback now — fetch SPY's 200d/50d MA from a
  public source, record which source + how, and add the method to
  strategy/playbook.md as a note. No verified MA source = S0/S1/S2 cannot run.

## 3. Order capability check (schema-read only, place NOTHING)
From the order tool's schema: which order types exist? (limit? stop? stop-limit?
time-in-force?) Record whether broker-side stops are possible — this decides
whether invalidations are hard stops or per-tick soft stops (CLAUDE.md
Execution discipline).

## 4. Account baseline + reconcile
- Pull NAV, cash, positions, open orders. Write the baseline row to
  eval/nav_log.csv and a position inventory to today's finding.
- Any existing positions/orders the journal doesn't know → record them now as
  the starting state (inherited, no thesis — decide hold/exit in next daily pass).

## 5. Sizing dry-run (arithmetic only)
Hypothetical S1 trade: NAV from step 4, entry $100, invalidation $96.
Show: risk$ = 0.75% × NAV; shares = risk$ / 4; position value; then apply
per-order cap, max position %, cash floor. Compute twice, confirm identical.

## 6. News pipeline smoke test
One Tier-1 people sweep + one headline sweep for SPY. Confirm items get
classified and logged to news/ in the correct format, with sources tiered.

## 7. Verdict
PASS only if: (2) has a verified MA source, (3) order types are known,
(4) reconciliation is clean. Any FAIL → fix before SIM graduates to ADVISE.
