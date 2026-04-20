# Arm B — Patient-Facing Consumer Side

Measurement of Claude's direct interaction with patients — observed routing, sex counterfactual on ambiguous presentations, and HealthEx-style own-data queries (the Jan 2026 consumer integrations).

## Artifacts

- **[patient_side_synthesis.md](patient_side_synthesis.md)** — integrating memo across all patient-facing pilots.
- **[pilot_observed_exposure_writeup.md](pilot_observed_exposure_writeup.md)** — endo routing at 3 journey nodes. 100% ESHRE guideline match.
- **[pilot_sex_counterfactual_writeup.md](pilot_sex_counterfactual_writeup.md)** — 60 prompts, sex-ambiguous complaints. Aggregate null (OR 1.00); epigastric-pain directional F-disadvantage gap.

## Scripts

`src/pilot_observed_exposure.py` · `src/pilot_sex_counterfactual.py` · `src/pilot_patient_ehr_queries.py` · `src/pilot_analyze.py` · `src/pilot_analyze_counterfactual.py` · `src/analyze_patient_side_synthesis.py`
