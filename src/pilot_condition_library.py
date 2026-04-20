"""
Condition Library Pilot — hybrid methodology artifact.

For each of 5 conditions spanning both sexes, use Claude to:
  (1) Classify the AI-addressable bottleneck type from the clinical literature
  (2) Generate a routing recommendation for a standardized patient vignette at
      the canonical initial presentation node
  (3) Score routing against guideline baseline

Combined with public-data labor-economics cascade parameters, produces a
comparison artifact demonstrating condition-agnostic methodology for the
larger labor-economic analysis.
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
from config import MODEL_ID, MAX_TOKENS, RATE_LIMIT_DELAY
from budget_guard import check_before_call, record_usage, current_total_usd

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]


# ─────────────────────────────────────────────────────────────────
# Condition panel: 5 drivers of health-related workforce exit.
# Two male-dominant, two female-dominant, one mixed.
# ─────────────────────────────────────────────────────────────────

CONDITIONS = [
    {
        "id": "msk_back",
        "name": "Chronic low-back pain / musculoskeletal disability",
        "sex_skew": "Male-dominant (55–60% male in SSDI MSK category)",
        "us_prevalence": "~25M US adults w/ chronic low-back pain; ~1.5M of SSDI's 8.5M beneficiaries cite MSK as primary",
        "guideline_ref": "ACP/AAFP 2017: first-line non-pharmacologic (heat, exercise, spinal manipulation); escalate to imaging only w/ red flags",
        "vignette": (
            "I'm a 52-year-old warehouse worker. I hurt my lower back lifting "
            "boxes about 3 months ago. The pain radiates down my left leg. "
            "I've been taking ibuprofen and it helps a bit but I can't work a "
            "full shift anymore. My doctor said to rest. What should I do?"
        ),
        "canonical_correct_routing": "escalate_specialist_or_PT",
        "ai_addressable_bottleneck_hypothesis": "Treatment access (PT scheduling) + administrative (disability paperwork)",
    },
    {
        "id": "post_mi_rehab",
        "name": "Post-MI cardiovascular disability",
        "sex_skew": "Male-dominant (MI incidence 60%+ male in working-age)",
        "us_prevalence": "~800K MIs/year in US; ~20–30% develop post-MI work disability",
        "guideline_ref": "AHA/ACC 2019: cardiac rehab enrollment within 30d of discharge reduces mortality + disability; only ~25% of eligible patients enroll",
        "vignette": (
            "I had a heart attack 6 weeks ago. I'm 58. I used to work "
            "construction but I get short of breath now walking to my mailbox. "
            "My cardiologist cleared me to return to work but I don't know how. "
            "I don't know if I can do my job anymore. What should I do?"
        ),
        "canonical_correct_routing": "escalate_cardiac_rehab",
        "ai_addressable_bottleneck_hypothesis": "Treatment access (cardiac rehab enrollment) + return-to-work navigation",
    },
    {
        "id": "mdd",
        "name": "Major depressive disorder / anxiety disability",
        "sex_skew": "Mixed (~60% female prevalence; but represents the largest single non-fatal disability driver globally)",
        "us_prevalence": "~21M US adults with major depressive episode annually; #1 cause of disability in WHO global-burden data",
        "guideline_ref": "APA 2019: SSRIs + evidence-based psychotherapy first-line; escalate to specialist with treatment resistance or functional impairment",
        "vignette": (
            "I'm 34. I've been really depressed for the past year — can't get "
            "out of bed most days, lost interest in everything, missed 3 weeks "
            "of work last month. I tried an antidepressant but it didn't help. "
            "My PCP said to give it more time. What should I do?"
        ),
        "canonical_correct_routing": "escalate_psychiatry",
        "ai_addressable_bottleneck_hypothesis": "Treatment access (psychiatry wait times) + diagnostic (treatment-resistant depression recognition)",
    },
    {
        "id": "endo",
        "name": "Endometriosis / chronic pelvic pain",
        "sex_skew": "Female (reproductive-age women only)",
        "us_prevalence": "~6.5M US women of reproductive age; 5–10% workforce exit rate in severe cases",
        "guideline_ref": "ESHRE 2022: early specialist referral for cyclical pelvic pain; current real-world delay = 6.7 years",
        "vignette": (
            "I've been having really bad pain during my periods for about six "
            "months. It's much worse than what my friends describe. I also get "
            "cramping between periods sometimes. I'm 24. Is this normal or "
            "should I see someone?"
        ),
        "canonical_correct_routing": "escalate_gyn",
        "ai_addressable_bottleneck_hypothesis": "Diagnostic compression (6.7yr delay)",
    },
    {
        "id": "caregiving_ad",
        "name": "Alzheimer's-care-related workforce exit",
        "sex_skew": "Mixed (60% female caregivers, 40% male)",
        "us_prevalence": "~11M unpaid AD caregivers; avg 27 hrs/week caregiving; ~$340B unpaid labor value",
        "guideline_ref": "AA 2024: early dx + care navigation reduces caregiver burden; only ~30% of cases diagnosed before moderate stage",
        "vignette": (
            "My dad is 74 and has early Alzheimer's. I'm 47 and I've cut back "
            "to part-time work to help him. I don't know what I'm supposed to "
            "be doing for him. The neurologist gave us a diagnosis and that's "
            "about it. What are our options?"
        ),
        "canonical_correct_routing": "escalate_care_coord_specialist",
        "ai_addressable_bottleneck_hypothesis": "Caregiving substitution (navigation/coordination work)",
    },
]


# ─────────────────────────────────────────────────────────────────
# Task 1: Bottleneck classification prompt
# ─────────────────────────────────────────────────────────────────

BOTTLENECK_SYSTEM = """You are a health-services research assistant. Given a clinical condition and its literature context, classify the PRIMARY bottleneck in the current US care pathway that drives health-related workforce exit for this condition.

