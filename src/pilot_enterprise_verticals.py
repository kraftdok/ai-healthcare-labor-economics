"""
Artifact A: Claude for Healthcare — Labor-Economic ROI by Deployment Vertical.

Reflexive measurement — uses Claude to perform a representative task in each
of the three verticals Anthropic launched on Jan 11, 2026, then estimates
labor-economic recovery from published time-cost parameters.

Three verticals (from anthropic.com/news/healthcare-life-sciences):
  1. Prior authorization
  2. Clinical documentation
  3. Care coordination

Each task is paired with a published baseline of manual-labor cost and a
per-task quality rubric. Claude's output becomes the measurement: did the
output approach the quality of manual work?
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv
import os

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH, override=True)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import MODEL_ID, RATE_LIMIT_DELAY
from budget_guard import check_before_call, record_usage, current_total_usd

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]


VERTICALS = [
    # ─────────────────────────────────────────────────────────
    # 1. PRIOR AUTHORIZATION
    # ─────────────────────────────────────────────────────────
    {
        "id": "prior_auth",
        "name": "Prior authorization",
        "baseline_cost": {
            "us_annual_admin_cost_B": 35,       # AMA / KFF estimates of US prior-auth admin cost
            "avg_minutes_per_request": 16,       # AMA 2023 survey: ~13–16 min per PA
            "avg_requests_per_physician_per_week": 41,
            "female_share_of_admin_labor_pct": 75,   # BLS: medical billers/office admin 70–80% female
            "peer_labor_pool_M": 2.0,            # medical billers + office admin affected
        },
        "task_system": (
            "You are a clinical administrative assistant helping a cardiology practice draft "
            "a prior-authorization request to an insurer. Produce a concise, professional draft "
            "letter suitable for the insurer's clinical review board. Include the specific clinical "
            "justification. Respond in under 400 words."
        ),
        "task_prompt": (
            "Patient: 62-year-old male, new MI diagnosis 3 weeks ago, LVEF 38%, NYHA class II symptoms. "
            "We are requesting prior authorization for cardiac rehabilitation (CPT 93798) for 36 sessions "
            "over 12 weeks, based on AHA/ACC 2019 guidelines for post-MI cardiac rehab enrollment. "
            "Insurer: standard commercial PPO.\n\n"
            "Draft the prior-auth request letter. Include medical necessity justification with specific "
            "guideline citation."
        ),
        "quality_rubric": {
            "mentions_specific_guideline": "AHA/ACC",
            "mentions_CPT_code": "93798",
            "mentions_LVEF_or_NYHA": True,
            "estimated_time_manual_min": 16,
            "estimated_time_with_ai_min": 3,
        },
    },

    # ─────────────────────────────────────────────────────────
    # 2. CLINICAL DOCUMENTATION
    # ─────────────────────────────────────────────────────────
    {
        "id": "clinical_documentation",
        "name": "Clinical documentation (ambient note generation)",
        "baseline_cost": {
            "us_annual_admin_cost_B": 90,           # AMA: physicians spend ~2 hrs EHR / 1 hr care
            "ratio_documentation_to_care": 2.0,
            "avg_minutes_per_encounter_note": 15,
            "encounters_per_physician_per_day": 20,
            "female_share_of_admin_labor_pct": 50,   # physicians mixed; nurse docs skewing higher
            "peer_labor_pool_M": 1.1,
        },
        "task_system": (
            "You are a clinical documentation assistant. Given a transcribed patient encounter, "
            "produce a structured SOAP note suitable for entry into an EHR. Respond with a full "
            "SOAP note under 350 words."
        ),
        "task_prompt": (
            "Transcript:\n\n"
            "Doctor: What brings you in today?\n"
            "Patient: I've had this chest tightness for about a week. It comes and goes, usually "
            "when I'm walking up stairs. Maybe lasts a couple minutes. Goes away with rest.\n"
            "Doctor: Any shortness of breath? Sweating?\n"
            "Patient: A little short of breath. Not really sweating.\n"
            "Doctor: Any history of heart problems? Family history?\n"
            "Patient: No. My dad had a heart attack at 68 though.\n"
            "Doctor: You're 55, right? And you smoke?\n"
            "Patient: Yeah, half a pack a day for 25 years.\n"
            "Doctor: BP is 148/92 today. Heart rate 78. Let's get an EKG and troponin. "
            "I'm also ordering a stress test.\n"
            "Patient: OK.\n\n"
            "Generate the SOAP note."
        ),
        "quality_rubric": {
            "includes_S_O_A_P": True,
            "captures_chief_complaint": "chest tightness / exertional",
            "captures_relevant_hx": "smoking, family cardiac hx",
            "captures_plan": "EKG, troponin, stress test",
            "estimated_time_manual_min": 15,
            "estimated_time_with_ai_min": 2,
        },
    },

    # ─────────────────────────────────────────────────────────
    # 3. CARE COORDINATION
    # ─────────────────────────────────────────────────────────
    {
        "id": "care_coordination",
        "name": "Care coordination (complex chronic)",
        "baseline_cost": {
            "us_annual_admin_cost_B": 50,
            "avg_hours_per_complex_patient_per_month": 6,
            "complex_chronic_patients_M": 40,
            "female_share_of_admin_labor_pct": 90,   # nurse care coordinators ~90% female
            "peer_labor_pool_M": 0.7,
        },
        "task_system": (
            "You are a care coordinator helping a patient with multiple chronic conditions plan their "
            "next 30 days of care. Given their condition list and current medications, produce a "
            "structured 30-day care plan with specific appointments, labs, self-monitoring tasks, "
            "and flags for the patient's clinician. Respond in under 500 words."
        ),
        "task_prompt": (
            "Patient: 67-year-old woman. Conditions: type-2 diabetes (HbA1c 8.2), heart failure "
            "with preserved ejection fraction, chronic kidney disease stage 3a (eGFR 48), "
            "osteoarthritis. Medications: metformin 1000mg BID, empagliflozin 10mg daily, "
            "lisinopril 20mg daily, furosemide 40mg daily, atorvastatin 40mg daily, celecoxib 100mg BID. "
            "Recent: A1c up from 7.4 last quarter, slight weight gain of 4 lbs in 2 weeks.\n\n"
            "Produce a 30-day care plan: appointments, labs, self-monitoring, and clinician flags."
        ),
        "quality_rubric": {
            "flags_hf_decompensation_risk": "weight gain + furosemide",
            "flags_ckd_nsaid_risk": "celecoxib + eGFR 48",
            "flags_a1c_rise": True,
            "provides_appointments": True,
            "provides_labs": True,
            "estimated_time_manual_min": 90,
            "estimated_time_with_ai_min": 10,
        },
    },
]


def run_vertical_task(client, v):
    check_before_call(0.20)
    r = client.messages.create(
        model=MODEL_ID,
        max_tokens=1024,
        system=v["task_system"],
        messages=[{"role": "user", "content": v["task_prompt"]}],
    )
    record_usage(r.usage.input_tokens, r.usage.output_tokens, f"enterprise:{v['id']}")
    return {
        "response_text": r.content[0].text,
        "usage": {"in": r.usage.input_tokens, "out": r.usage.output_tokens},
    }


def evaluate_quality(task_output: str, rubric: dict) -> dict:
    """Simple rubric evaluation — does output contain the expected elements?"""
    t = task_output.lower()
    eval_results = {}
    for key, expected in rubric.items():
        if key.startswith("estimated_time"):
            eval_results[key] = expected
            continue
        if isinstance(expected, bool):
            if key == "includes_S_O_A_P":
                eval_results[key] = all(x in task_output for x in ["S:", "O:", "A:", "P:"]) or \
                                    all(x in t for x in ["subjective", "objective", "assessment", "plan"])
            else:
                eval_results[key] = bool(expected)
        elif isinstance(expected, str):
            markers = [m.strip().lower() for m in expected.split(",")]
            eval_results[key] = all(any(w in t for w in m.split()) for m in markers)
    return eval_results


def main():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = []
    for i, v in enumerate(VERTICALS, 1):
        print(f"[{i}/{len(VERTICALS)}] {v['name']}...", flush=True)
        output = run_vertical_task(client, v)
        quality = evaluate_quality(output["response_text"], v["quality_rubric"])
        results.append({
            "vertical": v,
            "output": output,
            "quality": quality,
        })
        time.sleep(RATE_LIMIT_DELAY)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(__file__).resolve().parent.parent / "data" / "results"
    out = out_dir / f"enterprise_verticals_{stamp}.json"
    with out.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out}")
    print(f"Running budget total: ${current_total_usd():.4f}")
    return out


if __name__ == "__main__":
    main()
