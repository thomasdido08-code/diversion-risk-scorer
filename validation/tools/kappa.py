#!/usr/bin/env python3
"""Agreement between first and second coding (PROTOCOL.md, section 6).

    python validation/tools/kappa.py

Reads validation/second_coding/sample_blind.csv once the second coder has
filled it in, compares it with cases.csv, and prints:
  - agreement that the row is a case at all;
  - Cohen's kappa on mechanism (leakage / re-transfer / unclear), over rows
    both coders treat as cases;
  - raw agreement on confidence;
  - every disagreement, for discussion.
Run it before the evaluation; the protocol reports kappa first. Standard
library only.
"""
import collections
import csv
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAL = os.path.dirname(HERE)
MECH = "mechanism (leakage/re-transfer/unclear)"
CONF = "confidence (established/probable)"
CASE = "is_case (yes/no)"


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca = collections.Counter(a for a, _ in pairs)
    cb = collections.Counter(b for _, b in pairs)
    pe = sum(ca[x] * cb[x] for x in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    first = {hashlib.sha1(r["case_id"].encode("utf-8")).hexdigest()[:8]: r
             for r in csv.DictReader(open(os.path.join(VAL, "cases.csv"), encoding="utf-8"))}
    path = os.path.join(VAL, "second_coding", "sample_blind.csv")
    second = list(csv.DictReader(open(path, encoding="utf-8")))
    filled = [r for r in second if r[CASE].strip()]
    if len(filled) < len(second):
        sys.exit(f"{len(second) - len(filled)} of {len(second)} sample rows are not coded yet.")

    not_case = [r for r in filled if r[CASE].strip().lower() != "yes"]
    pairs, conf, diffs = [], [], []
    for r in filled:
        a = first[r["row_ref"]]
        if r[CASE].strip().lower() != "yes":
            diffs.append((a["case_id"], "first coder: case; second coder: not a case", r["second_coder_notes"]))
            continue
        m2 = r[MECH].strip().lower()
        pairs.append((a["mechanism"], m2))
        conf.append(a["confidence"] == r[CONF].strip().lower())
        if a["mechanism"] != m2:
            diffs.append((a["case_id"], f"mechanism {a['mechanism']} vs {m2}", r["second_coder_notes"]))
    print(f"Sample: {len(filled)} rows. Second coder agrees {len(filled) - len(not_case)} are cases.")
    print(f"Mechanism: raw agreement {sum(a == b for a, b in pairs)}/{len(pairs)}, Cohen's kappa {kappa(pairs):.2f}")
    print(f"Confidence: raw agreement {sum(conf)}/{len(conf)}")
    for d in diffs:
        print("  -", " | ".join(d))


if __name__ == "__main__":
    main()
