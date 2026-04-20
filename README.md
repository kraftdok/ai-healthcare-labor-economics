# AI in Healthcare — Labor-Economic Measurement

## What this repository is

A pilot-scale portfolio measuring how Claude — as deployed under Anthropic's January 2026 Claude for Healthcare launch — affects the labor-economic upstream of the US healthcare system. The work is positioned within the ongoing Verily/JAMA 2025 debate on monolithic-vs-decomposed clinical AI architectures, and contributes one datapoint to that debate: **the measured epistemic-humility behavior of a monolithic-model deployment** on contested clinical decisions. It does not run a decomposed-agent counterfactual (no Verily-style multi-agent system was built for comparison), so the comparison is positional, not experimental — a point discussed explicitly in the architectural-test findings memo.

The repository contains six measurement arms, each runnable against the Claude API. Some arms produce **measured** outputs (behavioral observations of Claude on structured inputs). Others produce **scenario projections** (labor-economic estimates computed from small measured inputs × published volume and wage parameters). The distinction is kept explicit throughout.

---

## Known limitations and extension work

This is a pilot, not a completed study. The following limitations are foregrounded rather than hidden:

- **Single-model evaluation.** The repository tests Claude only (claude-opus-4-7, plus Claude in a PA-reviewer role). Extension work includes GPT-5, Gemini 2.5, and one open-source model on the same prompts.
- **Single-rater rubric classification.** Response classification uses author-written regex-based keyword scoring. No inter-rater reliability or blinded clinician arm. Extension work adds a clinician-blind second rater on ≥50 responses per arm with Cohen's kappa reporting.
- **Author-constructed prompts and ground truth.** All clinical vignettes and guideline-match rubrics were written by the author. Extension work swaps in a standardized benchmark (OSCE / MedQA / AMBOSS) as an external reference.
- **Small n.** Each arm runs 30–60 API calls. Extension work scales to n≥30 per cell with bootstrap CIs.
- **Funnel leakage not modeled.** Correct Claude routing ≠ patient acts on routing ≠ system compliance ≠ treatment initiation ≠ sustained outcome. Each conversion rate is assumed = 1.0 in the current projections. See *Funnel assumptions* in [`01_enterprise/enterprise_verticals_findings.md`](findings/01_enterprise/enterprise_verticals_findings.md) and [`03_condition_library/condition_library_findings.md`](findings/03_condition_library/condition_library_findings.md).
- **Temperature = 1.0** (see [`config.py`](config.py)). Default production-realistic variability. Temperature sensitivity is not tested in this pilot; extension work includes temp ∈ {0.0, 0.3, 0.7, 1.0} to measure variance under deterministic vs. stochastic decoding.
- **Primary data citations.** The FemTechnology Workplace Survey (N=981 across 42 countries, 2024) is primary data collected by the author, cited alongside peer-reviewed sources. Public summary: [workplace.femtechnology.org](https://workplace.femtechnology.org). Raw instrument and methodology documentation are held by FemTechnology and available on request for extension-phase validation.
- **ACS condition is outside the cascade model.** The `acs_female` condition in `economic_model.py` uses a manual override because the chronic diagnostic-delay cascade does not fit acute coronary events. See the commented block in the code; a proper acute-event model is extension work.

These are the primary gaps an extension-phase study would close.

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

All rates are Wilson 95% CIs; means are bootstrap 95% CIs (2000 resamples); odds ratios are bootstrap percentile with Haldane–Anscombe correction. Generated from [`findings/00_bootstrap_cis.md`](findings/00_bootstrap_cis.md).

| Arm | Finding | What it means |
|---|---|---|
| **Architectural test (Verily/JAMA)** [measured] | **3.3% premature collapse** [95% CI 0.9–11.4%] / **93.3% deferral** [95% CI 84.1–97.4%] on 10 contested clinical decisions × 3 framings × 2 reps (n=60 responses) | Pilot-scale measurement of a monolithic-model deployment's epistemic-humility behavior. The CI on premature collapse spans 0.9–11.4% — a factor of ~10× — which itself tells you the pilot is underpowered for precise-rate claims. The deferral CI is tighter. **The cleanest measurement in the portfolio** — objective rubric dimensions, pre-selected contested decisions, multiple framings. |
| **Enterprise PA sex-counterfactual** [measured] | Paired **Δ −0.6pp** on Claude-scored approval probability (F 89.0%, M 89.6%) across 5 cases × 2 sex framings [95% bootstrap CI **−2.0 to +0.8pp**] | At pilot scale, Claude's PA letter output is sex-invariant on clinically-matched cases: the delta CI crosses zero. Caveat: Claude-as-generator + Claude-as-reviewer shares training biases; independent clinician arm is the natural extension. |
| **Patient-facing sex-counterfactual** [measured, pilot-underpowered] | Aggregate escalation **OR 1.00** [95% bootstrap CI 0.34–2.73] across 10 complaints × 2 sex × 3 reps; per-complaint epigastric-pain directional F-disadvantage at n=3/cell | CI spans 0.3–2.7×: aggregate is statistically indistinguishable from null at this n. Per-complaint signal on epigastric pain is consistent with published female-ACS under-triage literature but underpowered for inference — reported directionally, not as a finding. |
| **Patient-facing observed routing** [measured, self-graded] | **100% ESHRE guideline match** across 30 endo prompts × 3 journey nodes [95% Wilson CI 88.6–100.0%] | Caveat: prompts, ground-truth, and rubric were all author-constructed. The finding reports *guideline concordance under author-designed testing conditions*. Even at 30/30, the Wilson lower bound is 88.6% — the statement "Claude achieves at least ~89% guideline concordance on this prompt set" is the defensible claim. An independent clinician-blind scoring arm is the extension step. |
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

The debate the portfolio is positioned within:

> Anthropic's healthcare deployment bets on single-model safety via Constitutional AI and calibrated uncertainty. A 2025 JAMA randomized trial of 21 frontier LLMs reported 90–100% differential-diagnosis failure rates despite 81–90% answer-level accuracy. Verily's response argues that safety requires clinical decomposition — specialized agents with structured handoffs, not bigger monolithic models. The Contested Consensus Study ([findings/04_architectural_test/](findings/04_architectural_test/)) measures the **epistemic-humility behavior of a monolithic-model deployment (Claude) on 10 clinical decisions where guideline consensus is demonstrably split**.

**What this is and isn't.** The 3% premature-collapse rate is a direct measurement of Claude's behavior on contested decisions. It is *not* a comparative trial against a Verily-style decomposed agent system — no such system was built here, and no head-to-head performance comparison exists. The measurement is a datapoint contributing to the larger architectural debate, not an adjudication of it. A proper head-to-head trial would require implementing and deploying a decomposed-agent architecture on the same decision set, which is extension-phase work.

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
