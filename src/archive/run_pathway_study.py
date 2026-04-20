"""
Run Pathway Study: Test where AI routes patients at each stage of the diagnostic journey.

For each condition:
  - Sends patient prompts at each journey node (initial symptoms → dismissal → misdiagnosis → years in)
  - Scores routing: does AI direct to correct next step or reinforce the wrong path?
  - Maps the AI-mediated pathway alongside fragmented and integrated pathways
  - Computes economic cascade for AI routing at each node

Usage:
    python3 src/run_pathway_study.py                 # Full study (~$0.50)
    python3 src/run_pathway_study.py --condition endo  # Single condition
    python3 src/run_pathway_study.py --dry-run         # Preview prompts
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ANTHROPIC_API_KEY, MODEL_ID, RATE_LIMIT_DELAY, MAX_TOKENS, RESULTS_DIR
from pathways import PATHWAYS, get_all_conditions, get_journey_nodes
from economic_model import compute_cascade, compute_all_cascades, format_cascade


# ═══════════════════════════════════════════════════════════════
# COST PROTECTION — Hard ceiling to protect your API budget
# ═══════════════════════════════════════════════════════════════

COST_CEILING_USD = 5.00  # Hard ceiling — will abort if exceeded
# Opus pricing: $15/M input, $75/M output
PRICE_PER_INPUT_TOKEN = 15.0 / 1_000_000
PRICE_PER_OUTPUT_TOKEN = 75.0 / 1_000_000

_cumulative_cost = 0.0

def _track_cost(input_tokens: int, output_tokens: int) -> float:
    """Track cumulative cost. Returns current total."""
    global _cumulative_cost
    call_cost = (input_tokens * PRICE_PER_INPUT_TOKEN +
                 output_tokens * PRICE_PER_OUTPUT_TOKEN)
    _cumulative_cost += call_cost
    return _cumulative_cost

def _check_budget():
    """Abort if we've exceeded the cost ceiling."""
    if _cumulative_cost >= COST_CEILING_USD:
        print(f"\n🛑 COST CEILING REACHED: ${_cumulative_cost:.4f} >= ${COST_CEILING_USD}")
        print("   Study aborted to protect your API budget.")
        print("   Raise COST_CEILING_USD in run_pathway_study.py to continue.")
        sys.exit(0)


# ═══════════════════════════════════════════════════════════════
# SYSTEM PROMPT — Natural, patient-facing context
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are a medical AI assistant. A patient is describing their health "
    "situation and asking for guidance. Be helpful, thorough, and empathetic.\n\n"
    "Respond with a JSON object in the following format:\n\n"
    "{\n"
    '  "assessment": "Your assessment of what might be going on (2-3 sentences)",\n'
    '  "likely_conditions": [\n'
    '    {"condition": "...", "likelihood": "high/medium/low"},\n'
    '    {"condition": "...", "likelihood": "high/medium/low"},\n'
    '    {"condition": "...", "likelihood": "high/medium/low"}\n'
    "  ],\n"
    '  "recommended_action": "What should the patient do next (specific)",\n'
    '  "urgency": <integer 1-5, where 1=no rush and 5=seek immediate care>,\n'
    '  "specialist_referral": "Which type of doctor to see, if any",\n'
    '  "key_tests": ["test1", "test2"],\n'
    '  "what_to_tell_your_doctor": "Key points to raise at appointment"\n'
    "}\n\n"
    "Respond ONLY with this JSON, no other text."
)


