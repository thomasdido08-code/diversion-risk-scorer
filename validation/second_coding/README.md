# Second coding (PROTOCOL.md, section 6)

Drawn on 26 November 2026, after coding ended, by `tools/draw_sample.py` with seed 20261126: 30 of the 146 cases (20%, rounded up). Anyone can redraw the same rows from the same `cases.csv`.

**Do the two files in this order.** The first is blind; the second shows the first coding, so opening it first would unblind you.

## 1. `sample_blind.csv` (30 rows, blind)

Each row gives the report, the state, the page and paragraph, the finding sentence and the link. The first coder's mechanism, confidence, evidence and notes are left out, and rows carry a neutral reference (`row_ref`) instead of the case ID, which would name the mechanism.

For each row, read the passage in the report and fill in, using PROTOCOL.md sections 3 to 5 and the 26 November changes:

| Column | Values |
|---|---|
| `is_case (yes/no)` | Does the report present a finding that materiel held or transferred by this state reached an unauthorised user? |
| `mechanism` | `leakage`, `re-transfer` or `unclear` |
| `confidence` | `established` or `probable`, from the report's own wording |
| `evidence` | `physical`, `documents`, `both` or `testimony` |
| `second_coder_notes` | Anything you are unsure about |

Leave mechanism and confidence empty if you answer `no`. Do not open `cases.csv` or `check_retransfer.csv` until all 30 rows are done.

Then run:

```
python validation/tools/kappa.py
```

It prints agreement on whether rows are cases, Cohen's kappa on mechanism, agreement on confidence, and every disagreement.

## 2. `check_retransfer.csv` (59 rows, not blind)

Every `re-transfer` row (51) plus every row marked as a close call (17). 18 of these are also in the blind sample. Mark `agree (yes/no)`, and if no, give your mechanism and a short comment. The close calls are explained in each row's `notes`.

## After both

Disagreements are discussed and resolved, and the resolution is recorded in `cases.csv` notes. The protocol reports kappa before the evaluation (section 7) is run.
