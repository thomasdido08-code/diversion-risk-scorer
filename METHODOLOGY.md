# Diversion Risk Scorer: method

Snapshot 30 October 2026 · Thomas Di Domenico

## What it operationalises

Criterion 7 of EU Common Position 2008/944/CFSP: the risk that military technology or equipment will be diverted within the buyer country or re-exported under undesirable conditions. The tool scores states, not individual licences.

## Components

Five components, each scaled from 0 (low risk) to 1 (high risk), weighted and summed to a 0–100 score.

- **Governance (40%)**: mean of the World Bank's WGI Rule of Law, Control of Corruption and Government Effectiveness, flipped from the −2.5…+2.5 scale so that weaker governance means higher risk.
- **Conflict at home (20%)**: half log-scaled battle deaths 2020–24, half WGI Political Stability and Absence of Violence.
- **Arms embargo (10%)**: full UN or EU embargo 1; embargo limited to non-state forces or targeted 0.5; non-binding OSCE request 0.25.
- **Neighbourhood (15%)**: the highest conflict score among the state's land neighbours. Islands score 0.
- **Outside the ATT (15%)**: Arms Trade Treaty State Party 0, signatory 0.5, outside the treaty 1.

```
score = 100 × Σ weight × component      (weights normalised to sum to 1)
```

**Exposure** multiplies the score by the state's arms imports 2015–25 (SIPRI trend-indicator values, millions), so large importers with moderate risk rise in the ranking.

**Risk levels** used in the tool: Critical ≥ 70, High ≥ 55, Elevated ≥ 40, Lower below 40.

**Rank range.** Each state carries a 5th–95th percentile rank range from re-scoring under perturbed weights, and the share of the top 10 that stays in the top 10 under those perturbations (88% on average). These figures were computed when the snapshot was built; the perturbation code is not in this repository yet.

## Sources

- World Bank Worldwide Governance Indicators 2025, via the World Bank API.
- SIPRI Arms Transfers Database, imports by recipient 2015–25 (TIV), via the World Bank API.
- UCDP battle-related deaths 2020–24, via the World Bank API.
- ATT Secretariat lists of States Parties (118) and signatories (25), February 2026.
- Embargoes in force: hand-coded from SIPRI's embargo archive and UN/EU sanctions lists, October 2026.
- Borders and map: world-countries and Natural Earth (world-atlas).

## Validation

Fifteen states with documented diversion, split by mechanism:

- **Leakage** (weak states losing their stocks): 10 cases, mean percentile 95.
- **Deliberate re-transfer by governments**: 5 cases, mean percentile 76.

The model is far better at the first than the second. Governance data measures whether a state *can* control its arsenal, not whether it *chooses* to: the United Arab Emirates ranks 134th despite UN Panel findings on Libya.

These cases were picked knowing the outcome, so this is a sanity check, not a blind test. The cases and their documented patterns are in `data/raw/validation_cases.csv`.

## Re-transfer component (proposal, not adopted)

The index cannot see deliberate re-transfer: governance data measures whether a state *can* control its arsenal, not whether it *chooses* to pass arms on. Roadmap item 3 tests whether a sixth component fixes that. `scripts/retransfer_preview.py` computes it without changing the published scores.

- **Input.** UN Panel reports that find the state's government transferred or re-transferred materiel in breach of an embargo, coded under `validation/PROTOCOL.md` (`validation/cases.csv`, re-transfer, established findings only).
- **Scaling.** Distinct reports with such a finding: none 0, one 0.5, two or more 1. Counting reports rather than findings stops long-running regimes with many reports from dominating, and the cap stops one state's record from swamping everything else.
- **Weight.** 10%, taken from the other five components in proportion, so their ratios stay as they are. 5% and 15% are shown for comparison. The weight was set before looking at where the UAE lands and was not changed afterwards.
- **No circularity.** The component uses only reports published to the end of 2020. Validation of the component may use only re-transfer cases from 2021–2025 reports and CAR reports.

**Result, with the coding done so far** (Libya, Yemen and South Sudan, partly read; so this is a test of the mechanics, not a finding):

| State | Reports with a finding (to 2020) | Rank now | 5% | 10% | 15% |
|---|---|---|---|---|---|
| United Arab Emirates | 2 | 134 | 107 | 83 | 70 |
| Uganda | 2 | 28 | 19 | 13 | 8 |
| Qatar | 1 | 100 | 89 | 79 | 74 |
| Jordan | 1 | 54 | 42 | 35 | 30 |
| Türkiye | 1 | 41 | 36 | 29 | 22 |
| Sudan | 4 | 1 | 1 | 1 | 1 |

The top 10 does not change at any of the three weights.

**It does not fix the blind spot.** The UAE rises 51 places at 10% but stays in the lower half and below the "Elevated" band (40). That is arithmetic, not a matter of tuning: at weight *w*, the component adds at most 100*w* points, and a well-governed state's other components are low. The UAE scores 29.8 now; at 10% the most it can reach is 0.9 × 29.8 + 10 = 36.8. At 15% it reaches 40.3, the bottom edge of "Elevated", and still ranks only 70th, because many states sit in that band. It would take 20% to reach 45th and 25% to reach 28th: weights at or above that of conflict at home (20%), chosen only to move one case, which is tuning. The additive design measures capacity well; intent needs a different instrument.

**Recommendation:** publish deliberate re-transfer as a separate flag beside the score ("documented re-transfer in N UN Panel reports"), not inside it, so the two questions (*can* the state keep control, and *does* it choose to pass arms on) stay visible. This is listed as a limit until the validation coding is complete and the flag can be tested on 2021–2025 cases.

## Overlap between components (roadmap item 5)

Governance and conflict at home are correlated: Pearson 0.66, Spearman 0.77 across the 205 states. Part of that is built in, since the conflict component is half WGI Political Stability, a sibling of the governance indicators. Conflict and neighbourhood also correlate (0.59, Spearman 0.71), as neighbourhood is the neighbours' conflict score. The other pairs are below 0.5.

Does the overlap matter? Dropping the conflict component altogether (weights renormalised) leaves the ranking almost unchanged: rank correlation 0.989 with the published ranking, and 8 of the top 10 kept. So instability is partly counted twice, but that changes little. Merging the two is not worth the loss of a separately readable "conflict" signal. Kept as is, and documented here.

## Known limits

- Scores states, not licences. A real Criterion 7 assessment looks at the end user and the item.
- Weights are set by judgement, not fitted. Validation cases were not chosen blind.
- Arms imports are from all suppliers, not EU deliveries only.
- Taiwan and small territories without World Bank data are missing.
- UCDP counts deaths where fighting happens: Israel reflects Gaza; Russia reflects only fighting on its own territory.
- Governance and conflict measures overlap, so instability may be counted twice.
- Static snapshot dated 30 October 2026.

## Planned improvements

See the roadmap in [README.md](README.md): an automated World Bank pull, blind validation from Conflict Armament Research and UN Panel reports, a UN Panel findings component, fitted weights, an overlap check, EU-only deliveries, and separate scores by weapon type.

## Change log

- **30 October 2026**: first snapshot.
- **25 November 2026**: input pipeline added (`scripts/pipeline/`): the World Bank API and UN Treaty Collection reproduce every hand-collected value; no data changed. Blind-validation protocol fixed and coding started (`validation/`). Re-transfer component previewed and not adopted (see above). Overlap check added. Scores unchanged.
