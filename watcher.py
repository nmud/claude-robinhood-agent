#!/usr/bin/env python3
"""
watcher.py — token-free market watcher for the agentic trading repo.

Why this exists (GitHub issues #1, #2, #3):
  #2  Don't burn LLM tokens polling. This process polls quotes DIRECTLY from a
      free market-data API (no Claude, no MCP) and only wakes the agent when a
      ticker actually moves past a threshold.
  #1  1:1 agent-to-stock. Each trigger spawns ONE `claude -p` agent scoped to a
      SINGLE ticker (prompts/watch_trigger.md), never one brain juggling all.
  #3  Runs headless as a daemon (scripts/start.sh uses setsid) so it survives an
      ssh drop; it owns watcher.pid for single-instance + stop/status/resume.

Data source: Yahoo Finance v8 chart endpoint — free, NO API key, near real-time
for liquid US equities. (v7 /quote now needs a crumb+cookie; v8 /chart does not.)
Mirror host query2 is tried if query1 fails.

Objective bias: SHORT setups, take 2-3% profit. The cash account is long-only,
so "short" is expressed by the agent as an inverse ETF / put (see config.md
short_via). The watcher is direction-agnostic: it wakes the agent on any move
past the threshold; the agent decides side + instrument per CLAUDE.md.

Stdlib only. Python 3.8+. No pip installs, no tzdata (Eastern time computed here).
"""

import argparse
import datetime as dt
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(ROOT, "logs")
PIDFILE = os.path.join(ROOT, "watcher.pid")
CONFIG = os.path.join(ROOT, "config.md")
PROMPT_TEMPLATE = os.path.join(ROOT, "prompts", "watch_trigger.md")

UA = "Mozilla/5.0 (watcher.py; agentic-trading)"
TRADE_TOOLS = ["mcp__robinhood-trading__*", "Read", "Write", "Edit",
               "Glob", "Grep", "WebSearch", "WebFetch"]
SAFE_TOOLS = ["Read", "Glob", "Grep"]

DEFAULTS = {
    "watch_tickers": "SPY, QQQ, AAPL, SG",
    "poll_seconds": 60,
    "move_trigger_pct": 0.6,
    "take_profit_pct": 2.5,
    "cooldown_seconds": 600,
    "max_concurrent_agents": 2,
    "market_hours_only": True,
    "stale_seconds": 300,
    "short_via": "inverse_etf",
}

_STOP = False


# ---------------------------------------------------------------- logging
def log(msg):
    ts = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} | {msg}", flush=True)


# ---------------------------------------------------------------- config
def _coerce(key, val):
    if key in ("poll_seconds", "cooldown_seconds", "max_concurrent_agents",
               "stale_seconds"):
        return int(float(val))
    if key in ("move_trigger_pct", "take_profit_pct"):
        return float(val)
    if key == "market_hours_only":
        return str(val).strip().lower() in ("1", "true", "yes", "on")
    return val.strip()


def load_config(path=CONFIG):
    """Parse simple 'key: value' lines out of config.md. Single source of truth;
    falls back to DEFAULTS + env for anything missing or if the file is absent."""
    cfg = dict(DEFAULTS)
    allowlist_line = None
    text = ""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    for raw in text.splitlines():
        line = raw.strip().lstrip("-* ").strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower().replace(" ", "_")
        val = val.split("#")[0].split("(")[0].strip()  # drop inline comments
        if key in DEFAULTS:
            try:
                cfg[key] = _coerce(key, val)
            except ValueError:
                pass
        elif key == "allowlist" and allowlist_line is None:
            allowlist_line = val

    # tickers: explicit watch_tickers wins, else the Core rails Allowlist line
    raw_tk = os.environ.get("WATCHER_TICKERS") or cfg.get("watch_tickers") \
        or allowlist_line or DEFAULTS["watch_tickers"]
    tickers = [t.strip().upper() for t in raw_tk.replace(",", " ").split()
               if t.strip().isalpha()]
    cfg["tickers"] = tickers or ["SPY"]
    return cfg


