"""
Analyze enterprise prior-auth agreement pilot.

Does Claude's prior-auth letter quality depend on clinically-irrelevant
patient-sex labeling? Using Claude-as-reviewer in a blinded capacity to score
20 PA letters (5 cases × 2 sexes × 2 roles).
"""
import json
import csv
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results"
OUT = Path(__file__).resolve().parent.parent / "findings" / "01_enterprise"


def latest():
    files = sorted(RESULTS.glob("enterprise_pa_agreement_*.json"))
    return files[-1]


DIMS = [
    "clinical_justification",
    "guideline_citation_specificity",
    "completeness_of_clinical_info",
    "appropriate_language_tone",
    "likely_approval_probability_pct",
]


def main():
    data = json.loads(latest().read_text())

    # Group by sex
    by_sex = defaultdict(list)
    for r in data:
        by_sex[r["sex"]].append(r)

    def mean(lst):
        return sum(lst) / len(lst) if lst else 0

    summary_by_sex = {}
    for sex, rs in by_sex.items():
        by_dim = {}
        for d in DIMS:
            vals = []
            for r in rs:
                v = r["review"].get(d)
                if isinstance(v, (int, float)):
                    vals.append(v)
            by_dim[d] = {"mean": mean(vals), "n": len(vals)}
        summary_by_sex[sex] = by_dim

    # Per-case sex delta
    by_case = defaultdict(lambda: {"female": {}, "male": {}})
    for r in data:
        cid = r["case"]["id"]
        by_case[cid][r["sex"]] = r["review"]

    case_deltas = {}
    for cid, cs in by_case.items():
        deltas = {}
        for d in DIMS:
            f_val = cs["female"].get(d) if isinstance(cs["female"].get(d), (int, float)) else None
            m_val = cs["male"].get(d) if isinstance(cs["male"].get(d), (int, float)) else None
            if f_val is not None and m_val is not None:
                deltas[d] = f_val - m_val
        case_deltas[cid] = deltas

    # CSV
    with (OUT / "enterprise_pa_agreement_table.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dimension", "female_mean", "male_mean", "female_minus_male"])
        for d in DIMS:
            f_val = summary_by_sex.get("female", {}).get(d, {}).get("mean", 0)
            m_val = summary_by_sex.get("male", {}).get(d, {}).get("mean", 0)
            w.writerow([d, f"{f_val:.2f}", f"{m_val:.2f}", f"{f_val - m_val:+.2f}"])

    # Figure — grouped bars
    fig, ax = plt.subplots(figsize=(10, 5))
    display_labels = {
        "clinical_justification": "Clinical\njustification (/5)",
        "guideline_citation_specificity": "Guideline\ncitation (/5)",
        "completeness_of_clinical_info": "Completeness\n(/5)",
        "appropriate_language_tone": "Tone\n(/5)",
        "likely_approval_probability_pct": "Approval\nprobability (%)",
    }
    female_vals = [summary_by_sex.get("female", {}).get(d, {}).get("mean", 0) for d in DIMS]
    male_vals = [summary_by_sex.get("male", {}).get(d, {}).get("mean", 0) for d in DIMS]
    # Rescale approval probability to /5 for visualization
    female_vals_disp = [v if d != "likely_approval_probability_pct" else v / 20 for v, d in zip(female_vals, DIMS)]
    male_vals_disp = [v if d != "likely_approval_probability_pct" else v / 20 for v, d in zip(male_vals, DIMS)]
    x = range(len(DIMS))
    w = 0.38
    ax.bar([i - w/2 for i in x], female_vals_disp, w, label="Female", color="#d62728")
    ax.bar([i + w/2 for i in x], male_vals_disp, w, label="Male", color="#1f77b4")
    ax.set_xticks(list(x))
    ax.set_xticklabels([display_labels[d] for d in DIMS], fontsize=9)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Score (approval probability rescaled /20)")
    ax.set_title("PA letter quality by patient sex — Claude as generator and blinded reviewer")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "enterprise_pa_agreement_figure.png", dpi=140)
    plt.close()

    # Memo
    f_ap = summary_by_sex.get("female", {}).get("likely_approval_probability_pct", {}).get("mean", 0)
    m_ap = summary_by_sex.get("male", {}).get("likely_approval_probability_pct", {}).get("mean", 0)
    overall_ap = (f_ap + m_ap) / 2

    lines = [
        "# Enterprise Prior-Auth Agreement Pilot — Does Claude's Output Quality Depend on Patient Sex?",
        "",
        "*Reflexive measurement at the administrative-AI layer: Claude generates a prior-auth letter for each of 5 cases across both sexes, then Claude in a blinded medical-reviewer role scores each letter on 5 dimensions.*",
        "",
        f"**Author:** Oriana Kraft | **Date:** {datetime.now().strftime('%Y-%m-%d')} | **Model:** claude-opus-4-7 | **Sample:** {len(data)} letters (5 cases × 2 sex framings × 2 roles)",
        "",
        "## Why this artifact",
        "",
        "The enterprise-vertical artifact [`enterprise_verticals_findings.md`] estimated ~$51B/yr labor recovery across Claude for Healthcare's three deployment verticals. But that estimate assumed the labor saved is fungible — i.e., that Claude-generated administrative documents are equivalent in quality regardless of patient. The Verily / JAMA 2025 architectural critique raises a sharper question: does clinically-irrelevant patient information (like sex) change the quality of Claude's administrative output? If yes, the labor-recovery estimate needs to be qualified by a quality-distribution, not just a time-saving.",
        "",
        "This pilot tests that question directly on the prior-auth vertical, which Anthropic's January 2026 launch named as a flagship deployment use case.",
        "",
        "## Method",
        "",
        "Five clinical cases with genuinely-supported PA indications (cardiac rehab post-MI, GLP-1 for T2DM+obesity, biologic DMARD for RA, MRI for new neurologic symptoms, CGM for insulin-dependent DM). Each case was run through Claude Opus 4.7 with two patient framings identical in all clinical content except sex (female vs male, age 62 in all cases). Claude then scored each generated letter in a blinded reviewer role, on five dimensions: clinical justification (0-5), guideline citation specificity (0-5), completeness of clinical information (0-5), appropriate language/tone (0-5), and likely approval probability (0-100%).",
        "",
        "## Top-line: sex-asymmetry in Claude's administrative output",
        "",
        "| Dimension | Female-labeled (mean) | Male-labeled (mean) | Δ (F − M) |",
        "|---|---|---|---|",
    ]
    for d in DIMS:
        f_val = summary_by_sex.get("female", {}).get(d, {}).get("mean", 0)
        m_val = summary_by_sex.get("male", {}).get(d, {}).get("mean", 0)
        delta = f_val - m_val
        unit = " pp" if d == "likely_approval_probability_pct" else " /5"
        lines.append(f"| {d.replace('_', ' ')} | {f_val:.2f}{unit} | {m_val:.2f}{unit} | {delta:+.2f}{unit} |")

    lines += [
        "",
        f"**The headline quantity: estimated approval probability.** Female-labeled letters scored {f_ap:.0f}% vs male-labeled {m_ap:.0f}% (Δ {f_ap - m_ap:+.0f} percentage points). This is **Claude evaluating Claude's own output blindly on quality**, with patient-sex as the only controlled variable.",
        "",
        "## Per-case breakdown — where the Δ concentrates",
        "",
        "| Case | Δ clinical justification | Δ guideline specificity | Δ completeness | Δ tone | Δ approval probability |",
        "|---|---|---|---|---|---|",
    ]
    for cid, deltas in case_deltas.items():
        row = [cid]
        for d in DIMS:
            v = deltas.get(d, 0)
            unit = "pp" if d == "likely_approval_probability_pct" else ""
            row.append(f"{v:+.1f}{unit}")
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        "## What this says about the enterprise-vertical $51B estimate",
        "",
        "The [`enterprise_verticals_findings.md`] artifact estimated $51B/yr US labor recovery across the three Claude for Healthcare verticals, of which ~$12B was from prior authorization specifically. That estimate assumed output-quality invariance. This pilot shows pilot-scale evidence of sex-distributed quality differences at the PA-letter layer. Three interpretations worth weighing:",
        "",
        "1. **The effect is small and within noise** — n=10 per sex, single-rater (Claude as reviewer), no blinded human validation. Treat as a pilot signal, not a finding.",
        "2. **The effect is real and compounds downstream** — if approval probabilities for identical clinical cases differ by sex, the realized labor-recovery distribution is skewed, and Anthropic's deployment is reproducing the same administrative bias pattern documented in human prior-auth review.",
        "3. **The reflexive-measurement method (Claude rating Claude) has its own bias** — if Claude's generation and review are both trained on similar data, agreement between them may not reflect objective quality. Extension-phase work would include blinded human reviewer arm (clinicians or industry medical reviewers).",
        "",
        "## Verily / JAMA frame",
        "",
        "Verily's argument — that monolithic models produce opaque reasoning and fail to surface uncertainty — extends naturally to the administrative layer. If Claude-generated PA letters differ in quality by patient sex, the mechanism is probably opacity at the training-data level: the documents in Claude's training corpus reflect whatever sex-biased patterns exist in historical PA drafting. A decomposed-agent architecture (as Verily proposes) would have specialized agents whose behavior on patient-sex inputs could be audited independently. A monolithic architecture (Anthropic's bet) relies on the single model's own Constitutional-AI behavior to correct upstream data patterns. This pilot is the minimal empirical test of that bet at the administrative layer.",
        "",
        "## Limitations",
        "",
        "- n=5 cases × 2 sexes × 2 roles = 20 letters total. Pilot scale only.",
        "- Claude-as-reviewer is single-rater and may share training biases with Claude-as-generator.",
        "- No clinician arm or blinded human validation; extension work required.",
        "- Approval-probability is Claude's estimate, not a real payer decision.",
        "",
        "---",
        "",
        "*Code: `src/pilot_enterprise_prior_auth_agreement.py` + `analysis/analyze_enterprise_pa_agreement.py`. Raw: `data/results/enterprise_pa_agreement_<timestamp>.json`.*",
    ]

    (OUT / "enterprise_pa_agreement_findings.md").write_text("\n".join(lines))
    print(f"Wrote: {OUT/'enterprise_pa_agreement_findings.md'}")
    print(f"Wrote: {OUT/'enterprise_pa_agreement_table.csv'}")
    print(f"Wrote: {OUT/'enterprise_pa_agreement_figure.png'}")
    print(f"Avg approval F: {f_ap:.1f}% | M: {m_ap:.1f}% | Δ: {f_ap - m_ap:+.1f}pp")


if __name__ == "__main__":
    main()
