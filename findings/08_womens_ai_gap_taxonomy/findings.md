# The Shadow Taxonomy of Women's AI-Healthcare Gaps

## A Clio-Style Taxonomy of 618 Open-Ended Responses from 981 Working Women Across 42 Countries

*Primary-data empirical analysis. Clio-style two-stage taxonomy (Tamkin, Handa, Durmus et al., 2024) applied to survey free-text responses. Author: Oriana Kraft. April 2026.*

---

## One-paragraph summary

In a primary-data survey of 981 working women across 42 countries, 618 respondents answered two open-ended questions: (Q49) where AI healthcare fails women, and (Q50) what organizations should do about it. We taxonomize these responses into 16 themes (Q49) and 9 themes (Q50). **Five novel findings emerge, none of which appears in the existing published literature on AI healthcare bias:** (1) working women name **symptom-presentation gaps** more than any specific disease (29% primary / 37% any-label), (2) **menopause/perimenopause** is the top specific-condition gap (10% primary), ahead of cardiovascular, reproductive, and autoimmune conditions, (3) a **measurable AI-literacy gap** — 15% of Q49 and 30% of Q50 respondents report they don't know enough about AI to answer, (4) respondents name **"collect more data" (23%)** as the dominant organizational remedy but only **1.4% name "bias audits"** — the most technically sophisticated fix — suggesting working women understand the *input* problem but not the *deployment-time* mitigation tools, and (5) despite a women-only respondent pool, **only 0.3%** spontaneously name *hire women into AI leadership* as a remedy.

---

## Method

