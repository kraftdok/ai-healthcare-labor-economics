# Physician-Identified Diagnostic Bottlenecks: Evidence from the Roche / HBA / FemTechnology 6-Country Physician Survey

*A pilot re-analysis using the Women's Health Physician Survey as an AI-vs-clinician comparative baseline.*

**Author:** Oriana Kraft
**Date:** April 2026
**Dataset:** Women's Health Physician Survey (2024), co-produced with Roche Diagnostics and the Healthcare Businesswomen's Association. N = 200 physicians; 6 countries (US 50, Germany 50, Brazil 25, Thailand 25, Morocco 25, Egypt 25); 5 therapy areas (Oncology, Ophthalmology, Neurology, Cardiology, Endocrinology); 40 respondents per therapy area. Fielded August–October 2024.

---

## Why this survey matters

The AI-in-clinical-decision-support audit literature scores model outputs against published guidelines. But **the guidelines themselves are what physicians tell us, in this survey, are inadequate to current clinical practice in women's health** — across every therapy area studied. The survey provides:

1. A **physician-reported bottleneck map**: where clinicians themselves say the diagnostic and treatment-protocol limits are.
2. A **comparative-baseline reference**: what the current human-clinician standard of care achieves on these specific conditions, which any AI-comparison study must control against.
3. A **cross-country gradient**: six countries spanning high-, middle-, and low-income contexts, providing natural variation for cross-system deployment comparison.

---

## Headline physician findings — high-income (US) subset

### Cardiology — the largest research-gap signal

From 9 US cardiologists treating female cardiovascular disease:

| Condition | % identifying as requiring more gender-specific research |
|---|---|
| Stroke | **100%** |
| Heart failure | **89%** |
| Heart attack symptoms | **89%** |
| Hypertension | **78%** |

Physician experience of treating the gap:
- **67%** report "often" or "always" seeing cardiovascular disease manifest differently in women vs men.
- **77%** report significant challenges diagnosing and treating heart disease in women due to **lack of research and gender-specific guidelines**.
- **Only 10%** report that current protocols adequately account for sex differences. Half report that current protocols only "slightly" account for them.

Where physicians believe improved research would have the most impact: diagnosis accuracy (100%), treatment effectiveness (100%), preventative care (90%), improved patient education (60%).

### Oncology

- **100%** identify ovarian and breast cancers as conditions requiring more focused research.
- 70% identify endometrial and cervical cancers; 50% lung cancer.
- **80%** frequently observe gender differences in cancer symptoms and progression that "need further investigation."
- 30% often encounter cases where limited research on women's cancers negatively impacts patient care.
- What they want: personalized treatments (80%), early detection (70%), better understanding of gender-specific symptoms (70%).

### Endocrinology

- **90%** identify polycystic ovary syndrome (PCOS) as requiring more research.
- 80% identify osteoporosis; 70% thyroid disorders.
- **90%** believe research gaps on endocrine disorders impact women's health (45% significantly, 45% moderately).
- 55% "significantly" address gender-based differences in treatment response in their practice; 36% only "moderately" — indicating the practice-level gap is wider than the research-level gap.
- Key impact areas flagged: preventative care, management across life stages, gender-specific symptom understanding.

---

## What the data tells us about the bottleneck taxonomy

The bottleneck taxonomy classifies each cause of health-related workforce exit by AI-addressable bottleneck type (diagnostic compression, treatment access, ongoing management, caregiving substitution, administrative burden). This survey directly validates that taxonomy from the clinician side:

| Bottleneck type | Physician-reported signal |
|---|---|
| **Diagnostic compression** | 67–80% of cardiology / oncology / endocrinology respondents frequently observe gender-differential presentation patterns. Diagnostic accuracy is flagged as the #1 improvement area in cardiology (100%) and a top-3 area in oncology and endocrinology. |
| **Ongoing management / protocols** | Only 10% of cardiologists report current protocols adequately account for sex differences — the largest single guideline-inadequacy signal in the dataset. |
| **Research-base inadequacy upstream of all three** | 100% (stroke), 90% (endocrine), 100% (ovarian/breast cancer) identify specific conditions as requiring more gender-specific research — meaning the training data that any clinical AI uses is itself gap-ridden in exactly the domains where it is most needed. |

This is validation of the bottleneck-classification step from the clinician side — not just from literature review.

---

## Why this makes AI-vs-clinician comparison a necessary study, not an optional one

If 77% of cardiologists report facing significant diagnostic challenges in female patients because the research base is gap-ridden, then:

1. Any AI tool trained on the same research base will inherit the same gaps.
2. Any bias-audit study that scores AI against "clinician accuracy" without sex-disaggregated data is comparing two systems with identical upstream contamination.
3. The meaningful question is not *"is AI biased"* but *"is AI's routing behavior, on the specific conditions physicians themselves flag as gap-ridden, better, worse, or differently biased than the current clinician baseline?"*

The survey makes that comparison possible. The extension work would operationalize this at scale, using Claude routing outputs vs the physician-response distributions on matched clinical scenarios.

---

## Cross-country validation potential

The 6-country design — US, Germany, Brazil, Thailand, Egypt, Morocco — provides natural variation in health-system structure, clinical-guideline authority, and specialist availability. Preliminary readings (detailed country reports in progress) suggest substantial cross-country variation in reported adequacy of protocols, which is the empirical basis for cross-system deployment comparison (California Medi-Cal / Andhra Pradesh / Switzerland). The middle- and low-income-country arms (Brazil, Thailand, Egypt, Morocco) are particularly load-bearing for augmentation-vs-substitution analysis.

---

## Limitations

1. Sample size per therapy-area × country cell is small (5–10 physicians per cell).
2. Respondents are not random — they are HBA / Roche network physicians, likely over-representing clinicians engaged with women's-health research.
3. Self-reported practice adequacy is subject to social-desirability bias; the fact that physicians still report large gaps is notable, because the bias direction runs toward under-reporting.
4. Physician agreement on "gaps exist" is not the same as "AI would address the gaps"; the main study operationalizes that second question.

---

## Implications for the larger analysis

1. The survey serves as the clinician-baseline reference for any AI-vs-clinician comparison; this memo is the evidentiary anchor.
2. Step 2 of the cascade (bottleneck classification) now has two independent validation channels: literature review + physician self-report.
3. The cross-country design provides the natural-variation basis for payer-structure comparison in the extension analyses.
4. The physician-identified specific conditions requiring research (stroke, heart failure, PCOS, osteoporosis, ovarian cancer) are candidate conditions for the top-10 condition set in the full analysis.

---

*Source: Women's Health Physician Survey 2024 — Detailed Country Report (Roche / HBA / FemTechnology). Full country-level analyses in progress.*
