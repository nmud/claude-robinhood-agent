# WATCHER — event-driven runtime

Replaces "Claude polls in a loop" with "a cheap process watches the tape and
only wakes Claude when something happens." Implements three issues:

- **#2 — no token waste.** `watcher.py` polls quotes **directly from a free,
  no-key API** (Yahoo Finance v8 chart endpoint). No Claude, no MCP, no tokens
  while the market is quiet. It wakes the agent only on a real move.
- **#1 — 1:1 agent-to-stock.** Each trigger spawns **one** `claude -p` scoped to
  **one** ticker (`prompts/watch_trigger.md`). One brain per name, never one
  agent juggling the whole list.
- **#3 — start / stop / resume.** The watcher runs as a detached daemon that
  survives an ssh disconnect. Scripts manage and reattach to it.

## Flow per tick (no LLM in this path)
```
watcher.py  --poll-->  Yahoo v8 chart (free)  -->  |move| >= move_trigger_pct ?
                                                      |                |
                                                     no               yes
                                                      |                |
                                              log one line     spawn ONE `claude -p TICKER`
                                              (cheap, quiet)    (the only place tokens are spent)
```
The agent then does the real work per `CLAUDE.md` + `prompts/watch_trigger.md`:
regime → strategy → risk → act by mode (SIM/ADVISE/AUTO), then logs to
`findings/` + `SCORECARD.md`.

## Run it
```bash
scripts/start.sh     # start daemon (survives ssh drop); writes watcher.pid
scripts/status.sh    # running? recent ticks + in-flight agents
scripts/resume.sh    # "tap back in" — follow the live log (Ctrl-C just detaches)
scripts/stop.sh      # SIGTERM, clean exit (does NOT flatten positions)
```
`start.sh` uses `python3`; override with `WATCHER_PY=/path/to/python`.
The agent binary defaults to `claude`; override with `WATCHER_CLAUDE_BIN`.

## Configure
All tunables live in `config.md` under **## Watcher** (machine-read `key: value`):
`watch_tickers, poll_seconds, move_trigger_pct, take_profit_pct,
cooldown_seconds, max_concurrent_agents, market_hours_only, stale_seconds,
short_via`. If `watch_tickers` is omitted it falls back to the Core `Allowlist`.

## Shorting note (important)
The agentic account is a **long-only cash account** — it can't short equities
directly. The objective ("short, take 2–3%") is expressed by the agent via
`short_via`: an **inverse ETF** (SPY→SH/SPXU, QQQ→PSQ/SQQQ) or **puts** once the
options sleeve is armed. Single names with no clean inverse → the agent stands
down rather than forcing a bad proxy.

## Safety
- Quotes are a **wake signal only**. The agent re-checks the live MCP quote
  before any order; a stale/errored watcher quote during RTH never triggers.
- All hard rails stay in `CLAUDE.md` + `config.md` (allowlist, caps, daily loss
  limit, max trades/day, market hours, always-an-invalidation). The watcher can
  only *wake* the agent — every order still passes the rails.
- Market-hours gate is built in (US Eastern, DST-aware; holidays not modeled —
  the MCP/rails catch a closed market).

## Test without trading (no real orders, tiny/zero tokens)
```bash
# 1) prove the free API + the spawn plumbing — no Claude, no tokens
python3 watcher.py --selftest

# 2) one real pass, but never spawn Claude — just log what it WOULD trigger
python3 watcher.py --once --dry-run

# 3) force a trigger and actually call the agent, but read-only + a stub prompt
python3 watcher.py --force-trigger SPY --safe-tools \
  --test-prompt "Reply with exactly: READY. Do not use any tools."
#   -> check logs/agent_SPY_*.log for READY  (proves watcher -> agent end to end)
```
On Windows (dev box) use the full interpreter path, e.g.
`& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" watcher.py --selftest`.
