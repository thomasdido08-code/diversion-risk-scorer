# Blind validation: coding protocol

Fixed 25 November 2026, before any case is coded. Changes after this date are listed at the bottom with the reason, and the evaluation reports results under both the original and the changed rule.

## 1. Question

Which states were documented, in Conflict Armament Research (CAR) or UN Panel of Experts reports published 2015–2025, as the **source** of conventional arms, ammunition or related materiel that reached an unauthorised end user? And does the Diversion Risk Scorer rank those states high?

The index scores *recipient* states: the risk that arms sold to a state leave its control. So a case is the state from whose possession, or by whose decision, materiel went astray. It is not the state that made the item.

## 2. Which reports count

A complete sweep, not a sample. Every report below published from 1 January 2015 to 31 December 2025.

**UN Security Council Panels and Groups of Experts: final reports and published mid-term updates**

| Regime | Committee / resolution | Notes |
|---|---|---|
| Libya | 1970 (2011) | |
| Yemen | 2140 (2014) | |
| Sudan | 1591 (2005) | |
| South Sudan | 2206 (2015) | |
| Central African Republic | 2127 (2013) | |
| Democratic Republic of the Congo | 1533 (2004) | |
| Somalia (and Eritrea until 2018) | 751 (1992) / 2713 (2023) | Monitoring Group reports to 2018, Panel reports from 2019 |
| Mali | 2374 (2017) | Panel ran 2018–2023 |
| Haiti | 2653 (2022) | From 2023 |
| DPRK | 1718 (2006) | Arms and related materiel sections only |

**Conflict Armament Research**: every publicly released report, dispatch and Frontline Perspective listed on conflictarm.com with a publication date in the window. iTrace database entries are not used: they are not a citable published finding.

**Out of scope:** reports of national governments, NGOs other than CAR, media investigations, and UN reports other than Panel reports. They can corroborate a case in `notes` but cannot create one.

The list of reports actually read is kept in `validation/reports.csv` (symbol, regime or CAR series, date, URL, read on, cases found). A report that could not be obtained is listed with `status = missing`.

## 3. What counts as a case

One row = **one state × one report × one mechanism**.

A row is created when the report itself (not a source it cites without endorsing) states that materiel **held by, or transferred by the government of,** a named state reached an unauthorised end user: a non-state armed group, a sanctioned party, or any user in an embargoed territory without the required exemption.

The report must present it as a finding: wording such as "the Panel finds", "concluded", "documented", "established", "traced", "identified", or "in non-compliance with". Include findings the report qualifies as "highly likely" or "probable"; record the qualifier in `confidence`.

**Not a case**

- The state only **manufactured** the item and it passed through another state's stocks. Code the state that held it; put the manufacturer in `notes`.
- Allegations the report says it could not confirm, or reports it merely relays.
- A state's failure to inspect, intercept or report a shipment by others (a compliance failure, not diversion from its own control).
- Aircraft or vessel movements where the report does not establish that arms or related materiel were carried.
- Training, advisers or personnel without materiel.
- Private companies registered in a state, unless the report attributes the transfer to the government or to forces under its control.
- The non-state end user itself.

## 4. Fields (`validation/cases.csv`)

| Field | Content |
|---|---|
| `case_id` | `<report>-<iso3>-<mechanism>` |
| `source_type` | `UN` or `CAR` |
| `report` | UN symbol (e.g. `S/2019/914`) or CAR report title |
| `report_date` | publication date, YYYY-MM-DD |
| `event_years` | year(s) of the diversion if the report says, else empty |
| `theatre` | where the materiel was found |
| `state_iso3`, `state_name` | the source state |
| `mechanism` | `leakage`, `re-transfer` or `unclear` (rules in section 5) |
| `equipment` | `small arms`, `light weapons`, `ammunition`, `UAV`, `missile or rocket`, `armoured vehicle`, `aircraft`, `other` (semicolon-separated if several) |
| `evidence` | `physical` (inspected items, serials, markings), `documents` (end-user certificates, contracts, flight records), `both`, or `testimony` |
| `confidence` | `established` or `probable`, from the report's own wording |
| `page`, `paragraph` | page of the PDF and the report's paragraph or annex number |
| `quote` | the finding sentence, at most 30 words |
| `url` | link to the report PDF |
| `coded_on`, `coder` | date and coder |
| `notes` | manufacturer, corroborating sources, doubts |

## 5. Leakage or re-transfer

