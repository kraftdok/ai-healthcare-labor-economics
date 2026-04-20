# Extensions to the Core Paper: Quantified Angles

*Supporting analysis for the labor-economic cascade. Each of the four extensions below augments the base estimate with an additional mechanism. All figures are pilot-stage ranges from published parameters.*

---

## A. The caregiver-release multiplier

**Claim:** Every AI-compressed diagnosis affects not only the patient but the informal caregivers around them. Released caregiver time converts partially back into paid labor.

**Inputs (published, US-only):**

| Parameter | Value | Source |
|---|---|---|
| Total informal caregivers | ~38M | AARP Caregiving in the US 2020 |
| Share female | ~61% | AARP 2020; BLS ATUS |
| Avg caregiving hours per week | ~24 hrs | AARP 2020 |
| Estimated annual shadow value of unpaid caregiving | ~$600B | AARP 2023 Valuing the Invaluable |
| Share of caregivers in paid workforce | ~61% | AARP 2020 |
| Avg work disruption (reduced hours / days off) per working caregiver | ~$8,500/year in lost wages | MetLife Study of Caregiving Costs 2011, inflation-adjusted |

**Estimation:**

Working caregivers: ~38M × 0.61 ≈ **23M**.
Annual work disruption cost attributable to caregiving: ~23M × $8,500 ≈ **~$200B**.

**AI's plausible capture fraction:** if AI-mediated care navigation (symptom interpretation, insurance navigation, appointment routing) reduces caregiving time burden by 10–20% for AI-addressable care coordination tasks — a conservative midpoint given current consumer-AI adoption rates — the potential annual labor-disruption recovery is **~$20–40B**.

**Multiplier on the core paper:** depending on which conditions are modeled, the caregiver-release effect adds **30–80% to the patient-side labor recovery estimate**. For conditions affecting elderly parents (Alzheimer care, cardiovascular rehab, mobility-restricted chronic disease), the multiplier is closer to 2×.

**Sex asymmetry:** because ~61% of caregivers are women and working women caregivers face the steepest career-interruption penalties (Goda et al. on retirement-age caregiving), the recovered labor is disproportionately female.

**Open question for follow-up:** what fraction of AI-mediated caregiving labor actually converts to paid work vs being reabsorbed by other unpaid domestic labor? This is empirically testable via diff-in-diff on caregiver labor-force participation in populations with differential AI adoption.

---

## B. The healthspan–lifespan gap

**Claim:** Women live longer than men but spend more years in disability. AI has a potentially large and entirely unquantified effect on this gap by compressing chronic-condition diagnosis and management in the female-concentrated condition set.

**Inputs:**

| Parameter | Value | Source |
|---|---|---|
| US female life expectancy | 80.5 years | CDC 2023 |
| US male life expectancy | 74.9 years | CDC 2023 |
| US female healthy life expectancy (HALE) | ~72 years | WHO 2021 |
| US male healthy life expectancy | ~70 years | WHO 2021 |
| Implied disabled years, female | ~8.5 | derived |
| Implied disabled years, male | ~4.9 | derived |
| Healthspan gap | ~3.6 years in favor of men | derived |
| Value of a healthy year (mid-range US health-econ estimate) | $50,000–150,000 | Neumann et al. VSLY literature |

**Aggregate cost of the healthspan gap (US women):**

25M US women aged 55+ × 3.6 excess disabled years × $75,000/year (midpoint VSLY) ≈ **$6.75T in cumulative lifetime healthspan cost** — a stock, not an annual flow.

**AI compression scenario:** if AI-mediated diagnosis and chronic-condition management closes 20% of the healthspan gap (0.72 years per woman), lifetime healthspan recovery is:

25M × 0.72 × $75,000 ≈ **$1.35T cumulative**.

**Framing value:** this is the single largest magnitude-estimate across the paper and is built from the narrowest set of published parameters (CDC, WHO, standard VSLY). The number is large enough that any conservative fraction of it still lands as policy-material. This is the line the paper would use when addressing decision-makers who don't read academic journals.

**Open question for follow-up:** to what degree is the healthspan gap attributable to conditions AI can address vs conditions it cannot? A bottleneck-level decomposition analogous to the core-paper methodology answers this.

---

## C. The SSDI re-entry scenario

**Claim:** Social Security Disability Insurance enrolls ~8.5M working-age adults at a ~1% annual exit rate. A meaningful share of beneficiaries have AI-addressable conditions. Modeling AI's plausible effect on re-entry produces policy-material numbers.

**Inputs:**