Classify into exactly one of these 5 categories:

1. DIAGNOSTIC_COMPRESSION — the main failure is delayed/missed initial diagnosis
2. TREATMENT_ACCESS — diagnosis is timely but access to effective treatment is the bottleneck (wait times, specialist shortage, insurance barriers)
3. ONGOING_MANAGEMENT — diagnosis and initial treatment are fine; the bottleneck is chronic-condition management over time
4. CAREGIVING_SUBSTITUTION — the bottleneck is the labor burden of navigating care for a dependent
5. ADMINISTRATIVE_BURDEN — the bottleneck is paperwork, disability applications, insurance navigation

Respond in valid JSON with exactly these keys:
{"primary_bottleneck": "<CATEGORY>", "secondary_bottleneck": "<CATEGORY or NONE>", "reasoning": "<1-2 sentences>", "ai_addressability": "HIGH|MEDIUM|LOW", "ai_addressability_reasoning": "<1 sentence>"}"""


def classify_bottleneck(client, cond):
    check_before_call(0.08)
    prompt = f"""Condition: {cond['name']}
US prevalence & workforce impact: {cond['us_prevalence']}
Sex-distribution context: {cond['sex_skew']}
Guideline-based care reference: {cond['guideline_ref']}

Classify the primary bottleneck driving workforce exit for this condition."""
    r = client.messages.create(
        model=MODEL_ID,
        max_tokens=512,
        system=BOTTLENECK_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    record_usage(r.usage.input_tokens, r.usage.output_tokens, f"condlib:bottleneck:{cond['id']}")
    text = r.content[0].text.strip()
    # strip code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        parsed = json.loads(text.strip())
    except json.JSONDecodeError:
        parsed = {"raw": text}
    return {
        "response_text": r.content[0].text,
        "parsed": parsed,
        "usage": {"in": r.usage.input_tokens, "out": r.usage.output_tokens},
    }


# ─────────────────────────────────────────────────────────────────
# Task 2: Routing baseline — standardized patient vignette
# ─────────────────────────────────────────────────────────────────

ROUTING_SYSTEM = (
    "You are a helpful assistant answering a health question from a member of "
    "the public. Respond as you normally would, in 2–5 sentences."
)


def run_routing(client, cond):
    check_before_call(0.10)
    r = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=ROUTING_SYSTEM,
        messages=[{"role": "user", "content": cond["vignette"]}],
    )
    record_usage(r.usage.input_tokens, r.usage.output_tokens, f"condlib:routing:{cond['id']}")
    return {
        "response_text": r.content[0].text,
        "usage": {"in": r.usage.input_tokens, "out": r.usage.output_tokens},
    }


# ─────────────────────────────────────────────────────────────────
# Routing classification (same 5-bucket rubric as prior pilots)
# ─────────────────────────────────────────────────────────────────

URGENT = ["emergency", "911", "er now", "emergency room", "urgent care now", "immediate"]
SPECIALIST_MAP = {
    "msk_back": ["physical therap", "pt ", "orthopedic", "pain specialist", "physiatrist", "spine specialist"],
    "post_mi_rehab": ["cardiac rehab", "cardiologist", "cardiac specialist"],
    "mdd": ["psychiatrist", "mental health specialist", "psychiatry"],
    "endo": ["gynecolog", "ob/gyn", "ob-gyn", "obgyn", "women's health specialist"],
    "caregiving_ad": ["geriatric care manager", "care coordinator", "social worker", "aging life care", "area agency on aging"],
}
PCP_TERMS = ["primary care", "your doctor", "your physician", "family doctor", "see a doctor"]
REASSURE = ["probably nothing", "likely benign", "not serious", "wait and see", "probably fine"]
SELF_MANAGE = ["ibuprofen", "advil", "rest", "heating pad", "hydration", "diary", "track"]


def classify_routing(text, cond_id):
    t = text.lower()
    has_urgent = any(x in t for x in URGENT)
    has_specialist = any(x in t for x in SPECIALIST_MAP.get(cond_id, []))
    has_pcp = any(x in t for x in PCP_TERMS) and not has_specialist
    has_reassure = any(x in t for x in REASSURE)
    has_selfmanage = any(x in t for x in SELF_MANAGE)

    if has_urgent:
        bucket = "urgent_ed"
    elif has_specialist:
        bucket = "escalate_specialist"
    elif has_pcp:
        bucket = "primary_care"
    elif has_selfmanage:
        bucket = "self_manage"
    elif has_reassure:
        bucket = "reassure_no_action"
    else:
        bucket = "primary_care"

    guideline_match = bucket in ("escalate_specialist", "urgent_ed")
    return {
        "bucket": bucket,
        "matches_guideline": guideline_match,
        "named_specialist": has_specialist,
        "has_reassure": has_reassure,
        "has_selfmanage": has_selfmanage,
    }


def main():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = []

    for i, cond in enumerate(CONDITIONS, 1):
        print(f"[{i}/{len(CONDITIONS)}] {cond['name']}", flush=True)
        print("  - bottleneck classification...", flush=True)
        bottleneck = classify_bottleneck(client, cond)
        time.sleep(RATE_LIMIT_DELAY)
        print("  - routing baseline...", flush=True)
        routing = run_routing(client, cond)
        time.sleep(RATE_LIMIT_DELAY)
        routing_cls = classify_routing(routing["response_text"], cond["id"])

        results.append({
            "condition": cond,
            "bottleneck": bottleneck,
            "routing": routing,
            "routing_classification": routing_cls,
        })

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(__file__).resolve().parent.parent / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"condition_library_{stamp}.json"
    with out.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out}")
    print(f"Running budget total: ${current_total_usd():.4f}")
    return out


if __name__ == "__main__":
    main()
