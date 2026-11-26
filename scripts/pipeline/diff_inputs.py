#!/usr/bin/env python3
"""Compare the API pull with the hand-collected inputs. Changes nothing.

    python scripts/pipeline/fetch_worldbank.py
    python scripts/pipeline/fetch_att.py --as-of 2026-10-30
    python scripts/pipeline/diff_inputs.py

Reads the latest data/raw/api/worldbank_wide_*.csv and att_untc_*.csv and
compares them with
  data/raw/archive/worldbank_handcopied_2026-10-30.psv   raw World Bank values
  data/raw/archive/att_parties_2026-02.txt, att_signatories_2026-02.txt
  data/raw/components.csv                                 the five components
Components are recomputed from the API values with the October 2026 formulas
(METHODOLOGY.md). Embargo levels are hand-coded and taken as they are.

Writes data/raw/api/diff_<date>.csv (one row per mismatch) and prints a
summary, including how ranks would move if the API values were used.
Standard library only.
"""
import csv
import datetime as dt
import json
import math
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_att import UNTC_ISO3, norm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw")
API = os.path.join(RAW, "api")
WGI = ["RL", "CC", "PV", "GE", "VA"]
COUNTS = ["arms_imp_tiv_m_2015on", "battle_deaths_2020on", "battle_deaths_2015on"]
COMP = ["gov_risk", "conflict_risk", "embargo_risk", "neighbourhood_risk", "att_risk"]


def latest(prefix):
    files = sorted(f for f in os.listdir(API) if f.startswith(prefix))
    if not files:
        raise SystemExit(f"No {prefix}* file in data/raw/api/: run the fetch scripts first")
    return os.path.join(API, files[-1])


def num(x):
    return None if x in ("", None) else float(x)


def components(rows, borders, att, embargo):
    """The October 2026 formulas, applied to {iso3: raw values}."""
    deaths_max = max(r["battle_deaths_2020on"] for r in rows.values())
    own = {}
    for iso, r in rows.items():
        gov = min(1, max(0, (2.5 - (r["RL"] + r["CC"] + r["GE"]) / 3) / 5))
        inst = min(1, max(0, (2.5 - r["PV"]) / 5))
        deaths = math.log10(1 + r["battle_deaths_2020on"]) / math.log10(1 + deaths_max)
        own[iso] = {"gov_risk": gov, "conflict_risk": 0.5 * deaths + 0.5 * inst}
    for iso in own:
        nb = [own[n]["conflict_risk"] for n in borders.get(iso, []) if n in own]
        own[iso]["neighbourhood_risk"] = max(nb) if nb else 0.0
        own[iso]["att_risk"] = {"party": 0.0, "signatory": 0.5}.get(att.get(iso, "none"), 1.0)
        own[iso]["embargo_risk"] = embargo.get(iso, 0.0)
    return own


def scores(comp, weights):
    s = {iso: round(100 * sum(weights[k] * c[k] for k in COMP), 1) for iso, c in comp.items()}
    order = sorted(s.values(), reverse=True)
    rank = {iso: 1 + sum(1 for v in order if v > sc) for iso, sc in s.items()}
    return s, rank


