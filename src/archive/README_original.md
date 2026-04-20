# AI Pathway Economics

**Does AI compress or extend the diagnostic journey — and what is the economic cost either way?**

People are already using AI for healthcare questions. This study measures the economic consequences of that usage by testing where AI routes patients at each stage of the diagnostic journey, then modeling the downstream cascade: diagnosis timing → treatment cost → work capacity → disability onset → lifetime economic output.

## The Question

When AI becomes the first triage point for patients navigating broken healthcare pathways, three things can happen:

1. **AI compresses the journey** — Patient gets to correct diagnosis faster. Years of productive work restored. Healthcare spending reduced. GDP impact positive.
2. **AI reproduces the journey** — Patient gets the same IBS diagnosis, the same "it's just stress," at scale. No improvement. Same economic drain.
3. **AI extends the journey** — Patient is reassured by AI instead of seeking care. Diagnosis delayed further. Economic damage worse than status quo.

**Nobody has measured which one is happening.** This study does.

## What Makes This Different

This is not a model bias study. It is a **labor economics study** that uses clinical pathways as the measurement instrument.

| What most studies measure | What this study measures |
|---|---|
| Does AI give biased medical advice? | How does AI change the *economic trajectory* of workers navigating the healthcare system? |
| Model behavior (single interaction) | System behavior (full patient journey, node by node) |
| Clinical accuracy | Diagnostic delay → treatment cost → work capacity → disability → pension → GDP |

## Study Design

### 1. Pathway Comparison (11 prompts, ~$0.50)

For each condition, test AI at **each stage of the diagnostic journey**:

```
Node 1: Initial symptoms       → Where does AI route the patient?
Node 2: After first dismissal  → Does AI catch what the doctor missed?
Node 3: After misdiagnosis     → Does AI challenge the wrong diagnosis?
Node 4: Years into the odyssey → Does AI finally identify the pattern?
```

Then overlay the AI-mediated pathway against two baselines:

| Pathway | Source | Example (Endometriosis) |
|---|---|---|
| **Fragmented** (current system) | Published claims data | 6.7 years, 3.7 doctors, $21,370 |
| **Integrated** (guideline-based) | Clinical guidelines | 1.5 years, 2 doctors, $8,050 |
| **AI-Mediated** (this study) | Claude API responses | ? years, measured empirically |

### 2. Economic Cascade Model

For each routing decision, compute the full downstream cascade:

```
Diagnosis acceleration (years saved)
  → Healthcare cost saved (excess annual cost × years)
  → Work days restored (absenteeism × years)
  → Presenteeism recovered (reduced output while working)
  → Employer absence savings (replacement + lost output)
  → Disability deferral (SSDI onset deferred by N years)
  → Pension system savings (fewer years on benefits)
  → TOTAL: Per-patient lifetime economic value
  → POPULATION: Affected population × per-patient value
```

### 3. Demographic Bias Stress Test (~$2)

Test whether AI routes patients differently based on:

| Axis | Variants |
|---|---|
| **Insurance / SES** | PPO (professional) → Employer HMO → Medicaid (shift work) |
| **Health literacy** | Clinical vocabulary → Standard → Colloquial / low-literacy |
| **Emotional presentation** | Stoic/matter-of-fact → Neutral → Anxious/emotional |

If Claude suggests a specialist referral for the PPO patient but "try ibuprofen" for the Medicaid patient — that's measurable algorithmic replication of the health equity gap, with a dollar value attached.

## Conditions Studied

| Condition | Journey Nodes | Diagnostic Delay | Healthcare Excess | Productivity Loss |
|---|---|---|---|---|
| Endometriosis | 4 nodes | 6.7 years | $10,002/yr | 45.6 days/yr |
| Fibromyalgia | 3 nodes | 5.0 years | $6,282/yr | 50.4 days/yr |
| GDM → Type 2 Diabetes | 2 nodes | 5-7 years | $16,752/yr | 27.6 days/yr |
| ACS (Female Presentation) | 2 nodes | Hours (acute) | $20,000 per event | 45 days/event |

## Quick Start

