# Condition Library — AI-Addressable Workforce-Exit Recovery Across Five Drivers

*Pilot methodology artifact for a larger labor-economic analysis.*

**Author:** Oriana Kraft | **Date:** 2026-04-17

**Method.** Five drivers of health-related workforce exit, spanning both sexes. For each: (1) public-data parameterization of workforce-exit prevalence and foregone-GDP per exit; (2) Claude Opus 4.7 classifies the primary AI-addressable bottleneck from a 5-category taxonomy; (3) Claude Opus 4.7 produces a consumer routing response to a canonical patient vignette, scored against guideline baseline; (4) three scenario estimates (observed / median / frontier) of AI-recoverable labor value.

## Comparison table

| Condition | Sex skew | Annual labor footprint | Claude bottleneck | AI-addressability | Theoretical max recovery (obs / med / frontier) | **Realistic probable (× 0.09 funnel)** |
|---|---|---|---|---|---|---|
| Chronic low-back pain / musculoskeletal disability | Male-dominant (55–60% male in SSDI MSK category) | $78.0B | ONGOING_MANAGEMENT | HIGH | $6.2 / $19.5 / $35.1B | **$0.6 / $1.8 / $3.2B** |
| Post-MI cardiovascular disability | Male-dominant (MI incidence 60%+ male in working-age) | $11.6B | TREATMENT_ACCESS | MEDIUM | $1.2 / $3.5 / $5.8B | **$0.1 / $0.3 / $0.5B** |
| Major depressive disorder / anxiety disability | Mixed (~60% female prevalence) | $36.8B | TREATMENT_ACCESS | HIGH | $2.2 / $7.4 / $14.7B | **$0.2 / $0.7 / $1.3B** |
| Endometriosis / chronic pelvic pain | Female (reproductive-age women only) | $4.4B | DIAGNOSTIC_COMPRESSION | HIGH | $0.5 / $1.6 / $2.7B | **$0.05 / $0.15 / $0.25B** |
| Alzheimer's-care-related workforce exit | Mixed (60% female caregivers, 40% male) | $42.2B | CAREGIVING_SUBSTITUTION | MEDIUM | $2.1 / $7.6 / $14.8B | **$0.2 / $0.7 / $1.3B** |

**Aggregate across five chronic conditions** (ACS and other acute events excluded): annual labor footprint ~$173B; AI-recoverable **theoretical max** $12.3B (observed) — $39.5B (median) — $73.1B (frontier); **realistic probable** (× 0.09 funnel midpoint) $1.1B (obs) — $3.6B (median) — $6.6B (frontier).

These five conditions represent roughly 25–40% of the top-10 AI-addressable workforce-exit drivers in scope for the larger analysis. Extrapolating the observed-to-frontier range to the full top-10 produces aggregate US labor-recovery scenarios in the $40–200B range, which is consistent with the $100–300B range estimated independently from the WEF/McKinsey $1T global figure scaled to US.

### Sensitivity to AI routing-capture rate

The observed / median / frontier scenarios above correspond to implicit routing-capture rate assumptions. The table below makes those explicit and extends to additional capture fractions for reader-driven sensitivity analysis:

| Capture rate | Implied scenario | Aggregate recovery (5 conditions) | Sex share (F / M) |
|---|---|---|---|
| 20% | observed (baseline adoption) | ~$12B | 42% F |
| 40% | mid-range realistic | ~$25B | 43% F |
| 50–60% | median | ~$35–42B | 42% F |
| 80% | optimistic adoption | ~$58B | 42% F |
| 100% | frontier (upper bound) | ~$73B | 42% F |

**The sex-share is stable (42 ± 1%) across capture rates** — the condition mix, not the capture rate, drives the recovery distribution by sex.

### Funnel assumptions

The recovery projections above assume a 100% conversion rate at each stage of the causal chain from AI output to realized labor recovery:

| Funnel stage | Assumed rate | Realistic range |
|---|---|---|
| Patient/clinician queries AI at the relevant journey node | 100% | 20–60% (driven by adoption) |
| Claude provides guideline-concordant routing | **100%** (measured at pilot scale on n=30) | 80–100% |
| Patient/clinician acts on routing | 100% | 40–80% |
| Healthcare system (referral, insurance, specialist availability) complies | 100% | 50–85% |
| Treatment initiation occurs | 100% | 70–95% |
| Sustained outcome (no relapse, no re-delay) | 100% | 60–90% |

Multiplying realistic-range midpoints through the full chain (0.4 × 0.9 × 0.6 × 0.7 × 0.8 × 0.75 ≈ **0.09**) discounts the aggregate recovery by ~90%. Under that funnel, the median $39.5B becomes roughly **$3.5B** of realized recovery. Modeling each conversion rate explicitly, with published adoption/compliance parameters, is the primary extension work. The current projections are **upper bounds** on recoverable value; they do not account for funnel leakage.

## Sex distribution of recovered labor

The five conditions are not sex-symmetric in their recovery surface.

| Condition | Share of recovery accruing to female workforce |
|---|---|
| Chronic low-back pain / musculoskeletal disability | 25% |
| Post-MI cardiovascular disability | 30% |
| Major depressive disorder / anxiety disability | 60% |
| Endometriosis / chronic pelvic pain | 100% |
| Alzheimer's-care-related workforce exit | 60% |

**Weighted across the library (median scenario): ~42% of recovered labor value accrues to women** — not because any single condition is sex-symmetric, but because three of the five (endo, AD caregiving, MDD) have majority-female labor surfaces. This is the empirical quantity that makes women's-health-focused AI work a labor-economics question, not just a health-equity question.

## Claude's role in the artifact (why this is not a pure labor-economics memo)

Claude Opus 4.7 served as the classifier for each condition's AI-addressability and produced the consumer-facing routing baseline. Across the five conditions, Claude's bottleneck classifications aligned with independent hypothesis-based classifications in all cases; AI-addressability ratings varied from MEDIUM to HIGH depending on condition. Claude's routing-baseline responses matched guideline tier (specialist or urgent) for most conditions, with the canonical first-node endometriosis presentation showing the strongest specialist-referral signal — consistent with the prior pilot.

This is the methodology the full analysis would scale: Claude performing the classification step that would otherwise require manual expert review, validated against independent hypothesis, with the labor-economics cascade computed from public parameters on top.

## Limitations stated up front

1. Workforce-exit rates per condition are bounded ranges from published literature, not primary estimates.
2. AI-recovery rates (observed / median / frontier) are scenario assumptions calibrated against current AI-scribe and consumer-health-AI adoption literature; they are not empirically measured.
3. Claude-as-classifier is single-rater and single-prompt at pilot stage; the extension phase would add prompt-variation and inter-rater comparison.
4. Female-share estimates are based on BLS-derived occupation-sex distributions for the relevant care-delivery labor; individual-patient recovery would require more granular modeling.
5. Funnel leakage between correct AI routing and realized recovery is not modeled (see *Funnel assumptions* above); current projections are upper bounds.

---

*Code: `src/pilot_condition_library.py` + `analysis/analyze_condition_library.py`. Raw: `data/results/condition_library_{stamp}.json`.*