def call_claude(prompt: str) -> dict:
    """Send prompt to Claude and return parsed response."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            temperature=1.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = response.content[0].text.strip()
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        # Track cost
        current_total = _track_cost(usage["input_tokens"], usage["output_tokens"])

        # Parse JSON
        try:
            clean = raw_text
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
                clean = clean.strip()
            parsed = json.loads(clean)
            return {"parsed": parsed, "raw": raw_text, "usage": usage, "error": None}
        except json.JSONDecodeError:
            return {"parsed": None, "raw": raw_text, "usage": usage,
                    "error": "JSON parse failed"}

    except Exception as e:
        return {"parsed": None, "raw": None, "usage": None, "error": str(e)}


def normalize(text: str) -> str:
    return text.lower().strip().replace("-", " ").replace("_", " ")


def score_routing(response: dict, node: dict) -> dict:
    """Score AI routing at a specific journey node."""
    parsed = response.get("parsed")
    if not parsed:
        return {"valid": False, "error": response.get("error", "No parsed response")}

    assessment = normalize(parsed.get("assessment", ""))
    action = normalize(parsed.get("recommended_action", ""))
    specialist = normalize(parsed.get("specialist_referral", ""))
    conditions = [normalize(c.get("condition", ""))
                  for c in parsed.get("likely_conditions", [])]
    urgency = parsed.get("urgency", 0)
    tell_doc = normalize(parsed.get("what_to_tell_your_doctor", ""))

    # Combine all text fields for matching
    all_text = f"{assessment} {action} {specialist} {' '.join(conditions)} {tell_doc}"

    # Check correct routing
    correct_hits = []
    for correct in node.get("correct_routing", []):
        if normalize(correct) in all_text:
            correct_hits.append(correct)

    # Check red flag routing (incorrect/dismissive)
    red_flag_hits = []
    for red in node.get("red_flag_routing", []):
        if normalize(red) in all_text:
            red_flag_hits.append(red)

    # Check correct next steps
    step_hits = []
    for step in node.get("correct_next_steps", []):
        if normalize(step) in all_text:
            step_hits.append(step)

    # Routing score (0-5)
    routing_score = 0
    if correct_hits:
        routing_score += 2
    if step_hits:
        routing_score += 1
    if not red_flag_hits:
        routing_score += 1
    if urgency >= node.get("urgency_required", 2):
        routing_score += 1

    return {
        "valid": True,
        "correct_routing_found": correct_hits,
        "red_flag_routing_found": red_flag_hits,
        "correct_steps_found": step_hits,
        "urgency_given": urgency,
        "routing_score": routing_score,
        "routed_correctly": len(correct_hits) > 0 and len(red_flag_hits) == 0,
        "dismissed": len(red_flag_hits) > 0 and len(correct_hits) == 0,
        "conditions_identified": conditions,
        "specialist_recommended": parsed.get("specialist_referral", ""),
        "action_recommended": parsed.get("recommended_action", ""),
    }


def run_pathway_study(conditions: list = None, dry_run: bool = False):
    """Run the pathway study across all conditions and nodes."""
    if conditions is None:
        conditions = get_all_conditions()

    results = []
    total_prompts = sum(len(PATHWAYS[c]["journey_nodes"]) for c in conditions)
    call_num = 0
    total_input = 0
    total_output = 0

    print(f"\n{'='*65}")
    print(f"AI PATHWAY ECONOMICS STUDY")
    print(f"{'='*65}")
    print(f"Conditions: {conditions}")
    print(f"Total prompts: {total_prompts}")
    print(f"Estimated cost: ~${total_prompts * 0.04:.2f}")
    print(f"Model: {MODEL_ID}")
    print(f"{'='*65}\n")

    for cid in conditions:
        pathway = PATHWAYS[cid]
        nodes = pathway["journey_nodes"]

        print(f"\n{'─'*65}")
        print(f"  {pathway['name']}")
        print(f"  Fragmented: {pathway['fragmented_pathway']['total_years']} yrs, "
              f"${pathway['fragmented_pathway']['total_healthcare_cost']:,}")
        print(f"  Integrated: {pathway['integrated_pathway']['total_years']} yrs, "
              f"${pathway['integrated_pathway']['total_healthcare_cost']:,}")
        print(f"  Testing {len(nodes)} journey nodes...")
        print(f"{'─'*65}")

        condition_results = []

        for node in nodes:
            call_num += 1
            label = f"[{call_num}/{total_prompts}] Node {node['node']}: {node['stage']}"

            if dry_run:
                print(f"\n  DRY RUN: {label}")
                print(f"    Prompt: {node['patient_prompt'][:90]}...")
                continue

            print(f"\n  {label}", end="", flush=True)

            _check_budget()  # Abort if over cost ceiling
            response = call_claude(node["patient_prompt"])
            score = score_routing(response, node)

            if response["usage"]:
                total_input += response["usage"]["input_tokens"]
                total_output += response["usage"]["output_tokens"]

            result = {
                "condition_id": cid,
                "condition_name": pathway["name"],
                "node": node["node"],
                "stage": node["stage"],
                "years_into_journey": node["years_into_journey"],
                "response": response,
                "score": score,
                "timestamp": datetime.now().isoformat(),
            }

            condition_results.append(result)

            # Print immediate result
            if score["valid"]:
                status = "✓ CORRECT" if score["routed_correctly"] else (
                    "✗ DISMISSED" if score["dismissed"] else "⚠ PARTIAL"
                )
                print(f" → {status}")
                if score["correct_routing_found"]:
                    print(f"    ✓ Found: {', '.join(score['correct_routing_found'][:3])}")
                if score["red_flag_routing_found"]:
                    print(f"    ✗ Red flags: {', '.join(score['red_flag_routing_found'][:3])}")
                print(f"    Specialist: {score['specialist_recommended']}")
                print(f"    Urgency: {score['urgency_given']}/5")
                print(f"    Running cost: ${_cumulative_cost:.4f}")
            else:
                print(f" → ❌ {score.get('error', 'failed')}")

            time.sleep(RATE_LIMIT_DELAY)

        results.extend(condition_results)

        # Print condition summary
        if not dry_run and condition_results:
            scored = [r for r in condition_results if r["score"].get("valid")]
            correct = sum(1 for r in scored if r["score"]["routed_correctly"])
            dismissed = sum(1 for r in scored if r["score"]["dismissed"])

            print(f"\n  SUMMARY: {correct}/{len(scored)} correctly routed, "
                  f"{dismissed}/{len(scored)} dismissed")

            # Identify which node AI first routes correctly
            first_correct = None
            for r in sorted(scored, key=lambda x: x["node"]):
                if r["score"]["routed_correctly"]:
                    first_correct = r
                    break

            if first_correct:
                n = first_correct["node"]
                yrs = first_correct["years_into_journey"]
                frag_yrs = pathway["fragmented_pathway"]["total_years"]
                if frag_yrs and frag_yrs > yrs:
                    saved = frag_yrs - yrs
                    print(f"  → AI catches at Node {n} (Year {yrs}), "
                          f"saving ~{saved:.1f} years vs. fragmented pathway")

    # Final summary
    if not dry_run:
        cost = (total_input * 3 + total_output * 15) / 1_000_000
        print(f"\n{'='*65}")
        print(f"STUDY COMPLETE")
        print(f"  Tokens: {total_input:,} in / {total_output:,} out")
        print(f"  Cost: ${cost:.2f}")
        print(f"{'='*65}")

    return results


def save_pathway_results(results: list):
    """Save pathway study results."""
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(RESULTS_DIR, f"pathway_results_{timestamp}.json")
    latest = os.path.join(RESULTS_DIR, "latest_pathway_results.json")

    output = {
        "study": "AI Pathway Economics",
        "model": MODEL_ID,
        "timestamp": datetime.now().isoformat(),
        "results": results,
    }

    for path in [filepath, latest]:
        with open(path, "w") as f:
            json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {filepath}")
    return filepath


def generate_pathway_comparison(results: list):
    """Generate three-way pathway comparison report."""
    lines = []
    lines.append("# AI Pathway Economics — Three-Way Comparison Report\n")
    lines.append(f"**Model:** {MODEL_ID}")
    lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")

    conditions_seen = {}
    for r in results:
        cid = r["condition_id"]
        if cid not in conditions_seen:
            conditions_seen[cid] = []
        conditions_seen[cid].append(r)

    for cid, cond_results in conditions_seen.items():
        pathway = PATHWAYS[cid]
        frag = pathway["fragmented_pathway"]
        integ = pathway["integrated_pathway"]

        lines.append(f"## {pathway['name']}\n")
        lines.append(f"**Prevalence:** {pathway['prevalence']}\n")

        # Three-way table
        lines.append("### Pathway Comparison\n")
        lines.append("| Metric | Fragmented (Current) | Integrated (Guidelines) | AI-Mediated |")
        lines.append("|---|---|---|---|")

        # Find AI catch node
        scored = [r for r in cond_results if r["score"].get("valid")]
        first_correct = None
        for r in sorted(scored, key=lambda x: x["node"]):
            if r["score"]["routed_correctly"]:
                first_correct = r
                break

        ai_years = "Not caught" if not first_correct else first_correct["years_into_journey"]
        ai_cost = "N/A"
        if first_correct and isinstance(ai_years, (int, float)):
            node_data = None
            for node in pathway["journey_nodes"]:
                if node["node"] == first_correct["node"]:
                    node_data = node
                    break
            if node_data:
                ai_cost = f"${node_data.get('cumulative_system_cost', 0):,} + AI triage"

        frag_years = frag.get("total_years", "N/A")
        integ_years = integ.get("total_years", "N/A")

        lines.append(f"| Years to diagnosis | {frag_years} | {integ_years} | {ai_years} |")
        lines.append(f"| Healthcare cost | ${frag['total_healthcare_cost']:,} | "
                     f"${integ['total_healthcare_cost']:,} | {ai_cost} |")
        lines.append(f"| Physicians seen | {frag.get('total_physicians', 'N/A')} | "
                     f"{integ.get('total_physicians', 'N/A')} | 1 (AI) + referral |")

        # Node-by-node AI results
        lines.append("\n### AI Routing at Each Journey Node\n")
        lines.append("| Node | Stage | Years In | Routed Correctly? | AI Suggested | Red Flags |")
        lines.append("|---|---|---|---|---|---|")

        for r in sorted(cond_results, key=lambda x: x["node"]):
            s = r["score"]
            if not s.get("valid"):
                continue

            status = "✓" if s["routed_correctly"] else ("✗ Dismissed" if s["dismissed"] else "⚠ Partial")
            specialist = s.get("specialist_recommended", "—")
            red = ", ".join(s.get("red_flag_routing_found", [])[:2]) or "—"

            lines.append(f"| {r['node']} | {r['stage']} | {r['years_into_journey']} | "
                         f"{status} | {specialist} | {red} |")

        # Economic cascade (if AI catches it)
        if first_correct and isinstance(ai_years, (int, float)):
            prod = pathway.get("productivity_data", {})
            frag_total_years = frag.get("total_years")
            if frag_total_years and frag_total_years > ai_years:
                acceleration = frag_total_years - ai_years
                lines.append(f"\n### Economic Cascade (AI accelerates diagnosis by "
                             f"{acceleration:.1f} years)\n")

                cascade = compute_cascade(
                    condition_name=pathway["name"],
                    diagnosis_acceleration_years=acceleration,
                    excess_annual_healthcare_cost=pathway.get(
                        "fragmented_pathway", {}).get(
                        "total_healthcare_cost", 0) / max(frag_total_years, 1),
                    productivity_days_lost_per_year=prod.get("days_lost_per_year", 30),
                    affected_population=pathway.get("affected_us_population", 0),
                    early_disability_rate=prod.get("early_disability_rate", 0.15),
                )

                pp = cascade["per_patient"]
                pop = cascade["population"]

                lines.append("| Impact | Per Patient | Population |")
                lines.append("|---|---|---|")
                lines.append(f"| Healthcare saved | ${pp['healthcare_saved']:,} | "
                             f"${pop['healthcare_saved']:,} |")
                lines.append(f"| Work days restored | {pp['absenteeism_days_restored']:.0f} | "
                             f"{pp['absenteeism_days_restored'] * pop['affected_population']:,.0f} |")
                lines.append(f"| Earnings restored | ${pp['total_productivity_restored']:,} | "
                             f"${pop['productivity_restored']:,} |")
                lines.append(f"| Disability deferral | ${pp['disability_deferral_value']:,} | "
                             f"${pop['disability_savings']:,} |")
                lines.append(f"| **TOTAL** | **${pp['total_lifetime_economic_value']:,}** | "
                             f"**${pop['total_economic_impact']:,}** "
                             f"(**${pop['total_billions']}B**) |")

        lines.append("\n---\n")

    # Save report
    Path("outputs").mkdir(exist_ok=True)
    path = "outputs/pathway_comparison_report.md"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nPathway comparison report saved to: {path}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run AI Pathway Economics Study")
    parser.add_argument("--condition", type=str, help="Run single condition (e.g., 'endo')")
    parser.add_argument("--dry-run", action="store_true", help="Preview without API calls")
    args = parser.parse_args()

    if not args.dry_run and not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Create a .env file: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    conditions = [args.condition] if args.condition else None
    results = run_pathway_study(conditions=conditions, dry_run=args.dry_run)

    if not args.dry_run and results:
        save_pathway_results(results)
        report = generate_pathway_comparison(results)
        print("\n" + report)

        # Also print economic cascades for reference
        print("\n\nREFERENCE: Maximum potential economic cascades\n")
        cascades = compute_all_cascades()
        for cid, cascade in cascades.items():
            print(format_cascade(cascade))
            print()


if __name__ == "__main__":
    main()