```bash
# Clone and install
git clone https://github.com/kraftdok/ai-pathway-economics.git
cd ai-pathway-economics
pip install -r requirements.txt

# Set API key (get free $5 credits at console.anthropic.com)
cp .env.example .env
# Edit .env: ANTHROPIC_API_KEY=sk-ant-...

# Preview all prompts (no API calls, free)
python3 src/run_pathway_study.py --dry-run

# Run pathway study (11 calls, ~$0.50)
python3 src/run_pathway_study.py

# Run demographic bias test (81 calls, ~$2)
python3 src/bias_stress_test.py

# Or test a single condition
python3 src/run_pathway_study.py --condition endo
python3 src/bias_stress_test.py --condition endo --node 1

# View economic cascades (no API needed)
python3 economic_model.py
```

## Repository Structure

```
ai-pathway-economics/
├── README.md
├── requirements.txt
├── config.py                       # API keys, model config
├── pathways.py                     # Node-by-node patient journey definitions
├── economic_model.py               # Cascade: diagnosis → work capacity → GDP
├── conditions.py                   # Additional conditions (voice divergence study)
├── .env.example
├── src/
│   ├── run_pathway_study.py       # Test AI at each journey node
│   ├── bias_stress_test.py        # Demographic perturbation testing
│   ├── run_study.py               # Voice divergence experiment (supplementary)
│   ├── score.py                   # Score responses against ground truth
│   └── analyze.py                 # Analysis + economic impact
├── data/
│   └── results/                   # Raw API responses (gitignored)
└── outputs/
    ├── pathway_comparison_report.md
    ├── bias_test_report.md
    └── study_report.md
```

## Economic Model Output

Running `python3 economic_model.py` produces per-condition economic cascades:

```
=================================================================
ECONOMIC CASCADE: Endometriosis
Diagnosis accelerated by 5.2 years
=================================================================

  PER PATIENT:
    Healthcare saved:           $    52,010
    Work days restored:                237 days
    Earnings restored:          $    56,454
    Presenteeism recovered:     $    22,581
    Employer absence savings:   $    91,291
    Disability deferral value:  $    26,767
    Pension system savings:     $    16,088
    ──────────────────────────────────────────────
    TOTAL PER PATIENT:          $   265,191

  POPULATION (6,500,000 affected):
    TOTAL:             $1,723,741,119,360
                       ($1,724B)
```

## Methodology Notes

**All clinical ground truth** sourced from published guidelines (ESHRE, AHA, ACR, ADA/ACOG, NAMS, DSM-5). **All cost data** sourced from peer-reviewed literature. **All economic parameters** sourced from BLS, SSA, and DOL.

This is a proof-of-concept. The following methodological enhancements are deferred to the extension phase:

- **Temporal discounting**: Apply standard health economics discount rate (3%) to convert future economic values to NPV
- **Monte Carlo simulation**: Replace point estimates with distributional parameters (e.g., diagnostic delay as normal distribution) and run probabilistic sensitivity analysis
- **Markov state transitions**: Model pathway nodes as probabilistic state transitions rather than linear sequences, capturing the loops and re-entries that characterize real diagnostic journeys
- **Clio integration**: Replace synthetic pathway testing with classification of real-world Claude healthcare conversations from Clio, measuring actual patient routing behavior at scale

## Sources

### Clinical Guidelines
- ESHRE — Endometriosis diagnosis and management guidelines
- ACR 2010/2016 — Fibromyalgia diagnostic criteria
- ADA/ACOG — GDM postpartum screening guidelines
- AHA — Sex-specific ACS presentation guidelines

### Cost Data
| Source | Used For |
|---|---|
| Soliman AM et al., *Adv Ther* 2018 | Endometriosis excess costs |
| Berger A et al., *Int J Clin Pract* 2007 | Fibromyalgia costs |
| Parker ED et al., *Diabetes Care* 2024 | T2DM economic burden |
| AHA Statistical Updates 2024 | Cardiovascular disease costs |

### Economic Parameters
| Source | Data |
|---|---|
| Bureau of Labor Statistics (BLS) 2024 | Median hourly wage ($29.76) |
| Social Security Administration (SSA) 2024 | SSDI benefit levels ($22,344/yr) |
| SHRM Employee Benefits Survey 2024 | Employer cost per absence day ($385) |

## Author

**Oriana Kraft** — Founder, FemTechnology

Built on six years of research quantifying where healthcare systems produce systematically different outcomes by sex and what those failures cost the economy: a 200-physician survey across 6 countries (with Roche/HBA), a 1,000+ woman workplace productivity survey across 42 countries, government pathway economics partnerships (California Surgeon General, Government of Andhra Pradesh), and published research across clinical, economic, AI, and workplace dimensions of the health gap.

## License

MIT
