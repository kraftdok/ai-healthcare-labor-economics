"""
Produce analysis/enterprise_verticals_findings.md + CSV + figure.

Labor-economic translation: for each vertical, convert
(time_manual - time_with_ai) × volume × hourly wage → annual US recovery.
"""
import json
import sys
import csv
from datetime import datetime
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "data" / "results"
OUT = Path(__file__).resolve().parent.parent / "findings" / "01_enterprise"

HOURLY_WAGE_USD = 29.76  # BLS median hourly wage

VOLUME = {
    "prior_auth": {
        "annual_requests_M_us": 850,   # CAQH 2023 estimate: ~850M prior auth requests/yr in US
        "label": "prior-auth requests",
    },
    "clinical_documentation": {
        # 1.1M practicing physicians × ~15 encounters/day × 250 workdays / 1e6 → ~4.1B encounters/yr
        "annual_encounters_M_us": 4100,
        "label": "documented patient encounters",
    },
    "care_coordination": {
        # 40M complex-chronic patients × 12 coordination events/yr
        "annual_events_M_us": 480,
        "label": "care-coordination events",
    },
}


def main():
    files = sorted(RESULTS.glob("enterprise_verticals_*.json"))
    if not files:
        sys.exit("No enterprise verticals results found.")
    data = json.loads(files[-1].read_text())

    rows = []
    for entry in data:
        v = entry["vertical"]
        q = entry["quality"]
        vid = v["id"]
        baseline = v["baseline_cost"]
        t_manual = q["estimated_time_manual_min"]
        t_ai = q["estimated_time_with_ai_min"]
        time_saved_min = t_manual - t_ai
        pct_time_saved = time_saved_min / t_manual * 100

        if vid == "prior_auth":
            annual_volume_M = VOLUME[vid]["annual_requests_M_us"]
        elif vid == "clinical_documentation":
            annual_volume_M = VOLUME[vid]["annual_encounters_M_us"]
        else:
            annual_volume_M = VOLUME[vid]["annual_events_M_us"]

        annual_time_saved_hrs_M = annual_volume_M * time_saved_min / 60
        annual_labor_value_recovered_B = annual_time_saved_hrs_M * HOURLY_WAGE_USD / 1000
        female_labor_share_pct = baseline["female_share_of_admin_labor_pct"]
        female_labor_recovered_B = annual_labor_value_recovered_B * female_labor_share_pct / 100

        # Quality pass indicators
        quality_keys = [k for k in q.keys() if not k.startswith("estimated_time")]
        quality_pass_count = sum(1 for k in quality_keys if q[k] is True or (isinstance(q[k], str) and q[k]))
        quality_pass_rate = quality_pass_count / max(1, len(quality_keys)) * 100

        rows.append({
            "vertical": v["name"],
            "annual_volume_M": annual_volume_M,
            "t_manual_min": t_manual,
            "t_ai_min": t_ai,
            "pct_time_saved": pct_time_saved,
            "annual_labor_recovered_B": annual_labor_value_recovered_B,
            "female_share_pct": female_labor_share_pct,
            "female_recovered_B": female_labor_recovered_B,
            "quality_pass_rate": quality_pass_rate,
            "quality_detail": q,
        })

    # CSV
    with (OUT / "enterprise_verticals_table.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vertical", "annual_volume_M_events", "t_manual_min", "t_ai_min",
                    "pct_time_saved", "annual_labor_recovered_usd_B",
                    "female_share_pct", "female_labor_recovered_usd_B",
                    "quality_pass_rate_pct"])
        for r in rows:
            w.writerow([r["vertical"], r["annual_volume_M"], r["t_manual_min"],
                        r["t_ai_min"], f"{r['pct_time_saved']:.0f}",
                        f"{r['annual_labor_recovered_B']:.1f}",
                        r["female_share_pct"],
                        f"{r['female_recovered_B']:.1f}",
                        f"{r['quality_pass_rate']:.0f}"])

    # Figure: two-bar per vertical — total vs female-accruing
    verticals = [r["vertical"].split("(")[0].strip() for r in rows]
    total = [r["annual_labor_recovered_B"] for r in rows]
    female = [r["female_recovered_B"] for r in rows]
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(verticals))
    w = 0.38
    ax.bar([i - w/2 for i in x], total, w, label="Total labor recovered", color="#1f77b4")
    ax.bar([i + w/2 for i in x], female, w, label="Accruing to female labor", color="#d62728")
    ax.set_xticks(list(x))
    ax.set_xticklabels(verticals, rotation=12, ha="right", fontsize=10)
    ax.set_ylabel("Annual US labor-value recovery ($B)")
    ax.set_title("Claude for Healthcare — labor-economic recovery by deployment vertical")
    ax.legend()
    plt.tight_layout()
    plt.savefig(OUT / "enterprise_verticals_figure.png", dpi=140)
    plt.close()

    total_B = sum(r["annual_labor_recovered_B"] for r in rows)
    total_female_B = sum(r["female_recovered_B"] for r in rows)
    pct_female = total_female_B / total_B * 100 if total_B else 0

    lines = [
        "# Claude for Healthcare: Labor-Economic ROI by Deployment Vertical",
        "",
        "*Reflexive measurement artifact — Claude performs a representative task in each of the three verticals Anthropic launched on January 11, 2026, and the labor-economic impact is translated through published time-cost parameters.*",
        "",
        f"**Author:** Oriana Kraft | **Date:** {datetime.now().strftime('%Y-%m-%d')} | **Model:** claude-opus-4-7",
        "",
        "## Why this artifact",
        "",
        "Anthropic's Claude for Healthcare launched January 2026 with three stated deployment verticals: **prior authorization**, **clinical documentation**, and **care coordination**. Of the three, which produces the largest measurable US labor-economic recovery — and how is that recovery distributed across the labor force that currently performs this work?",
        "",
        "This pilot uses Claude Opus 4.7 to perform a representative task in each vertical, evaluates output quality against a simple rubric, and translates the time-saving into annualized US labor-value recovery using BLS wage data and published volume estimates.",
        "",
        "## Comparison table",
        "",
        "| Vertical | Annual US volume | Time-saving per task (manual → AI) | Quality rubric pass | Annual labor-value recovered | Accruing to female labor |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['vertical']} | ~{r['annual_volume_M']:.0f}M events | "
            f"{r['t_manual_min']}→{r['t_ai_min']} min ({r['pct_time_saved']:.0f}% reduction) | "
            f"{r['quality_pass_rate']:.0f}% | "
            f"${r['annual_labor_recovered_B']:.1f}B | "
            f"${r['female_recovered_B']:.1f}B ({r['female_share_pct']}%) |"
        )

    lines += [
        "",
        f"**Aggregate annual labor-value recovery across all three verticals: ~${total_B:.0f}B/year.** Roughly **{pct_female:.0f}%** (${total_female_B:.0f}B) accrues to the labor pool of medical billers, office administrators, nurses, and care coordinators — work that is disproportionately performed by women (BLS occupational demographics). This is the specific empirical channel through which Claude-for-Healthcare has a sex-asymmetric labor-economic footprint, even though the vertical targets (providers, payers, health systems) are not themselves sex-specific.",
        "",
        "## Quality detail",
        "",
    ]
    for r in rows:
        lines.append(f"**{r['vertical']}** — rubric pass rate {r['quality_pass_rate']:.0f}%")
        for k, val in r["quality_detail"].items():
            if not k.startswith("estimated_time"):
                lines.append(f"  - {k}: {'✓' if val else '✗'}")
        lines.append("")

    lines += [
        "## What this demonstrates",
        "",
        "1. **Claude is already deployed in healthcare — in verticals that are administratively dense, labor-heavy, and disproportionately female-staffed.** Follow-up research would measure whether deployment actually produces the labor-value recoveries projected here.",
        "",
        "2. **The measurement can be done reflexively.** Claude itself performs the task under test. Output quality is rubric-evaluated. Labor-economic translation uses public data. No protected health information is required. This is the methodology scaled to full deployment data via enterprise partner collaborations.",
        "",
        "3. **The three verticals together recover a materially larger annual labor-economic value than the patient-triage scenarios alone.** This is the reason this portfolio frames AI in healthcare as a labor-economics question rather than a clinical-accuracy question — the administrative and coordination layer is where the largest immediate recovery channel exists.",
        "",
        "## Limitations",
        "",
        "1. Single representative task per vertical at pilot scale; extension work would add n≥30 tasks per vertical with inter-rater quality evaluation.",
        "2. Time-saving estimates are based on published AI-scribe / AI-prior-auth adoption studies; actual deployment efficiency at enterprise partners would replace these.",
        "3. Labor-value translation assumes recovered time fully converts to alternative productive work; portion re-absorbed in administrative slack is not yet modeled.",
        "4. Volume parameters are US 2024–25 estimates; global extrapolation is not attempted here.",
        "",
        "---",
        "",
        "*Code: `src/pilot_enterprise_verticals.py` + `analysis/analyze_enterprise_verticals.py`. Raw: `data/results/enterprise_verticals_<timestamp>.json`.*",
        "",
        "*Anthropic Claude for Healthcare launch reference: [https://www.anthropic.com/news/healthcare-life-sciences](https://www.anthropic.com/news/healthcare-life-sciences), Jan 11 2026.*",
    ]

    (OUT / "enterprise_verticals_findings.md").write_text("\n".join(lines))
    print(f"Wrote: {OUT/'enterprise_verticals_findings.md'}")
    print(f"Wrote: {OUT/'enterprise_verticals_table.csv'}")
    print(f"Wrote: {OUT/'enterprise_verticals_figure.png'}")
    print(f"Total labor-value recovery: ${total_B:.0f}B/yr; female share: ${total_female_B:.0f}B ({pct_female:.0f}%)")


if __name__ == "__main__":
    main()
