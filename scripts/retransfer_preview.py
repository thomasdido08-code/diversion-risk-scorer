#!/usr/bin/env python3
"""Preview a sixth component: UN Panel findings of deliberate re-transfer.

    python scripts/retransfer_preview.py [--cutoff 2020-12-31] [--include-probable]

Does NOT change the published scores. Reads data/raw/components.csv and
weights.json, and validation/cases.csv for the findings, and writes
data/derived/retransfer_preview.csv: every state's rank now, and with the new
component at 5%, 10% and 15%.

Component (proposal, METHODOLOGY.md "Re-transfer component"):
  input    UN Panel reports published on or before --cutoff that find the
           state's government transferred or re-transferred materiel in breach
           of an embargo (cases.csv: source_type UN, mechanism re-transfer,
           confidence established unless --include-probable)
  scaling  distinct reports with such a finding: 0 -> 0, 1 -> 0.5, 2+ -> 1
  weight   10%, taken from the other five in proportion, so their ratios
           are unchanged
Only reports published after the cutoff, and CAR reports, can then be used to
test it, so the component is never graded on its own inputs.
Standard library only.
"""
import argparse
import collections
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = {"governance": "gov_risk", "conflict": "conflict_risk", "embargo": "embargo_risk",
        "neighbourhood": "neighbourhood_risk", "att": "att_risk"}


def ranks(score):
    vals = sorted(score.values(), reverse=True)
    return {k: 1 + sum(1 for v in vals if v > s) for k, s in score.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cutoff", default="2020-12-31")
    p.add_argument("--include-probable", action="store_true")
    a = p.parse_args()

    comp = {r["iso3"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data", "raw", "components.csv"), encoding="utf-8"))}
    w = json.load(open(os.path.join(ROOT, "data", "raw", "weights.json"), encoding="utf-8"))["weights"]
    tot = sum(w.values())
    w = {k: v / tot for k, v in w.items()}

    reports = collections.defaultdict(set)
    for r in csv.DictReader(open(os.path.join(ROOT, "validation", "cases.csv"), encoding="utf-8")):
        if r["source_type"] == "UN" and r["mechanism"] == "re-transfer" and r["report_date"] <= a.cutoff \
                and (r["confidence"] == "established" or a.include_probable):
            reports[r["state_iso3"]].add(r["report"])
    retr = {iso: (0.0 if not reports.get(iso) else 0.5 if len(reports[iso]) == 1 else 1.0) for iso in comp}

    def score(share):
        return {iso: round(100 * ((1 - share) * sum(w[k] * float(c[COMP[k]]) for k in w) + share * retr[iso]), 1)
                for iso, c in comp.items()}

    base = score(0.0)
    out = {iso: {"iso3": iso, "name": comp[iso]["name"], "retransfer_reports": len(reports.get(iso, ())),
                 "retransfer_risk": retr[iso], "score_now": base[iso], "rank_now": rk}
           for iso, rk in ranks(base).items()}
    for share in (0.05, 0.10, 0.15):
        s = score(share)
        for iso, rk in ranks(s).items():
            out[iso][f"score_{int(share * 100)}"] = s[iso]
            out[iso][f"rank_{int(share * 100)}"] = rk
    rows = sorted(out.values(), key=lambda r: r["rank_10"])
    path = os.path.join(ROOT, "data", "derived", "retransfer_preview.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)

    print(f"Findings in UN reports to {a.cutoff} ({'established and probable' if a.include_probable else 'established only'}):")
    for iso in sorted(reports, key=lambda i: -len(reports[i])):
        if iso in out:
            r = out[iso]
            print(f"  {r['name']:<28} reports {len(reports[iso])}  rank now {r['rank_now']:>3}  "
                  f"at 5% {r['rank_5']:>3}  at 10% {r['rank_10']:>3}  at 15% {r['rank_15']:>3}")
    top_now = {r["iso3"] for r in rows if r["rank_now"] <= 10}
    top_10 = {r["iso3"] for r in rows if r["rank_10"] <= 10}
    print(f"Top 10 at 10%: {len(top_now & top_10)} of 10 unchanged. Full table -> {path}")


if __name__ == "__main__":
    main()
