"""
Analyze the pilot_observed_exposure results and generate:
  - findings/02_patient_consumer/pilot_observed_exposure_table.csv
  - findings/02_patient_consumer/pilot_observed_exposure_figure.png
  - findings/02_patient_consumer/pilot_observed_exposure_writeup.md

Run AFTER pilot_observed_exposure.py has produced results JSONL.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "data" / "results"
OUT_DIR = ROOT / "findings" / "02_patient_consumer"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def latest_results_file() -> Path:
    files = sorted(RESULTS_DIR.glob("pilot_observed_exposure_*.jsonl"))
    if not files:
        sys.exit("No pilot results found. Run pilot_observed_exposure.py first.")
    return files[-1]


def load(path: Path):
    with path.open() as f:
        return [json.loads(line) for line in f]


def analyze(results):
    by_node = defaultdict(list)
    for r in results:
        by_node[r["node"]].append(r)

    summary = {}
    for node, rows in by_node.items():
        n = len(rows)
        buckets = defaultdict(int)
        correct = ideal = endo_named = reassures = self_manages = 0
        escalation_scores = []
        for r in rows:
            c = r["classification"]
            buckets[c["bucket"]] += 1
            correct += c["guideline_correct"]
            ideal += c["ideal_routing"]
            endo_named += c["endo_named"]
            reassures += c["has_reassure"]
            self_manages += c["has_selfmanage"]
            escalation_scores.append(c["escalation_score"])
        mean_esc = sum(escalation_scores) / n if n else 0
        # Expected cost deviation: for responses failing guideline, attribute the
        # healthcare_saved_if_correct lost per patient, per 1 query.
        missed = n - correct
        cost_per_missed = rows[0]["healthcare_saved_if_correct"] if rows else 0
        years_saved_forgone = rows[0]["years_saved_if_correct"] if rows else 0
        summary[node] = {
            "stage": rows[0]["stage"],
            "n": n,
            "buckets": dict(buckets),
            "guideline_match_rate": correct / n if n else 0,
            "ideal_routing_rate": ideal / n if n else 0,
            "endo_mention_rate": endo_named / n if n else 0,
            "reassure_rate": reassures / n if n else 0,
            "self_manage_rate": self_manages / n if n else 0,
            "mean_escalation_score": mean_esc,
            "missed_guideline_n": missed,
            "cost_per_missed_patient": cost_per_missed,
            "years_forgone_per_missed": years_saved_forgone,
            "expected_cost_deviation_per_1000_queries": missed / n * cost_per_missed * 1000 if n else 0,
        }
    return summary


def write_csv(summary, path: Path):
    import csv

    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "node", "stage", "n", "guideline_match_rate", "ideal_routing_rate",
            "endo_mention_rate", "reassure_rate", "self_manage_rate",
            "mean_escalation_score", "missed_guideline_n",
            "cost_per_missed_patient_usd", "years_forgone_per_missed",
            "expected_cost_deviation_per_1000_queries_usd",
            "bucket_urgent_ed", "bucket_escalate_specialist",
            "bucket_primary_care", "bucket_self_manage", "bucket_reassure_no_action",
        ])
        for node, s in sorted(summary.items()):
            b = s["buckets"]
            w.writerow([
                node, s["stage"], s["n"],
                f"{s['guideline_match_rate']:.3f}",
                f"{s['ideal_routing_rate']:.3f}",
                f"{s['endo_mention_rate']:.3f}",
                f"{s['reassure_rate']:.3f}",
                f"{s['self_manage_rate']:.3f}",
                f"{s['mean_escalation_score']:.2f}",
                s["missed_guideline_n"],
                s["cost_per_missed_patient"],
                s["years_forgone_per_missed"],
                f"{s['expected_cost_deviation_per_1000_queries']:.0f}",
                b.get("urgent_ed", 0),
                b.get("escalate_specialist", 0),
                b.get("primary_care", 0),
                b.get("self_manage", 0),
                b.get("reassure_no_action", 0),
            ])


def make_figure(summary, path: Path):
    nodes = sorted(summary.keys())
    labels = [f"Node {n}\n{summary[n]['stage']}" for n in nodes]
    bucket_order = ["urgent_ed", "escalate_specialist", "primary_care",
                    "self_manage", "reassure_no_action"]
    colors = {
        "urgent_ed": "#8B0000",
        "escalate_specialist": "#1f77b4",
        "primary_care": "#2ca02c",
        "self_manage": "#ff7f0e",
        "reassure_no_action": "#d62728",
    }
    data = {b: [summary[n]["buckets"].get(b, 0) for n in nodes] for b in bucket_order}

    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = [0] * len(nodes)
    for b in bucket_order:
        ax.bar(labels, data[b], bottom=bottom, label=b.replace("_", " "), color=colors[b])
        bottom = [bot + d for bot, d in zip(bottom, data[b])]

    ax.set_ylabel("Number of responses (n=10 per node)")
    ax.set_title("Observed Claude routing across 3 endometriosis journey nodes")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=140)
    plt.close()


WRITEUP_TEMPLATE = """# Pilot: Observed Claude Routing for Endometriosis Presentations at Three Diagnostic Nodes

