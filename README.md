# AI in Healthcare — Labor-Economic Measurement

## What this repository is

A pilot-scale portfolio measuring how Claude — as deployed under Anthropic's January 2026 Claude for Healthcare launch — affects the labor-economic upstream of the US healthcare system. The work tests the architectural bet Anthropic has made (monolithic-model safety via Constitutional AI and calibrated uncertainty) against the decomposed-agent critique raised in JAMA 2025 and by Verily's Violet product team.

The repository contains six measurement arms, each runnable against the Claude API. Some arms produce **measured** outputs (behavioral observations of Claude on structured inputs). Others produce **scenario projections** (labor-economic estimates computed from small measured inputs × published volume and wage parameters). The distinction is kept explicit throughout.

---

## Core question

> When Claude enters clinical pathways, how much of the ~$600B annual labor-economic footprint of health-related workforce exit is recoverable, and for whom?

Healthcare is adopting AI 2.2× faster than the rest of the economy. Twelve million working-age Americans are out of the labor force for health or caregiving reasons. The WEF/McKinsey Health Institute estimates that closing the women's-health gap alone would add at least $1T to annual global GDP by 2040. Anthropic's January 2026 launch brought Claude into three specific healthcare verticals (prior auth, documentation, care coordination) and two consumer integrations (HealthEx, Apple/Android Health). Whether the model performs safely and distributes its benefits equitably is now an empirical question.

---

## Portfolio structure

```
findings/
├── 01_enterprise/             ← Claude for Healthcare vertical deployment
├── 02_patient_consumer/       ← patient-facing deployment surface  
├── 03_condition_library/      ← methodology validation across 5 conditions
├── 04_architectural_test/     ← monolithic vs decomposed (Verily/JAMA)
├── 05_proprietary_data/       ← workplace + physician survey re-analyses
└── 06_methodology/            ← citation anchors + quantifications
```

---

## Headline findings

Findings below are labeled **[measured]** (behavioral observations of Claude on structured inputs at pilot scale) or **[projected]** (labor-economic scaling of measured inputs through published volume and wage parameters — scenario estimates, not observed recoveries). Limitations of each arm — small n, single-rater rubric, self-constructed prompts, assumption-driven volume parameters — are detailed in the corresponding findings memo.

### Measurement-grade (observed Claude behavior)

| Arm | Finding | What it means |
|---|---|---|
| **Architectural test (Verily/JAMA)** [measured] | **3% premature collapse / 93% deferral** on 10 contested clinical decisions × 3 framings × 2 reps (n=60 responses) | Direct empirical answer to the JAMA 2025 "monolithic vs. decomposed" critique. Claude passes the epistemic-humility test at the cost of near-total deferral when evidence is genuinely split. **The cleanest measurement in the portfolio** — objective rubric dimensions, pre-selected contested decisions, multiple framings. |
| **Enterprise PA sex-counterfactual** [measured] | Δ **−0.6pp** on Claude-scored approval probability (F 89.0%, M 89.6%) across 5 cases × 2 sex framings | At pilot scale, Claude's PA letter output is sex-invariant on clinically-matched cases. Caveat: Claude-as-generator + Claude-as-reviewer shares training biases; independent clinician arm is the natural extension. |
| **Patient-facing sex-counterfactual** [measured, pilot-underpowered] | Aggregate **OR 1.00** (95% CI 0.34–2.93) for escalation across 10 complaints × 2 sex × 3 reps; epigastric-pain directional **67-pt F-disadvantage** at n=3/cell | CI spans 0.3–3×: aggregate is statistically indistinguishable from null. Per-complaint signal on epigastric pain is consistent with published female-ACS under-triage literature but underpowered for inference. |
| **Patient-facing observed routing** [measured, self-graded] | **100% ESHRE guideline match** across 30 endo prompts × 3 journey nodes | Caveat: prompts, ground-truth, and rubric were all author-constructed. The finding reports *guideline concordance under author-designed testing conditions*, not external clinical validation. An independent clinician-blind scoring arm is the extension step. |
| **Workplace survey (n=981, 42 countries)** [measured] | **62% time-off rate** for women's-health conditions; **77% agree gender data gap significantly impacts AI healthcare quality for women**; **only 5%** agree current AI is equally effective by sex | Primary survey data; proportions with Wilson CIs. The measured prevalence is the finding; see below for the projected dollar-footprint scaling. |

### Scenario projections (labor-economic scaling)

| Arm | Projection | Basis + caveat |
|---|---|---|
| **Enterprise verticals** [projected] | ~**$51B/yr** US labor recovery across prior auth / documentation / care coordination; **68% to female-majority occupations** | Computed as (annual US volume × AI-assumed time-saving × BLS wage). Claude performed *one representative task per vertical* at rubric-pass quality; the rest is arithmetic on published volume and time-saving parameters. Not a measured recovery. Sensitivity: halving time-savings halves the estimate. |
| **Condition library (direct)** [projected] | $12–73B aggregate across 5 conditions; **42% female-accruing** | Cascade model × published prevalence + wage parameters. Scenario estimates (observed / median / frontier). Claude's role: bottleneck classifier only. |
| **Condition library (+ indirect)** [projected] | $77B total; 48% female-accruing | Direct + presenteeism + unpaid caregiving + bias-tax. The **sign-change (42% → 48%)** is the methodological finding; absolute numbers are sensitive to the indirect-channel parameter choices. |
| **Workplace survey US scale-up** [projected] | US-scaled labor footprint **$616–862B/yr** | Measured per-respondent days lost × BLS wage × US female labor force, extrapolated from a convenience sample. Upper-bound illustrative; sensitivity to wage assumption is large. |

---

## Verily / JAMA framing

The architectural question the portfolio answers empirically:

> Anthropic has bet on single-model safety via Constitutional AI and calibrated uncertainty. A 2025 JAMA randomized trial of 21 frontier LLMs reported 90–100% differential-diagnosis failure rates despite 81–90% answer-level accuracy. Verily's response: safety requires clinical decomposition — specialized agents with structured handoffs, not bigger monolithic models. The Contested Consensus Study ([findings/04_architectural_test/](findings/04_architectural_test/)) is the direct pilot test of Anthropic's bet on the type of clinical uncertainty the Verily critique targets.

The 3% premature-collapse rate is the quantitative answer.

---

## Execution summary

| | |
|---|---|
| Model | claude-opus-4-7 |
| Pilots | 7 ([src/pilot_*.py](src/)) |
| Analyzers | 8 ([src/analyze_*.py](src/)) |
| Findings memos | 10 across 6 themes |
| Raw API outputs | committed under [`data/results/`](data/results/) |

---

## How to reproduce

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# edit .env: ANTHROPIC_API_KEY=sk-ant-...

# 3. Run any pilot
python3 src/pilot_observed_exposure.py
python3 src/pilot_sex_counterfactual.py
python3 src/pilot_condition_library.py
python3 src/pilot_enterprise_verticals.py
python3 src/pilot_enterprise_prior_auth_agreement.py
python3 src/pilot_contested_consensus.py
python3 src/pilot_patient_ehr_queries.py

# 4. Analyze (runs on the JSON the pilot saved)
python3 src/analyze_condition_library.py
# etc.

# 5. Delete the API key from console.anthropic.com/settings/keys after the run
```

No protected health information is used in any pilot. All clinical scenarios are expert-constructed from published guidelines (ESHRE, AHA/ACC, ACP, ADA, ACR, ACOG).

---

## Author

Oriana Kraft · [femtechnology.org](https://femtechnology.org)

---

## License

MIT
