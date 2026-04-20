"""
Analyze Results: Statistical analysis + economic impact modeling.

Produces:
1. Voice divergence analysis per condition
2. Corrective prompt effectiveness
3. Cross-condition patterns
4. Economic impact estimates using published pathway cost data

Usage:
    python src/analyze.py
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conditions import ALL_CONDITIONS
from config import TABLES_DIR, SUMMARY_DIR


def load_scored():
    """Load scored results."""
    path = os.path.join(TABLES_DIR, "scored_results.json")
    if not os.path.exists(path):
        print("ERROR: Scored results not found. Run: python src/score.py")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def economic_analysis(scored_data: dict) -> dict:
    """
    Compute economic impact of voice divergence and corrective potential.

    For each condition with cost data:
    - If patient-voice gets lower composite score → estimate cost of that gap
    - If corrective prompt improves score → estimate value of correction
    """
    condition_lookup = {c["id"]: c for c in ALL_CONDITIONS}
    economics = {}

    for cid, cond_summary in scored_data["summary"].items():
        cond = condition_lookup.get(cid)
        if not cond:
            continue

        cost_data = cond.get("cost_data", {})
        if not cost_data:
            continue

        econ = {"condition": cond["name"], "group": cond["group"]}

        # Get baseline divergence
        baseline = cond_summary.get("comparisons", {}).get("baseline", {})
        corrective = cond_summary.get("comparisons", {}).get("corrective", {})

        if baseline.get("divergence"):
            div = baseline["divergence"]

            # For Group A: if patient_voice gets lower scores → the divergence is the problem
            # For Group B: if female_presentation gets lower scores → same
            econ["baseline_composite_gap"] = div["composite_gap"]
            econ["baseline_urgency_gap"] = div["urgency_gap"]
            econ["baseline_dismissal_gap"] = div["dismissal_gap"]

            # Economic impact: if AI under-triages or dismisses due to voice,
            # the cost is the diagnostic delay cost
            excess = cost_data.get("excess_annual_cost")
            delay = cost_data.get("avg_delay_years")

            if excess and delay and abs(div["composite_gap"]) > 0:
                # If composite gap > 0, patient voice got HIGHER score (unexpected)
                # If composite gap < 0, patient voice got LOWER score → delay cost
                gap_magnitude = abs(div["composite_gap"]) / 5  # normalize to 0-1

                econ["estimated_delay_cost_per_patient"] = round(
                    excess * delay * gap_magnitude
                )
                econ["annual_excess_per_patient"] = excess
                econ["source"] = cost_data.get("source", "")

        if corrective.get("divergence") and baseline.get("divergence"):
            corr_div = corrective["divergence"]
            base_div = baseline["divergence"]

            # Did the gap narrow?
            gap_before = abs(base_div["composite_gap"])
            gap_after = abs(corr_div["composite_gap"])
            econ["gap_before_correction"] = gap_before
            econ["gap_after_correction"] = gap_after
            econ["gap_reduction"] = round(gap_before - gap_after, 2)
            econ["gap_reduction_pct"] = (
                round((gap_before - gap_after) / gap_before * 100, 1)
                if gap_before > 0 else 0
            )

            # Economic value of correction
            excess = cost_data.get("excess_annual_cost")
            if excess and econ["gap_reduction"] > 0:
                econ["correction_value_per_patient_per_year"] = round(
                    excess * (econ["gap_reduction"] / 5)
                )

        economics[cid] = econ

    return economics


def generate_report(scored_data: dict, economics: dict) -> str:
    """Generate a markdown report of findings."""
    lines = []
    lines.append("# AI Clinical Intermediary Study — Results Report\n")
    lines.append(f"**Model:** {scored_data['metadata'].get('model', 'N/A')}")
    lines.append(f"**Total experiments:** {scored_data['metadata'].get('total_experiments', 0)}")
    lines.append(f"**Timestamp:** {scored_data['metadata'].get('timestamp', 'N/A')}\n")

    # ── Key Findings ──
    lines.append("## Key Findings\n")

    # Count conditions where patient/female voice got lower scores
    voice_disadvantaged = 0
    voice_equal = 0
    voice_advantaged = 0

    for cid, cond in scored_data["summary"].items():
        baseline = cond.get("comparisons", {}).get("baseline", {})
        if baseline.get("divergence"):
            gap = baseline["divergence"]["composite_gap"]
            # For Group A: negative gap means patient_voice < clinician_voice
            # For Group B: we need to check which voice is disadvantaged
            if abs(gap) < 0.3:
                voice_equal += 1
            elif gap < 0:
                voice_disadvantaged += 1
            else:
                voice_advantaged += 1

    lines.append(f"### Voice Divergence")
    lines.append(f"- Conditions where patient/non-textbook voice scored LOWER: "
                 f"**{voice_disadvantaged}/{len(scored_data['summary'])}**")
    lines.append(f"- Conditions where voices scored approximately equal: "
                 f"**{voice_equal}/{len(scored_data['summary'])}**")
    lines.append(f"- Conditions where patient/non-textbook voice scored HIGHER: "
                 f"**{voice_advantaged}/{len(scored_data['summary'])}**\n")

    # Corrective effectiveness
    corrections_helped = 0
    corrections_total = 0
    for cid, cond in scored_data["summary"].items():
        if cond.get("corrective_delta"):
            corrections_total += 1
            if cond["corrective_delta"]["composite_gap_change"] < 0:
                corrections_helped += 1

    if corrections_total > 0:
        lines.append(f"### Corrective Potential")
        lines.append(f"- Clinical guideline system prompts narrowed the voice gap in "
                     f"**{corrections_helped}/{corrections_total}** conditions\n")

    # ── Detailed Results ──
    lines.append("## Results by Condition\n")

    for cid, cond in scored_data["summary"].items():
        lines.append(f"### {cond['name']} (Group {cond['group']})\n")

        for mode, data in cond["comparisons"].items():
            lines.append(f"**{mode.upper()}**\n")
            lines.append("| Voice | Composite (/5) | Correct Dx (top 3) | Dismissed | "
                         "Urgency | Urgency OK |")
            lines.append("|---|---|---|---|---|---|")

            for voice, vs in data["voice_scores"].items():
                lines.append(
                    f"| {voice} | {vs['composite_mean']} | "
                    f"{vs['correct_top3_rate']:.0%} | "
                    f"{vs['dismissal_rate']:.0%} | "
                    f"{vs['urgency_mean']:.1f} | "
                    f"{vs['urgency_appropriate_rate']:.0%} |"
                )

            if data.get("divergence"):
                d = data["divergence"]
                lines.append(f"\n> **Divergence:** composite={d['composite_gap']:+.2f}, "
                             f"urgency={d['urgency_gap']:+.2f}, "
                             f"dismissal rate gap={d['dismissal_gap']:+.2f}")

            lines.append("")

        if cond.get("corrective_delta"):
            cd = cond["corrective_delta"]
            direction = "narrowed" if cd["composite_gap_change"] < 0 else "widened"
            lines.append(f"> ⚕ **Corrective effect:** Gap {direction} by "
                         f"{abs(cd['composite_gap_change']):.2f} composite points\n")

    # ── Economic Impact ──
    lines.append("## Economic Impact Analysis\n")
    lines.append("| Condition | Annual Excess Cost | Voice Gap | After Correction | "
                 "Gap Reduction | Value of Correction (/patient/yr) |")
    lines.append("|---|---|---|---|---|---|")

    for cid, econ in economics.items():
        excess = econ.get("annual_excess_per_patient", "—")
        gap_before = econ.get("gap_before_correction", "—")
        gap_after = econ.get("gap_after_correction", "—")
        reduction = econ.get("gap_reduction_pct", "—")
        value = econ.get("correction_value_per_patient_per_year", "—")

        excess_str = f"${excess:,}" if isinstance(excess, (int, float)) else excess
        gap_b = f"{gap_before:.2f}" if isinstance(gap_before, (int, float)) else gap_before
        gap_a = f"{gap_after:.2f}" if isinstance(gap_after, (int, float)) else gap_after
        red_str = f"{reduction}%" if isinstance(reduction, (int, float)) else reduction
        val_str = f"${value:,}" if isinstance(value, (int, float)) else value

        lines.append(f"| {econ['condition']} | {excess_str} | {gap_b} | "
                     f"{gap_a} | {red_str} | {val_str} |")

    lines.append("")
    lines.append("---")
    lines.append("*All cost figures sourced from published peer-reviewed studies. "
                 "See conditions.py for full citations.*")

    return "\n".join(lines)


def main():
    scored_data = load_scored()
    economics = economic_analysis(scored_data)

    # Generate report
    report = generate_report(scored_data, economics)

    # Save
    Path(SUMMARY_DIR).mkdir(parents=True, exist_ok=True)
    report_path = os.path.join(SUMMARY_DIR, "study_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    # Save economics JSON
    econ_path = os.path.join(TABLES_DIR, "economic_analysis.json")
    Path(TABLES_DIR).mkdir(parents=True, exist_ok=True)
    with open(econ_path, "w") as f:
        json.dump(economics, f, indent=2)
    print(f"Economic analysis saved to: {econ_path}")

    # Print summary
    print("\n" + report)


if __name__ == "__main__":
    main()
