# news/ — the agent's news memory

One file per day: `news/YYYY-MM-DD.md`. Every loop tick appends non-noise items;
this is what makes ticks idempotent — a headline logged once is never
re-classified or re-acted-on.

Line format:
```
HH:MM | TKR | THESIS-BREAKING|THESIS-CONFIRMING|ENTRY-RELEVANT | one-line summary | source
HH:MM | tick | no escalation
HH:MM | macro | one-line regime-relevant summary
```

Rules:
- NOISE is never logged. If most of a day's file is noise, the classifier is broken.
- THESIS-BREAKING items must reference which position/finding they break.
- Append-only. Never rewrite history.