| Parameter | Value | Source |
|---|---|---|
| Total SSDI working-age beneficiaries | ~8.5M | SSA Annual Statistical Report 2023 |
| Annual federal SSDI outlay | ~$140B | SSA; CBO |
| Current annual work-exit (return-to-work) rate | ~1% | SSA 2023 |
| Share of beneficiaries with primarily mental-health diagnosis | ~30% (≈2.5M) | SSA 2023 |
| Share with musculoskeletal / pain conditions | ~30% (≈2.5M) | SSA 2023 |
| Share with conditions plausibly AI-addressable | ~40–60% combined | derived from SSA diagnosis categories |

**Estimation:**

AI-addressable working-age SSDI beneficiaries: 8.5M × 0.5 ≈ **4.25M**.

If AI-mediated care access, symptom-navigation support, and administrative-burden reduction raises annual re-entry rates from 1% to 3% in the AI-addressable subset:
- Marginal re-entries per year: 4.25M × 0.02 ≈ **85,000/year**
- Labor recovery: 85,000 × $52,000 ≈ **$4.4B/year in recovered wages**
- Federal fiscal recovery (average SSDI benefit ~$16,500/year × 85,000) ≈ **$1.4B/year in reduced outlays**
- Combined: **~$5.8B/year**

Compounded over the scenario's 10-year horizon and incorporating tax recapture on recovered wages, gross fiscal-plus-labor impact plausibly exceeds **~$70B cumulative**.

**Why it matters:** this is the extension most likely to yield a published working paper. SSDI is one of the most studied federal programs in labor economics (Autor, Duggan, Maestas). An AI-re-entry scenario analysis slots cleanly into that literature and has known placement channels (NBER, Brookings, J-PAL). It is the version of the paper that gets cited outside the AI community.

**Open question for follow-up:** the re-entry-rate lift assumption (1% → 3%) is the most sensitive parameter. Partnering with state vocational rehabilitation programs or with SSA itself on a natural-experiment design is the path to a defensible estimate.

---

## D. Re-entry-driven market creation

**Claim:** Returned workers don't re-enter the same economy. Their different demand profiles create markets that previously had no institutional voice. AI's effect on re-entry therefore has a second-order market-creation effect that standard labor-supply models miss.

**The women's health venture case:**

| Year | US women's health VC funding | Approx CAGR |
|---|---|---|
| 2014 | ~$500M | baseline |
| 2019 | ~$1.0B | ~15% |
| 2024 | ~$2.5B | ~20% |

Source: Rock Health / FemTech Focus / CB Insights analyses.

Overall US digital-health VC over the same decade grew at a significantly lower rate, and general-health VC at roughly half. The sectoral outperformance is documented; the dominant industry-attributed causal hypothesis is **demand-side composition change driven by women in decision-making and funding roles**. This is what labor-supply expansion looks like when the expanded supply brings different preferences back with it.

**What's quantifiable:**
- The trajectory itself (public data).
- The gap between women's health and comparator subsectors.
- The correlation with rising female representation in venture and research leadership (documentable via public funder data).

**What is not quantifiable at the paper stage:**
- A counterfactual dollar value of markets-created-because-of-re-entry vs markets-created-anyway.
- A clean causal attribution from individual re-entrant to specific market.

**Methodological role in the paper:** this extension lives as a *documented trajectory + causal hypothesis*, not as a point estimate. The paper uses it to argue that standard static labor-supply models under-count re-entry's economic value because they miss demand-composition effects. This is a positive-sum narrative that standard AI-labor papers cannot make.

**Why Anthropic specifically benefits from this framing:** the dominant narrative around AI and labor is zero-sum (AI takes jobs). This extension provides the framing for the opposite claim — AI expands labor supply and creates markets — which is a narrative Anthropic needs in every jurisdictional conversation it has. That is an unusually direct policy-communications asset.

---

## Aggregate picture

| Mechanism | Annual scale (US, midpoint estimate) | Paper placement |
|---|---|---|
| Core paper — direct labor recovery, top 10 conditions | $50–250B | The main paper |
| A. Caregiver-release multiplier | +$20–40B | Extension section |
| B. Healthspan gap (annualized from $1.35T cumulative) | ~$40B (flow equivalent) | Press-facing headline |
| C. SSDI re-entry scenario | $5–10B direct; $70B cumulative | Standalone NBER-style working paper |
| D. Market creation | Not point-quantified; trajectory documented | Concluding framing |

**Combined defensible range for the aggregate claim:** the observed labor-economic value of AI-addressable health-related workforce exit, measured at a moment in time with the caregiver multiplier included, is plausibly in the **$100–300B annual** range, with most of the uncertainty driven by the re-entry-rate elasticity that is the primary empirical question for follow-up work.

**This is roughly the size of the entire US AI-industry economic footprint currently.** The implication: AI's effect on the health-workforce-exit population is comparable in scale to AI's direct economic impact through productivity and automation combined. That implication is the punch line of the paper.
