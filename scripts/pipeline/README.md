# Input pipeline

Pulls the scorer's inputs from their sources and compares them with the hand-collected file. It changes nothing in `data/raw/components.csv`; any fix is a separate, reviewed step. Standard library only.

```
python scripts/pipeline/fetch_worldbank.py               # WGI and WDI through the World Bank API
python scripts/pipeline/fetch_att.py --as-of 2026-10-30  # ATT status from the UN Treaty Collection
python scripts/pipeline/diff_inputs.py                   # compare with the hand-collected inputs
```

| Input | Source pulled | How |
|---|---|---|
| Rule of law, control of corruption, government effectiveness, political stability, voice and accountability | World Bank WGI (API source 3, `GOV_WGI_*.EST`) | latest year per economy |
| Arms imports 2015 onwards | SIPRI trend-indicator values, via World Bank WDI `MS.MIL.MPRT.KD` | summed, millions |
| Battle-related deaths 2020 onwards, 2015 onwards | UCDP, via World Bank WDI `VC.BTL.DETH` | summed |
| ATT status | UN Treaty Collection, chapter XXVI-8 (the depositary record) | party once the treaty is in force for the state (deposit + 90 days) |
| Arms embargoes | not automated | see below |

**Not automated, and why.**

- **Embargoes.** No single machine-readable official list covers UN, EU and OSCE measures and their scope (full, non-state actors only, targeted). The file stays hand-coded from SIPRI's embargo archive and the UN and EU sanctions lists. Check it against [SIPRI's arms embargo archive](https://www.sipri.org/databases/embargoes) and the [EU Sanctions Map](https://www.sanctionsmap.eu/) at each update.
- **UCDP and SIPRI directly.** UCDP's own API now needs an access token, and SIPRI's trade register is a form-based export. Both reach the World Bank with a lag (battle deaths to 2024, arms imports to 2025), which is what the index used.

## Result of the first run (25 November 2026)

- **World Bank values:** 1,736 values for 217 economies compared; **0 mismatches**.
- **Components:** recomputing the five components from the API values with the October 2026 formulas gives **0 differences** from `data/raw/components.csv` at three decimals.
- **ATT:** status on 30 October 2026 from the UN Treaty Collection matches the February 2026 lists for every scored state. Niue is on the list but has no World Bank data, so it is not scored.
- **Ranks:** none change.
- **Labels:** the World Bank API now names Nauru "Naoero". No effect.

Full list: `data/raw/api/diff_2026-11-25.csv`.
