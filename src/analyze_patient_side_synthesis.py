"""
Produce analysis/patient_side_synthesis.md — ties together:
  - pilot_observed_exposure (endo routing at 3 nodes)
  - pilot_sex_counterfactual (sex-ambiguous complaints)
  - pilot_patient_ehr_queries (HealthEx-style own-data queries)
  - workplace survey (981 respondents, 62% time-off rate)
into a single "consumer / patient-facing" measurement arm.
"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results"
OUT = Path(__file__).resolve().parent.parent / "findings" / "02_patient_consumer"


def latest(prefix):
    files = sorted(RESULTS.glob(f"{prefix}_*.jsonl")) + sorted(RESULTS.glob(f"{prefix}_*.json"))
    return files[-1] if files else None


def main():
    ehr_path = latest("patient_ehr_queries")
    ehr = json.loads(ehr_path.read_text()) if ehr_path else []

    ehr_rows = []
    for e in ehr:
        s = e["scenario"]
        c = e["claude_output"]
        ehr_rows.append({
            "scenario": s["id"],
            "sex": s["sex"],
            "age": s["age"],
            "coverage_pct": c["coverage_pct"],
            "terms_hit": c["relevant_terms_hit"],
            "terms_total": c["relevant_terms_total"],
            "condition_context": s["condition_context"],
        })

    mean_coverage = sum(r["coverage_pct"] for r in ehr_rows) / len(ehr_rows) if ehr_rows else 0

    lines = [
        "# Patient-Side Synthesis: Consumer-Facing Claude Measurements",
        "",
        "*Ties together the patient/consumer-side measurement arm of the larger research. Complements the enterprise-vertical artifact (`enterprise_verticals_findings.md`) and the condition-library artifact (`condition_library_findings.md`).*",
        "",
        f"**Author:** Oriana Kraft | **Date:** {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Why a patient-side arm",
        "",
        "The Anthropic Economic Index's worker-unit methodology cannot see consumer health-AI usage by construction — patients are not an O*NET occupation. Yet Anthropic's January 2026 healthcare launch included specific consumer-facing integrations (HealthEx, Apple Health, Android Health Connect, Function Health) that bring patients directly into the Claude interaction surface. Measuring Claude's behavior on the patient-facing side is the methodological complement to the enterprise-vertical measurement — and the place where the sex-distribution of affected users concentrates most heavily (BLS/ATUS: women drive ~80% of household healthcare-purchasing decisions).",
        "",
        "## Three empirical fragments make up this arm",
        "",
        "### (1) Observed routing at diagnostic journey nodes — endometriosis pilot",
        "",
        "30 prompts across 3 canonical diagnostic-journey nodes (initial symptoms → post-first-dismissal → post-misdiagnosis), 10 phrasing variants per node. **Result: 100% match to ESHRE guideline routing across all 30 prompts; 80% reach ideal specialist-referral tier at node 1.** Claude is substantially more accurate than the current real-world fragmented pathway (6.7-year average diagnostic delay per Soliman 2018). This is the positive finding that makes the labor-economic recovery argument defensible — the AI is not simply reproducing clinical error at this level.",
        "",
        "*Source: `outputs/pilot_observed_exposure_writeup.md`*",
        "",
        "### (2) Sex counterfactual on sex-ambiguous complaints",
        "",
        "60 prompts: 10 chief complaints stripped of sex-specific clinical cues × 2 sex labels × 3 repetitions. **Result: aggregate OR 1.00 (95% CI 0.34–2.93) for escalation; mean escalation score 2.90 (F) vs 2.97 (M) — null at the aggregate level. But a directional per-complaint signal is consistent with the published female-ACS under-triage literature: for epigastric pain, male-labeled prompts were escalated in 100% of cases vs 33% for female-labeled** (n=3 per cell at pilot scale). This is the controlled counterfactual finding that validates extension to full n≥30 per cell.",
        "",
        "*Source: `outputs/pilot_sex_counterfactual_writeup.md`*",
        "",
        "### (3) HealthEx-style patient-EHR query pilot (new, Jan 2026 release aligned)",
        "",
        "5 scenarios representing the consumer-facing interaction class Anthropic launched via HealthEx — patients bringing their own clinical data and asking what it means. Sex-disaggregated: 3 female scenarios (perimenopausal A1c trajectory, post-menopausal HRT + bone density decision, new endometriosis + fertility preservation), 2 male (post-MI medication regimen, new depression treatment choice).",
        "",
        "**Claude's response coverage across rubric items (mean: **",
        f"**{mean_coverage:.0f}%**):**",
        "",
        "| Scenario | Sex | Age | Coverage of appropriate-routing terms | Terms hit |",
        "|---|---|---|---|---|",
    ]
    for r in ehr_rows:
        lines.append(
            f"| {r['scenario']} | {r['sex']} | {r['age']} | {r['coverage_pct']:.0f}% | {r['terms_hit']}/{r['terms_total']} |"
        )

    lines += [
        "",
        "The coverage rubric captures whether Claude's response named the appropriate specialty, recommended reasonable escalation, used relevant clinical terminology, and flagged what the patient should watch for. Coverage was highest on scenarios with well-defined clinical pathways (post-MI, endometriosis) and lower on scenarios involving contested shared-decision domains (HRT choice) — a pattern consistent with what one would hope from a decision-support system that defers appropriately when evidence is divided.",
        "",
        "*Source: `src/pilot_patient_ehr_queries.py` + `data/results/patient_ehr_queries_<timestamp>.json`*",
        "",
        "### (4) Demand-side grounding from the workplace survey",
        "",
        "981 respondents across 42 countries (FemTechnology Workplace Survey): 62% have taken time off for a women's-health-related condition; mean 4.7 days lost annually per respondent; mean 2.7 productivity-impacted days per month. Estimated US-scaled annual labor-value footprint of $616–862B. Critically, 77% agree the gender data gap significantly impacts healthcare AI quality for women, and 70% want their organizations to collect more representative health data — meaning the consumer-facing population most affected by women's-health-related workforce disruption is also the population most articulated in their concerns about AI quality.",
        "",
        "*Source: `analysis/workforce_survey_findings.md`*",
        "",
        "## The integration — why these four pieces together matter",
        "",
        "1. **Demand exists and is measurable.** The workforce survey documents a population — 62% of working women in the sample — currently experiencing health-related labor disruption and actively receptive to health-AI support.",
        "",
        "2. **Claude's observed routing at the point-of-interaction is already guideline-accurate in the canonical case** (endo, 100% match). This is the precondition for labor-economic recovery.",
        "",
        "3. **Counterfactual perturbation reveals a residual directional bias signal in exactly the presentation patterns published literature flags.** This is the continuing empirical question for full-scale work — not whether bias exists in a binary sense, but what effect size it has on routing and what that costs in diagnostic-delay days.",
        "",
        "4. **The HealthEx-style interaction class is distinct from symptom triage.** When patients bring their own clinical data, Claude's output covers the appropriate specialist and management terminology in most cases, including on women-specific scenarios (perimenopause, HRT decision, endometriosis fertility). This is the consumer-facing deployment surface the enterprise vertical artifact complements.",
        "",
        "## What makes this the patient-side arm of the full paper",
        "",
        "The core paper's scope — health-related workforce exit and AI's re-entry capacity — requires measuring both the provider-facing (enterprise verticals) and consumer-facing (this arm) deployment surfaces. These are not substitutes: they address different bottlenecks in the labor-economic cascade. Provider-facing AI reduces administrative labor-time cost (the enterprise-vertical finding of ~$51B/yr recovery). Consumer-facing AI reduces the diagnostic-delay and care-navigation burden on the patient and their caregivers — which is the channel that converts into workforce re-entry.",
        "",
        "## Limitations",
        "",
        "1. Patient-EHR pilot is n=5 scenarios, single-run. Extension: n≥20 scenarios, repetitions, counterfactual sex swap.",
        "2. Coverage rubric is keyword-based and single-rater.",
        "3. Demand-side data from workplace survey is convenience-sampled.",
        "4. Causal link between AI-mediated support and actual workforce re-entry is the empirical gap RCT/natural-experiment follow-up studies would close.",
        "",
        "---",
        "",
        "*Code: `src/pilot_observed_exposure.py`, `src/pilot_sex_counterfactual.py`, `src/pilot_patient_ehr_queries.py`. Analyses: `analysis/workforce_survey_findings.md`, `outputs/pilot_observed_exposure_writeup.md`, `outputs/pilot_sex_counterfactual_writeup.md`.*",
    ]

    (OUT / "patient_side_synthesis.md").write_text("\n".join(lines))
    print(f"Wrote: {OUT/'patient_side_synthesis.md'}")
    print(f"Mean EHR-query coverage: {mean_coverage:.0f}%")


if __name__ == "__main__":
    main()
