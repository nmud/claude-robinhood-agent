#!/usr/bin/env python3
"""Compare bot NAV against buy-and-hold SPY since inception.

Reads eval/nav_log.csv (real) with rows: date,nav,spy_close.
Pass --sim to read eval/nav_log_sim.csv (paper NAV). Never mixed.
"""
import csv
import sys
from pathlib import Path

SIM = "--sim" in sys.argv
LOG = Path(__file__).parent / ("nav_log_sim.csv" if SIM else "nav_log.csv")


def max_drawdown(series):
    peak, mdd = series[0], 0.0
    for x in series:
        peak = max(peak, x)
        mdd = min(mdd, x / peak - 1)
    return mdd


def main():
    if not LOG.exists():
        sys.exit("no nav_log.csv yet — run the bot first")
    rows = [r for r in csv.reader(LOG.open()) if r and not r[0].startswith("date")]
    if len(rows) < 2:
        sys.exit("need at least 2 data points")

    dates = [r[0] for r in rows]
    nav = [float(r[1]) for r in rows]
    spy = [float(r[2]) for r in rows]

    bot_ret = nav[-1] / nav[0] - 1
    spy_ret = spy[-1] / spy[0] - 1

    print(f"period            {dates[0]} -> {dates[-1]}  ({len(rows)} days)")
    print(f"bot return        {bot_ret:+.2%}   (NAV ${nav[0]:.2f} -> ${nav[-1]:.2f})")
    print(f"SPY buy-and-hold  {spy_ret:+.2%}")
    print(f"alpha             {bot_ret - spy_ret:+.2%}")
    print(f"bot max drawdown  {max_drawdown(nav):+.2%}")
    print(f"SPY max drawdown  {max_drawdown(spy):+.2%}")
    print("verdict:          " + ("bot ahead" if bot_ret > spy_ret else "buy-and-hold ahead"))


if __name__ == "__main__":
    main()
