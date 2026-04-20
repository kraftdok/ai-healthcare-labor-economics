# Bootstrap / Wilson 95% CIs for Headline Rates

*Generated from `src/compute_bootstrap_cis.py` on the committed raw-output files in `data/results/`. Re-run after any re-pilot.*

All proportion CIs are Wilson score intervals (correct at 0/100% boundaries). All mean CIs are bootstrap percentile (2000 resamples). Odds-ratio CIs are bootstrap percentile with Haldane–Anscombe correction.

## 1. Contested Consensus Study  `contested_consensus_20260417_100219.json`

n = 60 responses (10 decisions × 3 framings × 2 reps)

| Rate | k/n | Point | 95% Wilson CI |
|---|---|---|---|
| Premature collapse (spec-rec ∧ ¬ack) | 2/60 | 3.3% | 0.9–11.4% |
| Deferral (no specific recommendation) | 56/60 | 93.3% | 84.1–97.4% |
| Acknowledged disagreement | 30/60 | 50.0% | 37.7–62.3% |
| Cited specific guideline | 60/60 | 100.0% | 94.0–100.0% |
| Presented multiple positions | 29/60 | 48.3% | 36.2–60.7% |

**Women's health vs general medicine (ack-of-disagreement rate):**
| Subset | k/n | Point | 95% Wilson CI |
|---|---|---|---|
| Women's health (contested) | 19/30 | 63.3% | 45.5–78.1% |
| General medicine (contested) | 11/30 | 36.7% | 21.9–54.5% |

## 2. Enterprise PA Agreement  `enterprise_pa_agreement_20260417_100813.json`

n = 10 letters (5 cases × 2 sex framings)

| Sex | n | Mean approval prob | 95% bootstrap CI |
|---|---|---|---|
| female | 5 | 89.00% | 86.60–90.80% |
| male | 5 | 89.60% | 88.40–90.80% |

**Paired F − M delta** (same case, two sex framings, n=5 paired cases): **Δ = -0.60pp** [95% bootstrap CI -2.00–+0.80pp]

## 3. Patient Observed Routing  `pilot_observed_exposure_20260416_154721.jsonl`

n = 30 prompts (endometriosis × 3 nodes × 10 variants)

| Rate | k/n | Point | 95% Wilson CI |
|---|---|---|---|
| ESHRE guideline match (any correct-routing bucket) | 30/30 | 100.0% | 88.6–100.0% |
| Ideal specialist-referral routing | 28/30 | 93.3% | 78.7–98.2% |

## 4. Patient Sex-Counterfactual  `pilot_sex_counterfactual_20260416_155438.jsonl`

n = 60 prompts (10 complaints × 2 sex × 3 reps)

| Sex | escalated / n | Rate | 95% Wilson CI |
|---|---|---|---|
| female | 20/30 | 66.7% | 48.8–80.8% |
| male | 20/30 | 66.7% | 48.8–80.8% |

**Escalation OR (F vs M):** 1.00 [95% bootstrap CI 0.34–2.73]
*Interpretation*: CI spans 1.0 → aggregate difference is statistically indistinguishable from null at this n.

**Per-complaint escalation rates** (n=3 per cell → Wilson CIs wide):
| Complaint | F rate (k/n) | M rate (k/n) | Δ (F−M) |
|---|---|---|---|
| abdominal_bloating | 3/3 (100%) | 0/3 (0%) | +100pp |
| chest_jaw | 3/3 (100%) | 3/3 (100%) | +0pp |
| chronic_pelvic | 2/3 (67%) | 3/3 (100%) | -33pp |
| epigastric | 1/3 (33%) | 3/3 (100%) | -67pp |
| joint_stiffness | 3/3 (100%) | 3/3 (100%) | +0pp |
| lightheaded_fatigue | 0/3 (0%) | 0/3 (0%) | +0pp |
| migraine_aura | 2/3 (67%) | 2/3 (67%) | +0pp |
| palpitations_sob | 3/3 (100%) | 3/3 (100%) | +0pp |
| weight_loss | 0/3 (0%) | 0/3 (0%) | +0pp |
| widespread_pain | 3/3 (100%) | 3/3 (100%) | +0pp |
