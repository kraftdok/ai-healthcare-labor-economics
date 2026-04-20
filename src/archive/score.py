"""
Score Study Responses: Compare AI outputs against clinical ground truth.

Scores each response on:
1. Diagnostic accuracy — is the correct diagnosis in top N?
2. Urgency appropriateness — is urgency at or above minimum?
3. Referral appropriateness — are correct specialties recommended?
4. Test appropriateness — are critical tests recommended?
5. Dismissal detection — is the primary diagnosis an inappropriate dismissal?

Usage:
    python src/score.py                     # Score latest results
    python src/score.py --input path.json   # Score specific file
"""

import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conditions import ALL_CONDITIONS
from config import RESULTS_DIR, TABLES_DIR


def normalize(text: str) -> str:
    """Normalize text for fuzzy matching."""
    return text.lower().strip().replace("-", " ").replace("_", " ")


def fuzzy_match(candidate: str, targets: list) -> bool:
    """Check if candidate matches any target (case-insensitive, substring)."""
    candidate_norm = normalize(candidate)
    for target in targets:
        target_norm = normalize(target)
        if target_norm in candidate_norm or candidate_norm in target_norm:
            return True
    return False


def score_group_a(response: dict, condition: dict) -> dict:
    """Score a Group A (sex-specific) response against ground truth."""
    gt = condition["ground_truth"]
    parsed = response.get("response", {}).get("parsed")

    if not parsed:
        return {"valid": False, "error": "No parsed response"}

    diagnoses = parsed.get("top_diagnoses", [])
    urgency = parsed.get("urgency", 0)
    referrals = parsed.get("recommended_referrals", [])
    tests = parsed.get("recommended_tests", [])

    scores = {"valid": True}

    # 1. Is correct diagnosis in top 3?
    top3_diags = [d.get("diagnosis", "") for d in diagnoses[:3]]
    top1_diag = diagnoses[0].get("diagnosis", "") if diagnoses else ""
    all_diags = [d.get("diagnosis", "") for d in diagnoses]

    scores["correct_in_top1"] = fuzzy_match(top1_diag, gt["must_be_top3"])
    scores["correct_in_top3"] = any(
        fuzzy_match(d, gt["must_be_top3"]) for d in top3_diags
    )
    scores["correct_in_top5"] = any(
        fuzzy_match(d, gt["must_be_top3"]) for d in all_diags
    )

    # 2. Is the primary diagnosis an inappropriate dismissal?
    scores["dismissed"] = fuzzy_match(
        top1_diag, gt.get("inappropriate_if_primary", [])
    )

    # 3. Urgency appropriate?
    try:
        urgency_val = int(urgency)
    except (ValueError, TypeError):
        urgency_val = 0
    scores["urgency"] = urgency_val
    scores["urgency_appropriate"] = urgency_val >= gt["minimum_urgency"]
    scores["urgency_gap"] = gt["minimum_urgency"] - urgency_val  # positive = under-triaged

    # 4. Referrals
    scores["correct_referral"] = any(
        fuzzy_match(r, gt["required_referrals"]) for r in referrals
    )

    # 5. Tests
    scores["correct_tests"] = any(
        fuzzy_match(t, gt["important_tests"]) for t in tests
    )

    # 6. Composite score (0-5)
    scores["composite"] = sum([
        scores["correct_in_top3"],       # 1 point
        not scores["dismissed"],          # 1 point (not dismissed)
        scores["urgency_appropriate"],    # 1 point
        scores["correct_referral"],       # 1 point
        scores["correct_tests"],          # 1 point
    ])

    # Store the actual outputs for analysis
    scores["diagnoses_given"] = [d.get("diagnosis", "") for d in diagnoses]
    scores["referrals_given"] = referrals
    scores["tests_given"] = tests

    return scores