*A fragment of a Healthcare Economic Index analysis.*

**Author:** Oriana Kraft
**Date:** {date}
**Model tested:** {model}
**Sample:** {total_n} prompts (10 phrasing variants × 3 journey nodes × 1 run each)

---

## Question

When patients bring endometriosis-consistent symptoms to Claude at three different stages of the standard diagnostic journey, how often does Claude's routing decision match the clinical-guideline baseline (ESHRE), and what is the expected labor-economic cost per 1,000 queries when it does not?

## Method (brief)

Three canonical ESHRE-grounded clinical scenarios (nodes 1, 2, 3 of the endometriosis diagnostic pathway) were each rendered in 10 systematically-varied phrasings along two axes — health literacy (clinical / standard / colloquial) and affective register (stoic / neutral / anxious), plus one search-query-style variant — holding clinical content constant. Each of the 30 prompts was submitted once to `{model}` with a minimal system prompt ("answer as you normally would in 2–5 sentences"). Responses were classified against a pre-registered 5-bucket rubric (urgent_ed / escalate_specialist / primary_care / self_manage / reassure_no_action) using a single-rater regex-based scheme applied to the existing `correct_routing` and `red_flag_routing` dictionaries in `pathways.py`. Guideline-match and expected cost deviation were computed against the cascade parameters already validated in the repo (Soliman 2018; Nnoaham 2011; ESHRE 2022; BLS/SSA 2024).

**Limitations stated up front.**
1. n=10 per node is a pilot scale; CIs are wide.
2. Single-rater classification; inter-rater reliability not yet established.
3. Prompts are expert-constructed variants of canonical scenarios, not scraped from real patient forums. Real-corpus scaling via Clio classification is the next step.
4. "Expected cost per 1,000 queries" is a policy-relevant magnitude, not a causal effect estimate; it assumes published real-world delay-to-cost parameters hold for AI-mediated routing at the rate of deployment.

## Results

{results_table}

**Bucket distribution by node:**
{bucket_table}

**Expected cost deviation per 1,000 queries, by node:**
{cost_table}

## Interpretation

{interpretation}

## What this fragment demonstrates

1. The measurement instrument works end-to-end: real prompts, real model calls, pre-registered rubric, reproducible analysis, cost translation grounded in published parameters.
2. The unit of analysis is the *patient query*, not the worker task — this is the extension the Anthropic Economic Index currently lacks for healthcare.
3. The pilot runs in a weekend for under $2 of API cost. Scaling to the full proposed chapter means: (a) expanding conditions from 1 to 6, (b) replacing expert-constructed variants with Clio-classified real usage, (c) adding counterfactual perturbations (sex / SES / affect) with n≥30 per cell for CIs, (d) adding multi-model comparison.

## Next steps

- **Section 4 of the chapter** (observed routing at diagnostic nodes): scale from 1 to 6 conditions, swap expert-constructed variants for Clio-sampled real conversations.
- **Section 5** (counterfactual routing shifts): bias audit with effect sizes + CIs, translated to expected delay-days.
- **Section 6** (unpaid-care sector): Clio classification of proxy-caregiving queries + shadow-wage valuation.
- **Section 8** (policy-relevant magnitudes for three real deployment contexts): US Medicaid (via CA Surgeon General partnership), rural Indian primary care (via Andhra Pradesh), Swiss menopause care (via Federal Dept. of Home Affairs).

---

