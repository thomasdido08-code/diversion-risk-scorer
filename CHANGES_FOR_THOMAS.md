# Changes for Thomas: Diversion Risk Scorer

What changed on branch `iaw-prep-2026-12` (25 November 2026), why, and how to defend it. **One score changed, on your decision of 26 November: the United States** (below). The headline (top 10, Sudan first, UAE 134th, leakage 95th vs re-transfer 76th percentile) is exactly as published.

## Roadmap #1: the input pipeline (done)

**What.** `scripts/pipeline/fetch_worldbank.py` pulls the five WGI indicators, SIPRI arms imports and UCDP battle deaths through the World Bank API. `fetch_att.py` reads ATT status from the UN Treaty Collection, the treaty's depositary. `diff_inputs.py` compares both with your hand-collected file and recomputes the components.

**Result.** 1,736 values, 0 mismatches. Components recomputed from the API equal `components.csv` exactly. ATT status on 30 October matches for every scored state. No rank changes. So there was nothing to fix, and I changed no data.

- *Sceptic: "Your inputs were typed by hand."* → They were collected by hand in October; a script now pulls them from the World Bank API and the UN depositary, and they match to the last digit. The script and the diff are in the repo.
- *Sceptic: "Embargoes?"* → Still hand-coded: no single official machine-readable list covers UN, EU and OSCE measures with their scope. The sources to check them against are listed in `scripts/pipeline/README.md`.
- *Sceptic: "UCDP via the World Bank lags."* → Yes, battle deaths run to 2024. UCDP's own API now needs a token. The lag is stated.

**Decided 26 November: the US counts as outside the ATT.** See the section below.

## Roadmap #2: blind validation (under way)

**Done.**
- `validation/PROTOCOL.md` was committed **before** any case was coded: sources, what counts as a case, fields, leakage vs re-transfer rules, and the evaluation plan.
- `validation/reports.csv` lists every source in scope: 139 UN Panel and Group of Experts reports, 2015–2025, taken from each sanctions committee's own page, and 63 CAR items.
- Tools to download reports and list candidate passages with page numbers.
- A first Libya tranche: 10 cases and 12 documented exclusions, each with page and quote.

**Not done, deliberately.** No evaluation was run. The protocol says to evaluate only after complete coding and your 20% second coding. Running it on a partial, Libya-heavy set would produce exactly the kind of number a reviewer should distrust.

**About blindness: be upfront.** I had seen the headline (top 10, UAE 134th) and your October coding before writing the protocol. The protocol says so. The mitigations: fixed rules, coding from report text alone, a page reference for every row, the October coding not reused, and your second coding.

**Your October work.** `COVERAGE.md` (31 Oct) said seven regimes were coded with AUCs of 0.94/0.85, but the surviving `cases.csv` had only 12 Libya rows. Don't cite those AUCs: they can't be traced to rows.

**Timeline.** Superseded on 26 November: every UN report has had a first pass (see the update at the end of this file).

- *Sceptic: "UN Panels only exist in conflict theatres, so of course your index catches leakage."* → Exactly why the protocol reports leakage and re-transfer separately. Re-transfer is the fair test, because the supplier states can come from anywhere.
- *Sceptic: "Why exclude 'failure to inspect' findings?"* → They're compliance failures by transit states, not diversion from the state's own control. Counting them would mix a different question into the test. Every exclusion is listed with its reason in `excluded.csv`.

## Roadmap #3: re-transfer component (tested, not adopted)

**Proposal.** A sixth component: UN Panel reports that find a state's government transferred arms in breach of an embargo. Scaled 0 / 0.5 (one report) / 1 (two or more). Weight 10%, taken from the others in proportion. It uses reports to 2020 only, so 2021–2025 cases stay free to test it.

**Before and after** (partial coding of Libya, Yemen, South Sudan, Sudan and the DPRK, so this tests the mechanics, not a finding):

| State | Now | 5% | 10% | 15% |
|---|---|---|---|---|
| UAE | 134 | 108 | 83 | 70 |
| Qatar | 101 | 89 | 79 | 74 |
| Jordan | 54 | 42 | 35 | 30 |
| Türkiye | 41 | 36 | 29 | 22 |
| Uganda | 28 | 19 | 14 | 9 |
| DPRK | 14 | 13 | 11 | 6 |

