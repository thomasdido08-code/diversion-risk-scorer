# Data dictionary

## raw/

| File | Contents |
|---|---|
| `components.csv` | One row per state: `iso3`, `name`, `region`, `income` (World Bank groups), `arms_imp_tiv_m_2015on` (SIPRI arms imports 2015–25, TIV millions), `battle_deaths_2020on` (UCDP), the five components on a 0–1 scale (`gov_risk`, `conflict_risk`, `embargo_risk`, `neighbourhood_risk`, `att_risk`), `att_status` (`party`, `signatory`, `none`), `embargo_bodies` (e.g. `UN;EU`; empty if none), `embargo_note` |
| `weights.json` | Base weights of the five components and the snapshot date |
| `rank_ranges.csv` | `iso3`, `rank_p05`, `rank_p95`: 5th–95th percentile rank under perturbed weights |
| `sensitivity.json` | `top10_overlap_avg`: average number of the base top 10 that stay in the top 10 under perturbed weights |
| `validation_cases.csv` | `iso3`, `mode` (`leakage` or `re-transfer`), `example` (documented pattern) |
| `borders.json` | Land neighbours by ISO3 code |
| `iso_numeric.json` | ISO 3166 numeric code → ISO3, to join the map to the scores |

## derived/

| File | Contents |
|---|---|
| `scores.json` | The published snapshot the page loads: weights, every state's components, score, rank, exposure, exposure rank, rank range, and the validation cases with their ranks and percentiles |
| `scores.csv` | The same scores as a flat table, written by `scripts/build.py` |

Ranks in `scores.json` are competition ranks on the rounded score, so tied states share a rank. Scores were computed from unrounded components; recomputing from `components.csv` (three decimals) can differ by up to 0.1, which `scripts/build.py` checks.
