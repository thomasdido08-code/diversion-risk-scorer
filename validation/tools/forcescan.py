"""List sentences where a state's own forces are named next to diversion language.

    python forcescan.py S_2015_19 COD [max_hits]

candidates.py matches state names, but Panel reports usually name the army or
police ("FARDC", "FACA", "Somali National Army") rather than the state, which is
where most leakage findings sit. This scans for those force names instead.
It points the coder to passages; it does not code. Run from validation/.
"""
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
FORCES = {
    "COD": r"FARDC|Congolese (soldiers|officers|military)|Congolese army|Congolese armed forces|Congolese National Police|Police nationale congolaise|\bPNC\b|Republican Guard",
    "CAF": r"\bFACA\b|Central African (soldiers|officers|army)|Central African armed forces|Central African Armed Forces|Forces armées centrafricaines|national defence and security forces|Central African police|gendarmerie",
    "SOM": r"Somali (soldiers|security forces|army)|Somali National Army|\bSNA\b|Somali Police Force|Federal Government of Somalia|Federal Government's|Puntland (Security|Maritime|Dervish)|Jubaland|Galmudug|federal member state",
    "MLI": r"\bFAMa\b|Malian (soldiers|officers)|Malian armed forces|Malian Defence and Security Forces|Malian army|Forces armées maliennes|Malian Government",
    "HTI": r"Haitian (police|officers)|Haitian National Police|\bPNH\b|Police nationale d.Haïti|Haitian Armed Forces|\bFAd.H\b",
    "SSD": r"\bSSPDF\b|\bSPLA\b|South Sudan People.s Defence Forces|National Security Service",
    "SDN": r"Sudanese Armed Forces|\bSAF\b|Rapid Support Forces|\bRSF\b",
    "LBY": r"Libyan National Army|\bLNA\b|Government of National Accord|\bGNA\b|Government of National Unity",
    "YEM": r"Government of Yemen|Yemeni (armed forces|army|military|Armed Forces)|legitimate Government|Republican Guard|state stockpile|national stockpile|government stocks",
}
DIVERSION = re.compile(
    r"divert|diversion|leak|captured|seized from|looted|stolen|theft|sold|sale|resold|smuggl|deserter|defect|"
    r"traced|originat|from the stock|stockpile|armoury|depot|end up|ended up|in the (hands|possession) of|"
    r"handed over|provided to|supplied to|distributed to|transferred to|recovered from", re.I)
MATERIEL = re.compile(r"arms|weapon|ammunition|materiel|matériel|rifle|missile|rocket|grenade|mortar|cartridge|"
                      r"launcher|vehicle|munition|explosive|AK|PKM|RPG", re.I)


def main():
    pdf, iso = sys.argv[1], sys.argv[2]
    mx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    force = re.compile(FORCES[iso])
    txt = subprocess.run(["pdftotext", "-enc", "UTF-8", f"cache/{pdf}.pdf", "-"], capture_output=True).stdout
    hits = 0
    seen = set()
    for i, page in enumerate(txt.decode("utf-8", "replace").split("\f"), 1):
        p = re.sub(r"-\n\s*", "", page)
        p = re.sub(r"\s+", " ", p)
        for s in re.split(r"(?<=[.;])\s+(?=[A-Z(\d])", p):
            if len(s) > 1000 or s[:120] in seen:
                continue
            if force.search(s) and DIVERSION.search(s) and MATERIEL.search(s):
                seen.add(s[:120])
                print(f"p{i}: {s[:420]}")
                hits += 1
                if hits >= mx:
                    return


if __name__ == "__main__":
    main()
