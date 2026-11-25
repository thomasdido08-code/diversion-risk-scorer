#!/usr/bin/env python3
"""Pull the World Bank inputs of the Diversion Risk Scorer through the API.

    python scripts/pipeline/fetch_worldbank.py

Writes, with today's date:
  data/raw/api/worldbank_long_<date>.csv  every observation as returned
                                          (iso3, indicator, year, value)
  data/raw/api/worldbank_wide_<date>.csv  one row per economy, in the
                                          layout of the hand-collected file

Indicators (World Bank API v2):
  WGI, source 3:  GOV_WGI_RL.EST rule of law, GOV_WGI_CC.EST control of
                  corruption, GOV_WGI_GE.EST government effectiveness,
                  GOV_WGI_PV.EST political stability, GOV_WGI_VA.EST voice
                  and accountability. Latest year available per economy.
  WDI, source 2:  MS.MIL.MPRT.KD arms imports (SIPRI trend-indicator values),
                  summed 2015 onwards, in millions.
                  VC.BTL.DETH battle-related deaths (UCDP), summed 2020
                  onwards and 2015 onwards.
Economy metadata (name, region, income group) from /v2/country.

Same derivation as the October 2026 ingest script, so the wide file can be
compared field by field with the hand-collected one. Standard library only.
"""
import csv
import datetime as dt
import json
import os
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data", "raw", "api")
API = "https://api.worldbank.org/v2"
WGI = {"RL": "GOV_WGI_RL.EST", "CC": "GOV_WGI_CC.EST", "PV": "GOV_WGI_PV.EST",
       "GE": "GOV_WGI_GE.EST", "VA": "GOV_WGI_VA.EST"}
WDI = {"ARMSIMP": "MS.MIL.MPRT.KD", "BATTLE": "VC.BTL.DETH"}


def get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 - retry any network error
            print(f"  retry {i + 1}: {e}")
            time.sleep(2 ** (i + 1))
    raise SystemExit(f"Giving up on {url}")


def pages(path):
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        d = get(f"{API}/{path}{sep}format=json&per_page=20000&page={page}")
        if len(d) < 2 or d[1] is None:
            break
        out.extend(d[1])
        if page >= int(d[0]["pages"]):
            break
        page += 1
        time.sleep(0.5)
    return out


def main():
    today = dt.date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)

    meta = {}
    for c in pages("country"):
        if c["region"]["value"] == "Aggregates":
            continue
        meta[c["id"]] = {"name": c["name"].strip(), "region": c["region"]["value"].strip(), "income": c["incomeLevel"]["value"].strip()}

    long_rows = []
    for short, code in WGI.items():
        for r in pages(f"country/all/indicator/{code}?source=3&date=2015:2025"):
            if r["value"] is not None and r["countryiso3code"] in meta:
                long_rows.append((r["countryiso3code"], short, int(r["date"]), r["value"]))
        print(f"{short}: done")
        time.sleep(3)
    for short, code in WDI.items():
        for r in pages(f"country/all/indicator/{code}?source=2&date=2015:2025"):
            if r["value"] is not None and r["countryiso3code"] in meta:
                long_rows.append((r["countryiso3code"], short, int(r["date"]), r["value"]))
        print(f"{short}: done")
        time.sleep(3)

    with open(os.path.join(OUT, f"worldbank_long_{today}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["iso3", "indicator", "year", "value"])
        w.writerows(sorted(long_rows))

    by = {}
    for iso, ind, year, val in long_rows:
        by.setdefault(iso, {}).setdefault(ind, []).append((year, val))
    wide = []
    for iso in sorted(meta):
        d = by.get(iso, {})
        row = {"iso3": iso, **meta[iso]}
        for ind in WGI:
            obs = sorted(d.get(ind, []))
            row[ind] = round(obs[-1][1], 3) if obs else ""
            row[ind + "_year"] = obs[-1][0] if obs else ""
        row["arms_imp_tiv_m_2015on"] = round(sum(v for y, v in d.get("ARMSIMP", []) if y >= 2015) / 1e6)
        row["battle_deaths_2020on"] = round(sum(v for y, v in d.get("BATTLE", []) if y >= 2020))
        row["battle_deaths_2015on"] = round(sum(v for y, v in d.get("BATTLE", []) if y >= 2015))
        row["battle_deaths_years"] = ";".join(str(y) for y, _ in sorted(d.get("BATTLE", [])) if y >= 2020)
        wide.append(row)
    with open(os.path.join(OUT, f"worldbank_wide_{today}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(wide[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(wide)
    print(f"{len(wide)} economies, {len(long_rows):,} observations -> {OUT}")


if __name__ == "__main__":
    main()
