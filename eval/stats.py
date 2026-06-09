#!/usr/bin/env python3
"""Trade statistics from SCORECARD.md — real and sim tallied separately.

Parses the markdown table: | Date | Mode | Tkr | Regime | Strat | Entry | Inval | Target | Result | +/- |
Rows with a numeric +/- are counted as resolved.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

SCORECARD = Path(__file__).parent.parent / "SCORECARD.md"


def parse_rows():
    rows = []
    for line in SCORECARD.read_text().splitlines():
        if not line.startswith("|") or set(line) <= {"|", "-", " "}:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 10 or cells[0] in ("Date", "—", ""):
            continue
        m = re.search(r"[-+]?\d+(?:\.\d+)?", cells[9].replace("$", ""))
        if not m:
            continue
        pnl = float(m.group())
        kind = "sim" if "SIM" in cells[1].upper() else "real"
        rows.append({"kind": kind, "strat": cells[4] or "?", "pnl": pnl})
    return rows


def report(name, trades):
    if not trades:
        print(f"{name}: no resolved trades")
        return
    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    hit = len(wins) / len(pnls)
    avg_w = sum(wins) / len(wins) if wins else 0.0
    avg_l = sum(losses) / len(losses) if losses else 0.0
    expectancy = hit * avg_w + (1 - hit) * avg_l
    gross_w, gross_l = sum(wins), abs(sum(losses))
    pf = gross_w / gross_l if gross_l else float("inf")
    print(f"{name}: n={len(pnls)}  hit={hit:.0%}  avgW=${avg_w:.2f}  "
          f"avgL=${avg_l:.2f}  expectancy=${expectancy:.2f}/trade  PF={pf:.2f}")

    by_strat = defaultdict(list)
    for t in trades:
        by_strat[t["strat"]].append(t["pnl"])
    for s, ps in sorted(by_strat.items()):
        w = sum(1 for p in ps if p > 0)
        print(f"  {s:14s} n={len(ps):3d}  {w}W/{len(ps)-w}L  total=${sum(ps):+.2f}")


def main():
    rows = parse_rows()
    report("REAL", [r for r in rows if r["kind"] == "real"])
    report("SIM ", [r for r in rows if r["kind"] == "sim"])


if __name__ == "__main__":
    sys.exit(main())
