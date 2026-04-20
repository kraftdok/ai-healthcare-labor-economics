"""
Run Study: AI Clinical Intermediary — Voice Divergence, Equity, and Corrective Potential.

Executes all prompt combinations across conditions and stores structured results.

Usage:
    python src/run_study.py              # Full study (240 calls, ~$5)
    python src/run_study.py --pilot      # Pilot run (48 calls, ~$1)
    python src/run_study.py --condition acs    # Single condition
    python src/run_study.py --dry-run    # Print prompts without calling API
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ANTHROPIC_API_KEY, MODEL_ID, REPETITIONS, PILOT_REPETITIONS,
    RATE_LIMIT_DELAY, MAX_TOKENS, TEMPERATURE, RESULTS_DIR
)
from conditions import ALL_CONDITIONS, get_system_prompt, get_prompt_pairs


def call_claude(system_prompt: str, user_prompt: str) -> dict:
    """Send a prompt to Claude and return the parsed response."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=MODEL_ID,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text.strip()
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }

        # Try to parse JSON from response
        try:
            # Handle potential markdown code blocks
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()

            parsed = json.loads(raw_text)
            return {"parsed": parsed, "raw": raw_text, "usage": usage, "error": None}
        except json.JSONDecodeError:
            return {"parsed": None, "raw": raw_text, "usage": usage,
                    "error": "JSON parse failed"}

    except Exception as e:
        return {"parsed": None, "raw": None, "usage": None, "error": str(e)}


def build_experiment_matrix(conditions: list, reps: int) -> list:
    """
    Build the full experiment matrix.

    For each condition:
      - 2 voice/framing types (patient/clinician or male/female)
      - 2 prompt modes (baseline / corrective)
      - N repetitions

    Returns list of experiment dicts.
    """
    experiments = []

    for cond in conditions:
        prompt_pairs = get_prompt_pairs(cond)
        corrective = cond.get("corrective_system_prompt")

        for voice_label, prompt_text in prompt_pairs:
            for mode in ["baseline", "corrective"]:
                system = get_system_prompt(
                    voice_label,
                    corrective if mode == "corrective" else None
                )

                for rep in range(reps):
                    experiments.append({
                        "condition_id": cond["id"],
                        "condition_name": cond["name"],
                        "group": cond["group"],
                        "voice": voice_label,
                        "mode": mode,
                        "repetition": rep + 1,
                        "system_prompt": system,
                        "user_prompt": prompt_text,
                    })

    return experiments


def run_experiment(experiments: list, dry_run: bool = False) -> list:
    """Execute all experiments and return results."""
    results = []
    total = len(experiments)
    total_input_tokens = 0
    total_output_tokens = 0

    print(f"\n{'='*60}")
    print(f"AI CLINICAL INTERMEDIARY STUDY")
    print(f"{'='*60}")
    print(f"Total experiments: {total}")
    print(f"Model: {MODEL_ID}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    for i, exp in enumerate(experiments):
        label = (f"[{i+1}/{total}] {exp['condition_id']} | "
                 f"{exp['voice']} | {exp['mode']} | rep {exp['repetition']}")

        if dry_run:
            print(f"  DRY RUN: {label}")
            print(f"    System: {exp['system_prompt'][:80]}...")
            print(f"    User:   {exp['user_prompt'][:80]}...")
            print()
            continue

        print(f"  Running: {label}", end="", flush=True)

        response = call_claude(exp["system_prompt"], exp["user_prompt"])

        result = {
            **exp,
            "timestamp": datetime.now().isoformat(),
            "model": MODEL_ID,
            "response": response,
        }
        # Don't store the full prompts in results (save space)
        result.pop("system_prompt")
        result.pop("user_prompt")

        results.append(result)

        if response["usage"]:
            total_input_tokens += response["usage"]["input_tokens"]
            total_output_tokens += response["usage"]["output_tokens"]
            cost_est = (total_input_tokens * 3 / 1_000_000 +
                        total_output_tokens * 15 / 1_000_000)

        if response["error"]:
            print(f" ❌ {response['error']}")
        else:
            print(f" ✓")

        time.sleep(RATE_LIMIT_DELAY)

    if not dry_run:
        cost_est = (total_input_tokens * 3 / 1_000_000 +
                    total_output_tokens * 15 / 1_000_000)
        print(f"\n{'='*60}")
        print(f"COMPLETE")
        print(f"  Total tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
        print(f"  Estimated cost: ${cost_est:.2f}")
        print(f"  Success rate: {sum(1 for r in results if r['response']['parsed'])}/{total}")
        print(f"{'='*60}\n")

    return results


def save_results(results: list, output_dir: str):
    """Save results to timestamped JSON file."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"study_results_{timestamp}.json")

    # Also save as latest
    latest_path = os.path.join(output_dir, "latest_results.json")

    metadata = {
        "study": "AI Clinical Intermediary: Voice Divergence, Equity, and Corrective Potential",
        "model": MODEL_ID,
        "timestamp": datetime.now().isoformat(),
        "total_experiments": len(results),
        "conditions": list(set(r["condition_id"] for r in results)),
        "successful": sum(1 for r in results if r["response"]["parsed"]),
        "failed": sum(1 for r in results if r["response"]["error"]),
    }

    output = {"metadata": metadata, "results": results}

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    with open(latest_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {filepath}")
    print(f"Latest symlink: {latest_path}")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Run AI Clinical Intermediary Study"
    )
    parser.add_argument("--pilot", action="store_true",
                        help="Pilot run (1 rep per combination, ~$1)")
    parser.add_argument("--condition", type=str,
                        help="Run only a specific condition (e.g., 'acs', 'endo')")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print prompts without calling API")
    parser.add_argument("--reps", type=int,
                        help="Override number of repetitions")
    args = parser.parse_args()

    # Validate API key
    if not args.dry_run and not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Create a .env file with: ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    # Filter conditions if specified
    conditions = ALL_CONDITIONS
    if args.condition:
        conditions = [c for c in ALL_CONDITIONS if c["id"] == args.condition]
        if not conditions:
            valid = [c["id"] for c in ALL_CONDITIONS]
            print(f"ERROR: Unknown condition '{args.condition}'")
            print(f"Valid: {valid}")
            sys.exit(1)

    # Set repetitions
    reps = args.reps or (PILOT_REPETITIONS if args.pilot else REPETITIONS)

    # Build experiment matrix
    experiments = build_experiment_matrix(conditions, reps)

    # Estimate cost
    est_tokens_per_call = 1500  # ~800 system + 200 user + 500 output
    est_cost = len(experiments) * est_tokens_per_call * 9 / 1_000_000  # blended rate
    print(f"\nExperiment matrix: {len(experiments)} API calls")
    print(f"Estimated cost: ~${est_cost:.2f}")

    if not args.dry_run:
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            sys.exit(0)

    # Run
    results = run_experiment(experiments, dry_run=args.dry_run)

    # Save
    if not args.dry_run and results:
        save_results(results, RESULTS_DIR)

    return results


if __name__ == "__main__":
    main()
