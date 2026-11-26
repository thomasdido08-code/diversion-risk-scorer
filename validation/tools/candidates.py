#!/usr/bin/env python3
"""Download validation reports and list candidate findings for manual coding.

    python validation/tools/candidates.py --regime Libya          # one UN regime
    python validation/tools/candidates.py --report S/2019/914     # one report
    python validation/tools/candidates.py --all                   # everything in reports.csv

For each report in validation/reports.csv it downloads the PDF (cached in
validation/cache/, not committed), extracts text page by page with pdftotext
(poppler), and writes validation/candidates/<report>.tsv: one row per
sentence that (a) uses finding or diversion language and (b) names a state,
with the PDF page number. Nothing is coded automatically: the coder reads
each candidate in the PDF and applies PROTOCOL.md.

Scanned reports with no text layer produce no candidates and are flagged;
they need OCR (for example `ocrmypdf`) before coding.

Needs: Python 3 and pdftotext on the PATH (poppler-utils; Git for Windows
ships it). No Python packages.
"""
import argparse
import csv
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VAL = os.path.dirname(HERE)
ROOT = os.path.dirname(VAL)
CACHE = os.path.join(VAL, "cache")
OUT = os.path.join(VAL, "candidates")

FINDING = re.compile(
    r"\b(the (panel|group|monitoring group)\b[^.]{0,60}\b(finds|found|concluded|concludes|considers|established|"
    r"identified|determined|documented|traced|confirmed))|non-compliance|in violation of|violated|diverted|diversion|"
    r"captured from|looted|leaked|leakage|re-?transfer|originat\w+ from (the )?(national )?(stock|stockpile|arsenal)|"
    r"supplied by the (government|armed forces)|national stockpile|from the stocks of|end-user certificate",
    re.I)
MATERIEL = re.compile(r"arms|weapon|ammunition|materiel|matériel|rifle|missile|rocket|UAV|UCAV|drone|grenade|mortar|"
                      r"armoured|vehicle|munition|explosive|launcher|cartridge|aircraft", re.I)


def state_names():
    """Country names from the World Bank pull, plus UN-document spellings."""
    api = os.path.join(ROOT, "data", "raw", "api")
    wide = sorted(f for f in os.listdir(api) if f.startswith("worldbank_wide_"))[-1]
    names = {}
    for r in csv.DictReader(open(os.path.join(api, wide), encoding="utf-8")):
        n = r["name"].split(",")[0].strip()
        if len(n) >= 4:
            names[n] = r["iso3"]
    names.update({
        "United Arab Emirates": "ARE", "Türkiye": "TUR", "Turkey": "TUR", "the Sudan": "SDN", "Sudan": "SDN",
        "South Sudan": "SSD", "Iran": "IRN", "Islamic Republic of Iran": "IRN", "Russian Federation": "RUS",
        "Democratic People's Republic of Korea": "PRK", "DPRK": "PRK", "Democratic Republic of the Congo": "COD",
        "Central African Republic": "CAF", "Syrian Arab Republic": "SYR", "Syria": "SYR", "Egypt": "EGY",
        "Saudi Arabia": "SAU", "Eritrea": "ERI", "Uganda": "UGA", "Rwanda": "RWA", "Chad": "TCD", "Belarus": "BLR",
        "Bulgaria": "BGR", "Serbia": "SRB", "Ukraine": "UKR", "Jordan": "JOR", "Qatar": "QAT", "Yemen": "YEM",
        "Libya": "LBY", "Burundi": "BDI", "Kenya": "KEN", "Ethiopia": "ETH", "Mali": "MLI", "Niger": "NER",
        "Burkina Faso": "BFA", "Somalia": "SOM", "Djibouti": "DJI", "Oman": "OMN", "Haiti": "HTI",
        "Dominican Republic": "DOM", "United States": "USA", "Myanmar": "MMR", "Viet Nam": "VNM",
    })
    names.pop("Congo", None)  # too ambiguous in DRC reports; matched by the long names above
    return names


def safe(symbol):
    return re.sub(r"[^A-Za-z0-9]+", "_", symbol).strip("_")


def download(row):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, safe(row["report"]) + ".pdf")
    if os.path.exists(path) and os.path.getsize(path) > 10000:
        return path
    req = urllib.request.Request(row["url"], headers={"User-Agent": "diversion-risk-scorer validation (research)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    time.sleep(2)
    if not data.startswith(b"%PDF"):
        raise ValueError("the server returned a web page, not a PDF (symbol not public?)")
    with open(path, "wb") as f:
        f.write(data)
    return path


def pages(pdf):
    txt = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", pdf, "-"], capture_output=True).stdout
    return txt.decode("utf-8", errors="replace").split("\f")


def sentences(text):
    text = re.sub(r"-\n\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.;])\s+(?=[A-Z(\d])", text)


def candidates(row, names, name_re):
    pdf = download(row)
    out, seen, chars = [], set(), 0
    for i, page in enumerate(pages(pdf), 1):
        chars += len(page.strip())
        for s in sentences(page):
            if len(s) > 1200 or not FINDING.search(s) or not MATERIEL.search(s):
                continue
            states = sorted({names[m] for m in name_re.findall(s)})
            if not states or s[:160] in seen:
                continue
            seen.add(s[:160])
            out.append([row["report"], i, ";".join(states), s.strip()])
    return out, chars


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--regime")
    g.add_argument("--report")
    g.add_argument("--all", action="store_true")
    a = p.parse_args()
    rows = list(csv.DictReader(open(os.path.join(VAL, "reports.csv"), encoding="utf-8")))
    if a.regime:
        rows = [r for r in rows if r["regime_or_series"].lower().startswith(a.regime.lower())]
    elif a.report:
        rows = [r for r in rows if r["report"] == a.report]
    names = state_names()
    name_re = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b")
    os.makedirs(OUT, exist_ok=True)
    for r in rows:
        if r["source_type"] != "UN":
            print(f"skip {r['report']}: CAR reports are coded by reading, not by keyword")
            continue
        try:
            cands, chars = candidates(r, names, name_re)
        except Exception as e:  # noqa: BLE001
            print(f"{r['report']}: download or extraction failed ({e})")
            continue
        with open(os.path.join(OUT, safe(r["report"]) + ".tsv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["report", "pdf_page", "states", "sentence"])
            w.writerows(cands)
        flag = "  <-- little text: scanned? needs OCR" if chars < 20000 else ""
        print(f"{r['report']}: {len(cands)} candidates, {chars:,} characters of text{flag}", flush=True)


if __name__ == "__main__":
    main()
