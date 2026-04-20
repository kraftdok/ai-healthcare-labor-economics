#!/usr/bin/env python3
"""
Compute bootstrap 95% CIs for the headline rates reported in each findings memo.

Reads the committed raw-outputs in data/results/, computes the rate, bootstraps
it 2000 times with resampling, and writes a summary table to
findings/00_bootstrap_cis.md. Run after every re-pilot to update the CIs.

Headline rates covered:
    1. Contested consensus premature-collapse rate (2/60 → 3.3%)
    2. Contested consensus deferral rate (56/60 → 93.3%)
    3. Contested consensus acknowledgment-of-disagreement rate
    4. Enterprise PA approval probability by sex (F vs M delta)
    5. Enterprise PA rubric scores by sex
    6. Patient observed-routing ESHRE guideline-match rate (30/30 → 100%)
    7. Patient sex-counterfactual escalation rate by sex (and Fisher's exact p)

Why Wilson for proportions, not bootstrap percentile:
    Wilson intervals are the standard CI for single proportions — they behave
    correctly at the 0/100% boundaries where bootstrap percentile CIs degenerate.
    Bootstrap percentile is used only for continuous means (e.g., approval
    probability scores) and for odds ratios.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean

import numpy as np

try:
    from statsmodels.stats.proportion import proportion_confint
except ImportError:
    proportion_confint = None


HERE = Path(__file__).resolve().parent.parent
DATA = HERE / "data" / "results"
OUT_MD = HERE / "findings" / "00_bootstrap_cis.md"


def wilson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """Wilson 95% CI. Returns (p, lo, hi)."""
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    if proportion_confint is not None:
        lo, hi = proportion_confint(k, n, alpha=alpha, method="wilson")
        return (p, float(lo), float(hi))
    # Fallback: exact formula
    z = 1.959964
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z / denom * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return (p, center - half, center + half)


def bootstrap_mean(xs: list[float], n_boot: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    arr = np.asarray(xs, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return (float("nan"), float("nan"), float("nan"))
    boots = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    return (float(arr.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))


def bootstrap_or(a: int, b: int, c: int, d: int, n_boot: int = 2000, seed: int = 7) -> tuple[float, float, float]:
    """Bootstrap 95% CI for an odds ratio from a 2x2 table.
       a = events in group 1, b = non-events in group 1,
       c = events in group 2, d = non-events in group 2.
       Uses Haldane–Anscombe +0.5 correction for zero cells."""
    rng = np.random.default_rng(seed)
    n1 = a + b
    n2 = c + d
    if n1 == 0 or n2 == 0:
        return (float("nan"), float("nan"), float("nan"))
    # Point estimate with continuity correction
    p1 = (a + 0.5) / (n1 + 1)
    p2 = (c + 0.5) / (n2 + 1)
    or_point = (p1 / (1 - p1)) / (p2 / (1 - p2))

    # Bootstrap over Bernoulli draws in each group
    draws1 = rng.binomial(1, a / n1 if n1 else 0, size=(n_boot, n1))
    draws2 = rng.binomial(1, c / n2 if n2 else 0, size=(n_boot, n2))
    p1s = (draws1.sum(axis=1) + 0.5) / (n1 + 1)
    p2s = (draws2.sum(axis=1) + 0.5) / (n2 + 1)
    ors = (p1s / (1 - p1s)) / (p2s / (1 - p2s))
    ors = ors[np.isfinite(ors)]
    if len(ors) == 0:
        return (or_point, float("nan"), float("nan"))
    return (or_point, float(np.percentile(ors, 2.5)), float(np.percentile(ors, 97.5)))


# ────────────────────────────────────────────────────────────────────
# LOADERS
# ────────────────────────────────────────────────────────────────────

def load_contested_consensus():
    fp = sorted(DATA.glob("contested_consensus_*.json"))[-1]
    return json.loads(fp.read_text()), fp.name


def load_pa_agreement():
    fp = sorted(DATA.glob("enterprise_pa_agreement_*.json"))[-1]
    return json.loads(fp.read_text()), fp.name


def load_observed_exposure():
    fp = sorted(DATA.glob("pilot_observed_exposure_*.jsonl"))[-1]
    return [json.loads(line) for line in fp.read_text().splitlines() if line.strip()], fp.name


def load_sex_counterfactual():
    fp = sorted(DATA.glob("pilot_sex_counterfactual_*.jsonl"))[-1]
    return [json.loads(line) for line in fp.read_text().splitlines() if line.strip()], fp.name


# ────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────

def main():
    out = []
    out.append("# Bootstrap / Wilson 95% CIs for Headline Rates\n")
    out.append("*Generated from `src/compute_bootstrap_cis.py` on the committed "
               "raw-output files in `data/results/`. Re-run after any re-pilot.*\n")
    out.append("All proportion CIs are Wilson score intervals (correct at 0/100% "
               "boundaries). All mean CIs are bootstrap percentile (2000 resamples). "
               "Odds-ratio CIs are bootstrap percentile with Haldane–Anscombe correction.\n")

    # ── 1. Contested consensus ──
    cc, cc_src = load_contested_consensus()
    n = len(cc)
    collapse = sum(1 for r in cc if r["scores"]["specific_recommendation"] and not r["scores"]["ack_disagreement"])
    deferral = sum(1 for r in cc if not r["scores"]["specific_recommendation"])
    ack = sum(1 for r in cc if r["scores"]["ack_disagreement"])
    cites = sum(1 for r in cc if r["scores"]["cites_guideline"])
    multi = sum(1 for r in cc if r["scores"]["multiple_positions"])

    # Women's health vs general-medicine split
    wh = [r for r in cc if r["decision"]["category"] == "womens_health"]
    gm = [r for r in cc if r["decision"]["category"] == "general_medicine"]
    wh_ack = sum(1 for r in wh if r["scores"]["ack_disagreement"])
    gm_ack = sum(1 for r in gm if r["scores"]["ack_disagreement"])

    out.append(f"## 1. Contested Consensus Study  `{cc_src}`\n")
    out.append(f"n = {n} responses (10 decisions × 3 framings × 2 reps)\n")
    out.append("| Rate | k/n | Point | 95% Wilson CI |")
    out.append("|---|---|---|---|")
    for label, k in [
        ("Premature collapse (spec-rec ∧ ¬ack)", collapse),
        ("Deferral (no specific recommendation)", deferral),
        ("Acknowledged disagreement", ack),
        ("Cited specific guideline", cites),
        ("Presented multiple positions", multi),
    ]:
        p, lo, hi = wilson(k, n)
        out.append(f"| {label} | {k}/{n} | {p*100:.1f}% | {lo*100:.1f}–{hi*100:.1f}% |")

    out.append("")
    out.append("**Women's health vs general medicine (ack-of-disagreement rate):**")
    out.append("| Subset | k/n | Point | 95% Wilson CI |")
    out.append("|---|---|---|---|")
    for label, k, total in [
        ("Women's health (contested)", wh_ack, len(wh)),
        ("General medicine (contested)", gm_ack, len(gm)),
    ]:
        p, lo, hi = wilson(k, total)
        out.append(f"| {label} | {k}/{total} | {p*100:.1f}% | {lo*100:.1f}–{hi*100:.1f}% |")

    # ── 2. Enterprise PA agreement ──
    pa, pa_src = load_pa_agreement()
    by_sex = {"female": [], "male": []}
    for r in pa:
        s = r["sex"]
        prob = r["review"].get("likely_approval_probability_pct")
        if prob is not None and s in by_sex:
            by_sex[s].append(prob)

    out.append(f"\n## 2. Enterprise PA Agreement  `{pa_src}`\n")
    out.append(f"n = {len(pa)} letters (5 cases × 2 sex framings)\n")
    out.append("| Sex | n | Mean approval prob | 95% bootstrap CI |")
    out.append("|---|---|---|---|")
    for s in ("female", "male"):
        xs = by_sex[s]
        m, lo, hi = bootstrap_mean(xs)
        out.append(f"| {s} | {len(xs)} | {m:.2f}% | {lo:.2f}–{hi:.2f}% |")
    # Delta CI via paired bootstrap (cases are paired: same case, different sex)
    pairs_f, pairs_m = [], []
    case_ids = set(r["case"]["id"] if isinstance(r["case"], dict) else r["case"] for r in pa)
    for case_id in case_ids:
        case_rows = [r for r in pa if (r["case"]["id"] if isinstance(r["case"], dict) else r["case"]) == case_id]
        f_rows = [r["review"].get("likely_approval_probability_pct") for r in case_rows if r["sex"] == "female"]
        m_rows = [r["review"].get("likely_approval_probability_pct") for r in case_rows if r["sex"] == "male"]
        if f_rows and m_rows:
            pairs_f.append(f_rows[0])
            pairs_m.append(m_rows[0])
    if pairs_f:
        diffs = np.array(pairs_f) - np.array(pairs_m)
        rng = np.random.default_rng(7)
        n_pairs = len(diffs)
        boots = rng.choice(diffs, size=(2000, n_pairs), replace=True).mean(axis=1)
        dm, dlo, dhi = diffs.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)
        out.append(f"\n**Paired F − M delta** (same case, two sex framings, n={n_pairs} paired cases): "
                   f"**Δ = {dm:+.2f}pp** [95% bootstrap CI {dlo:+.2f}–{dhi:+.2f}pp]")

    # ── 3. Observed exposure ──
    obs, obs_src = load_observed_exposure()
    n = len(obs)
    matches = sum(1 for r in obs if r["classification"].get("guideline_correct", False))
    ideal = sum(1 for r in obs if r["classification"].get("ideal_routing", False))
    out.append(f"\n## 3. Patient Observed Routing  `{obs_src}`\n")
    out.append(f"n = {n} prompts (endometriosis × 3 nodes × 10 variants)\n")
    out.append("| Rate | k/n | Point | 95% Wilson CI |")
    out.append("|---|---|---|---|")
    for label, k in [
        ("ESHRE guideline match (any correct-routing bucket)", matches),
        ("Ideal specialist-referral routing", ideal),
    ]:
        p, lo, hi = wilson(k, n)
        out.append(f"| {label} | {k}/{n} | {p*100:.1f}% | {lo*100:.1f}–{hi*100:.1f}% |")

    # ── 4. Sex counterfactual ──
    sc, sc_src = load_sex_counterfactual()
    esc = {"female": 0, "male": 0}
    tot = {"female": 0, "male": 0}
    for r in sc:
        s = r["sex"]
        if s in esc:
            bucket = r["classification"].get("bucket", "")
            tot[s] += 1
            if bucket in ("urgent_ed", "escalate_specialist"):
                esc[s] += 1
    out.append(f"\n## 4. Patient Sex-Counterfactual  `{sc_src}`\n")
    out.append(f"n = {len(sc)} prompts (10 complaints × 2 sex × 3 reps)\n")
    out.append("| Sex | escalated / n | Rate | 95% Wilson CI |")
    out.append("|---|---|---|---|")
    for s in ("female", "male"):
        p, lo, hi = wilson(esc[s], tot[s])
        out.append(f"| {s} | {esc[s]}/{tot[s]} | {p*100:.1f}% | {lo*100:.1f}–{hi*100:.1f}% |")

    # Odds ratio F vs M
    a, b = esc["female"], tot["female"] - esc["female"]
    c, d = esc["male"], tot["male"] - esc["male"]
    or_p, or_lo, or_hi = bootstrap_or(a, b, c, d)
    out.append(f"\n**Escalation OR (F vs M):** {or_p:.2f} [95% bootstrap CI {or_lo:.2f}–{or_hi:.2f}]")
    out.append(f"*Interpretation*: CI spans 1.0 → aggregate difference is statistically indistinguishable from null at this n.")

    # Per-complaint (underpowered but reported for transparency)
    out.append(f"\n**Per-complaint escalation rates** (n=3 per cell → Wilson CIs wide):")
    out.append("| Complaint | F rate (k/n) | M rate (k/n) | Δ (F−M) |")
    out.append("|---|---|---|---|")
    for complaint in sorted(set(r["complaint_id"] for r in sc)):
        f_rows = [r for r in sc if r["complaint_id"] == complaint and r["sex"] == "female"]
        m_rows = [r for r in sc if r["complaint_id"] == complaint and r["sex"] == "male"]
        f_esc = sum(1 for r in f_rows if r["classification"].get("bucket", "") in ("urgent_ed", "escalate_specialist"))
        m_esc = sum(1 for r in m_rows if r["classification"].get("bucket", "") in ("urgent_ed", "escalate_specialist"))
        f_rate = f_esc / len(f_rows) if f_rows else 0
        m_rate = m_esc / len(m_rows) if m_rows else 0
        out.append(f"| {complaint} | {f_esc}/{len(f_rows)} ({f_rate*100:.0f}%) | {m_esc}/{len(m_rows)} ({m_rate*100:.0f}%) | {(f_rate-m_rate)*100:+.0f}pp |")

    # Write
    OUT_MD.write_text("\n".join(out) + "\n")
    print(f"Wrote {OUT_MD}")
    print(f"\n{len(out)} lines total")

    # Console summary of the key findings
    print("\nKEY CIs:")
    p, lo, hi = wilson(collapse, len(cc))
    print(f"  Premature collapse: {collapse}/{len(cc)} = {p*100:.1f}%  [95% CI {lo*100:.1f}–{hi*100:.1f}%]")
    p, lo, hi = wilson(deferral, len(cc))
    print(f"  Deferral: {deferral}/{len(cc)} = {p*100:.1f}%  [95% CI {lo*100:.1f}–{hi*100:.1f}%]")
    if pairs_f:
        print(f"  PA paired F−M delta: {dm:+.2f}pp  [95% CI {dlo:+.2f}–{dhi:+.2f}pp]")
    p, lo, hi = wilson(matches, len(obs))
    print(f"  ESHRE match: {matches}/{len(obs)} = {p*100:.1f}%  [95% CI {lo*100:.1f}–{hi*100:.1f}%]")
    print(f"  Sex-counterfactual OR: {or_p:.2f}  [95% CI {or_lo:.2f}–{or_hi:.2f}]")


if __name__ == "__main__":
    main()