**Data:** FemTechnology Workplace Survey 2024 (primary data by author; public summary at [workplace.femtechnology.org](https://workplace.femtechnology.org)). 981 women-respondents across 42 countries. This analysis uses the two open-ended questions (Q49, Q50) that 330 and 288 respondents answered non-trivially.

**Taxonomy construction (Clio-style, two-stage):**
- *Stage 1* — human-read all 618 responses, propose a taxonomy of 16 Q49 themes and 9 Q50 themes, each with a definition and canonical example quote.
- *Stage 2* — rule-based classifier with priority-ordered keyword matching assigns each response a primary theme (first matching bucket wins) plus all secondary themes it matches. Manual spot-check of ~50 responses confirms ≥90% classification agreement with reading-time interpretation.

**Code + data:** [`src/taxonomy_analysis.py`](../../src/taxonomy_analysis.py) · [`q49_labeled.csv`](q49_labeled.csv) · [`q50_labeled.csv`](q50_labeled.csv) · [`taxonomy.json`](taxonomy.json) · raw responses at [`q49_raw.json`](q49_raw.json) and [`q50_raw.json`](q50_raw.json) (country-tagged, PII-stripped).

---

## Q49: Where does AI healthcare fail women? (n=330 non-empty)

| Rank | Theme | Primary label | Any-label | Notable quote |
|---|---|---|---|---|
| 1 | Symptoms-presentation (women's symptoms differ from men's, not captured) | **29.4%** | 36.7% | *"All — so often, women's symptoms are attributed to 'stress' or their cycle and disregarded. Women go untreated, or over-treated."* (US) |
| 2 | AI-literacy / refusal to engage | **13.0%** | 14.8% | *"I have no experience with AI models."* / *"I don't think AI models belong in healthcare at all."* |
| 3 | Menopause & perimenopause | **10.0%** | 10.0% | *"So many symptoms related to menopause — weight gain, joint pain, elevated cholesterol — are not being treated as menopausal in nature."* (US) |
| 4 | Treatment outcomes / PROs / preferences | **6.7%** | 25.8% | *"Symptoms, treatment outcomes, patient reported outcomes, preferences."* (multiple, echoing SurveyMonkey prompt options) |
| 5 | "Across the board" / all areas | 5.2% | 6.7% | *"Across the board — limited publicly available data, limited R&D investment, antiquated medical practices, under-reporting."* (US) |
| 6 | Cardiovascular disease (female atypical presentation) | **3.3%** | 4.5% | *"I have a friend who is 42 just had a heart attack and was turned away because her symptoms as a woman were not indicative of an MI. She could have died."* (US) |
| 7 | Fertility / pregnancy / postpartum | 3.0% | 5.5% | *"I was shocked when I was pregnant at the lack of information from medication on pregnancy."* (US) |
| 8 | Intersectional (women of color, mature, LMIC, trans/non-binary) | 2.7% | 3.3% | *"I would like to see more emphasis on transgender and non-binary employees and understanding and supporting their unique needs."* (US) |
| 9 | Clinical trial underrepresentation | 2.4% | 3.6% | *"Women's underrepresentation in clinical trials — both as Principal Investigators and as Patients."* (Germany) |
| 10 | Pharmacokinetics / dosing (drugs tested on male subjects) | 1.8% | 3.6% | *"'The normal dose' mandated on label (eg for hormones) is often not appropriate for me, leading me to question the diversity of data used to set the doses."* (UK) |
| 11 | Endometriosis / PCOS / fibroids | 1.8% | 3.6% | *"Where I live there are practically no doctors who can diagnose and treat endometriosis. This is very scary for all the women who suffer from that condition."* (Czech Republic) |
| 12 | Medical dismissal / gaslighting | 1.2% | 1.8% | *"Symptoms even such as extreme fatigue during PMS is not believed and I have been told many times that I should just deal with it."* (US) |
| 13–16 | Mental health / ADHD, pain management, cancer, autoimmune, caregiver burden, diagnostic accuracy, treatment access | <2% each | 1–7% each | (specific condition clusters) |

*"Other" residual: 13.0% — responses too generic ("needs study", "lab data") to assign a theme.*

## Q50: What should organizations do? (n=288 non-empty)

| Rank | Theme | Primary | Notable quote |
|---|---|---|---|
| 1 | Don't know / not my company / N/A | **29.9%** | *"I am unsure if my organization uses AI models for healthcare decisions."* |
| 2 | Collect more representative data | **23.3%** | *"Diverse data collection: ensure datasets include a balanced representation of women across age, race, and medical conditions, capturing gender-specific symptoms, outcomes, and experiences."* (Austria) |
| 3 | Education / awareness / training | 12.2% | *"Proactively build new databases after raising awareness of their support of women's health. It still won't be perfect given how embedded bias is."* (US) |
| 4 | Clinical trial diversity | 2.4% | *"More inclusive clinical trials (not just gender, but gender breakdown by different racial groups)."* (US) |
| 5 | Sex-stratified data / gender-specific models | 1.7% | *"Develop gender-specific models; increase collaboration with healthcare experts."* (India) |
| 6 | Human-in-the-loop / limit AI scope | 1.7% | *"AI should not be making decisions; it can provide information, options."* (US) |
| 7 | Bias audit / fairness testing | **1.4%** | *"Conduct regular bias audits on AI models to identify and mitigate any potential gender biases."* (US) |
| 8 | Regulatory standards / policy | 1.4% | *"Demand insurance companies work on this issue — cover more tests."* (US) |
| 9 | Hire women into AI leadership | **0.3%** | *"Employ a more diverse executive leadership / decision-making team."* (US) |

*"Other" residual: 25.7%.*

---

## Cross-country patterns

**Top-5 country primary-theme distributions (Q49):**

| Country | n | Top theme (primary) | % |
|---|---|---|---|
| United States | 198 | Symptoms-presentation | 24% |
| Switzerland | 22 | **Symptoms-presentation** | **45%** |
| Canada | 15 | **AI-literacy / refusal** | **27%** |
| United Kingdom | 14 | Symptoms-presentation | 43% |
| India | 11 | **PROs / preferences** | **27%** |

**Interpretation.** Swiss and UK respondents concentrate on symptoms-presentation more than any other country (45% and 43%), while the US is symptoms-dominant but shows the highest AI-literacy-refusal rate (15%). Canadian respondents show an even higher refusal rate (27%) — a pattern that warrants follow-up. Indian respondents, uniquely, foreground *patient-reported outcomes and preferences* (27%) rather than symptoms — suggesting a different framing of the AI-bias question in LMIC-adjacent respondents, consistent with distinct healthcare delivery structures (out-of-pocket payment, lower LLM-deployment rates).

**LMIC subset (India, Brazil, Mexico, South Africa, Turkey, Colombia, Libya, n=23):** symptoms-presentation remains the top theme (35%), but AI-literacy refusal is lower than in US/Canada (9% vs 15%/27%) — possibly reflecting lower AI deployment familiarity rather than informed refusal.

---

## Five novel findings

1. **Symptoms-presentation dominates over any specific disease.** The dominant perceived AI-healthcare failure mode among working women is not cardiovascular or reproductive or autoimmune — it's *the upstream training-data problem that women's symptoms present differently from men's and are not captured*. This finding reframes the AI-bias conversation: respondents intuitively identify the training-data gap as the structural issue, not any one clinical domain.

2. **Menopause is the #1 specific condition.** Across 42 countries, 10% of responses name menopause or perimenopause as the specific condition-level gap, ahead of cardiovascular (3.3%), reproductive conditions (3.0% fertility/pregnancy + 1.8% endo/PCOS/fibroids), autoimmune (<1%), and cancer (0.6%). Published AI-healthcare-bias literature under-indexes menopause research almost entirely; respondent perception contradicts that.

3. **Measurable AI-literacy gap in the working-women population.** 15% of Q49 and 30% of Q50 respondents are primary-labeled as "don't know" / "unfamiliar" / "unaware of AI use." This is the same population reporting 77% agreement that the gender data gap impacts AI healthcare quality (main survey finding) — meaning **women are concerned about AI healthcare bias but simultaneously report insufficient understanding of how AI is being deployed in their own care**. This is a consumer-protection finding and a policy-relevance finding.

4. **The "data-in vs audit-out" asymmetry.** 23% of Q50 respondents name "collect more data" as the remedy. Only 1.4% name "bias audit / fairness testing." Working women understand the *input-side* fix (more data) intuitively but do not name the *deployment-time mitigation* (audits, fairness standards). This is a literacy-curriculum finding: if AI-ethics training is to equip this population, it must teach the deployment-time toolkit, not just the training-data framing.

5. **Women do not spontaneously name "hire women into AI leadership" as a fix.** Only 0.3% of 288 respondents — in a women-only respondent pool — name representation in AI leadership as the organizational remedy. Respondents name data, education, stratification, and audits before they name representation. This contradicts the dominant public-discourse framing that "the fix for AI gender bias is more women in AI."

---

## Limitations

1. **Convenience sample.** Recruited via FemTechnology channels; respondents are women engaged enough to complete a women's-health workplace survey. Likely over-represents those most affected; under-represents women without AI-adjacent workplaces.
2. **Rule-based classifier.** Priority-ordered keyword matching has ~90% spot-check agreement with reading but is not a Clio-style embedding-based clustering. An LLM-judge validation pass is the extension step.
3. **Response-length bias.** Short responses ("symptoms") dominate the primary-theme counts. Multi-label (any-theme) analysis partially addresses this.
4. **Country-level cells are small** (non-US countries n=4–22). Country comparisons beyond the top-5 have wide confidence bounds.
5. **Q49 "other" bucket is 13%.** Responses too generic ("needs study", "lab data", "across the board" without specifics) to classify. Not discarded — labeled as "other."
6. **US dominance.** 198/330 = 60% of Q49 responses are US. Cross-country generalization is bounded.

---

## Extension work

- **LLM-embedding-based clustering** to complement rule-based classifier; measure inter-method agreement.
- **Second-stage inductive theme discovery** — what themes did I miss that a full Clio pass would surface?
- **Cross-tabulate with structured survey data** — do respondents who report higher personal workforce disruption (Q4) name different themes than those who report less disruption?
- **Expand sample to physician respondents** (the 200-physician survey) — where do women and physicians *agree* on gap locations?
- **Comparative corpus** — does this taxonomy match what appears in Claude conversation logs (Huang et al. Clio methodology applied to real AI usage)?

---

## Citation

> Kraft, O. *The Shadow Taxonomy of Women's AI-Healthcare Gaps: A Clio-Style Analysis of 618 Open-Ended Responses from 981 Working Women Across 42 Countries.* FemTechnology Research, April 2026.
> Repository: `github.com/kraftdok/ai-healthcare-labor-economics`

*Source data: FemTechnology Workplace Survey 2024 (primary data by author, N=981 × 42 countries). Public summary: [workplace.femtechnology.org](https://workplace.femtechnology.org).*
