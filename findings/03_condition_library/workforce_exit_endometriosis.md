# Health-Related Workforce Exit by Condition: A Pilot Estimate for Endometriosis

*A methodology fragment extensible to the top 10 health-exit drivers.*

**Author:** Oriana Kraft
**Date:** April 2026
**Status:** Pilot / first-pass. All figures are bounded ranges using published parameters. Full IRB-ready version deferred to extension phase.

---

## Purpose

The Anthropic Economic Index measures AI's effects on workers currently doing tasks. It cannot measure AI's effects on labor-force non-participation, because the denominator excludes non-workers by construction. Yet ~12 million working-age Americans are currently out of the labor force citing disability or caregiving (BLS CPS, 2024–25). This memo demonstrates a methodology for quantifying the labor-economic footprint of a single health condition and the scale of labor recovery achievable under AI-mediated diagnostic compression. The methodology is extensible to the top 10 AI-addressable conditions and is the instrument for the larger analysis.

## Condition: Endometriosis

Selected because: (a) the largest published body of cost and productivity parameters exists for this condition, (b) the pathway-economics cascade used here has been validated in prior work, (c) the condition is sex-concentrated, which surfaces the sex-asymmetric labor-recovery effect that is the headline claim of the larger paper.

## Parameter inputs

All parameters from published sources. No original data required at pilot stage.

| Parameter | Value | Source |
|---|---|---|
| US prevalence (reproductive-age women) | ~6.5M | ACOG; Soliman 2018 |
| Severe / moderate-severe subset | ~15–20% of diagnosed | Nnoaham, *Fertil Steril* 2011 |
| Diagnostic delay (US) | 6.7 years | Soliman, *Adv Ther* 2018 |
| Annual productivity loss (severe cases) | 10.8 hrs/week; ~45 work days/year | Nnoaham 2011; FemTech Workplace Survey 2024 |
| Share reporting work disruption | 30–50% among severe | Nnoaham 2011; Hansen 2013 |
| Share reporting extended career disruption / LF exit | 5–10% among severe (lower-bound estimate) | Culley 2013 qualitative; extrapolated from UK / EU workplace studies |
| Median female working-age earnings (US, 2024) | ~$52,000 | BLS CES |
| Presenteeism factor (addition to absenteeism cost) | 1.4× | Simoens, *Hum Reprod* 2012 |
| Excess healthcare cost per undiagnosed year | ~$10,000 | Soliman 2018 |

## Step 1 — Baseline workforce-exit footprint (endometriosis alone)

**Severe-endo population (US, working-age):** 6.5M × 0.175 (midpoint severe share) ≈ **1.14M**.

**Workforce-exit subset (point estimate range):**
- Lower bound: 1.14M × 0.05 ≈ **57,000 women**
- Upper bound: 1.14M × 0.10 ≈ **114,000 women**

**Annual foregone earnings (endo alone):**
- Lower bound: 57,000 × $52,000 ≈ **$3.0B**
- Upper bound: 114,000 × $52,000 ≈ **$5.9B**

**Annual presenteeism / degraded-capacity cost (among still-employed severe cases):**
- 1.14M × (0.30–0.50 reporting work disruption) × 45 days × ($200/day) ≈ **$3.1B–$5.1B**

**Total labor-economic footprint of endometriosis, US:** ~**$6–11B annually**.

This is the condition-level denominator of the recovery scenario.

## Step 2 — AI-addressable bottleneck classification

For endometriosis, the primary labor-economic loss is upstream of treatment. The 6.7-year diagnostic delay is the dominant driver. Treatment itself, once accurately diagnosed, has known protocols (GnRH agonists, excision surgery). The bottleneck is **diagnostic compression** — specifically, early recognition of cyclical pelvic pain as endometriosis-specific rather than generic dysmenorrhea.

This is an AI-addressable bottleneck. My existing pilot data (30 prompts across 3 journey nodes, Claude Opus 4.7) shows the model matches ESHRE guideline routing in 100% of canonical cases — a floor estimate of the achievable compression if AI becomes the first triage point.

## Step 3 — Scenario estimates of labor recovery

Three scenarios, using diagnostic delay compression as the key variable:

**Scenario A — Observed adoption (conservative):**
AI reaches 20% of the symptom-stage patient population; reduces average delay by 1.5 years (from 6.7 to 5.2 years) in that subset.
- Affected: 1.14M × 0.20 × 0.075 (midpoint exit share) ≈ 17,000 women
- If 40% of affected avoid full LF exit → **~7,000 re-entries annually**
- Labor recovery: 7,000 × $52,000 × avg 15 remaining working years ≈ **~$5.5B lifetime value** / **~$360M annually**

**Scenario B — Median realistic (10-year horizon):**
AI reaches 50% of the symptom-stage population; reduces average delay by 3 years.
- Affected: 1.14M × 0.50 × 0.075 ≈ 43,000 women
- If 50% avoid full LF exit → **~21,000 re-entries annually**
- Labor recovery: 21,000 × $52,000 × 15 ≈ **~$16.4B lifetime value** / **~$1.1B annually**

**Scenario C — Frontier:**
AI reaches 80% of the symptom-stage population; reduces delay to <2 years.
- Affected: 1.14M × 0.80 × 0.075 ≈ 68,000 women
- If 70% avoid full LF exit → **~48,000 re-entries annually**
- Labor recovery: 48,000 × $52,000 × 15 ≈ **~$37B lifetime value** / **~$2.5B annually**

**Ranges for endometriosis alone:** $0.4–2.5B annually, or $5–40B in cumulative lifetime value, depending on adoption scenario.

## What this implies for the ten-condition paper

Endometriosis is a mid-sized driver of health-related workforce exit — larger than cystic fibrosis, smaller than chronic musculoskeletal pain or depression. If this methodology extends to the top 10 AI-addressable causes of workforce exit (chronic pain, depression/anxiety, migraine, fibromyalgia, autoimmune conditions, diabetes complications, cardiovascular rehabilitation, endometriosis, adult ADHD, and caregiving navigation), the aggregate recovery scale plausibly falls in the range of **$50–250B annually in recovered US GDP**. Half that range is plausibly attributable to female-concentrated conditions, which is the sex-asymmetric recovery claim at the center of the paper.

## Limitations stated up front

1. LF-exit share for endo specifically is an extrapolation; direct US survey data on condition-attributed exit rates is sparse.
2. Re-entry fractions assume that diagnostic compression translates to effective treatment and return to work; this is bounded by downstream care access.
3. The earnings parameter uses median female wage; actual affected-cohort wages vary.
4. The pilot treats AI as a diagnostic-compression instrument only; other mechanisms (administrative relief, self-management, caregiver release) are deferred to the full paper.
5. None of the numbers in this memo are submitted as settled estimates. They are a demonstration of the instrument. The full paper would use sex-disaggregated CPS, SSA, and MEPS data with condition-level coding and IRB-reviewed methodology.

## What this fragment demonstrates

1. The instrument works end-to-end: public data + published parameters + pathway cascade → condition-level labor-recovery range.
2. The methodology is condition-extensible.
3. For a single condition that affects ~1% of the US population, AI-mediated diagnostic compression plausibly recovers $0.5–2.5B/year in GDP, not counting second-order caregiver effects.
4. Fully built across 10 conditions, the aggregate number is large enough to be policy-material — which is the core claim the full paper would establish rigorously.

---

*Methodology code: `/analysis/workforce_exit_endometriosis.py` (forthcoming, pilot-stage calculation spreadsheet deferred to repo). Companion empirical AI-behavior pilot: `src/pilot_observed_exposure.py` / `src/pilot_sex_counterfactual.py`.*