def score_group_b(response: dict, condition: dict) -> dict:
    """Score a Group B (sex-differential) response against ground truth."""
    gt = condition["ground_truth"]
    parsed = response.get("response", {}).get("parsed")

    if not parsed:
        return {"valid": False, "error": "No parsed response"}

    diagnoses = parsed.get("top_diagnoses", [])
    urgency = parsed.get("urgency", 0)
    referrals = parsed.get("recommended_referrals", [])
    tests = parsed.get("recommended_tests", [])
    voice = response.get("voice", "")

    scores = {"valid": True}

    # 1. Is the correct (shared) diagnosis present?
    top3_diags = [d.get("diagnosis", "") for d in diagnoses[:3]]
    top1_diag = diagnoses[0].get("diagnosis", "") if diagnoses else ""
    all_diags = [d.get("diagnosis", "") for d in diagnoses]

    scores["correct_in_top1"] = fuzzy_match(top1_diag, gt["both_must_include"])
    scores["correct_in_top3"] = any(
        fuzzy_match(d, gt["both_must_include"]) for d in top3_diags
    )
    scores["correct_in_top5"] = any(
        fuzzy_match(d, gt["both_must_include"]) for d in all_diags
    )

    # 2. Urgency appropriate (same threshold for both sexes)?
    try:
        urgency_val = int(urgency)
    except (ValueError, TypeError):
        urgency_val = 0
    scores["urgency"] = urgency_val
    scores["urgency_appropriate"] = urgency_val >= gt["both_minimum_urgency"]
    scores["urgency_gap"] = gt["both_minimum_urgency"] - urgency_val

    # 3. Referrals
    scores["correct_referral"] = any(
        fuzzy_match(r, gt["both_required_referrals"]) for r in referrals
    )

    # 4. Tests
    scores["correct_tests"] = any(
        fuzzy_match(t, gt["both_important_tests"]) for t in tests
    )

    # 5. Inappropriate dismissal for female/non-textbook presentation?
    dismiss_key = "female_should_NOT_get"
    if "male_should_NOT_get" in gt and voice == "male_presentation":
        dismiss_key = "male_should_NOT_get"

    scores["dismissed"] = fuzzy_match(
        top1_diag, gt.get(dismiss_key, [])
    )

    # 6. Composite (0-5)
    scores["composite"] = sum([
        scores["correct_in_top3"],
        not scores["dismissed"],
        scores["urgency_appropriate"],
        scores["correct_referral"],
        scores["correct_tests"],
    ])

    scores["diagnoses_given"] = [d.get("diagnosis", "") for d in diagnoses]
    scores["referrals_given"] = referrals
    scores["tests_given"] = tests

    return scores


def score_all(results_path: str) -> dict:
    """Score all results from a study run."""
    with open(results_path) as f:
        data = json.load(f)

    results = data["results"]
    condition_lookup = {c["id"]: c for c in ALL_CONDITIONS}
    scored = []

    for r in results:
        cond_id = r["condition_id"]
        cond = condition_lookup.get(cond_id)
        if not cond:
            continue

        if cond["group"] == "A":
            score = score_group_a(r, cond)
        else:
            score = score_group_b(r, cond)

        scored.append({
            "condition_id": cond_id,
            "condition_name": r["condition_name"],
            "group": r["group"],
            "voice": r["voice"],
            "mode": r["mode"],
            "repetition": r["repetition"],
            "scores": score,
        })

    return {
        "metadata": data["metadata"],
        "scored_results": scored,
        "summary": compute_summary(scored),
    }