# ------------------------------------------------------------ market hours
def eastern_now(utcnow=None):
    """US Eastern wall-clock, EDT/EST handled without tzdata.
    DST: 2nd Sun Mar 02:00 -> 1st Sun Nov 02:00."""
    u = utcnow or dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)

    def nth_sunday(year, month, n):
        first = dt.date(year, month, 1)
        first_sun = 1 + (6 - first.weekday()) % 7
        return first_sun + (n - 1) * 7

    y = u.year
    dst_start = dt.datetime(y, 3, nth_sunday(y, 3, 2), 7)    # 02:00 EST = 07:00 UTC
    dst_end = dt.datetime(y, 11, nth_sunday(y, 11, 1), 6)    # 02:00 EDT = 06:00 UTC
    edt = dst_start <= u < dst_end
    off = -4 if edt else -5
    return u + dt.timedelta(hours=off), ("EDT" if edt else "EST")


def market_open():
    et, _ = eastern_now()
    if et.weekday() >= 5:               # Sat/Sun
        return False
    mins = et.hour * 60 + et.minute
    return 9 * 60 + 30 <= mins <= 16 * 60   # 09:30–16:00 ET (holidays not handled)


# ---------------------------------------------------------------- quotes
def fetch_quote(symbol):
    """Return (price, market_time_epoch) or (None, None) on failure."""
    last_err = None
    for host in ("query1", "query2"):
        url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/"
               f"{symbol}?interval=1m&range=1d")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.load(r)
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice")
            mtime = meta.get("regularMarketTime")
            if price is not None:
                return float(price), (int(mtime) if mtime else None)
        except (urllib.error.URLError, KeyError, TypeError,
                ValueError, IndexError) as e:
            last_err = e
            continue
    log(f"WARN quote fetch failed {symbol}: {last_err}")
    return None, None


# ---------------------------------------------------------------- trigger
def render_prompt(ticker, price, anchor, move_pct, cfg):
    direction = "UP" if move_pct >= 0 else "DOWN"
    fields = {
        "TICKER": ticker,
        "PRICE": f"{price:.2f}",
        "ANCHOR": f"{anchor:.2f}",
        "MOVE": f"{move_pct:+.2f}%",
        "DIRECTION": direction,
        "TAKE_PROFIT_PCT": str(cfg["take_profit_pct"]),
        "SHORT_VIA": str(cfg["short_via"]),
        "TIME": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "DATE": eastern_now()[0].strftime("%Y-%m-%d"),
        "TICKER_LOWER": ticker.lower(),
    }
    if os.path.exists(PROMPT_TEMPLATE):
        with open(PROMPT_TEMPLATE, "r", encoding="utf-8") as f:
            tmpl = f.read()
        for k, v in fields.items():
            tmpl = tmpl.replace("{" + k + "}", v)
        return tmpl
    # inline fallback if the template is missing
    return (f"Wake reason: {ticker} moved {fields['MOVE']} to {fields['PRICE']} "
            f"(anchor {fields['ANCHOR']}). Run ONE pass for {ticker} ONLY per "
            f"CLAUDE.md (regime -> strategy -> risk). Short bias; express short "
            f"via {fields['SHORT_VIA']}. Target +{fields['TAKE_PROFIT_PCT']}%. "
            f"Always set invalidation. Log to findings/ + SCORECARD.md.")


