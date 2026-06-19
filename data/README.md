# Data

This folder contains **input data** consumed by the simulation and validation pipeline.

## Contents

| File                              | Description                                                                                | Source                                              |
| --------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------- |
| `st_petersburg_winter2022.csv`    | Normalised reference outbreak curve for the St. Petersburg COVID-19 Omicron wave (120 days). Two columns: `day`, `normalised_cases` (peak normalised to 1.0). | Smoothed representation of the St. Petersburg open monitoring data for Winter 2022. |

## Notes on data licensing and ethics

- The reference outbreak curve is a **smoothed, normalised** representation, free of any personally-identifying or patient-level information.
- All disease and behavioural parameters used by the simulation are encoded **directly in source code** (`src/seir.py`) and are derived from published literature; see `docs/related_work.md` for citations.
- Synthetic populations are generated **stochastically** from the Stochastic Block Model in `src/network.py` and are not derived from any individual-level records.

## Replacing the validation curve with raw monitoring data

`st_petersburg_winter2022.csv` is intended as a reference for the validation figure. Researchers with access to raw monitoring data can drop in a CSV with the same two columns (`day`, `normalised_cases`); `src/figures.py` will use the new file automatically.