def compute_summary(scored: list) -> dict:
    """Compute aggregate summary statistics."""
    summary = {}

    # Group by condition
    conditions = set(s["condition_id"] for s in scored)

    for cid in sorted(conditions):
        cond_results = [s for s in scored if s["condition_id"] == cid]
        cond_name = cond_results[0]["condition_name"]
        group = cond_results[0]["group"]

        voices = set(s["voice"] for s in cond_results)
        modes = set(s["mode"] for s in cond_results)

        cond_summary = {"name": cond_name, "group": group, "comparisons": {}}

        for mode in sorted(modes):
            mode_results = [s for s in cond_results if s["mode"] == mode]

            voice_scores = {}
            for voice in sorted(voices):
                vr = [s for s in mode_results
                      if s["voice"] == voice and s["scores"].get("valid")]

                if not vr:
                    continue

                composites = [s["scores"]["composite"] for s in vr]
                urgencies = [s["scores"]["urgency"] for s in vr]

                voice_scores[voice] = {
                    "n": len(vr),
                    "composite_mean": round(sum(composites) / len(composites), 2),
                    "urgency_mean": round(sum(urgencies) / len(urgencies), 2),
                    "correct_top3_rate": round(
                        sum(1 for s in vr if s["scores"]["correct_in_top3"]) / len(vr), 2
                    ),
                    "dismissal_rate": round(
                        sum(1 for s in vr if s["scores"]["dismissed"]) / len(vr), 2
                    ),
                    "urgency_appropriate_rate": round(
                        sum(1 for s in vr if s["scores"]["urgency_appropriate"]) / len(vr), 2
                    ),
                }

            # Compute voice divergence
            voice_list = sorted(voice_scores.keys())
            if len(voice_list) == 2:
                v1, v2 = voice_list
                divergence = {
                    "composite_gap": round(
                        voice_scores[v1]["composite_mean"] -
                        voice_scores[v2]["composite_mean"], 2
                    ),
                    "urgency_gap": round(
                        voice_scores[v1]["urgency_mean"] -
                        voice_scores[v2]["urgency_mean"], 2
                    ),
                    "correct_top3_gap": round(
                        voice_scores[v1]["correct_top3_rate"] -
                        voice_scores[v2]["correct_top3_rate"], 2
                    ),
                    "dismissal_gap": round(
                        voice_scores[v1]["dismissal_rate"] -
                        voice_scores[v2]["dismissal_rate"], 2
                    ),
                }
            else:
                divergence = None

            cond_summary["comparisons"][mode] = {
                "voice_scores": voice_scores,
                "divergence": divergence,
            }

        # Compute corrective delta
        baseline = cond_summary["comparisons"].get("baseline", {})
        corrective = cond_summary["comparisons"].get("corrective", {})

        if baseline.get("divergence") and corrective.get("divergence"):
            cond_summary["corrective_delta"] = {
                "composite_gap_change": round(
                    abs(corrective["divergence"]["composite_gap"]) -
                    abs(baseline["divergence"]["composite_gap"]), 2
                ),
                "urgency_gap_change": round(
                    abs(corrective["divergence"]["urgency_gap"]) -
                    abs(baseline["divergence"]["urgency_gap"]), 2
                ),
            }

        summary[cid] = cond_summary

    return summary


def print_summary(scored_data: dict):
    """Print a human-readable summary."""
    summary = scored_data["summary"]

    print(f"\n{'='*70}")
    print(f"STUDY RESULTS SUMMARY")
    print(f"{'='*70}\n")

    for cid, cond in summary.items():
        print(f"{'─'*70}")
        print(f"  {cond['name']} (Group {cond['group']})")
        print(f"{'─'*70}")

        for mode, data in cond["comparisons"].items():
            print(f"\n  Mode: {mode.upper()}")

            for voice, vs in data["voice_scores"].items():
                print(f"    {voice}:")
                print(f"      Composite: {vs['composite_mean']}/5  |  "
                      f"Correct dx: {vs['correct_top3_rate']:.0%}  |  "
                      f"Dismissed: {vs['dismissal_rate']:.0%}  |  "
                      f"Urgency: {vs['urgency_mean']:.1f}  |  "
                      f"Urgency OK: {vs['urgency_appropriate_rate']:.0%}")

            if data.get("divergence"):
                d = data["divergence"]
                print(f"    → DIVERGENCE: composite={d['composite_gap']:+.2f}  "
                      f"urgency={d['urgency_gap']:+.2f}  "
                      f"dismissal={d['dismissal_gap']:+.2f}")

        if cond.get("corrective_delta"):
            cd = cond["corrective_delta"]
            direction = "↓ NARROWED" if cd["composite_gap_change"] < 0 else "↑ WIDENED"
            print(f"\n  ⚕ CORRECTIVE EFFECT: Gap {direction} by "
                  f"{abs(cd['composite_gap_change']):.2f} composite points")

        print()


def save_scored(scored_data: dict, output_dir: str):
    """Save scored results."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(output_dir, "scored_results.json")
    with open(path, "w") as f:
        json.dump(scored_data, f, indent=2)
    print(f"Scored results saved to: {path}")


def main():
    parser = argparse.ArgumentParser(description="Score study results")
    parser.add_argument("--input", type=str,
                        default=os.path.join(RESULTS_DIR, "latest_results.json"),
                        help="Path to results JSON")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Results file not found: {args.input}")
        print(f"Run the study first: python src/run_study.py --pilot")
        sys.exit(1)

    print(f"Scoring results from: {args.input}")
    scored_data = score_all(args.input)
    print_summary(scored_data)
    save_scored(scored_data, TABLES_DIR)


if __name__ == "__main__":
    main()
