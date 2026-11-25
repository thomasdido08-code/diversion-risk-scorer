#!/usr/bin/env python3
"""Pull Arms Trade Treaty status from the UN Treaty Collection (the depositary).

    python scripts/pipeline/fetch_att.py [--as-of 2026-10-30]

Source: https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVI-8&chapter=26&clang=_en
Writes data/raw/api/att_untc_<date>.csv: participant, iso3, signature date,
deposit date (ratification, acceptance, approval or accession), the treaty's
entry into force for that state (deposit + 90 days, Article 22(2), or
24 December 2014 for deposits before the treaty entered into force), and the
status used by the index on --as-of:
  party      the treaty is in force for the state
  signatory  signed, no instrument deposited, or deposited but not yet in force
  none       not listed
Footnotes on the UNTC page (for example the United States' 2019 notice that
it does not intend to become a party) are not read; see METHODOLOGY.md.
Standard library only.
"""
import argparse
import csv
import datetime as dt
import html
import os
import re
import unicodedata
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL = "https://treaties.un.org/Pages/ViewDetails.aspx?src=TREATY&mtdsg_no=XXVI-8&chapter=26&clang=_en"
EIF = dt.date(2014, 12, 24)
MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
# UNTC spellings that differ from the World Bank names used for matching.
UNTC_ISO3 = {
    "bahamas the": "BHS", "bahamas": "BHS", "republic of north macedonia": "MKD", "nauru": "NRU", "gambia": "GMB", "cote d ivoire": "CIV", "turkiye": "TUR", "republic of korea": "KOR",
    "republic of moldova": "MDA", "north macedonia": "MKD", "state of palestine": "PSE", "congo": "COG",
    "democratic republic of the congo": "COD", "united republic of tanzania": "TZA", "cabo verde": "CPV",
    "united kingdom of great britain and northern ireland": "GBR", "united states of america": "USA",
    "guinea bissau": "GNB", "holy see": "VAT", "niue": None, "czech republic": "CZE", "czechia": "CZE",
    "iran islamic republic of": "IRN", "venezuela bolivarian republic of": "VEN", "viet nam": "VNM",
    "lao people s democratic republic": "LAO", "syrian arab republic": "SYR", "bolivia plurinational state of": "BOL",
    "micronesia federated states of": "FSM", "saint kitts and nevis": "KNA", "saint lucia": "LCA",
    "saint vincent and the grenadines": "VCT", "sao tome and principe": "STP", "eswatini": "SWZ",
    "kyrgyzstan": "KGZ", "slovakia": "SVK", "egypt": "EGY", "yemen": "YEM", "russian federation": "RUS",
    "democratic people s republic of korea": "PRK", "brunei darussalam": "BRN", "netherlands kingdom of the": "NLD",
    "netherlands": "NLD",
}


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[,.'()\-]", " ", s)
    return " ".join(s.split())


def cell(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s)).replace("\xa0", " ")
    return " ".join(s.split())


def date(s):
    m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", s)
    return dt.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1))) if m else None


def iso_lookup():
    """World Bank names from the latest API pull, plus UNTC spellings."""
    api = os.path.join(ROOT, "data", "raw", "api")
    files = sorted(f for f in os.listdir(api) if f.startswith("worldbank_wide_"))
    names = {}
    if files:
        with open(os.path.join(api, files[-1]), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                names[norm(r["name"])] = r["iso3"]
    names.update(UNTC_ISO3)
    return names


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--as-of", default=dt.date.today().isoformat())
    a = p.parse_args()
    as_of = dt.date.fromisoformat(a.as_of)
    req = urllib.request.Request(URL, headers={"User-Agent": "diversion-risk-scorer research script"})
    page = urllib.request.urlopen(req, timeout=120).read().decode("utf-8", errors="replace")
    table = page[page.find("tblgrid"):]
    table = table[:table.find("</table>")]
    names = iso_lookup()
    rows, unmatched = [], []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)[1:]:
        tds = [cell(td) for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(tds) < 4:
            continue
        name = re.sub(r"\s*\d+$", "", tds[0])  # drop footnote numbers
        signed, deposit = date(tds[1]), date(tds[3])
        if deposit:
            in_force = max(EIF, deposit + dt.timedelta(days=90))
        else:
            in_force = None
        if in_force and in_force <= as_of:
            status = "party"
        elif signed or deposit:
            status = "signatory"
        else:
            status = "none"
        key = norm(name)
        iso = names.get(key, "")
        if key not in names:
            unmatched.append(name)
        rows.append({"participant": name, "iso3": iso or "", "signed": signed or "", "deposit": deposit or "",
                     "deposit_type": tds[3].split()[-1] if deposit and tds[3].split()[-1] in ("a", "A", "AA") else ("ratification" if deposit else ""),
                     "in_force": in_force or "", "status": status})
    out = os.path.join(ROOT, "data", "raw", "api", f"att_untc_{dt.date.today().isoformat()}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    n = {s: sum(1 for r in rows if r["status"] == s) for s in ("party", "signatory")}
    print(f"{len(rows)} participants as of {as_of}: {n['party']} parties, {n['signatory']} signatories -> {out}")
    if unmatched:
        print("No ISO3 code for:", "; ".join(unmatched))


if __name__ == "__main__":
    main()
