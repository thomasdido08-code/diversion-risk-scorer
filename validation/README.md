# Blind validation (roadmap item 2)

**Status, 25 November 2026: coding has started. No evaluation has been run, and none will be until coding and second coding are complete (PROTOCOL.md, section 7).**

| File | What it is |
|---|---|
| `PROTOCOL.md` | The coding rules, fixed before coding (commit `Fix the blind-validation coding protocol before coding`). |
| `reports.csv` | Every source in scope: 139 UN Panel and Group of Experts reports, 2015–2025, taken from each sanctions committee's own reports page on 25 November 2026, and 63 items from the Conflict Armament Research publications page (17 flagged as possible translations, 36 without a title in the listing). `status` tracks progress. |
| `cases.csv` | Coded cases. One row per state × report × mechanism, with page, quote and URL. |
| `excluded.csv` | Findings that name a state but are not cases under the protocol, with the reason. Kept so that exclusions can be checked too. |
| `tools/candidates.py` | Downloads a report and lists candidate sentences with page numbers. It points the coder to passages; it does not code. |
| `tools/ctx.py`, `tools/statescan.py` | Read the text around a phrase on a page; list pages where a state is named next to embargo-violation language. |
| `candidates/` | Candidate lists for the reports processed so far. |

## Progress

- **Libya (9 reports): partly read.** The arms-embargo findings that name a state were checked in context. 10 cases coded (Sudan 2015 and 2016; UAE 2016 and 2019; Qatar 2016, for 2011 events; Jordan 2019; Türkiye 2019, 2021 and 2024; Libya leakage 2015) and 12 findings excluded. A full read of each report is still needed: for leakage from Libyan stocks, which the reports describe in many places without calling it a finding, and for transfers reported in tables and annexes. S/2024/914, annex 28, table 28.1 lists every transfer the Panel has confirmed since 2011 with the responsible state and the report that first found it (for example UAE AT-802i aircraft in S/2017/466 and Mirage 2000-9 in S/2021/229); use it as a checklist, but code each case from the original report.
- **Yemen (12 reports): partly read.** 2 leakage cases from Yemeni state stocks (Scud missiles captured around Sana'a, S/2018/193; government-batch rifles on sale in Houthi areas, S/2024/731). 7 findings excluded, including Iran's: the Panel finds Iran failed to *prevent* the supply of Iranian-origin missiles and drone material (S/2018/594) and that "individuals or entities within" Iran sent weapons (S/2021/79), but does not establish that the Iranian government held or transferred them. **This is a protocol question for Thomas**: as written, the protocol excludes failure-to-prevent findings, so Iran has no Yemen case. Changing that rule must be logged in PROTOCOL.md and reported under both rules.
- **South Sudan (22 reports): partly read.** 5 re-transfer cases: Sudan's supply of the armed opposition (S/2016/70, S/2016/793) and of South Sudan's security bureau after the 2018 embargo (S/2020/342); Uganda's re-transfer of Israeli rifles without the exporter's consent (S/2016/70, S/2016/963). 5 findings excluded, mainly the presence of Uganda's own troops, which breaches the embargo but is not a transfer of materiel. Leakage from South Sudanese stocks to militias still needs a full read.
- Four Yemen reports are public only under their reissue symbols (S/2018/192, S/2018/193, S/2018/594, S/2020/326); the original symbols return a web page, not a PDF. `candidates.py` now refuses non-PDF downloads.
- **All other regimes and CAR: not started.**

## What it takes to finish

1. Run `python validation/tools/candidates.py --all` (about 2 GB of PDFs, cached in `validation/cache/`, not committed).
2. **Sudan Panel reports may need OCR.** The October 2026 notes recorded five as scanned images with little text: S/2019/34, S/2020/36, S/2022/48, S/2023/93, S/2024/65 (not re-checked yet; `candidates.py` flags any report with little text). Run those through `ocrmypdf` first.
3. **CAR reports** are coded by reading, not keyword: they describe tracing chains rather than "findings". Download links are in `reports.csv`.
4. Code every report under PROTOCOL.md, then mark it `read`.
5. Second coding: Thomas codes a random 20% of rows (fixed seed) and checks every `re-transfer` row; report Cohen's kappa.
6. Only then run the evaluation in PROTOCOL.md, section 7.

At the pace of the Libya tranche, a full read of the 139 UN reports is several weeks of part-time work. Mid-January is realistic for Libya, Yemen, Sudan, South Sudan and the DPRK arms sections, which hold most re-transfer findings; the leakage-heavy regimes (DRC, CAR, Somalia, Mali, Haiti) would follow.

## A note on the October 2026 coding

`COVERAGE.md` from 31 October said seven regimes had been read and coded, but the surviving `cases.csv` from that work held only 12 Libya rows, and its AUC figures cannot be traced to rows. That work is not used here (PROTOCOL.md, section 6). The two codings will be compared once Libya is fully read. One rule already differs: the protocol excludes findings about military aircraft or vessel movements where cargo is not established, such as the UAE's and Russia's aircraft landings in S/2021/229 (pp224, 228). The October coding counted the UAE row for 2021 on that basis; under this protocol, the UAE's 2021 case will rest on the Mirage 2000-9 transfer instead, if the report supports it.
