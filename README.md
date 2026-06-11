# CLAUDE.md Workflow for Agentic Robinhood Trading

Built on [Robinhood Agentic Trading](https://robinhood.com/us/en/agentic-trading/) — connect Claude to your account via MCP and let it trade.

It gives you two things:

1. **An agent that trades for you** — reads the live market, decides, and places the order. Either it proposes each trade for your approval, or runs on its own inside limits you set.
2. **An agent that gets smarter over time** — every call is logged and graded once the outcome lands. Losing patterns get pruned; the track record is the edge.

## One bit of jargon

**Regime** = the market's current character: trending up, trending down, chopping sideways, calm, or wild. It matters because a strategy that prints in one regime bleeds in another. So the agent reads the regime *first*, then matches a strategy to it.

## How to use it

- **Ask it anything** — "regime on SPY?", "worth buying today?". You get a market read + a clear call (buy/hold/sell/wait) with the level that proves it wrong.
- **It starts in ADVISE** — proposes, waits for your "yes", then places. Nothing happens behind your back.
- **Before going hands-off, edit `config.md`** — set the tickers, max per order, daily loss limit, and check interval. The defaults are tiny placeholders, not advice.
- **"arm AUTO"** — it trades on its own, only within `config.md`.
- **"stop"** pauses · **"go flat"** closes everything + pauses. It also halts on a stale feed or your daily loss limit.
- **"run the loop"** — keeps checking + acting on a schedule until you stop it.
- **Review weekly** — `SCORECARD.md` + `NOTES.md` show if it's any good.

## What's in here

- `CLAUDE.md` — the agent's rulebook.
- `config.md` — safety limits for AUTO. **Edit before arming.**
- `watcher.py` + `scripts/` — event-driven runtime: a token-free process watches
  the tape (free API) and wakes a single-ticker agent only on a real move. See
  `WATCHER.md`.
- `findings/` — its write-up per analysis.
- `NOTES.md` — running log of what worked / flopped.
- `SCORECARD.md` — every call, with result + P/L.

## Caution

Not financial advice; AUTO moves real money. Start in ADVISE, keep limits tight until you trust it. The agent can be wrong — every call carries an invalidation level. Past results don't predict future ones.
