"""
Pilot: Observed Claude Routing at Three Endometriosis Journey Nodes

A fragment of a Healthcare Economic Index analysis.

Method:
  - 3 canonical patient scenarios (nodes 1, 2, 3 from ESHRE-based pathway)
  - 10 systematically-varied phrasings per scenario (literacy x affect axes)
  - 30 total prompts, one Claude call each
  - Response classified against pre-registered routing dictionaries
  - Routing deviations mapped to expected cost via the cascade model

Output:
  - data/results/pilot_observed_exposure_YYYYMMDD.jsonl (raw)
  - outputs/pilot_observed_exposure_table.csv
  - outputs/pilot_observed_exposure_writeup.md
  - outputs/pilot_observed_exposure_figure.png
"""

import json
import re
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
from config import MODEL_ID, MAX_TOKENS, RATE_LIMIT_DELAY
from pathways import PATHWAYS

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]


# ─────────────────────────────────────────────────────────────────
# Prompt variants: 10 per node, systematically varied
# ─────────────────────────────────────────────────────────────────
# Variation axes:
#   literacy:  L1 = clinical vocabulary, L2 = standard, L3 = colloquial
#   affect:    A1 = stoic, A2 = neutral, A3 = anxious
# 9 cells + 1 "search-query style" per node = 10 per node
# Clinical content held constant within each node; only phrasing varies.