def spawn_agent(ticker, prompt, claude_bin, safe=False, dry=False):
    os.makedirs(LOGS, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    logpath = os.path.join(LOGS, f"agent_{ticker}_{stamp}.log")
    tools = SAFE_TOOLS if safe else TRADE_TOOLS
    cmd = [claude_bin, "-p", prompt, "--allowedTools", *tools]
    if dry:
        with open(logpath, "w", encoding="utf-8") as f:
            f.write("[DRY-RUN] would spawn:\n" + " ".join(cmd[:3]) +
                    " ...\n\n--- PROMPT ---\n" + prompt + "\n")
        log(f"[DRY-RUN] trigger {ticker} -> {os.path.relpath(logpath, ROOT)}")
        return None
    f = open(logpath, "w", encoding="utf-8")
    try:
        proc = subprocess.Popen(
            cmd, stdout=f, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, cwd=ROOT,
            close_fds=(os.name != "nt"))
    except FileNotFoundError:
        f.close()
        log(f"ERROR claude binary not found: {claude_bin!r} "
            f"(set WATCHER_CLAUDE_BIN). Trigger for {ticker} dropped.")
        return None
    log(f"TRIGGER {ticker} -> agent pid {proc.pid}, log "
        f"{os.path.relpath(logpath, ROOT)}")
    return proc


# ---------------------------------------------------------------- state
class TickerState:
    __slots__ = ("anchor", "last_trigger", "proc", "anchor_day")

    def __init__(self):
        self.anchor = None
        self.last_trigger = 0.0
        self.proc = None
        self.anchor_day = None


# ---------------------------------------------------------------- core
def reap(states):
    """Clear finished agent processes; return count still running."""
    active = 0
    for tk, st in states.items():
        if st.proc is not None:
            rc = st.proc.poll()
            if rc is None:
                active += 1
            else:
                log(f"agent {tk} finished rc={rc}")
                st.proc = None
    return active


def poll_pass(cfg, states, claude_bin, force=None, test_prompt=None,
              safe=False, dry=False):
    if cfg["market_hours_only"] and not market_open() and not force:
        et, tz = eastern_now()
        log(f"market closed ({et:%H:%M} {tz}) — idle")
        return
    active = reap(states)
    et, tz = eastern_now()
    today = et.date()
    now = time.time()
    cells = []
    for tk in cfg["tickers"]:
        st = states[tk]
        price, mtime = fetch_quote(tk)
        if price is None:
            cells.append(f"{tk} ERR")
            continue

        # daily re-anchor at session rollover; first-ever read anchors here
        if st.anchor is None or st.anchor_day != today:
            st.anchor = price
            st.anchor_day = today
            st.last_trigger = 0.0

        move = (price - st.anchor) / st.anchor * 100.0
        cells.append(f"{tk} {price:.2f} {move:+.2f}%")

        forced = force == tk
        breach = abs(move) >= cfg["move_trigger_pct"]
        cooled = (now - st.last_trigger) >= cfg["cooldown_seconds"]
        free = st.proc is None and active < cfg["max_concurrent_agents"]
        stale = (mtime is not None
                 and (time.time() - mtime) > cfg["stale_seconds"]
                 and market_open())

        if forced or (breach and cooled and free and not stale):
            if stale and not forced:
                log(f"{tk} move {move:+.2f}% but quote STALE — no trigger")
                continue
            prompt = test_prompt or render_prompt(tk, price, st.anchor, move, cfg)
            proc = spawn_agent(tk, prompt, claude_bin, safe=safe, dry=dry)
            st.proc = proc
            st.last_trigger = now
            st.anchor = price            # re-anchor: need a fresh move next time
            if proc is not None:
                active += 1
        elif breach and not cooled:
            pass  # within cooldown; stay quiet

    log(f"TICK {tz} | " + " | ".join(cells) + f" | agents={active}")


# ---------------------------------------------------------------- pidfile
def acquire_pidfile(force=False):
    if os.path.exists(PIDFILE):
        try:
            old = int(open(PIDFILE).read().strip())
        except (ValueError, OSError):
            old = None
        if old and _pid_alive(old) and not force:
            log(f"already running (pid {old}) — refusing to start a second "
                f"instance. Use scripts/stop.sh first, or --force.")
            return False
    with open(PIDFILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _pid_alive(pid):
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                             capture_output=True, text=True)
        return str(pid) in out.stdout
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def release_pidfile():
    try:
        if os.path.exists(PIDFILE) and \
                open(PIDFILE).read().strip() == str(os.getpid()):
            os.remove(PIDFILE)
    except OSError:
        pass


def _handle_signal(signum, frame):
    global _STOP
    _STOP = True
    log(f"signal {signum} — stopping after this pass")


# ---------------------------------------------------------------- main
def run_loop(cfg, claude_bin, dry=False):
    states = {tk: TickerState() for tk in cfg["tickers"]}
    log(f"watcher up | tickers={cfg['tickers']} | poll={cfg['poll_seconds']}s "
        f"| trigger>={cfg['move_trigger_pct']}% | cooldown={cfg['cooldown_seconds']}s "
        f"| TP={cfg['take_profit_pct']}% | short_via={cfg['short_via']} "
        f"| dry={dry} | claude={claude_bin}")
    while not _STOP:
        try:
            poll_pass(cfg, states, claude_bin, dry=dry)
        except Exception as e:                       # never let one bad pass kill the daemon
            log(f"ERROR pass: {type(e).__name__}: {e}")
        # responsive sleep so a signal stops us promptly
        slept = 0
        while slept < cfg["poll_seconds"] and not _STOP:
            time.sleep(min(1, cfg["poll_seconds"] - slept))
            slept += 1
    reap(states)
    log("watcher stopped")


def selftest(cfg, claude_bin):
    log("SELFTEST: live quote fetch")
    tk = cfg["tickers"][0]
    price, mtime = fetch_quote(tk)
    if price is None:
        log("SELFTEST FAIL: could not fetch a quote")
        return 1
    age = (int(time.time()) - mtime) if mtime else "?"
    log(f"SELFTEST quote OK: {tk} {price:.2f} (age {age}s)")
    log("SELFTEST: stubbed agent spawn (proves Popen + log capture)")
    stub = [sys.executable, "-c",
            "import sys;print('AGENT-STUB OK argv=%d' % len(sys.argv))"]
    os.makedirs(LOGS, exist_ok=True)
    out = subprocess.run(stub, capture_output=True, text=True)
    if "AGENT-STUB OK" in out.stdout:
        log(f"SELFTEST spawn OK: {out.stdout.strip()}")
        log("SELFTEST PASS")
        return 0
    log(f"SELFTEST FAIL: spawn output {out.stdout!r} {out.stderr!r}")
    return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=CONFIG)
    ap.add_argument("--once", action="store_true", help="single pass then exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="log intended triggers, never spawn claude")
    ap.add_argument("--force-trigger", metavar="SYM",
                    help="force a trigger for SYM this pass (testing)")
    ap.add_argument("--test-prompt", metavar="TEXT",
                    help="override the agent prompt (testing)")
    ap.add_argument("--safe-tools", action="store_true",
                    help="restrict spawned agent to read-only tools (testing)")
    ap.add_argument("--selftest", action="store_true",
                    help="check the free API + spawn path, print PASS/FAIL, exit")
    ap.add_argument("--force", action="store_true",
                    help="start even if a pidfile exists")
    args = ap.parse_args()

    cfg = load_config(args.config)
    claude_bin = os.environ.get("WATCHER_CLAUDE_BIN") or cfg.get("claude_bin") \
        or "claude"
    dry = args.dry_run or os.environ.get("WATCHER_DRYRUN") in ("1", "true")

    os.makedirs(LOGS, exist_ok=True)

    if args.selftest:
        sys.exit(selftest(cfg, claude_bin))

    # one-shot modes don't claim the daemon pidfile
    if args.once or args.force_trigger:
        states = {tk: TickerState() for tk in cfg["tickers"]}
        poll_pass(cfg, states, claude_bin, force=args.force_trigger,
                  test_prompt=args.test_prompt, safe=args.safe_tools, dry=dry)
        # let a forced real agent finish so its log is captured
        st = states.get(args.force_trigger) if args.force_trigger else None
        if st and st.proc is not None:
            log("waiting for forced agent to finish...")
            st.proc.wait()
            reap(states)
        return

    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)

    if not acquire_pidfile(force=args.force):
        sys.exit(1)
    try:
        run_loop(cfg, claude_bin, dry=dry)
    finally:
        release_pidfile()


if __name__ == "__main__":
    main()