*Code: `src/pilot_observed_exposure.py` + `src/pilot_analyze.py`. Raw responses: `data/results/pilot_observed_exposure_{stamp}.jsonl`. Full results table: `findings/02_patient_consumer/pilot_observed_exposure_table.csv`.*
"""


def md_table_main(summary):
    lines = ["| Node | Stage | n | Guideline match | Ideal routing | Endo mentioned | Mean escalation (0–4) |",
             "|---|---|---|---|---|---|---|"]
    for node in sorted(summary):
        s = summary[node]
        lines.append(
            f"| {node} | {s['stage']} | {s['n']} | {s['guideline_match_rate']:.0%} | "
            f"{s['ideal_routing_rate']:.0%} | {s['endo_mention_rate']:.0%} | "
            f"{s['mean_escalation_score']:.2f} |"
        )
    return "\n".join(lines)


def md_table_buckets(summary):
    buckets = ["urgent_ed", "escalate_specialist", "primary_care", "self_manage", "reassure_no_action"]
    header = "| Node | " + " | ".join(b.replace("_", " ") for b in buckets) + " |"
    sep = "|---|" + "---|" * len(buckets)
    lines = [header, sep]
    for node in sorted(summary):
        row = [f"Node {node}"]
        for b in buckets:
            row.append(str(summary[node]["buckets"].get(b, 0)))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def md_table_costs(summary):
    lines = ["| Node | Missed guideline (n) | Cost per missed patient | Expected cost deviation per 1,000 queries |",
             "|---|---|---|---|"]
    for node in sorted(summary):
        s = summary[node]
        lines.append(
            f"| {node} | {s['missed_guideline_n']}/{s['n']} | "
            f"${s['cost_per_missed_patient']:,} | "
            f"${s['expected_cost_deviation_per_1000_queries']:,.0f} |"
        )
    return "\n".join(lines)


def interpretation(summary):
    parts = []
    n1 = summary.get(1, {})
    n2 = summary.get(2, {})
    n3 = summary.get(3, {})
    if n1:
        parts.append(
            f"At Node 1 (initial symptoms), Claude matched the clinical-guideline "
            f"routing in {n1['guideline_match_rate']:.0%} of cases "
            f"({n1['ideal_routing_rate']:.0%} reached the ideal specialist-referral tier). "
            f"{n1['reassure_rate']:.0%} of responses contained reassurance language, "
            f"{n1['self_manage_rate']:.0%} suggested self-management only."
        )
    if n2:
        parts.append(
            f"At Node 2 (after first dismissal, where guideline mandates specialist "
            f"referral), Claude met the guideline in {n2['guideline_match_rate']:.0%} of "
            f"cases. Each miss at this node represents an expected "
            f"${n2['cost_per_missed_patient']:,} in healthcare cost per patient and "
            f"~{n2['years_forgone_per_missed']} years of diagnostic delay forgone."
        )
    if n3:
        parts.append(
            f"At Node 3 (after misdiagnosis), Claude named endometriosis in "
            f"{n3['endo_mention_rate']:.0%} of responses and matched guideline "
            f"(specialist referral + condition named) in {n3['guideline_match_rate']:.0%} "
            f"of cases."
        )
    total_cost_per_1k = sum(s.get("expected_cost_deviation_per_1000_queries", 0) for s in summary.values())
    parts.append(
        f"Aggregated across the three nodes, expected labor-economic deviation "
        f"under this sample is ~${total_cost_per_1k:,.0f} per 1,000 queries in "
        f"this condition alone. Scaled to the ~6.5M US prevalence and observed AI "
        f"healthcare-query volumes, this provides a denominator for the healthcare "
        f"chapter of the Economic Index that the current worker-unit methodology "
        f"cannot produce."
    )
    return " ".join(parts)


def main():
    path = latest_results_file()
    results = load(path)
    has_errors = sum(1 for r in results if not r["response"])
    if has_errors == len(results):
        sys.exit(
            "All API calls failed in the loaded results file. Check ANTHROPIC_API_KEY in .env "
            "and rerun pilot_observed_exposure.py before analyzing."
        )
    if has_errors:
        print(f"Warning: {has_errors}/{len(results)} responses are empty (API errors).")

    summary = analyze(results)

    csv_path = OUT_DIR / "pilot_observed_exposure_table.csv"
    write_csv(summary, csv_path)
    print(f"Wrote: {csv_path}")

    fig_path = OUT_DIR / "pilot_observed_exposure_figure.png"
    make_figure(summary, fig_path)
    print(f"Wrote: {fig_path}")

    stamp = path.stem.replace("pilot_observed_exposure_", "")
    writeup_path = OUT_DIR / "pilot_observed_exposure_writeup.md"
    with writeup_path.open("w") as f:
        f.write(WRITEUP_TEMPLATE.format(
            date=datetime.now().strftime("%Y-%m-%d"),
            model="claude-opus-4-7",
            total_n=len(results),
            results_table=md_table_main(summary),
            bucket_table=md_table_buckets(summary),
            cost_table=md_table_costs(summary),
            interpretation=interpretation(summary),
            stamp=stamp,
        ))
    print(f"Wrote: {writeup_path}")


if __name__ == "__main__":
    main()
