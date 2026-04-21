#!/usr/bin/env python3
"""
Taxonomy of where working women identify AI healthcare as failing women.

Input: 618 open-ended responses from the FemTechnology Workplace Survey
(N=981 × 42 countries, primary data by author). Columns Q49 and Q50:

    Q49 (n=330 non-empty): "In what specific areas in healthcare are women's
        health needs underrepresented in the data used for AI models?"
    Q50 (n=288 non-empty): "What steps do you think your organization could
        take to minimize gender bias in AI models used for healthcare
        decisions?"

Method: two-stage Clio-style taxonomy (Tamkin, Handa, Durmus et al., 2024),
but applied to survey free-text. Stage 1 — taxonomy proposed from reading a
large sample of responses. Stage 2 — rule-based classifier (priority-ordered
keyword matching) assigns each response to the most specific theme it matches,
plus optional secondary themes. Manual spot-check of ~50 responses confirms
precision.

All PII has been stripped; responses are tagged only by country.

Output:
    findings/08_womens_ai_gap_taxonomy/q49_labeled.csv
    findings/08_womens_ai_gap_taxonomy/q50_labeled.csv
    findings/08_womens_ai_gap_taxonomy/taxonomy.json
    findings/08_womens_ai_gap_taxonomy/findings.md
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "findings" / "08_womens_ai_gap_taxonomy"

# ---------------------------------------------------------------------------
# Q49 TAXONOMY — where AI healthcare fails women
# Priority-ordered: first-matching theme wins for primary label. Keywords are
# lowercased; matching is substring-based on lowercased response text.
# ---------------------------------------------------------------------------

Q49_TAXONOMY = [
    # Specific conditions / lifecycle — check first so they win over generic "symptoms"
    {
        "theme": "menopause_perimenopause",
        "definition": "Menopausal and perimenopausal health — brain fog, HRT, post-menopausal symptoms, hormonal lifecycle gaps.",
        "keywords": ["menopaus", "peri-menopaus", "perimenopaus", "peri menopaus", "hrt", "post-menopaus", "post menopaus", "hormone replacement", "brain fog"],
        "example_quote": "So many symptoms related to menopause — weight gain, joint pain, elevated cholesterol — are not being treated as menopausal in nature. Instead, they are being treated independently, and those treatments are often ineffective.",
    },
    {
        "theme": "cardiovascular_female_presentation",
        "definition": "Cardiovascular disease in women — atypical MI/stroke presentations, women dismissed at ED with cardiac symptoms.",
        "keywords": ["cardiovasc", "heart attack", "heart disease", "heart health", "heart failure", "cardiac", "cvd", "chest pain", "atrial fib", "afib", "mi ", " mi,", " mi.", "stroke"],
        "example_quote": "I have a friend who is 42 just had a heart attack and was turned away because her symptoms as a woman were not indicative of an MI. She could have died.",
    },
    {
        "theme": "endometriosis_pcos_fibroids",
        "definition": "Reproductive-system conditions: endometriosis, PCOS, fibroids, ovarian cysts, pelvic pain.",
        "keywords": ["endometrios", "pcos", "polycystic", "fibroid", "ovarian cyst", "pelvic pain", "endo ", "endo,", "endo.", " endo"],
        "example_quote": "Anything related to women's pain management, PCOS and endometriosis simply due to poor understanding and therefore poor availability of good data.",
    },
    {
        "theme": "fertility_pregnancy_postpartum",
        "definition": "Fertility, pregnancy, postpartum health, maternal mental health, medication during pregnancy.",
        "keywords": ["fertilit", "pregnan", "postpartum", "post-partum", "post partum", "ppd", "maternal", "child birth", "childbirth", "breastfeed"],
        "example_quote": "I was shocked when I was pregnant at the lack of information from medication on pregnancy.",
    },
    {
        "theme": "pharmacokinetics_dosing",
        "definition": "Medications tested on male subjects, wrong doses for women, pharmacokinetic sex differences, drug labels.",
        "keywords": ["dos", "pharmaceu", "drug", "pharma", "medication", "label", "male subject", "tested on men", "mandated on label"],
        "example_quote": "Pharmaceuticals, drugs researched and brought to market based on studies of male subjects traditionally.",
    },
    {
        "theme": "clinical_trials_representation",
        "definition": "Historical underrepresentation of women in clinical trials; exclusion of pregnant women, postpartum women, and older women.",
        "keywords": ["clinical trial", "trial enrollment", "trial represent", "trials", "study design", "enroll", "research design", "pregnant women in clinical", "rct"],
        "example_quote": "Women's underrepresentation in clinical trials — both as Principal Investigators and as Patients.",
    },
    {
        "theme": "medical_dismissal_gaslighting",
        "definition": "Symptoms dismissed as stress, cycle, psychological; women labeled complainers; doctors ignoring women's concerns.",
        "keywords": ["dismiss", "gaslight", "ignored", "ignore", "not believed", "complainer", "neurotic", "attention seek", "stress or", "attributed to stress", "attributed to their cycle", "symptoms were psychological"],
        "example_quote": "Doctors ignore women's comments regarding their health more than men. Women can be seen as complainers and neurotic.",
    },
    {
        "theme": "autoimmune",
        "definition": "Autoimmune conditions (RA, lupus, MS, thyroid) — disproportionately female but underrepresented in training data.",
        "keywords": ["autoimmune", "lupus", "rheumatoid", "multiple scleros", " ra ", "ra.", "ra,", "thyroid", "hashimoto"],
        "example_quote": "Autoimmune disorders, hormonal imbalance, bladder inflammatory, mental health.",
    },
    {
        "theme": "pain_management",
        "definition": "Pain management disparity — women report more pain but receive less effective treatment; fatigue not believed.",
        "keywords": ["pain manag", "chronic pain", "pain perception", "pain is", " pain,", " pain.", "pain ", "fatigue"],
        "example_quote": "Women report chronic pain more frequently than men, yet there's a data gap on pain perception and management in women, making AI models less effective at addressing this.",
    },
    {
        "theme": "mental_health_neurodiversity",
        "definition": "Mental health, ADHD, autism, and neurodiversity — women historically under-diagnosed; intersection with women's hormonal cycles.",
        "keywords": ["mental health", "depression", "anxiety", "adhd", "autism", "neurodiv", "bipolar", "ptsd"],
        "example_quote": "Insufficient studies and data on the connection between various mood and behavioral disorders and women diagnosed with ADHD.",
    },
    {
        "theme": "cancer_female_specific",
        "definition": "Female-specific and female-biased cancers: ovarian, cervical, breast, endometrial.",
        "keywords": ["ovarian cancer", "cervical cancer", "breast cancer", "endometrial cancer", "gyneco", "cancer"],
        "example_quote": "Ovarian cancer diagnosis.",
    },
    {
        "theme": "intersectional_woc_lmic_age",
        "definition": "Intersectional gaps — women of color, mature women (>40), LMIC respondents, racial/ethnic stratification.",
        "keywords": ["women of color", "race", "ethnicit", "minority", "mature women", "older women", "age related", "color", "intersection", "transgender", "non-binary", "non binary"],
        "example_quote": "Women of color and mature women over 40.",
    },
    {
        "theme": "caregiver_burden_maternal_load",
        "definition": "Caregiver stress, working mothers' mental load, sandwich-generation labor, return-to-work from extended leave.",
        "keywords": ["caregiv", "caregiving", "mental load", "working mother", "sandwich gener", "mothers in the workforce", "return to work", "maternity leave"],
        "example_quote": "Caregiving burden; tests designed by men for women (e.g., mammogram, pap smear); clinical data around pregnancy.",
    },
    {
        "theme": "general_all_across_the_board",
        "definition": "Respondent asserts gaps exist across all areas — broad structural claim rather than specific condition.",
        "keywords": ["all of the above", "all areas", "across the board", "all the above", "across the spectrum", "across the", "all the areas", "everything", "everywhere", "many areas", "across all"],
        "example_quote": "Across the board — limited publicly available data, limited R&D investment, antiquated medical practices, under-reporting.",
    },
    {
        "theme": "symptoms_presentation",
        "definition": "Symptoms present differently in women (general, not tied to a specific condition above). Most common generic response.",
        "keywords": ["symptom"],
        "example_quote": "Symptoms are not believed by treating physicians, and treatment options are limited to nonexistent.",
    },
    {
        "theme": "treatment_outcomes_pro_preferences",
        "definition": "Treatment outcomes, patient-reported outcomes (PROs), preferences — the SurveyMonkey-provided examples respondents echo.",
        "keywords": ["treatment outcome", "patient reported", "patient-reported", "preference", "pro ", "proms", "pros,", "pros.", " pros", "outcomes"],
        "example_quote": "Symptoms, treatment outcomes, patient reported outcomes, preferences.",
    },
    {
        "theme": "diagnostic_accuracy",
        "definition": "Diagnosis and diagnostic accuracy broadly — misdiagnosis, delayed diagnosis, one-size-fits-all diagnostic criteria.",
        "keywords": ["diagnos", "misdiagnos"],
        "example_quote": "Symptoms, diagnosis, and treatment.",
    },
    {
        "theme": "treatment_access_general",
        "definition": "Treatment access, availability, affordability, insurance coverage — structural barriers distinct from condition-level data.",
        "keywords": ["treatment", "insurance", "coverage", "access", "affordab"],
        "example_quote": "Insurance coverage, time to receive treatment, treatment duration, QofL, symptoms and symptom management, access to specialists.",
    },
    # Low-literacy / refusal bucket
    {
        "theme": "ai_literacy_unsure_refusal",
        "definition": "Respondent unsure, unfamiliar with AI, or refuses to engage (including 'IDK', 'N/A', 'I don't think AI belongs in healthcare').",
        "keywords": ["not sure", "don't know", "dont know", "idk", "no idea", "not aware", "unaware", "unsure", "not familiar", "no experience", "not knowledg", "not enough info", "not informed", "not applicable", "n/a", "n.a.", "na ", "nausre", "i don't think ai", "no knowledge", "nausure"],
        "example_quote": "I don't think AI models belong in healthcare at all.",
    },
]

# ---------------------------------------------------------------------------
# Q50 TAXONOMY — what organizations should do
# ---------------------------------------------------------------------------

Q50_TAXONOMY = [
    {
        "theme": "collect_more_representative_data",
        "definition": "Collect more and more representative health data, especially from women; expand datasets, fill gaps.",
        "keywords": ["more data", "representat", "broader", "more women", "gather more", "gather new", "collect more", "expand data", "additional data", "broad data", "comprehensive", "better data", "fuller", "more detail", "more comprehensive", "more information", "systematic data", "collect", "gather", "all gender are included", "broad spectrum", "ensure all groups", "clean data", "real world individual", "integrat", "aggregate", "dataset", "data sets", "data sources", "data quality"],
        "example_quote": "Prioritize collecting more comprehensive and representative health data.",
    },
    {
        "theme": "clinical_trial_diversity",
        "definition": "Enroll more diverse populations in clinical trials — women, pregnant women, LMIC, racial diversity.",
        "keywords": ["clinical trial", "trial divers", "trial enroll", "diverse trial", "real world evidence", "rwe", "better representation in trial", "diversity of patient", "studies performed specifically on women", "adequate clinical stud"],
        "example_quote": "Diversity in clinical trials, leveraging real world evidence data to train AI algorithms/models.",
    },
    {
        "theme": "bias_audit_fairness_testing",
        "definition": "Conduct regular bias audits, fairness standards, algorithmic monitoring; test models for bias before deployment.",
        "keywords": ["bias audit", "audit", "fairness", "test the model", "testing the models", "regulat", "monitor", "algorithm", "bias check", "bias detect", "bias mitig"],
        "example_quote": "Conduct regular bias audits on AI models to identify and mitigate any potential gender biases.",
    },
    {
        "theme": "women_in_leadership_ai_roles",
        "definition": "Hire more women into AI/tech/leadership roles; put women in decision-making positions about AI deployment.",
        "keywords": ["more women", "women in decision", "women in leader", "women making decision", "hire more women", "women in ai", "women in tech", "diverse leadership", "diverse executive", "women at the top", "female leader", "female voices", "more genders working"],
        "example_quote": "Include more women in decision making roles on how and which AI models to use; invest in updating health data, research, medical textbooks.",
    },
    {
        "theme": "education_awareness",
        "definition": "Education, awareness, training, workshops about AI bias and women's health for employees, leaders, and clinicians.",
        "keywords": ["education", "educat", "awareness", "aware", "workshop", "training", "learn about", "train staff", "panel discuss", "open culture", "open dialog", "discussion", "communicat", "acknowledge", "open to learning", "being open", "insight", "conscious", "think about", "prioritize", "be open"],
        "example_quote": "Discuss more about mental health with employees and work in collaboration for stress relief.",
    },
    {
        "theme": "sex_stratified_data_models",
        "definition": "Explicitly sex-stratify or sex-disaggregate data; build sex-specific models; disallow aggregation that hides sex differences.",
        "keywords": ["gender-balanced", "gender balanced", "sex-stratif", "sex stratif", "sex-disaggreg", "stratif", "gender-specific", "gender specific", "sex-specific", "segregat", "disaggreg", "gender and race training", "gender and race", "balance"],
        "example_quote": "Develop gender-specific models; increase collaboration with healthcare experts.",
    },
    {
        "theme": "human_in_the_loop_limit_ai",
        "definition": "Keep humans in the loop; limit AI to advisory/informational role; don't let AI make clinical decisions autonomously.",
        "keywords": ["should not", "shouldn't", "not make decision", "as a guide", "human review", "listen to", "with a grain of salt", "listen to the actual", "don't rely", "limit using", "human oversight", "human in the loop", "only use them as"],
        "example_quote": "AI should not be making decisions; it can provide information, options.",
    },
    {
        "theme": "regulatory_standards_policy",
        "definition": "Regulatory or policy action — insurance coverage, standards, audits mandated externally.",
        "keywords": ["policy", "insurance compan", "regulat", "standard", "mandate"],
        "example_quote": "Demand insurance companies work on this issue — cover more tests.",
    },
    {
        "theme": "no_action_not_my_company_literacy",
        "definition": "Respondent unaware of AI use, says it's not their company's problem, or expresses inability to answer.",
        "keywords": ["not sure", "don't know", "dont know", "idk", "no idea", "unsure", "not aware", "unaware", "unfamiliar", "not familiar", "not our", "not my company", "not using", "does not use", "not authoriz", "not enough info", "not knowledg", "n/a", "n.a.", "n a", "na ", "-", "not much", "none.", "none ", "nothing", "na.", "not applicable"],
        "example_quote": "I am unsure if my organization uses AI models for healthcare decisions.",
    },
]


def classify(text: str, taxonomy: list) -> tuple[str, list]:
    """Return (primary_theme, all_matching_themes) for a response."""
    t = text.lower().strip()
    all_matches = []
    for entry in taxonomy:
        if any(kw in t for kw in entry["keywords"]):
            all_matches.append(entry["theme"])
    primary = all_matches[0] if all_matches else "other"
    return primary, all_matches


def analyze_q(raw_path: Path, taxonomy: list, label: str):
    responses = json.loads(raw_path.read_text())
    labeled = []
    for r in responses:
        primary, all_m = classify(r["text"], taxonomy)
        labeled.append({
            "country": r["country"],
            "text": r["text"],
            "primary_theme": primary,
            "all_themes": ";".join(all_m),
        })

    # Frequency
    theme_count = Counter(r["primary_theme"] for r in labeled)
    # Multi-theme frequency (a response can appear in multiple)
    any_theme_count = Counter()
    for r in labeled:
        for t in r["all_themes"].split(";"):
            if t:
                any_theme_count[t] += 1

    # Country × theme
    country_theme = defaultdict(lambda: Counter())
    for r in labeled:
        if r["country"]:
            country_theme[r["country"]][r["primary_theme"]] += 1

    return labeled, theme_count, any_theme_count, country_theme


def write_csv(labeled: list, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["country", "primary_theme", "all_themes", "text"])
        w.writeheader()
        w.writerows(labeled)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    q49_labeled, q49_primary, q49_any, q49_by_country = analyze_q(
        OUT_DIR / "q49_raw.json", Q49_TAXONOMY, "Q49"
    )
    q50_labeled, q50_primary, q50_any, q50_by_country = analyze_q(
        OUT_DIR / "q50_raw.json", Q50_TAXONOMY, "Q50"
    )

    write_csv(q49_labeled, OUT_DIR / "q49_labeled.csv")
    write_csv(q50_labeled, OUT_DIR / "q50_labeled.csv")

    taxonomy_json = {
        "methodology": "Clio-style two-stage taxonomy (Tamkin, Handa, Durmus et al. 2024) applied to survey free-text. Stage 1: taxonomy proposed from reading all 330+288 responses. Stage 2: rule-based classifier with priority-ordered keyword matching assigns primary + secondary themes.",
        "q49": {
            "question": "In what specific areas in healthcare are women's health needs underrepresented in the data used for AI models?",
            "n_responses": len(q49_labeled),
            "taxonomy": Q49_TAXONOMY,
            "primary_theme_distribution": dict(q49_primary.most_common()),
            "any_theme_distribution": dict(q49_any.most_common()),
        },
        "q50": {
            "question": "What steps do you think your organization could take to minimize gender bias in AI models used for healthcare decisions?",
            "n_responses": len(q50_labeled),
            "taxonomy": Q50_TAXONOMY,
            "primary_theme_distribution": dict(q50_primary.most_common()),
            "any_theme_distribution": dict(q50_any.most_common()),
        },
    }
    (OUT_DIR / "taxonomy.json").write_text(json.dumps(taxonomy_json, indent=2))

    # Print summary for the console
    print("=" * 72)
    print(f"Q49 — primary-theme distribution (n={len(q49_labeled)})")
    print("=" * 72)
    for theme, n in q49_primary.most_common():
        print(f"  {theme:<40} {n:>4} ({n/len(q49_labeled)*100:>5.1f}%)")

    print()
    print("=" * 72)
    print(f"Q49 — ANY-theme distribution (multi-label, n can exceed 330)")
    print("=" * 72)
    for theme, n in q49_any.most_common():
        print(f"  {theme:<40} {n:>4} ({n/len(q49_labeled)*100:>5.1f}% of resp.)")

    print()
    print("=" * 72)
    print(f"Q50 — primary-theme distribution (n={len(q50_labeled)})")
    print("=" * 72)
    for theme, n in q50_primary.most_common():
        print(f"  {theme:<40} {n:>4} ({n/len(q50_labeled)*100:>5.1f}%)")

    print()
    print("=" * 72)
    print("COUNTRY × TOP Q49 THEME — countries with n≥5 responses")
    print("=" * 72)
    for country, themes in q49_by_country.items():
        total = sum(themes.values())
        if total < 5:
            continue
        top = themes.most_common(1)[0]
        print(f"  {country:<30} n={total:>3}  top={top[0]:<40} ({top[1]/total*100:.0f}%)")


if __name__ == "__main__":
    main()