**It does not fix the blind spot**, and that is documented as a limit. A component at weight *w* adds at most 100*w* points. The UAE's other components are low (score 29.8), so at 10% it peaks at 36.8, below "Elevated". Reaching the top 50 would take 20% or more, which would be tuning to one case. I did not tune.

**Recommendation:** show re-transfer as a separate flag beside the score ("documented re-transfer in N UN Panel reports"). The index answers "can this state keep control?"; the flag answers "does it choose to pass arms on?".

- *Sceptic: "Then your index misses the UAE."* → Yes, and we say so. Governance data measures capacity, not intent. A separate, evidence-based flag shows intent without pretending one number can carry both.
- *Sceptic: "Why 0 / 0.5 / 1?"* → Counting reports rather than findings stops long-running regimes with many reports from dominating, and the cap stops one state's record from swamping the rest. The results are shown at three weights, so the choice is visible.

## Roadmap #5: overlap (done, short note)

Governance and conflict correlate at 0.66 (Spearman 0.77), partly by construction, since half of conflict is WGI Political Stability. Dropping conflict altogether leaves rank correlation 0.989 and 8 of the top 10. Kept as is; note in METHODOLOGY.md.

- *Sceptic: "You count instability twice."* → Partly, and it barely matters: removing the conflict component entirely changes the ranking very little.

## The United States and the ATT (decided 26 November)

**What.** New rule: a signatory that has notified the depositary that it does not intend to become a party counts as outside the treaty (1, not 0.5). Only the US is affected. Its notice was received by the UN Secretary-General on 18 July 2019 and is footnoted on the UN Treaty Collection page (retrieved 25 November). `fetch_att.py` now reads those footnotes and records the status `not_intending`.

| | Before | After |
|---|---|---|
| US score | 30.2 | **37.7** |
| US rank | 130th | **92nd** |
| US rank range | 118–142 | 76–126 |
| US exposure | 2,403 (15th) | 3,000 (11th) |
| States ranked 92nd–130th | – | each down one place (38 states) |
| Top 10, validation percentiles, top-10 overlap | – | unchanged |

**Rank ranges.** The October code that computed them used pandas and lived only in your local folder. It is now `scripts/rank_ranges.py`, standard library. Run on your October inputs at full precision, it reproduces all 205 published ranges exactly, so the new ranges come from the same method. On the three-decimal values in `components.csv`, 21 ranges differ by one rank; that is stated in the script and METHODOLOGY.md.

**A correction found on the way.** The re-transfer preview said the UAE reaches 28th at 25% weight. It is 29th, before and after the US change. Fixed.

- *Sceptic: "The UN still lists the US as a signatory."* → It does, with a footnote recording the 2019 notice. Signing obliges a state not to defeat the treaty's purpose until it makes clear it will not ratify (Vienna Convention, Article 18). The US has made that clear, so scoring it as a signatory would give it credit for a commitment it has withdrawn.
- *Sceptic: "Isn't this a political choice about one country?"* → It is a general rule, applied mechanically from the depositary's record. It happens to affect only the US today.

## Ready to go public?

**Not yet.** The US ATT question is settled (26 Nov). Before publishing I would still get the validation to at least the re-transfer-heavy regimes, so that "blind validation under way" is backed by real numbers.

**Publication check (done 25 Nov):** no secrets or local paths; licence files present for the code, d3, topojson and the IBM Plex fonts; every script, style and data path in the page is relative, so it works under GitHub Pages; the page renders from a local server with no console errors.

## Update, 25 November (later): Yemen coded, and a protocol question

Yemen's 12 reports are partly read: 2 leakage cases from Yemeni state stocks, 7 exclusions. Four of the reports are public only under their reissue symbols, which `reports.csv` now uses.

**Decided 25 November: keep the rule.** Iran stays excluded; the protocol is unchanged. The background: The Panel finds Iran in non-compliance for *failing to prevent* the supply of Iranian-origin missiles and drone material to the Houthis (S/2018/594), and later that "individuals or entities within" Iran sent weapons (S/2021/79). It does not find that the Iranian government transferred them. The protocol, as fixed before coding, excludes failure-to-prevent findings and non-state senders, so Iran has no Yemen case.

