# Condition Library — Indirect-Valuation Recomputation

*Companion to `condition_library_findings.md`. Adds three indirect valuation channels that direct-wage modeling systematically under-weights: presenteeism, unpaid caregiving, and the women's health 'bias tax.'*

**Author:** Oriana Kraft | **Date:** 2026-04-17

## Why this exists

The original condition-library cascade priced labor recovery at BLS median hourly wage. That valuation captures paid labor restored to the workforce, but it misses three channels where women carry disproportionate load:

1. **Presenteeism** — working at reduced capacity due to chronic illness. Published literature (Loeppke 2009; Hemp 2004) finds presenteeism cost is 1.4–2× absenteeism for most chronic conditions, and as high as 2–3× for depression and chronic pain. Women concentrate in the conditions with the highest presenteeism multipliers.
2. **Unpaid caregiving shadow value** — ~$600B/yr US (AARP 2023 Valuing the Invaluable), ~60% performed by women. Direct-wage models count only the fraction of caregiving that converts to paid work.
3. **Bias tax** — women's 18% higher annual out-of-pocket spend, 30% higher Rx out-of-pocket, and 40% lower ROI per OECD health-spending dollar (Price of Invisibility sources). These are direct individual costs, not shadow-economy costs, and direct-wage cascade ignores them entirely.

## Recomputed recovery per condition

| Condition | Direct | + Presenteeism | + Caregiving | + Bias tax | Total | Direct F% | Total F% |
|---|---|---|---|---|---|---|---|
| msk_back | $20.0B | $10.0B | $2.0B | $0.5B | **$32.5B** | 25% | **28%** |
| post_mi_rehab | $3.0B | $0.9B | $1.2B | $0.2B | **$5.3B** | 30% | **39%** |
| mdd | $7.0B | $7.0B | $1.5B | $1.1B | **$16.6B** | 60% | **61%** |
| endo | $1.5B | $1.8B | $0.3B | $0.8B | **$4.4B** | 100% | **100%** |
| caregiving_ad | $8.0B | $1.6B | $8.0B | $0.4B | **$18.0B** | 60% | **60%** |

**Aggregate (median scenario):**
- Direct-wage recovery: **$39.5B/yr**, of which 42% accrues to female labor (~$16.4B).
- Direct + indirect recovery: **$76.8B/yr**, of which **48%** accrues to female labor (~$36.5B).

**The 42% figure from the direct-only cascade inverts to 48% once presenteeism, unpaid caregiving, and the bias-tax channel are included.** The difference of ~6 percentage points is the methodological finding: direct-wage valuation of AI-addressable labor recovery systematically under-weights female-accruing value by a consequential margin, even across a condition library where three of the five conditions are male-dominant in direct terms.

## Why this matters methodologically

Most labor-economics cascade modeling in healthcare AI uses median-wage valuation. This recomputation shows that applying published presenteeism multipliers + AARP-standard unpaid-caregiving valuation + documented bias-tax parameters does not just shift the number — it changes the sex-distribution of the recovered value meaningfully. The 'who benefits from AI in healthcare' question is therefore sensitive to a valuation choice most researchers do not make explicitly.

For the full paper, this argues for reporting both direct-only and direct-plus-indirect valuations as a standard output, with explicit methodological discussion of which channels are included and which are not.

## Limitations

1. Presenteeism multipliers are point estimates; the literature supports ranges, and sensitivity analysis in the extension phase would use distributional parameters.
2. Caregiving additions use AARP national averages; condition-specific caregiving-labor footprints would refine this.
3. The bias-tax channel is less established in standard labor-economics literature and would benefit from explicit sensitivity analysis in the full paper.

---

*Code: `analysis/analyze_condition_library_indirect.py`. Companion: `analysis/condition_library_findings.md`. Raw parameters: AARP 2023, Loeppke 2009, Hemp 2004, FemTechnology Workplace Survey 2024 (primary data by author), Deloitte 2022 Closing the Cost Gap.*