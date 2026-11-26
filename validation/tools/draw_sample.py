#!/usr/bin/env python3
"""Draw the second-coding sample (PROTOCOL.md, section 6). Run once, after coding ends.

    python validation/tools/draw_sample.py

Writes:
  validation/second_coding/sample_blind.csv
      A random 20% of rows in cases.csv (rounded up), drawn with the fixed
      seed below from the case_ids in sorted order. The first coder's
      mechanism, confidence, evidence and notes are left out, and rows carry a
      neutral reference instead of the case_id (which names the mechanism);
      the second coder fills in the empty columns from the report alone.
  validation/second_coding/check_retransfer.csv
      Every `re-transfer` row (section 6 says the second coder checks all of
      them) plus every row marked as a close call, with the first coding shown,
      and empty columns for agree / disagree and a comment.

The seed is fixed so that anyone can redraw the same sample. Code the blind sample first and the check list second: the check list shows
the first coding. Refuses to
overwrite an existing sample, because redrawing after seeing it would defeat
the point. Standard library only.
"""
import csv
import hashlib
import math
import os
import random
import sys

SEED = 20261126
SHARE = 0.20
HERE = os.path.dirname(os.path.abspath(__file__))
VAL = os.path.dirname(HERE)
OUT = os.path.join(VAL, "second_coding")


def ref(case_id):
    """Neutral row reference: case_id ends in the mechanism, so it cannot go in the blind file."""
    return hashlib.sha1(case_id.encode("utf-8")).hexdigest()[:8]


def main():
    rows = list(csv.DictReader(open(os.path.join(VAL, "cases.csv"), encoding="utf-8")))
    blind_path = os.path.join(OUT, "sample_blind.csv")
    check_path = os.path.join(OUT, "check_retransfer.csv")
    if os.path.exists(blind_path) and "--force" not in sys.argv:
        sys.exit("A sample already exists; it is drawn once. Use --force only to rebuild it identically from the same cases.csv.")
    os.makedirs(OUT, exist_ok=True)

    ids = sorted(r["case_id"] for r in rows)
    k = math.ceil(SHARE * len(ids))
    chosen = set(random.Random(SEED).sample(ids, k))
    by_id = {r["case_id"]: r for r in rows}

    blind_cols = ["sample_no", "row_ref", "source_type", "report", "report_date", "theatre", "state_iso3", "state_name",
                  "page", "paragraph", "quote", "url"]
    fill_cols = ["is_case (yes/no)", "mechanism (leakage/re-transfer/unclear)", "confidence (established/probable)",
                 "evidence (physical/documents/both/testimony)", "second_coder_notes"]
    with open(blind_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(blind_cols + fill_cols)
        for n, cid in enumerate(sorted(chosen), 1):
            r = by_id[cid]
            w.writerow([n, ref(cid)] + [r[c] for c in blind_cols[2:]] + [""] * len(fill_cols))

    check = [r for r in rows if r["mechanism"] == "re-transfer" or "close call" in r["notes"].lower()]
    check_cols = ["case_id", "report", "state_iso3", "state_name", "mechanism", "confidence", "page", "paragraph",
                  "quote", "url", "notes", "why_listed"]
    with open(check_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(check_cols + ["agree (yes/no)", "your_mechanism_if_no", "comment"])
        for r in sorted(check, key=lambda r: (r["state_iso3"], r["report"])):
            why = ";".join(x for x, ok in (("re-transfer", r["mechanism"] == "re-transfer"),
                                            ("close call", "close call" in r["notes"].lower())) if ok)
            w.writerow([r[c] for c in check_cols[:-1]] + [why, "", "", ""])

    in_sample = sum(1 for r in check if r["case_id"] in chosen)
    print(f"{len(rows)} cases; blind sample {k} rows (seed {SEED}) -> {blind_path}")
    print(f"check list {len(check)} rows ({in_sample} also in the blind sample) -> {check_path}")


if __name__ == "__main__":
    main()