- Keep the rule: consistent, and it is the stricter reading of "the state chose to pass arms on". But a reviewer will ask why Iran is missing.
- Change the rule (count failure-to-prevent findings for materiel of the state's own origin as `unclear`): log it in PROTOCOL.md's change section with the date and reason, and report the evaluation under both rules, as the protocol requires.

You chose to keep the rule. When the evaluation is published, it should name Iran and these findings explicitly, so the exclusion is visible rather than silent.

- *Sceptic: "Your validation leaves out Iran's arming of the Houthis?"* → The Panel itself stops short of finding that the Iranian government transferred the weapons; it finds Iran failed to prevent their supply. Our protocol, fixed before coding, counts only what the Panel finds. We report the result both with and without such findings. If you want it public for the 10 December pitch anyway, it is honest as it stands: the README says what is done and what is not.

## Update, 26 November: first coding pass complete for the UN reports

**What.** The 69 UN reports not yet started (DR Congo, Central African Republic, Somalia, Mali, Haiti) were downloaded and coded, and 12 CAR publications were read for their findings. Totals now: **107 cases** (52 leakage, 39 re-transfer, 16 unclear) across 27 states, and 91 documented exclusions. Every row has a page, a quote and a URL. No evaluation was run, and I did not open the scores while coding.

**A new tool.** `validation/tools/forcescan.py`. `candidates.py` matches state names, but leakage findings usually name the army or police ("FARDC", "FACA", "Somali National Army"). Without it, most DRC and Somalia leakage would have been missed.

**What the new coding shows, without evaluating it.** Leakage dominates the new regimes, as the protocol expected: DRC, Somali, Haitian and CAR state stocks in almost every report. The new re-transfer cases are Rwanda (support to M23, 2022–2025), Burundi (army supplies to Congolese armed groups), the DRC itself (arming allied armed groups once the command directs it), Sudan, Uganda, the United States and Saudi Arabia (CAR's Islamic State investigation), and the CAR Government (arming co-opted militias).

**Decisions that need you (13 close calls are marked in `notes`).**

1. **Iran, again, but different.** Two CAR publications attribute materiel to the Iranian state: the 2016 dhow weapons to "a national stockpile", and the Qasef-1 drones to Iranian supply to the Houthis. Under the rule you kept, the Yemen Panel's failure-to-prevent findings stay excluded. These two are different: the materiel itself is attributed to the state. I coded both as `probable` (CAR's own wording is "suggests" and "plausibly"). If you read the rule as excluding Iran altogether, say so and I will move them to `excluded.csv`; that would be a protocol change and must be logged.
2. **When does a government arming militias count as re-transfer?** The DRC's support to Wazalendo groups and FDLR, and the CAR's arming of co-opted militias. I coded `unclear` where reports show units or commanders acting, and `re-transfer` where they show the command or government directing it (from S/2023/431). Check that line.
3. **Battlefield captures from peacekeepers** (Kenyan and Burundian AMISOM bases) are coded as leakage from those states' stocks, as the protocol's definition says. A reviewer may say AMISOM losses say little about Kenya's own controls. Keep them, or report them separately as a sensitivity?
4. **Embassy-level traces.** Single items traced to a state's purchase (a US Army machine gun, a Saudi grenade, UAE-end-user machine guns, Yemeni RPG rounds) are coded `unclear`, `established`. They will make some well-governed states "positive" on one item. The protocol's sensitivity run (one case per state, established only) shows the effect; it is worth stating in the evaluation.

- *Sceptic: "You coded 69 reports in a day; how careful can that be?"* → It is a first pass, marked `partly read`: findings located by three scans and read in context, each with page and quote. Full reads (annexes and tables) are still to do, and your 20% second coding and kappa come before any number is published.
- *Sceptic: "The United States is a positive case?"* → Under the protocol, yes: CAR traced US-purchased materiel re-transferred without the exporters' consent to Islamic State, and a US Army machine gun to a Somali arms dealer. The index scores the risk that arms leave a state's control; the evaluation will show these rows openly.

**Also fixed.** `candidates.py` crashed when printing CAR titles on a Windows console; it now writes UTF-8. One download (S/2022/479) failed on a reset connection and was retried. Four reports `candidates.py` flagged as "scanned?" are two-page letters with no findings, not scans.
