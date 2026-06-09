Run the weekly review. Friday after close (or weekend). No trades in this pass.

## 1. Numbers first
- Run `python3 eval/stats.py` (hit rate, expectancy, profit factor — real and sim
  tallied separately) and `python3 eval/benchmark.py` (vs SPY).
- Paste both outputs into this week's retro entry.

## 2. Grade the calls, not just the outcomes
For each SCORECARD row resolved this week, label it:
- GOOD CALL / GOOD OUTCOME — setup followed, worked
- GOOD CALL / BAD OUTCOME — setup followed, lost (this is fine; expected)
- BAD CALL / GOOD OUTCOME — rail bent or setup stretched, got lucky (worst kind)
- BAD CALL / BAD OUTCOME — process failure, study it
Decision quality is the thing we control. Outcomes follow with sample size.

## 3. Per-setup breakdown
Group resolved trades by playbook setup (S1–S4). Any setup with ≥5 resolved
trades and negative expectancy → propose tightening or suspending it.
Any setup never triggered in 3+ weeks → check if its conditions are realistic.

## 4. News-layer audit
- Sample this week's news/ files: how many ENTRY-RELEVANT items led to anything?
  How many THESIS-BREAKING calls were validated by the subsequent move?
- If NOISE leaked into the logs or breaking news was missed, tighten the
  classification wording in prompts/tick.md.

## 5. Consolidate memory (NOTES → lessons)
- Read this week's NOTES.md entries + lessons.md.
- Promote CANDIDATEs that reached ≥3 observations to ACTIVE (cite the rows).
- Demote ACTIVE lessons contradicted ≥2× this week to RETIRED (strikethrough, keep).
- Merge duplicate/overlapping lessons; lessons.md should stay under ~20 ACTIVE
  entries — if it's growing past that, consolidate harder. A memory that only
  grows is a junk drawer, not learning.
- Week 4+: re-examine the seeded literature priors against OUR scorecard data.

## 6. Write the retro
Append to top of NOTES.md:
`DATE — RETRO — stats one-liner; best/worst setup; one process change proposed`
Plus a findings/YYYY-MM-DD-retro.md with the full numbers.

## 7. Propose changes — within authority
- MAY edit: strategy/playbook.md (tighten/suspend/tune setups),
  prompts/tick.md classification wording, allowlist proposals in the retro.
- MUST NOT touch: CLAUDE.md hard rails, config.md caps/floors/mode.
  Those change only by human edit. Propose in the retro; a human applies.
