Run ONE pass for **{TICKER} ONLY**. You were woken by watcher.py — not on a clock,
but because {TICKER} actually moved. Do not analyze any other ticker. This is the
1:1 agent-to-stock pass (issue #1): one brain, one name, one decision.

## Wake reason
{TIME} — {TICKER} moved {MOVE} {DIRECTION} to {PRICE} (anchor {ANCHOR}).

## Objective
SHORT bias, take **+{TAKE_PROFIT_PCT}%** profit and exit. The account is a
long-only cash account — you CANNOT short the equity directly. Express short as
`{SHORT_VIA}`:
- inverse_etf — short SPY via SH/SPXU, QQQ via PSQ/SQQQ, broad market via SH.
  For single names with no clean inverse (e.g. AAPL, SG), prefer the sector/index
  inverse or stand down — do not force a bad proxy.
- puts — only if the options sleeve is armed in config.md (dormant by default).
If neither fits cleanly, the right answer is **NO-TRADE**. Say so.

## Do this, in order (per CLAUDE.md)
1. **Snapshot** — one batched MCP read: portfolio, cash, open orders, and a live
   quote for {TICKER} (and the inverse instrument you'd actually trade). The
   watcher price is a wake signal from a free feed; the MCP quote is the
   authority before any order.
2. **Regime?** — ≥2 signals, not vibes. Is this move a shortable pop / breakdown,
   or noise? Trend vs range vs vol.
3. **Strategy fit?** — name the setup, and why not the alternatives. A move past
   the watcher threshold is a *reason to look*, never a reason to trade.
4. **Risk?** — entry · invalidation (always) · target = **+{TAKE_PROFIT_PCT}%** ·
   size per config.md rails (per-order cap, max position %, risk per trade).
5. **Mode** — read `Mode` from config.md:
   - SIM → log a paper order, no real order ever.
   - ADVISE → propose (tkr·side·qty·price·why·invalidation) and STOP. Do not place.
   - AUTO → place within rails only; set the stop on entry; log the fill to
     SCORECARD.md immediately.

## Rails (hard — from config.md)
Allowlist only · per-order cap · max position % · risk per trade · daily loss
limit · max trades/day · market hours · always an invalidation. Any breach or
stale/errored quote → NO-TRADE this pass. If we already hold this name, manage
the existing position (take +{TAKE_PROFIT_PCT}% / honor stop) before adding.

## Log
- `findings/{DATE}-{TICKER_LOWER}.md` — regime, the call, entry/inval/target, why.
- SCORECARD.md on any order (real or SIM) — tkr·side·qty·price·fill.
- NOTES.md on resolve.

Be terse and decisive: **enter / hold / exit / no-trade** with conviction + the
level that proves it wrong. "No-trade" is a real answer. No essays.
