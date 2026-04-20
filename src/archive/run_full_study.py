"""
Run Full Study: 5 repetitions per prompt for statistical power.

Uses the same infrastructure as run_pathway_study.py but runs each prompt
5 times to measure response variability.

Usage:
    python3 src/run_full_study.py
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ANTHROPIC_API_KEY, MODEL_ID, RATE_LIMIT_DELAY, MAX_TOKENS, RESULTS_DIR
from pathways import PATHWAYS, get_all_conditions

# ═══════════════════════════════════════════════════════════════
# COST PROTECTION
# ═══════════════════════════════════════════════════════════════

COST_CEILING_USD = 5.00
PRICE_PER_INPUT_TOKEN = 15.0 / 1_000_000
PRICE_PER_OUTPUT_TOKEN = 75.0 / 1_000_000

_cumulative_cost = 0.0
_hit_ceiling = False

REPETITIONS = 5

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
    global _cumulative_cost, _hit_ceiling
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
        call_cost = (usage["input_tokens"] * PRICE_PER_INPUT_TOKEN +
                     usage["output_tokens"] * PRICE_PER_OUTPUT_TOKEN)
        _cumulative_cost += call_cost

        # Check ceiling
        if _cumulative_cost >= COST_CEILING_USD:
            _hit_ceiling = True

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
            return {"parsed": None, "raw": raw_text, "usage": usage, "error": "JSON parse failed"}

    except Exception as e:
        return {"parsed": None, "raw": None, "usage": None, "error": str(e)}


def normalize(text: str) -> str:
    return text.lower().strip().replace("-", " ").replace("_", " ")


def enhanced_score(response: dict, node: dict) -> dict:
    """Enhanced scoring with rank awareness and psychiatric overlay detection."""
    parsed = response.get("parsed")
    if not parsed:
        return {"valid": False, "error": response.get("error", "No parsed response")}

    conditions = parsed.get("likely_conditions", [])
    urgency = parsed.get("urgency", 0)
    specialist = normalize(parsed.get("specialist_referral", ""))
    assessment = normalize(parsed.get("assessment", ""))
    action = normalize(parsed.get("recommended_action", ""))
    tell_doc = normalize(parsed.get("what_to_tell_your_doctor", ""))
    all_text = f"{assessment} {action} {specialist} {tell_doc}"

    # ── Correct diagnosis detection with RANK ──
    correct_routing = node.get("correct_routing", [])
    red_flag_routing = node.get("red_flag_routing", [])

    # Check each listed condition
    condition_analysis = []
    correct_rank = None
    psychiatric_terms = ["anxiety", "panic", "stress", "depression", "psychiatric",
                         "somatoform", "psychosomatic", "somatic symptom",
                         "emotional", "psychological", "hysteria",
                         "tension headache", "migraine"]
    psychiatric_in_list = []

    for i, c in enumerate(conditions):
        cond_name = normalize(c.get("condition", ""))
        cond_likelihood = c.get("likelihood", "unknown")
        rank = i + 1

        # Is this the correct diagnosis?
        is_correct = False
        for cr in correct_routing:
            if normalize(cr) in cond_name:
                is_correct = True
                if correct_rank is None:
                    correct_rank = rank
                break

        # Is this a psychiatric/bias term?
        is_psychiatric = False
        for pt in psychiatric_terms:
            if pt in cond_name:
                is_psychiatric = True
                psychiatric_in_list.append({
                    "rank": rank,
                    "condition": c.get("condition", ""),
                    "likelihood": cond_likelihood,
                })
                break

        condition_analysis.append({
            "rank": rank,
            "condition": c.get("condition", ""),
            "likelihood": cond_likelihood,
            "is_correct": is_correct,
            "is_psychiatric": is_psychiatric,
        })

    # ── Red flag detection ──
    red_flag_hits = []
    for red in red_flag_routing:
        for c in conditions:
            if normalize(red) in normalize(c.get("condition", "")):
                red_flag_hits.append(red)
        if normalize(red) in all_text:
            red_flag_hits.append(red)
    red_flag_hits = list(set(red_flag_hits))

    # ── Correct routing in text fields ──
    correct_in_text = []
    for cr in correct_routing:
        if normalize(cr) in all_text:
            correct_in_text.append(cr)

    # ── Compute scores ──
    has_correct_in_list = correct_rank is not None
    has_correct_in_text = len(correct_in_text) > 0
    has_psychiatric_overlay = len(psychiatric_in_list) > 0
    psychiatric_outranks_correct = False
    if has_psychiatric_overlay and correct_rank is not None:
        for p in psychiatric_in_list:
            if p["rank"] < correct_rank:
                psychiatric_outranks_correct = True

    return {
        "valid": True,
        "correct_rank": correct_rank,
        "correct_in_text": correct_in_text,
        "has_correct_diagnosis": has_correct_in_list or has_correct_in_text,
        "red_flag_hits": red_flag_hits,
        "psychiatric_overlay": psychiatric_in_list,
        "has_psychiatric_overlay": has_psychiatric_overlay,
        "psychiatric_outranks_correct": psychiatric_outranks_correct,
        "urgency_given": urgency,
        "urgency_required": node.get("urgency_required", 2),
        "condition_analysis": condition_analysis,
        "specialist": parsed.get("specialist_referral", ""),
        "assessment": parsed.get("assessment", ""),
        "conditions_listed": [c.get("condition", "") for c in conditions],
    }


def run_full_study():
    """Run 5x repetitions across all conditions."""
    global _hit_ceiling

    conditions = get_all_conditions()
    total_prompts = sum(len(PATHWAYS[c]["journey_nodes"]) for c in conditions)
    total_calls = total_prompts * REPETITIONS

    print(f"\n{'='*65}")
    print(f"AI PATHWAY ECONOMICS — FULL STUDY (n={REPETITIONS})")
    print(f"{'='*65}")
    print(f"Conditions: {len(conditions)}")
    print(f"Prompts per condition: varies")
    print(f"Total unique prompts: {total_prompts}")
    print(f"Total API calls: {total_calls}")
    print(f"Estimated cost: ~${total_calls * 0.03:.2f}")
    print(f"Cost ceiling: ${COST_CEILING_USD}")
    print(f"Model: {MODEL_ID}")
    print(f"{'='*65}\n")

    all_results = []
    call_num = 0

    for cid in conditions:
        pathway = PATHWAYS[cid]
        nodes = pathway["journey_nodes"]

        print(f"\n{'─'*65}")
        print(f"  {pathway['name']} ({len(nodes)} nodes × {REPETITIONS} reps)")
        print(f"{'─'*65}")

        for node in nodes:
            node_results = []

            for rep in range(1, REPETITIONS + 1):
                call_num += 1

                if _hit_ceiling:
                    print(f"\n🛑 COST CEILING ${COST_CEILING_USD} reached at call {call_num}/{total_calls}")
                    print(f"   Total spent: ${_cumulative_cost:.4f}")
                    print(f"   Saving partial results...")
                    # Save what we have
                    save_results(all_results)
                    return all_results

                print(f"  [{call_num}/{total_calls}] {cid} N{node['node']} R{rep}", end="", flush=True)

                response = call_claude(node["patient_prompt"])
                score = enhanced_score(response, node)

                result = {
                    "condition_id": cid,
                    "condition_name": pathway["name"],
                    "node": node["node"],
                    "stage": node["stage"],
                    "repetition": rep,
                    "response": response,
                    "score": score,
                    "timestamp": datetime.now().isoformat(),
                    "cumulative_cost": round(_cumulative_cost, 4),
                }

                node_results.append(result)
                all_results.append(result)

                # Print compact result
                if score["valid"]:
                    rank_str = f"R{score['correct_rank']}" if score['correct_rank'] else "—"
                    psych = "🔴" if score['psychiatric_outranks_correct'] else ("🟡" if score['has_psychiatric_overlay'] else "🟢")
                    urg = score['urgency_given']
                    print(f" → {psych} rank={rank_str} urg={urg}/5 ${_cumulative_cost:.2f}")
                else:
                    print(f" → ❌ {score.get('error', 'failed')}")

                time.sleep(RATE_LIMIT_DELAY)

            # Node summary across reps
            valid_scores = [r["score"] for r in node_results if r["score"]["valid"]]
            if valid_scores:
                ranks = [s["correct_rank"] for s in valid_scores if s["correct_rank"]]
                psych_count = sum(1 for s in valid_scores if s["has_psychiatric_overlay"])
                psych_outrank = sum(1 for s in valid_scores if s["psychiatric_outranks_correct"])
                urgencies = [s["urgency_given"] for s in valid_scores]

                avg_rank = sum(ranks) / len(ranks) if ranks else None
                avg_urg = sum(urgencies) / len(urgencies) if urgencies else None

                print(f"    ╰─ Node {node['node']} summary: "
                      f"correct={len(ranks)}/{len(valid_scores)}, "
                      f"avg_rank={avg_rank:.1f}" if avg_rank else "", end="")
                if avg_rank:
                    print(f", avg_urg={avg_urg:.1f}, "
                          f"psych_overlay={psych_count}/{len(valid_scores)}, "
                          f"psych_outranks={psych_outrank}/{len(valid_scores)}")
                else:
                    print()

    print(f"\n{'='*65}")
    print(f"STUDY COMPLETE")
    print(f"  Total calls: {call_num}")
    print(f"  Total cost: ${_cumulative_cost:.4f}")
    print(f"{'='*65}")

    save_results(all_results)
    return all_results


def save_results(results):
    """Save full study results."""
    Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(RESULTS_DIR, f"full_study_{timestamp}.json")
    latest = os.path.join(RESULTS_DIR, "full_study_latest.json")

    output = {
        "study": "AI Pathway Economics — Full Study",
        "model": MODEL_ID,
        "repetitions": REPETITIONS,
        "timestamp": datetime.now().isoformat(),
        "total_cost": round(_cumulative_cost, 4),
        "hit_ceiling": _hit_ceiling,
        "total_results": len(results),
        "results": results,
    }

    for path in [filepath, latest]:
        with open(path, "w") as f:
            json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to: {filepath}")
    print(f"Latest symlink: {latest}")


if __name__ == "__main__":
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    results = run_full_study()
