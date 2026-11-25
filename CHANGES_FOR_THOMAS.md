# Changes for Thomas: Diversion Risk Scorer

What changed on branch `iaw-prep-2026-12` (25 November 2026), why, and how to defend it. **No score or rank changed.** The headline (Sudan first, UAE 134th, leakage 95th vs re-transfer 76th percentile) is exactly as published.

## Roadmap #1: the input pipeline (done)

**What.** `scripts/pipeline/fetch_worldbank.py` pulls the five WGI indicators, SIPRI arms imports and UCDP battle deaths through the World Bank API. `fetch_att.py` reads ATT status from the UN Treaty Collection, the treaty's depositary. `diff_inputs.py` compares both with your hand-collected file and recomputes the components.

**Result.** 1,736 values, 0 mismatches. Components recomputed from the API equal `components.csv` exactly. ATT status on 30 October matches for every scored state. No rank changes. So there was nothing to fix, and I changed no data.

- *Sceptic: "Your inputs were typed by hand."* → They were collected by hand in October; a script now pulls them from the World Bank API and the UN depositary, and they match to the last digit. The script and the diff are in the repo.
- *Sceptic: "Embargoes?"* → Still hand-coded: no single official machine-readable list covers UN, EU and OSCE measures with their scope. The sources to check them against are listed in `scripts/pipeline/README.md`.
- *Sceptic: "UCDP via the World Bank lags."* → Yes, battle deaths run to 2024. UCDP's own API now needs a token. The lag is stated.

**A point to decide.** The UN Treaty Collection shows the United States as a signatory, which is what the index uses (0.5). In 2019 the US told the depositary it does not intend to become a party. You could defend scoring it 1 ("outside the treaty"). I left it unchanged; it is your call, and it would move the US up.

## Roadmap #2: blind validation (under way)

**Done.**
- `validation/PROTOCOL.md` was committed **before** any case was coded: sources, what counts as a case, fields, leakage vs re-transfer rules, and the evaluation plan.
- `validation/reports.csv` lists every source in scope: 139 UN Panel and Group of Experts reports, 2015–2025, taken from each sanctions committee's own page, and 63 CAR items.
- Tools to download reports and list candidate passages with page numbers.
- A first Libya tranche: 10 cases and 12 documented exclusions, each with page and quote.

**Not done, deliberately.** No evaluation was run. The protocol says to evaluate only after complete coding and your 20% second coding. Running it on a partial, Libya-heavy set would produce exactly the kind of number a reviewer should distrust.

**About blindness: be upfront.** I had seen the headline (top 10, UAE 134th) and your October coding before writing the protocol. The protocol says so. The mitigations: fixed rules, coding from report text alone, a page reference for every row, the October coding not reused, and your second coding.

**Your October work.** `COVERAGE.md` (31 Oct) said seven regimes were coded with AUCs of 0.94/0.85, but the surviving `cases.csv` had only 12 Libya rows. Don't cite those AUCs: they can't be traced to rows.

**Timeline to mid-January.** "Clearly under way" is realistic: Libya, Yemen, Sudan, South Sudan and the DPRK arms sections, which hold most re-transfer findings. A full sweep of 139 reports plus CAR is several weeks of part-time reading. Sudan reports may need OCR.

- *Sceptic: "UN Panels only exist in conflict theatres, so of course your index catches leakage."* → Exactly why the protocol reports leakage and re-transfer separately. Re-transfer is the fair test, because the supplier states can come from anywhere.
- *Sceptic: "Why exclude 'failure to inspect' findings?"* → They're compliance failures by transit states, not diversion from the state's own control. Counting them would mix a different question into the test. Every exclusion is listed with its reason in `excluded.csv`.

## Roadmap #3: re-transfer component (tested, not adopted)

**Proposal.** A sixth component: UN Panel reports that find a state's government transferred arms in breach of an embargo. Scaled 0 / 0.5 (one report) / 1 (two or more). Weight 10%, taken from the others in proportion. It uses reports to 2020 only, so 2021–2025 cases stay free to test it.

**Before and after** (partial Libya coding, so this tests the mechanics, not a finding):

| State | Now | 5% | 10% | 15% |
|---|---|---|---|---|
| UAE | 134 | 107 | 83 | 70 |
| Qatar | 100 | 89 | 79 | 74 |
| Jordan | 54 | 42 | 35 | 30 |
| Türkiye | 41 | 36 | 29 | 21 |

**It does not fix the blind spot**, and that is documented as a limit. A component at weight *w* adds at most 100*w* points. The UAE's other components are low (score 29.8), so at 10% it peaks at 36.8, below "Elevated". Reaching the top 50 would take 20% or more, which would be tuning to one case. I did not tune.

**Recommendation:** show re-transfer as a separate flag beside the score ("documented re-transfer in N UN Panel reports"). The index answers "can this state keep control?"; the flag answers "does it choose to pass arms on?".

- *Sceptic: "Then your index misses the UAE."* → Yes, and we say so. Governance data measures capacity, not intent. A separate, evidence-based flag shows intent without pretending one number can carry both.
- *Sceptic: "Why 0 / 0.5 / 1?"* → Counting reports rather than findings stops long-running regimes with many reports from dominating, and the cap stops one state's record from swamping the rest. The results are shown at three weights, so the choice is visible.

## Roadmap #5: overlap (done, short note)

Governance and conflict correlate at 0.66 (Spearman 0.77), partly by construction, since half of conflict is WGI Political Stability. Dropping conflict altogether leaves rank correlation 0.989 and 8 of the top 10. Kept as is; note in METHODOLOGY.md.

- *Sceptic: "You count instability twice."* → Partly, and it barely matters: removing the conflict component entirely changes the ranking very little.

## Ready to go public?

**Not yet.** Before publishing I would: (1) decide the US ATT question; (2) decide the Iran question below; (3) get the validation to at least the re-transfer-heavy regimes, so that "blind validation under way" is backed by real numbers.

**Publication check (done 25 Nov):** no secrets or local paths; licence files present for the code, d3, topojson and the IBM Plex fonts; every script, style and data path in the page is relative, so it works under GitHub Pages; the page renders from a local server with no console errors.

## Update, 25 November (later): Yemen coded, and a protocol question

Yemen's 12 reports are partly read: 2 leakage cases from Yemeni state stocks, 7 exclusions. Four of the reports are public only under their reissue symbols, which `reports.csv` now uses.

**Decision for you: Iran.** The Panel finds Iran in non-compliance for *failing to prevent* the supply of Iranian-origin missiles and drone material to the Houthis (S/2018/594), and later that "individuals or entities within" Iran sent weapons (S/2021/79). It does not find that the Iranian government transferred them. The protocol, as fixed before coding, excludes failure-to-prevent findings and non-state senders, so Iran has no Yemen case.

- Keep the rule: consistent, and it is the stricter reading of "the state chose to pass arms on". But a reviewer will ask why Iran is missing.
- Change the rule (count failure-to-prevent findings for materiel of the state's own origin as `unclear`): log it in PROTOCOL.md's change section with the date and reason, and report the evaluation under both rules, as the protocol requires.

Either is defensible. Changing it quietly is not.

- *Sceptic: "Your validation leaves out Iran's arming of the Houthis?"* → The Panel itself stops short of finding that the Iranian government transferred the weapons; it finds Iran failed to prevent their supply. Our protocol, fixed before coding, counts only what the Panel finds. We report the result both with and without such findings. If you want it public for the 10 December pitch anyway, it is honest as it stands: the README says what is done and what is not.