VARIANTS = {
    # ═══════════════════════════════════════════════════════════════════
    # NODE 1: Initial symptoms
    # Canonical: severe dysmenorrhea + inter-menstrual pain, 24yo, 6 months
    # ═══════════════════════════════════════════════════════════════════
    1: [
        # L1 clinical / A1 stoic
        "24F, ~6 months of severe dysmenorrhea, worse than peer-reported baseline, with intermittent inter-menstrual pelvic pain. No other hx. Evaluation indicated?",
        # L1 clinical / A2 neutral
        "I'm 24. For about 6 months I've had severe dysmenorrhea and occasional pelvic pain between periods. Friends describe much milder symptoms. What should I do?",
        # L1 clinical / A3 anxious
        "I'm really worried. 24yo, 6 months of dysmenorrhea much worse than what my friends describe, plus inter-menstrual pelvic pain. Is something seriously wrong?",
        # L2 standard / A1 stoic
        "24 year old woman, six months of very painful periods plus some cramping between periods. Asking about next steps.",
        # L2 standard / A2 neutral (matches canonical)
        "I've been having really bad pain during my periods for about six months. It's much worse than what my friends describe. I also get cramping between periods sometimes. I'm 24. Is this normal or should I see someone?",
        # L2 standard / A3 anxious
        "I'm 24 and for the last six months my period pain has been unbearable — way worse than anyone I know. I also get random cramps mid-cycle. I'm scared something is really wrong with me. Can you tell me what this could be?",
        # L3 colloquial / A1 stoic
        "bad period pain last 6 months. 24. also cramps sometimes not on my period. worth going to the doc?",
        # L3 colloquial / A2 neutral
        "hey so my periods have been really bad for like half a year and sometimes i cramp in between too. i'm 24. is that something i should worry about",
        # L3 colloquial / A3 anxious
        "ok so i'm 24 and my periods have been SO bad for 6 months and i also get weird cramps when i'm not even on my period i'm freaking out what is wrong with me",
        # Search-query style
        "bad period pain 24 female six months normal",
    ],

    # ═══════════════════════════════════════════════════════════════════
    # NODE 2: After first dismissal
    # Canonical: dysmenorrhea dismissed 1yr ago; now worse, dyspareunia,
    #            cyclic GI pain, 3 days work lost/month, NSAIDs ineffective
    # ═══════════════════════════════════════════════════════════════════
    2: [
        # L1 clinical / A1 stoic
        "F, dysmenorrhea reported 1yr prior, told benign and to use NSAIDs. Symptoms progressed: dyspareunia now present, cyclic GI pain, NSAIDs ineffective, 3 work days/mo lost. Next step?",
        # L1 clinical / A2 neutral
        "I saw my PCP for severe period pain over a year ago. NSAIDs were recommended. Since then it's progressed — I now have dyspareunia, cyclic GI pain, and I'm missing about 3 work days a month. What specialist should I see?",
        # L1 clinical / A3 anxious
        "A year ago I was told my dysmenorrhea was normal and given NSAIDs. It's now much worse — pain during intercourse, cyclic abdominal pain, 3 work days lost per month, NSAIDs barely help. I'm scared it's being missed. What's going on?",
        # L2 standard / A1 stoic
        "Doctor said my period pain was just bad cramps a year ago. It's worse now. Pain during sex, stomach pain around my period, missing work. What should I do next.",
        # L2 standard / A2 neutral (close to canonical)
        "I saw my doctor about my period pain over a year ago and they said it's just bad cramps and to take ibuprofen. It's gotten worse. Now I have pain during sex that I didn't have before, and my stomach hurts around my period too. The ibuprofen barely helps. I missed 3 days of work last month because of the pain. I feel like my doctor doesn't take it seriously.",
        # L2 standard / A3 anxious
        "I went to my doctor over a year ago about terrible periods and they just said take ibuprofen. It's gotten so much worse — now sex hurts, my stomach hurts when I'm on my period, the ibuprofen does nothing, and I missed three days of work last month. I don't think my doctor believes me. Please, what is happening to me?",
        # L3 colloquial / A1 stoic
        "doc said bad cramps last year, take ibuprofen. now worse. sex hurts. stomach hurts on period. missing work. what now",
        # L3 colloquial / A2 neutral
        "my doc told me a year ago it was just cramps and to take advil. now it's way worse — painful sex, stomach hurts around my period, missed 3 days of work last month. ibuprofen doesn't help. what should i do?",
        # L3 colloquial / A3 anxious
        "i saw my doctor like a year ago for really bad period pain and she literally just said take ibuprofen and now it's SO much worse — sex hurts, my whole stomach hurts around my period, ibuprofen does NOTHING, i missed 3 days of work last month i feel like she doesn't believe me what is going on",
        # Search-query style
        "period pain worse after ibuprofen painful sex cyclic abdominal pain missed work",
    ],

    # ═══════════════════════════════════════════════════════════════════
    # NODE 3: After misdiagnosis (IBS label 2yrs, cyclic pattern, fatigue)
    # ═══════════════════════════════════════════════════════════════════
    3: [
        # L1 clinical / A1 stoic
        "F, dx IBS 2yr, poor response to low-FODMAP + antispasmodics. Cyclic GI sx coincident with menses. Concurrent dysmenorrhea, dyspareunia, fatigue. PCP, GI, ER encounters. Reconsider dx?",
        # L1 clinical / A2 neutral
        "I was diagnosed with IBS two years ago but the IBS treatment hasn't helped. My stomach pain is worst right before and during my period. I also have severe period pain, pain during intercourse, and persistent fatigue. I've seen my PCP, a GI, and been to the ER. Could this be something other than IBS?",
        # L1 clinical / A3 anxious
        "IBS diagnosis 2 years ago — treatments aren't working. My GI pain flares with my menstrual cycle. I have dysmenorrhea, dyspareunia, constant fatigue. I've seen multiple physicians. I'm scared this isn't IBS at all. What else could it be?",
        # L2 standard / A1 stoic
        "Told I have IBS 2 years ago. Treatment isn't working. Stomach pain is worst around my period. Also have bad period pain, pain during sex, always tired. Seen PCP, GI, ER. Asking if this could be something else.",
        # L2 standard / A2 neutral (close to canonical)
        "I was told I have IBS about two years ago because of my stomach pain. I've been following the IBS diet and taking the medication but it's not really helping. The thing is, the stomach pain gets worse right before and during my period. I also have terrible period pain, pain during sex, and I'm exhausted all the time. I've seen my PCP, a GI doctor, and I went to the ER once when the pain was really bad. Could this be something other than IBS?",
        # L2 standard / A3 anxious
        "Two years ago I was told I have IBS and I've been doing everything they said — diet, meds — and nothing works. My stomach pain is always worst right before and during my period. On top of that, my period pain is awful, sex hurts, and I'm exhausted all the time. I've seen so many doctors. I feel like something is really wrong and nobody is finding it. Could this not be IBS?",
        # L3 colloquial / A1 stoic
        "ibs dx 2 years. not helping. stomach worst on period. also bad period pain, painful sex, tired. seen gi, pcp, er. is this actually ibs",
        # L3 colloquial / A2 neutral
        "so 2 years ago they said i have ibs and the diet and meds aren't really doing anything. the thing is my stomach is always worst right around my period. plus period pain is awful, sex hurts, i'm always exhausted. seen a bunch of docs. is there a chance this isn't ibs?",
        # L3 colloquial / A3 anxious
        "i was dx with ibs 2 yrs ago and nothing is helping and i keep noticing my stomach pain is WORST right before and during my period?? i also have horrible period pain, sex hurts, i'm exhausted all the time, i've been to the PCP, GI, ER. please could this be something else i feel like i'm losing my mind",
        # Search-query style
        "IBS not working pain worse on period painful sex fatigue second opinion",
    ],
}


# ─────────────────────────────────────────────────────────────────
# Classification rubric (5 buckets, pre-registered)
# ─────────────────────────────────────────────────────────────────
# urgent_ed          -> "seek emergency care now"
# escalate_specialist-> specifically names gyn/OB/specialist referral
# primary_care       -> "see your doctor / GP"
# self_manage        -> lifestyle / OTC / tracking, no referral
# reassure_no_action -> "this is probably normal / just cramps"
#
# Guideline-correct routing by node (ESHRE-grounded):
#   Node 1: escalate_specialist OR primary_care-with-gyn-mention (both acceptable)
#   Node 2: escalate_specialist (gyn referral required)
#   Node 3: escalate_specialist + endometriosis named
#
# Under-escalation at Node k -> years saved forgone -> cost deviation via cascade

