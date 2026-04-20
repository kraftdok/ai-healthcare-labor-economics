"""
Run the diagnostic bias experiment across multiple LLMs.

For each vignette:
1. Send to each model with a standardized system prompt
2. Request structured JSON output
3. Repeat N times (default 30) for statistical power
4. Store all raw responses with metadata
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import anthropic
import openai
from dotenv import load_dotenv

# Add project root to path for config import
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODELS, REPETITIONS, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, RATE_LIMIT_DELAY, MAX_TOKENS

load_dotenv()


def call_anthropic(model_id: str, presentation: str) -> dict:
    """Send a vignette to an Anthropic model and return the response."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(presentation=presentation)}
        ],
    )
    return {
        "raw_text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": response.model,
    }


def call_openai(model_id: str, presentation: str) -> dict:
    """Send a vignette to an OpenAI model and return the response."""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model_id,
        max_tokens=MAX_TOKENS,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(presentation=presentation)},
        ],
    )
    return {
        "raw_text": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "model": response.model,
    }


PROVIDER_DISPATCH = {
    "anthropic": call_anthropic,
    "openai": call_openai,
}


def run_experiment(vignettes_path: str = "data/vignettes.json",
                   output_dir: str = "data/results",
                   repetitions: int = REPETITIONS,
                   models: dict = None,
                   conditions: list = None):
    """
    Run the full experiment.
    
    Args:
        vignettes_path: Path to the vignettes JSON file
        output_dir: Directory to save results
        repetitions: Number of repetitions per vignette per model
        models: Override model configuration (default: use config.py)
        conditions: If provided, only run these conditions (for pilot runs)
    """
    if models is None:
        models = MODELS
    
    with open(vignettes_path) as f:
        vignettes = json.load(f)
    
    # Filter out instruction entries and pending vignettes
    vignettes = [
        v for v in vignettes
        if "vignette_id" in v and not v.get("presentation", "").startswith("PENDING")
    ]
    
    if not vignettes:
        print("ERROR: No populated vignettes found.")
        print("You need to source vignettes from PubMed case reports first.")
        print("Run: python src/vignette_builder.py")
        print("Then manually populate the 'presentation' fields in data/vignettes.json")
        return None
    
    # Filter by condition if specified
    if conditions:
        vignettes = [v for v in vignettes if v["condition"] in conditions]
        print(f"Filtered to {len(vignettes)} vignettes for conditions: {conditions}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []
    errors = 0
    
    total = len(vignettes) * len(models) * repetitions
    print(f"\nExperiment configuration:")
    print(f"  Vignettes: {len(vignettes)}")
    print(f"  Models: {list(models.keys())}")
    print(f"  Repetitions: {repetitions}")
    print(f"  Total API calls: {total}")
    print(f"  Estimated time: {total * (RATE_LIMIT_DELAY + 2) / 60:.1f} minutes")
    print()
    
    with tqdm(total=total, desc="Running experiment") as pbar:
        for vignette in vignettes:
            for model_name, model_config in models.items():
                for rep in range(repetitions):
                    try:
                        provider = model_config["provider"]
                        call_fn = PROVIDER_DISPATCH.get(provider)
                        
                        if call_fn is None:
                            raise ValueError(f"Unknown provider: {provider}")
                        
                        response = call_fn(
                            model_config["model_id"],
                            vignette["presentation"]
                        )
                        
                        result = {
                            "vignette_id": vignette["vignette_id"],
                            "condition": vignette["condition"],
                            "patient_sex": vignette["patient_sex"],
                            "patient_age": vignette["patient_age"],
                            "model": model_name,
                            "repetition": rep,
                            "timestamp": datetime.now().isoformat(),
                            "response": response,
                            "correct_diagnoses": vignette["correct_diagnoses"],
                            "correct_workup": vignette["correct_workup"],
                            "known_bias_direction": vignette.get("known_bias_direction", ""),
                            "bias_indicators": vignette.get("bias_indicators", []),
                        }
                        results.append(result)
                        
                    except Exception as e:
                        errors += 1
                        results.append({
                            "vignette_id": vignette["vignette_id"],
                            "condition": vignette.get("condition", ""),
                            "patient_sex": vignette.get("patient_sex", ""),
                            "patient_age": vignette.get("patient_age", ""),
                            "model": model_name,
                            "repetition": rep,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        })
                    
                    pbar.update(1)
                    time.sleep(RATE_LIMIT_DELAY)
    
    # Save results
    output_path = os.path.join(output_dir, f"experiment_{timestamp}.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Also save as "latest" for convenience
    latest_path = os.path.join(output_dir, "experiment_latest.json")
    with open(latest_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExperiment complete:")
    print(f"  Total results: {len(results)}")
    print(f"  Errors: {errors}")
    print(f"  Saved to: {output_path}")
    print(f"  Also saved as: {latest_path}")
    
    return output_path


def run_pilot(vignettes_path: str = "data/vignettes.json"):
    """
    Run a minimal pilot experiment.
    
    Uses only ACS atypical condition, 10 repetitions, both models.
    3 sexes × 3 ages × 10 reps × 2 models = 180 API calls
    Cost: ~$10-20 | Time: ~2 hours
    """
    print("=" * 60)
    print("PILOT RUN — Acute Coronary Syndrome (Atypical) only")
    print("=" * 60)
    
    return run_experiment(
        vignettes_path=vignettes_path,
        repetitions=10,
        conditions=["acute_coronary_syndrome_atypical"],
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the LLM diagnostic bias experiment")
    parser.add_argument("--pilot", action="store_true", help="Run pilot (ACS only, 10 reps)")
    parser.add_argument("--vignettes", default="data/vignettes.json", help="Path to vignettes file")
    parser.add_argument("--output", default="data/results", help="Output directory")
    parser.add_argument("--reps", type=int, default=None, help="Override number of repetitions")
    parser.add_argument("--condition", nargs="+", default=None, help="Only run specific conditions")
    
    args = parser.parse_args()
    
    if args.pilot:
        run_pilot(args.vignettes)
    else:
        run_experiment(
            vignettes_path=args.vignettes,
            output_dir=args.output,
            repetitions=args.reps if args.reps else REPETITIONS,
            conditions=args.condition,
        )
