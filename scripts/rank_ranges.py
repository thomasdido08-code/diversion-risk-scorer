#!/usr/bin/env python3
"""Rank ranges under weight shocks (the 5th to 95th percentile rank).

    python scripts/rank_ranges.py            # print, and compare with data/raw/rank_ranges.csv
    python scripts/rank_ranges.py --write    # rewrite data/raw/rank_ranges.csv and sensitivity.json

The method, unchanged from the October 2026 edition: 2,000 draws with seed 7;
in each draw every base weight moves by a uniform amount between -10 and +10
points (floored at 0) and the weights are renormalised to sum to 1. Each state
is ranked by score in each draw (ties share the best rank). The range is the
5th and 95th percentile of its 2,000 ranks (linear interpolation, then
truncated to a whole rank). The script also reports how many of the base top
10 stay in the top 10, averaged over the draws.

Ported from the October code (which used pandas) to the standard library;
Python's random module gives the same draws for the same seed. It reads the
components to three decimals, as stored in data/raw/components.csv, so a
range can differ by one rank from one computed on unrounded inputs.
"""
import csv
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
COMP = {"governance": "gov_risk", "conflict": "conflict_risk", "embargo": "embargo_risk",
        "neighbourhood": "neighbourhood_risk", "att": "att_risk"}
RUNS, SEED, SHOCK = 2000, 7, 0.10


def min_rank(values):
    order = sorted(values, reverse=True)
    first = {}
    for i, v in enumerate(order, 1):
        first.setdefault(v, i)
    return [first[v] for v in values]


def quantile(sorted_vals, q):
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def compute(rows, weights):
    comps = [[float(r[c]) for c in COMP.values()] for r in rows]
    base = [round(100 * sum(weights[k] * x for k, x in zip(COMP, c)), 1) for c in comps]
    base_rank = min_rank(base)
    top10 = {i for i, rk in enumerate(base_rank) if rk <= 10}
    rng = random.Random(SEED)
    ranks = [[] for _ in rows]
    overlap = 0
    for _ in range(RUNS):
        w = {k: max(0.0, v + rng.uniform(-SHOCK, SHOCK)) for k, v in weights.items()}
        s = sum(w.values())
        w = [w[k] / s for k in COMP]
        sc = [100 * sum(a * x for a, x in zip(w, c)) for c in comps]
        rk = min_rank(sc)
        for i, x in enumerate(rk):
            ranks[i].append(x)
        # the October code took the ten lowest ranks, which with ties is the first ten in score order
        best = sorted(range(len(rows)), key=lambda i: (rk[i], i))[:10]
        overlap += len(top10 & set(best))
    out = []
    for r, rr in zip(rows, ranks):
        rr.sort()
        out.append({"iso3": r["iso3"], "rank_p05": int(quantile(rr, 0.05)), "rank_p95": int(quantile(rr, 0.95))})
    return out, overlap / RUNS


def main():
    weights = json.load(open(os.path.join(RAW, "weights.json"), encoding="utf-8"))["weights"]
    rows = list(csv.DictReader(open(os.path.join(RAW, "components.csv"), encoding="utf-8")))
    out, overlap = compute(rows, weights)
    path = os.path.join(RAW, "rank_ranges.csv")
    old = {r["iso3"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}
    diff = [(o["iso3"], old[o["iso3"]]["rank_p05"], old[o["iso3"]]["rank_p95"], o["rank_p05"], o["rank_p95"])
            for o in out if o["iso3"] in old and
            (int(old[o["iso3"]]["rank_p05"]), int(old[o["iso3"]]["rank_p95"])) != (o["rank_p05"], o["rank_p95"])]
    print(f"{len(out)} states; top-10 overlap {overlap:.2f}; {len(diff)} ranges differ from rank_ranges.csv")
    for d in diff:
        print("  {}: {}-{} -> {}-{}".format(*d))
    if "--write" in sys.argv:
        order = [r for r in old] + [o["iso3"] for o in out if o["iso3"] not in old]
        by = {o["iso3"]: o for o in out}
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["iso3", "rank_p05", "rank_p95"], lineterminator="\n")
            w.writeheader()
            w.writerows(by[i] for i in order if i in by)
        json.dump({"top10_overlap_avg": round(overlap, 2)},
                  open(os.path.join(RAW, "sensitivity.json"), "w", encoding="utf-8"), indent=2)
        print("written")


if __name__ == "__main__":
    main()