- **leakage** (weak control): the state's own stocks were lost, looted, captured on the battlefield, stolen, or sold or handed over by officials or units acting without government authorisation. The question the index's governance data answers: *could* the state keep control?
- **re-transfer** (deliberate): the government, or forces under its command acting as policy, passed materiel to a third party in breach of an embargo or of an end-user undertaking, or supplied an embargoed party. The question: did the state *choose* to pass it on?
- **unclear**: the report establishes that the materiel came from the state but not how. Coded, reported separately, never merged into either group.

Where a report documents both mechanisms for one state, two rows are coded.

## 6. Blindness, and its limits

- **Who codes.** Claude (the AI assistant that also worked on the index) codes first. Thomas Di Domenico second-codes a random 20% of rows, drawn with a fixed seed after coding ends, and checks every `re-transfer` row. Agreement on `mechanism` is reported (Cohen's kappa) before the evaluation is run.
- **What the coder has already seen.** Before this protocol was written, the coder had seen the published headline (the top 10, and the UAE ranked 134th), the 15 hand-picked validation cases, and a partial coding of Libya Panel reports done on 30–31 October 2026. Full blindness is therefore impossible. The mitigations:
  1. The rules above are fixed before coding and decide cases from the report text alone.
  2. During coding, the coder does not open `data/derived/`, `data/raw/components.csv`, `rank_ranges.csv` or the page.
  3. The October partial coding is not reused. Libya is coded again from the reports, and the two codings are compared only afterwards.
  4. Every row cites page and paragraph, so any reader can check it.
- **Selection bias that blindness does not fix.** UN Panels exist only for sanctioned theatres, all of them conflict states, so leakage cases cluster where the index already scores high. Re-transfer cases come from supplier states anywhere and are the harder test.

## 7. Evaluation (run only after coding and second coding are complete)

Unit: **states**. A state is a positive if it has at least one coded case of that mechanism. All other scored states are negatives.

Reported, for `leakage`, `re-transfer` and `any`:

1. **Mean and median percentile** of positive states under the current base weights, percentile = 100 × (1 − (rank − 1) / 205), as the current validation uses.
2. **AUC**: the probability that a random positive state outranks a random negative state.
3. The same two figures for **governance alone** as a naive baseline.
4. The same figures for the **current hand-picked set** (15 states), side by side.
5. Each positive state listed with its rank, number of cases and reports.

Sensitivity, reported but not used to change anything: positives counted only from `established` rows; UN-only and CAR-only; one case per state regardless of number of reports.

No weight, component or threshold is changed on the basis of this evaluation within the same release. Fitting weights (roadmap item 4) is a separate step, with its own protocol.

## Changes to this protocol

Sections 1–7 above are left as fixed on 25 November. Changes are listed here, dated, and the evaluation reports results under the original and the changed rule.

### 26 November 2026 (decided by Thomas Di Domenico, after the first coding pass and before any evaluation)

No case is recoded by these changes, and no score was looked at in making them.

1. **Clarification of section 5: state forces supplying armed groups.** Materiel passed by a state's own forces to an armed group is coded `re-transfer` only when the report shows the military command or the government directing or organising it (for example, meetings convened by the official hierarchy, a provincial government coordinating supplies, or a government programme). When the report shows units, officers or a regional commander acting without that, it is coded `unclear`. When the report shows sales or theft by individuals, it is `leakage`. This is the rule applied in the first pass; it is written down here because section 5 did not cover it.
   - *Why:* the DR Congo and Central African Republic reports describe a continuum from soldiers selling ammunition to a government using armed groups as proxies.
   - *Added sensitivity:* re-transfer results are also reported (a) without any row covered by this clarification, and (b) with those rows counted as `unclear`. The states concerned rank high on the index, so counting them as re-transfer positives would flatter the index on the re-transfer test.

2. **Added sensitivity: losses of forces deployed abroad.** Battlefield captures from a state's forces serving outside its territory (for example, AMISOM contingents in Somalia) remain `leakage` under section 5. Results are also reported without them, because such losses reflect the theatre more than the contributing state's own stock controls.

3. **Note on the Iran exclusion (no change).** The 25 November decision stands: failure-to-prevent findings and findings against non-state senders are not cases. Findings that attribute the materiel itself to the Iranian state (a national stockpile, or supply by the state) are cases under section 3, like those for any other state; they are coded with the confidence the source gives. The `established`-only sensitivity reports results without the `probable` ones.

4. **Note on reporting (no change).** Single items traced to a state's purchase, where the report does not say how they left that state's control, are coded `unclear` and so enter only the `any` results (section 5). The evaluation says so next to the `any` figures, together with the `established`-only and one-case-per-state results already listed in section 7.