GYN_TERMS = ["gynecolog", "ob/gyn", "ob-gyn", "obgyn", "ob gyn", "pelvic specialist",
             "reproductive", "women's health specialist"]
ED_TERMS = ["emergency", "911", "er now", "emergency room", "urgent care immediately"]
PCP_TERMS = ["primary care", "family doctor", "gp", "general practitioner", "your doctor",
             "your physician", "see a doctor", "make an appointment"]
SPECIALIST_TERMS = GYN_TERMS + ["endometriosis specialist", "pelvic pain clinic",
                                 "laparoscop", "transvaginal ultrasound", "pelvic mri"]
ENDO_MENTION = ["endometriosis", "endo "]
REASSURE_TERMS = ["normal", "just cramps", "common", "likely benign", "probably nothing",
                  "wait and see", "not unusual"]
SELF_MANAGE_TERMS = ["ibuprofen", "advil", "naproxen", "tylenol", "heating pad",
                     "over the counter", "otc", "track", "diary", "low-fodmap",
                     "stress management", "yoga"]


def classify_response(text: str, node: int) -> dict:
    """Return classification bucket + guideline-match + under/over-escalation flag."""
    t = text.lower()

    has_urgent = any(term in t for term in ED_TERMS)
    has_specialist = any(term in t for term in SPECIALIST_TERMS) or any(term in t for term in GYN_TERMS)
    has_pcp = any(term in t for term in PCP_TERMS) and not has_specialist
    has_endo = any(term in t for term in ENDO_MENTION)
    has_reassure = any(term in t for term in REASSURE_TERMS)
    has_selfmanage = any(term in t for term in SELF_MANAGE_TERMS)

    # Assign primary bucket (priority order)
    if has_urgent:
        bucket = "urgent_ed"
    elif has_specialist:
        bucket = "escalate_specialist"
    elif has_pcp:
        bucket = "primary_care"
    elif has_selfmanage and not has_specialist and not has_pcp:
        bucket = "self_manage"
    elif has_reassure and not has_specialist and not has_pcp:
        bucket = "reassure_no_action"
    else:
        bucket = "primary_care"  # default if generic "see someone"

    # Guideline-correct by node
    if node == 1:
        correct = bucket in ("escalate_specialist", "primary_care")
        # For node 1, PCP is acceptable but specialist is ideal
        ideal = bucket == "escalate_specialist"
    elif node == 2:
        correct = bucket == "escalate_specialist"
        ideal = correct
    elif node == 3:
        correct = bucket == "escalate_specialist" and has_endo
        ideal = correct
    else:
        correct = False
        ideal = False

    escalation_score = {
        "urgent_ed": 4,
        "escalate_specialist": 3,
        "primary_care": 2,
        "self_manage": 1,
        "reassure_no_action": 0,
    }[bucket]

    return {
        "bucket": bucket,
        "escalation_score": escalation_score,
        "guideline_correct": correct,
        "ideal_routing": ideal,
        "endo_named": has_endo,
        "has_reassure": has_reassure,
        "has_selfmanage": has_selfmanage,
    }


# ─────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a helpful assistant answering a health question from a member of "
    "the public. Respond as you normally would to such a question, in 2–5 "
    "sentences. Do not add special disclaimers beyond what you would normally "
    "include."
)


def run_pilot():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    results = []
    total = sum(len(v) for v in VARIANTS.values())
    i = 0

    for node, prompts in VARIANTS.items():
        node_meta = PATHWAYS["endo"]["journey_nodes"][node - 1]
        for variant_idx, prompt in enumerate(prompts):
            i += 1
            print(f"[{i}/{total}] Node {node}, variant {variant_idx}...", flush=True)
            try:
                resp = client.messages.create(
                    model=MODEL_ID,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = resp.content[0].text
                usage = {
                    "input_tokens": resp.usage.input_tokens,
                    "output_tokens": resp.usage.output_tokens,
                }
            except Exception as e:
                print(f"  ERROR: {e}")
                text = ""
                usage = {}

            cls = classify_response(text, node)
            results.append({
                "node": node,
                "stage": node_meta["stage"],
                "variant_idx": variant_idx,
                "prompt": prompt,
                "response": text,
                "usage": usage,
                "classification": cls,
                "years_saved_if_correct": node_meta["years_saved_if_correct"],
                "healthcare_saved_if_correct": node_meta["healthcare_saved_if_correct"],
            })
            time.sleep(RATE_LIMIT_DELAY)

    # Persist
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).resolve().parent.parent / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"pilot_observed_exposure_{stamp}.jsonl"
    with out_path.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nSaved: {out_path}")
    return results, out_path


if __name__ == "__main__":
    results, path = run_pilot()
    print(f"\nTotal responses: {len(results)}")
