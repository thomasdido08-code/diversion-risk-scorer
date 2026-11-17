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
