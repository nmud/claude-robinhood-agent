# playbook — the only trades that exist

## S0 · Core sleeve (the evidence-based default, checked MONTHLY)
- 50% of NAV lives in the core: SPY (or QQQ) held while price > 200d MA;
  moved to cash when it closes below. Checked on the first trading day of each
  month ONLY — no intra-month flip-flopping.
- Rationale: trend-filtered index exposure (Faber-style) is the highest-evidence
  strategy available to a small account; the tactical setups below (the other
  ~40%, beyond the cash floor) have to beat it to justify existing.
- The benchmark question every month: is the satellite sleeve beating the core?

Every trade must name its setup in the finding and the SCORECARD `Strat` column.
A trade that fits no setup is NO-TRADE by definition. Freestyle = rail breach.
The weekly review (prompts/weekly.md) tunes these setups from scorecard evidence.

## S1 · Trend pullback
- Regime required: uptrend (HH/HL, price > rising 50d MA)
- Trigger: 2–6% pullback to the 50d MA or prior breakout level, then a day that
  closes back above the pullback low's high (reclaim)
- Invalidation: below the pullback swing low
- Target: prior high first, then 2R
- Skip if: earnings ≤ 2 sessions; pullback on THESIS-BREAKING news (that's not
  a dip, that's information)

## S2 · Range breakout
- Regime required: tightening range/low vol after an uptrend, ≥ 2 weeks long
- Trigger: close above range high on above-average volume
- Invalidation: close back inside the range
- Target: range height projected from the breakout
- Skip if: breakout day is also a macro-event day (FOMC/CPI) — moves reverse

## S3 · Range fade
- Regime required: broad sideways range, ≥ 3 touches on each side, vol normal
- Trigger: probe of range support that holds (intraday reclaim)
- Invalidation: close below range support
- Target: mid-range, then range high
- Skip if: range is forming under a falling 200d MA; earnings inside the range trade's horizon

## S4 · Post-earnings drift
- Regime required: any non-high-vol regime
- Trigger: beat-and-raise gap up that HOLDS its day-1 closing range; enter day 2
- Invalidation: close into the gap (gap-fill begins)
- Target: 1.5–2R or 20 sessions, whichever first
- Note: the only setup where the catalyst IS the thesis; needs the actual
  numbers (EPS/rev/guide) in the finding, not "stock went up on earnings"

## S5 · High-vol regime
- Not a setup — a prohibition. VIX spiking / regime = high-vol:
  NO new entries. Manage exits, raise cash toward the floor, wait.

## Time stop (applies to every setup)
A position that has made no progress toward target AND produced no new
confirming information for 15 sessions is closed — the slot and the attention
are worth more than the hope. (S4 keeps its own 20-session limit.)

## Sizing (applies to every setup)
risk-based, not flat-dollar:
  shares = (Risk per trade % × NAV) / (entry − invalidation)
then cap by: per-order $ cap, max position %, min cash floor.
Wider stop ⇒ smaller position, automatically. If the computed size rounds to
a position too small to matter (< $20), the trade isn't worth taking — skip.
