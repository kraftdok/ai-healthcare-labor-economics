# Arm I — Physician–Patient Supply-Demand Triangulation

Cross-side comparison of two independent primary-data sources looking at the same underlying question:

| Side | Source | N | Question |
|---|---|---|---|
| **Patient / demand** | FemTechnology Workplace Survey 2024 | 981 × 42 countries | *Where does AI healthcare fail women?* (Q49 taxonomy, arm H) |
| **Physician / supply** | Roche/HBA/FemTechnology Women's Health Physician Survey 2024 | 200 × 6 countries × 5 specialties | *Which conditions require more gender-specific research?* |

Both datasets were collected by the author or under the author's co-production; both have country-tagged public summaries; neither has been triangulated against the other in the existing literature.

## Files

| File | Purpose |
|---|---|
| `physician_survey_data.json` | Structured extract of physician percentages by country × specialty × condition |
| `triangulation.json` | Machine-readable triangulation output: convergent / patient-only / physician-only categories |
| `../../src/triangulation_analysis.py` | Script that joins the two datasets and classifies each gap category |

## Top-line finding in one paragraph

Patients and physicians both flag the same three condition categories (cardiovascular, PCOS/endocrine, and female-specific cancer) as AI-healthcare research gaps — but **physicians report 16–28× higher urgency than patients surface in their open-ended responses**. Patients fragment into upstream framing (*"AI doesn't understand how my symptoms present"*, 29%); physicians fragment into specialty-specific condition lists (AMD, osteoporosis, Alzheimer's each >75%). Six patient-named themes have no physician-specialty counterpart in the Roche survey — most notably **menopause (10% of patient responses, no OB/GYN track)**, **medical dismissal / gaslighting** (clinician behavior, not self-reported in a condition survey), and **autoimmune conditions** (no rheumatology track). The **Roche/HBA survey's tier-1 specialty design (Oncology/Endocrinology/Cardiology/Neurology/Ophthalmology) systematically omits the specialties where patients name the largest gaps**. That omission is itself a finding.
