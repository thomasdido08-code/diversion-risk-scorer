"""Print text around a phrase on a given PDF page: python ctx.py S_2016_209 24 "United Arab Emirates" [chars]"""
import re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
pdf, page, phrase = sys.argv[1], int(sys.argv[2]), sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 700
t = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-enc", "UTF-8", f"cache/{pdf}.pdf", "-"], capture_output=True).stdout.decode("utf-8", "replace")
t = re.sub(r"\s+", " ", t)
for m in re.finditer(re.escape(phrase), t):
    print(f"[{pdf} p{page}] ...{t[max(0, m.start() - n):m.end() + n]}...\n")
    break
else:
    print(f"[{pdf} p{page}] phrase not found")
