Run the daily robustness iteration (7-day hardening cycle, then review whether to continue).

1. git pull origin news-framework first (user and bot also commit here).
2. Evidence review — everything new since the last iteration: logs/ (tick +
   daily transcripts), news/ files, findings/, NOTES.md, SCORECARD.md.
   Hunt these failure signatures specifically:
   - dedupe failures (re-logged headlines)
   - escalation gate misfires (escalates on noise / misses real triggers)
   - NOISE leaking into news logs; or real movers misclassified as NOISE
   - rail breaches or near-breaches; sizing arithmetic errors
   - reconciliation mismatches; order stacking
   - prompt vs reality MCP tool-name mismatches (see findings/preflight-*.md)
   - calendar entries past their VERIFY date
3. Fix what the evidence shows: prompts/, strategy/playbook.md, scripts/,
   classification wording. HARD CONSTRAINT: never loosen CLAUDE.md hard rails
   or config.md caps/floors/mode — human-only. Rail-change ideas → NOTES.md
   as proposals.
4. Run python3 eval/stats.py and python3 eval/benchmark.py --sim; include
   outputs in the iteration note.
5. Append a one-line iteration summary to NOTES.md
   (`DATE — ITERATE — found X, fixed Y, proposed Z`).
6. Commit descriptively; push to origin news-framework (if push fails, keep
   the commit local and say so in the note).
7. No new evidence since last time? Red-team ONE component instead (tick /
   daily / playbook / people-watch / learning loop) and harden it. Small,
   evidence-driven changes over speculation.
