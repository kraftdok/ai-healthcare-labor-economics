# AI in Healthcare — Labor-Economic Measurement

## What this repository is

An empirical portfolio measuring how Claude — as deployed under Anthropic's January 2026 Claude for Healthcare launch — affects the labor-economic upstream of the US healthcare system. The work tests the architectural bet Anthropic has made (monolithic-model safety via Constitutional AI and calibrated uncertainty) against the decomposed-agent critique raised in JAMA 2025 and by Verily's Violet product team.

The repository contains six measurement arms, each runnable against the Claude API.

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

| Arm | Finding | What it means |
|---|---|---|
| **Enterprise verticals** | ~$51B/yr recovery across prior auth / documentation / care coordination; **68% accrues to female labor** | Anthropic's enterprise deployment is disproportionately recovering labor value performed by a female-majority workforce (medical billers, nurses, care coordinators). |
| **Enterprise PA sex-counterfactual** | Δ **−0.6pp** on approval probability (F 89.0%, M 89.6%) | At pilot scale, Claude's PA letter output is sex-invariant on clinically-matched cases. Positive signal for the monolithic-model bet at the administrative layer. |
| **Patient-facing observed routing** | **100% ESHRE guideline match** across 30 endo prompts × 3 journey nodes | Claude is substantially better than the current real-world pathway (6.7yr delay) at the point of direct clinical routing. |
| **Patient-facing counterfactual** | Aggregate **OR 1.00** (95% CI 0.34–2.93); epigastric pain directional **67-pt F-disadvantage** (n=3/cell) | Null at aggregate; directional per-complaint signal consistent with published female-ACS under-triage literature. |
| **Architectural test (Verily/JAMA)** | **3% premature collapse / 93% deferral** on contested decisions | Claude passes the epistemic-humility test the JAMA critique raises — at the cost of near-total deferral when evidence is genuinely split. |
| **Condition library (direct)** | $12–73B aggregate recovery across 5 conditions; 42% female-accruing | Labor-economic methodology generalizes across MSK, post-MI, MDD, endo, Alzheimer's caregiving. |
| **Condition library (+ indirect)** | $77B total; 48% female-accruing | Recomputation with presenteeism, caregiving, and bias-tax channels. Valuation choice is not neutral. |
| **Workplace survey (n=981, 42 countries)** | 62% time-off rate; US-scaled labor footprint **$616–862B/yr** | Independent triangulation of the Q1 magnitude claim using primary cross-country data. |

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
| Logs | auditable in `data/results/` (gitignored) |

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