def main():
    today = dt.date.today().isoformat()
    diffs = []

    def add(kind, iso, field, hand, api, note=""):
        diffs.append({"kind": kind, "iso3": iso, "field": field, "hand_collected": hand, "api": api, "note": note})

    # ---- raw World Bank values
    hand = {r["iso3"]: r for r in csv.DictReader(open(os.path.join(RAW, "archive", "worldbank_handcopied_2026-10-30.psv"),
                                                       encoding="utf-8"), delimiter="|")}
    api = {r["iso3"]: r for r in csv.DictReader(open(latest("worldbank_wide_"), encoding="utf-8"))}
    for iso in sorted(set(hand) - set(api)):
        add("raw", iso, "economy", "present", "missing")
    for iso in sorted(set(api) - set(hand)):
        add("raw", iso, "economy", "missing", "present")
    n_values = 0
    for iso in sorted(set(hand) & set(api)):
        h, a = hand[iso], api[iso]
        for f in ("name", "region", "income"):
            if h[f].strip() != a[f].strip():
                add("label", iso, f, h[f], a[f])
        for f in WGI:
            n_values += 1
            hv, av = num(h[f]), num(a[f])
            if (hv is None) != (av is None) or (hv is not None and abs(hv - av) > 0.0005):
                add("raw", iso, f, h[f], a[f], f"API year {a[f + '_year']}")
        for f in COUNTS:
            n_values += 1
            if int(float(h[f] or 0)) != int(float(a[f] or 0)):
                add("raw", iso, f, h[f], a[f], f"battle-death years in API: {a['battle_deaths_years']}" if "battle" in f else "")

    # ---- ATT status
    names = {norm(r["name"]): r["iso3"] for r in api.values()}
    names.update(UNTC_ISO3)
    old = {}
    for status, fn in (("party", "att_parties_2026-02.txt"), ("signatory", "att_signatories_2026-02.txt")):
        for line in open(os.path.join(RAW, "archive", fn), encoding="utf-8"):
            if line.strip():
                iso = names.get(norm(line.strip()))
                if iso:
                    old[iso] = status
                else:
                    add("att", "", "unmatched name", line.strip(), "")
    untc = {r["iso3"]: r for r in csv.DictReader(open(latest("att_untc_"), encoding="utf-8")) if r["iso3"]}
    new = {iso: r["status"] for iso, r in untc.items() if r["status"] != "none"}
    for iso in sorted(set(old) | set(new)):
        if old.get(iso, "none") != new.get(iso, "none"):
            r = untc.get(iso, {})
            note = f"signed {r.get('signed', '')}; deposit {r.get('deposit', '')}; in force {r.get('in_force', '')}"
            if new.get(iso) == "not_intending":
                note += "; notified the depositary it does not intend to become a party: scored as outside (rule adopted 26 Nov 2026)"
            add("att", iso, "status", old.get(iso, "none"), new.get(iso, "none"), note)

    # ---- components
    comp_file = {r["iso3"]: r for r in csv.DictReader(open(os.path.join(RAW, "components.csv"), encoding="utf-8"))}
    borders = json.load(open(os.path.join(RAW, "borders.json"), encoding="utf-8"))
    weights = json.load(open(os.path.join(RAW, "weights.json"), encoding="utf-8"))
    names_ = {"governance": "gov_risk", "conflict": "conflict_risk", "embargo": "embargo_risk",
              "neighbourhood": "neighbourhood_risk", "att": "att_risk"}
    weights = {names_[k]: v for k, v in weights["weights"].items()}
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}
    embargo = {iso: float(r["embargo_risk"]) for iso, r in comp_file.items()}

    def raw_rows(src):
        out = {}
        for iso in comp_file:
            r = src.get(iso)
            if not r or any(num(r[f]) is None for f in ("RL", "CC", "GE", "PV")):
                continue
            out[iso] = {**{f: float(r[f]) for f in ("RL", "CC", "GE", "PV")},
                        "battle_deaths_2020on": float(r["battle_deaths_2020on"] or 0)}
        return out

    from_hand = components(raw_rows(hand), borders, {**old}, embargo)
    from_api = components(raw_rows(api), borders, new, embargo)
    recheck = sum(1 for iso in from_hand for k in COMP
                  if abs(from_hand[iso][k] - float(comp_file[iso][k])) > 0.0006)
    for iso in sorted(comp_file):
        if iso not in from_api:
            add("component", iso, "all", "scored", "missing from API")
            continue
        for k in COMP:
            hv, av = float(comp_file[iso][k]), from_api[iso][k]
            if abs(hv - av) > 0.0006:
                add("component", iso, k, comp_file[iso][k], f"{av:.3f}")

    # Ranks from unrounded components on both sides, so only real input differences move them.
    s_hand, r_hand = scores(from_hand, weights)
    s_api, r_api = scores({iso: from_api[iso] for iso in from_api}, weights)
    moves = sorted(((abs(r_api[i] - r_hand[i]), i) for i in r_api if r_api[i] != r_hand[i]), reverse=True)
    for _, iso in moves:
        add("rank", iso, "rank (base weights)", r_hand[iso], r_api[iso], f"score {s_hand[iso]} -> {s_api[iso]}")

    out = os.path.join(API, f"diff_{today}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["kind", "iso3", "field", "hand_collected", "api", "note"], lineterminator="\n")
        w.writeheader()
        w.writerows(diffs)

    count = lambda k: sum(1 for d in diffs if d["kind"] == k)
    print(f"Raw World Bank values compared: {n_values:,} across {len(set(hand) & set(api))} economies; "
          f"mismatches: {count('raw')}; label differences: {count('label')}")
    print(f"ATT status differences: {count('att')}")
    print(f"Formula check: recomputing components from the hand-collected file gives {recheck} differences "
          f"from components.csv (0 means the formulas are reproduced)")
    print(f"Component mismatches (API vs components.csv): {count('component')}")
    print(f"States whose rank would change at base weights: {count('rank')}")
    print(f"Every mismatch -> {out}")


if __name__ == "__main__":
    main()
