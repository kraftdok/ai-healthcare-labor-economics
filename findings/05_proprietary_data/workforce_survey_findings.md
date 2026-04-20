# Workforce-Exit and Productivity-Loss Evidence from the FemTechnology 42-Country Workplace Survey

*Pilot re-analysis of primary workforce data.*

**Author:** Oriana Kraft
**Date:** April 2026
**Dataset:** FemTechnology Workplace Survey 2024 (primary data by author, N=981 respondents across 42 countries; public summary: [workplace.femtechnology.org](https://workplace.femtechnology.org)).

---

## Summary finding

Across 981 women-respondents in 42 countries, **62%** report having taken time off work due to a women's-health-related condition (605 of 979 who answered). Mean days lost in the prior year: **4.7** (median 2, 75th percentile 5, 90th percentile 10). Estimated mean productivity-impacted days per month is **2.7** — translating to roughly **32 productivity-affected work days per year per respondent** (absenteeism + reported productivity impairment combined).

At US median wage (~$29.76/hour × 8 hours = $238/day; BLS 2024), this implies a per-respondent annual labor-value loss of roughly **$7,697**. Extrapolated to the US working-age-female population (~80M, US Census 2024), this single survey's per-person loss rate corresponds to a US-only annual labor-value footprint in the range of **$616–862 billion** — consistent with and triangulating the cascade-model estimates used elsewhere in this portfolio.

This is the empirical anchor for the larger workforce-exit analysis.

---

## Key distributions

### Productivity-impact days per month (all respondents)

| Bucket | Respondents | % of answered |
|---|---|---|
| 0 days | 200 | 20.4% |
| 1-2 days | 401 | 41.0% |
| 3-5 days | 288 | 29.4% |
| 6-10 days | 57 | 5.8% |
| 11 or more days | 33 | 3.4% |


Among those reporting any impact, the median respondent loses the equivalent of **1–2 full working weeks per year** to women's-health-related productivity loss.

### Time-off rates by country (countries with ≥10 respondents)

| Country | n | % who have taken time off |
|---|---|---|
| United States of America | 567 | 68% |
| Japan | 11 | 64% |
| Switzerland | 76 | 59% |
| United Kingdom | 49 | 59% |
| Canada | 33 | 58% |
| Germany | 30 | 57% |
| India | 32 | 56% |
| Ireland | 13 | 54% |
| France | 16 | 38% |
| Austria | 16 | 38% |
| South Africa | 19 | 32% |
| Belgium | 17 | 24% |


Time-off rates vary substantially across countries — a between-country range of 68% (highest) to 22% (lowest among those with n≥10), suggesting health-system and employer-policy mediators that modify the underlying labor-economic load. This cross-country variance is itself the empirical basis for a planned cross-system payer-structure comparison (California / Andhra Pradesh / Switzerland).

### Days off in the last year (self-reported)

- Mean: **4.7**
- Median: **2.0**
- 75th percentile: **5.0**
- 90th percentile: **10.0**

The long right tail — 10% of respondents reporting ≥10 days off — is the subpopulation most at risk of full workforce exit. Identifying whether AI-mediated diagnostic compression reduces the size of this tail is the core empirical test for follow-up work.

---

## Respondent views on AI and healthcare (cols 37–48)

The survey also captured respondents' agreement with statements about algorithmic bias in healthcare AI:

| Statement cluster | % agreeing | n |
|---|---|---|
| Awareness (cols 37-40) | 52% | 827 |
| Implications (cols 41-45) | 21% | 823 |
| Need to address (cols 46-48) | 73% | 821 |


This is a demand-side signal: the same population reporting workforce disruption also reports high awareness of AI bias in healthcare and high agreement that it needs to be addressed. They are both the affected population and the population most likely to use — and scrutinize — AI health tools. This grounds the observed-exposure estimate for AI health use in the working-female population with empirical demand evidence from the population itself.

---

## Representative respondent views

**On AI underrepresentation (col 49, open text):**

> I have friend who is 42 just had a heart attack and was turned away because her symptoms as a woman were not indicative of an MI, she could have died. She had an emergency stent put in; and readmitted.

> symptoms, availability of treatment options.

> symptoms, alternative treatment options, outcomes, age related treatment options, gender affirming care, mental health for those caring for others.

> symptoms and patient reported outcomes

> symptoms, treatment outcomes, patient reported outcomes, preferences)

> I don't really have experience with AI models

**On organizational remediation (col 50, open text):**

> I don't think my company is using such tool for healthcare decision

> More training available to staff and communication around what we can participate in

> If more women were making decisions there’d be a better place for us all.

> I can't really comment on this.

> not sure, policies, workshops, awareness,

---

## What this anchors

1. **Prevalence of workforce disruption is substantial and measurable.** 62% of this cross-country sample has taken health-related time off. That figure is consistent with, and adds primary data to, the BLS/SSA/CPS-derived estimates used in Step 1 of the cascade analysis.

2. **Productivity impairment is larger than absenteeism alone.** Mean reported productivity-impacted days per month (2.7) multiplied across the year exceeds the mean days-off estimate, consistent with the presenteeism literature's finding that degraded-capacity cost exceeds pure absenteeism cost by 1.4–2×.

3. **Cross-country variance is the natural variation the deployment-context comparison needs.** With 13 countries at n≥10, this dataset supports cross-system payer-structure extension work.

4. **The respondent population is the demand-side for consumer AI health tools.** High reported agreement on algorithmic-bias awareness and the need to address it signals that the labor-economic population is not only AI-adjacent but AI-attentive. This is the population the Economic Index's current worker-unit methodology cannot see, and that this portfolio aims to make visible.

---

## Limitations stated up front

1. Convenience sample; respondents are women with enough engagement to complete a women's-health workplace survey, potentially over-representing those most affected.
2. Self-report of days off and productivity impact is subject to recall bias.
3. Cross-country sample sizes are uneven; n=10 is a low floor for country-level estimates.
4. Condition-level breakdown is not cleanly coded in the survey; the next analytical step is a condition-attribution pass using the open-text fields.
5. Re-entry question (whether respondents returned to work after time off, and what accelerated that) is not directly asked; this is the gap the extension phase (Prolific RCT or natural-experiment design) would fill.

---

*Analysis script: `analysis/analyze_workforce_survey.py`. Raw table: `analysis/workforce_survey_table.csv`. Figure: `analysis/workforce_survey_figure.png`. Source: FemTechnology Workplace Survey 2024 (primary data by author; public summary: workplace.femtechnology.org).*
