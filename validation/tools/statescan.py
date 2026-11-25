"""List pages where a state is named next to embargo-violation language:
python statescan.py S_2017_466 "United Arab Emirates" [max_hits]"""
import re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
pdf, name = sys.argv[1], sys.argv[2]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 6
t = subprocess.run(["pdftotext", "-enc", "UTF-8", f"cache/{pdf}.pdf", "-"], capture_output=True).stdout.decode("utf-8", "replace")
hits = 0
for i, page in enumerate(t.split("\f"), 1):
    p = re.sub(r"\s+", " ", page)
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z(\d])", p):
        if name in s and re.search(r"non-compliance|in violation|violat|supplied|transferred|provided|delivered|support", s, re.I) \
                and re.search(r"materiel|arms|weapon|ammunition|aircraft|UAV|vehicle|missile|military", s, re.I):
            print(f"p{i}: {s[:380]}")
            hits += 1
            break
    if hits >= mx:
        break
