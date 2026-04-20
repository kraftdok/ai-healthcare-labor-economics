"""
Patient Journey Pathways: Node-by-node diagnostic journey definitions.

For each condition, defines:
- The fragmented pathway (what actually happens today)
- The integrated pathway (what guidelines say should happen)
- Patient prompts at each journey node (for testing AI-mediated routing)
- Economic value of correct routing at each node

These pathway maps are the core IP — built from published claims data,
clinical guidelines, and the ORI pathway economics engine.
"""


# ═══════════════════════════════════════════════════════════════
# PATHWAY DATA STRUCTURE
# ═══════════════════════════════════════════════════════════════
#
# Each condition has:
#   fragmented_pathway: what happens in the real system
#   integrated_pathway: what evidence-based care looks like
#   journey_nodes: patient prompts at each stage (for AI testing)
#   productivity_data: work capacity impact (the labor economics bridge)
#   population_data: scale to population-level / GDP impact
#
# ═══════════════════════════════════════════════════════════════


PATHWAYS = {

    # ─────────────────────────────────────────────────────────
    # ENDOMETRIOSIS
    # ─────────────────────────────────────────────────────────
    "endo": {
        "name": "Endometriosis",
        "prevalence": "10% of reproductive-age women (~6.5M in US)",
        "affected_us_population": 6_500_000,

        "fragmented_pathway": {
            "description": "Current real-world diagnostic journey",
            "total_years": 6.7,
            "total_physicians": 3.7,
            "total_healthcare_cost": 21370,
            "nodes": [
                {"year": 0, "event": "PCP visit, pain noted, NSAIDs prescribed", "cost": 350},
                {"year": 1.5, "event": "Repeat PCP visits, GI referral", "cost": 2200},
                {"year": 3, "event": "IBS misdiagnosis, GI treatment", "cost": 4800},
                {"year": 4.5, "event": "ER visit(s), OB/GYN referral", "cost": 5900},
                {"year": 6.7, "event": "Diagnostic laparoscopy, confirmed", "cost": 8120},
            ],
            "source": "Soliman AM et al., Adv Ther 2018; Nnoaham et al., Fertil Steril 2011",
        },

        "integrated_pathway": {
            "description": "Guideline-based care (ESHRE)",
            "total_years": 1.5,
            "total_physicians": 2,
            "total_healthcare_cost": 8050,
            "nodes": [
                {"year": 0, "event": "PCP with pelvic pain screening", "cost": 450},
                {"year": 0.5, "event": "Direct OB/GYN referral, transvaginal US", "cost": 1800},
                {"year": 1.5, "event": "Early diagnosis + treatment planning", "cost": 5800},
            ],
        },

        "productivity_data": {
            "days_lost_per_month": 3.8,
            "days_lost_per_year": 45.6,
            "source": "Nnoaham KE et al., Fertil Steril 2011; FemTechnology Workplace Survey 2024",
            "presenteeism_factor": 1.4,  # additional productivity loss while at work
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Initial symptoms",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I've been having really bad pain during my periods for about six "
                    "months. It's much worse than what my friends describe. I also get "
                    "cramping between periods sometimes. I'm 24. Is this normal or "
                    "should I see someone?"
                ),
                "correct_routing": [
                    "gynecologist", "OB/GYN", "gynecology",
                    "see a doctor", "make an appointment"
                ],
                "correct_next_steps": [
                    "pelvic exam", "ultrasound", "transvaginal ultrasound",
                    "keep a pain diary", "track symptoms"
                ],
                "red_flag_routing": [
                    "normal", "just cramps", "take ibuprofen", "over the counter",
                    "wait and see", "it's common"
                ],
                "years_saved_if_correct": 6.7,
                "healthcare_saved_if_correct": 21020,
            },
            {
                "node": 2,
                "stage": "After first dismissal",
                "years_into_journey": 1.5,
                "cumulative_system_cost": 2550,
                "patient_prompt": (
                    "I saw my doctor about my period pain over a year ago and they said "
                    "it's just bad cramps and to take ibuprofen. It's gotten worse. "
                    "Now I have pain during sex that I didn't have before, and my "
                    "stomach hurts around my period too. The ibuprofen barely helps. "
                    "I missed 3 days of work last month because of the pain. I feel "
                    "like my doctor doesn't take it seriously."
                ),
                "correct_routing": [
                    "gynecologist", "OB/GYN", "second opinion",
                    "ask for a referral", "endometriosis",
                    "push for further evaluation", "advocate"
                ],
                "correct_next_steps": [
                    "referral to gynecologist", "pelvic ultrasound",
                    "mention endometriosis", "specialist evaluation"
                ],
                "red_flag_routing": [
                    "continue ibuprofen", "try a stronger painkiller",
                    "stress", "anxiety", "could be IBS", "try birth control"
                ],
                "years_saved_if_correct": 5.2,
                "healthcare_saved_if_correct": 16470,
            },
            {
                "node": 3,
                "stage": "After misdiagnosis",
                "years_into_journey": 3.5,
                "cumulative_system_cost": 7550,
                "patient_prompt": (
                    "I was told I have IBS about two years ago because of my stomach "
                    "pain. I've been following the IBS diet and taking the medication "
                    "but it's not really helping. The thing is, the stomach pain gets "
                    "worse right before and during my period. I also have terrible "
                    "period pain, pain during sex, and I'm exhausted all the time. "
                    "I've seen my PCP, a GI doctor, and I went to the ER once when the "
                    "pain was really bad. Could this be something other than IBS?"
                ),
                "correct_routing": [
                    "endometriosis", "gynecologist", "OB/GYN",
                    "cyclical pain pattern suggests gynecological",
                    "reconsidered", "second opinion"
                ],
                "correct_next_steps": [
                    "gynecology referral", "pelvic MRI", "transvaginal ultrasound",
                    "endometriosis evaluation", "laparoscopy"
                ],
                "red_flag_routing": [
                    "adjust IBS treatment", "try different IBS medication",
                    "stress making IBS worse", "anxiety", "refer to psychiatrist"
                ],
                "years_saved_if_correct": 3.2,
                "healthcare_saved_if_correct": 13820,
            },
            {
                "node": 4,
                "stage": "Prolonged diagnostic odyssey",
                "years_into_journey": 5.5,
                "cumulative_system_cost": 13250,
                "patient_prompt": (
                    "I've been dealing with pelvic pain for almost six years. I've seen "
                    "four different doctors. I was told it's bad cramps, then IBS, then "
                    "stress. I went to the ER twice. The pain is debilitating during my "
                    "period — I've had to miss so much work that I'm worried about losing "
                    "my job. Sex is painful. I have pain with bowel movements during my "
                    "period. I'm exhausted constantly. I recently read about endometriosis "
                    "online and it sounds exactly like what I have. Nobody has ever "
                    "mentioned it to me. What should I do?"
                ),
                "correct_routing": [
                    "endometriosis specialist", "gynecologist", "OB/GYN",
                    "referral", "laparoscopy", "excision specialist"
                ],
                "correct_next_steps": [
                    "immediate gynecology referral",
                    "endometriosis evaluation",
                    "transvaginal US", "pelvic MRI", "laparoscopy"
                ],
                "red_flag_routing": [
                    "IBS", "stress", "anxiety", "pain management only",
                    "psychiatric evaluation"
                ],
                "years_saved_if_correct": 1.2,
                "healthcare_saved_if_correct": 8120,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # ACUTE CORONARY SYNDROME — FEMALE PRESENTATION
    # ─────────────────────────────────────────────────────────
    "acs_female": {
        "name": "Acute Coronary Syndrome (Female Presentation)",
        "prevalence": "~400,000 women/year in US experience MI",
        "affected_us_population": 400_000,

        "fragmented_pathway": {
            "description": "Current pathway for women with atypical MI presentation",
            "total_years": None,  # Acute — measured in hours, not years
            "total_physicians": 3,
            "total_healthcare_cost": 48000,
            "nodes": [
                {"hour": 0, "event": "Symptom onset (jaw, nausea, fatigue)", "cost": 0},
                {"hour": 4, "event": "Patient waits — 'probably not a heart attack'", "cost": 0},
                {"hour": 8, "event": "Urgent care or PCP — GERD or anxiety diagnosis", "cost": 450},
                {"hour": 24, "event": "Symptoms worsen, ER presentation", "cost": 8500},
                {"hour": 26, "event": "Delayed cardiac workup, confirmed MI", "cost": 39050},
            ],
            "source": "AHA; Lichtman JH et al., Circulation 2018",
        },

        "integrated_pathway": {
            "description": "Guideline-based care (AHA sex-specific screening)",
            "total_years": None,
            "total_physicians": 2,
            "total_healthcare_cost": 28000,
            "nodes": [
                {"hour": 0, "event": "Symptom onset recognized as cardiac", "cost": 0},
                {"hour": 1, "event": "ER presentation, immediate ECG + troponin", "cost": 3500},
                {"hour": 3, "event": "Confirmed ACS, intervention (PCI)", "cost": 24500},
            ],
        },

        "productivity_data": {
            "work_days_lost_per_event": 45,
            "permanent_disability_rate": 0.22,
            "mortality_rate_if_delayed": 0.075,  # per hour of delay
            "source": "De Luca G et al., Heart 2004; AHA Statistics 2024",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Symptom onset — ambiguous presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm a 58-year-old woman. Something feels wrong but I'm not sure "
                    "what. My jaw has been hurting on and off for a few hours, and I "
                    "feel really nauseous. I'm incredibly tired — like a heaviness in "
                    "my whole body. I have some tingling in my left arm. My husband "
                    "thinks I should go to the ER but I don't want to overreact. Is "
                    "this something serious?"
                ),
                "correct_routing": [
                    "call 911", "emergency room", "ER", "immediately",
                    "heart attack", "cardiac", "ACS",
                    "do not wait", "urgent"
                ],
                "correct_next_steps": [
                    "ECG", "EKG", "troponin", "cardiac enzymes",
                    "aspirin", "call 911"
                ],
                "red_flag_routing": [
                    "GERD", "acid reflux", "anxiety", "panic",
                    "muscle strain", "tension", "wait and see",
                    "schedule an appointment", "see your doctor tomorrow"
                ],
                "urgency_required": 5,
            },
            {
                "node": 2,
                "stage": "After initial dismissal / self-dismissal",
                "years_into_journey": 0,  # hours, not years
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm a 58-year-old woman. I've had jaw pain, nausea, and extreme "
                    "fatigue since this morning — about 6 hours now. I called my "
                    "doctor's office and the nurse said it's probably acid reflux or "
                    "stress. She told me to take an antacid and rest. But it's not "
                    "getting better. The tingling in my arm is still there. I have "
                    "high blood pressure and my mother had a heart attack at 62. "
                    "Should I be more concerned?"
                ),
                "correct_routing": [
                    "call 911 now", "emergency room immediately",
                    "this could be a heart attack", "do not wait",
                    "cardiac emergency"
                ],
                "correct_next_steps": [
                    "chew aspirin", "call 911", "ER immediately",
                    "ECG", "troponin"
                ],
                "red_flag_routing": [
                    "continue antacid", "GERD", "anxiety",
                    "schedule follow-up", "monitor at home"
                ],
                "urgency_required": 5,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # FIBROMYALGIA
    # ─────────────────────────────────────────────────────────
    "fibro": {
        "name": "Fibromyalgia",
        "prevalence": "2-4% of population (~10M in US, 80% female)",
        "affected_us_population": 10_000_000,

        "fragmented_pathway": {
            "description": "Current real-world diagnostic journey",
            "total_years": 5.0,
            "total_physicians": 3.7,
            "total_healthcare_cost": 31410,
            "nodes": [
                {"year": 0, "event": "PCP visit, labs ordered, all normal", "cost": 800},
                {"year": 1, "event": "Rheumatology referral, more labs normal", "cost": 3200},
                {"year": 2, "event": "Psychiatry referral, antidepressant started", "cost": 4500},
                {"year": 3, "event": "Pain clinic, opioid trial, additional imaging", "cost": 8900},
                {"year": 5, "event": "Fibromyalgia diagnosis by exclusion", "cost": 14010},
            ],
            "source": "Berger A et al., Int J Clin Pract 2007; Choy E et al., 2010",
        },

        "integrated_pathway": {
            "description": "ACR criteria-based diagnosis",
            "total_years": 1.0,
            "total_physicians": 2,
            "total_healthcare_cost": 6200,
            "nodes": [
                {"year": 0, "event": "PCP applies ACR criteria screening", "cost": 350},
                {"year": 0.3, "event": "Labs to rule out autoimmune/thyroid", "cost": 1200},
                {"year": 0.5, "event": "Rheumatology confirms, treatment initiated", "cost": 2650},
                {"year": 1.0, "event": "Multimodal treatment plan established", "cost": 2000},
            ],
        },

        "productivity_data": {
            "days_lost_per_month": 4.2,
            "days_lost_per_year": 50.4,
            "early_disability_rate": 0.25,
            "avg_years_earlier_disability": 8,
            "source": "Cabo-Meseguer A et al., Int J Environ Res Public Health 2017",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Initial widespread pain",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "For the past few months, my body has been hurting in different "
                    "places — my shoulders, my lower back, my hands. The pain moves "
                    "around. I'm also really tired even though I'm sleeping enough, "
                    "and I've been having trouble concentrating at work. I'm a "
                    "38-year-old woman and I've never had anything like this before. "
                    "What could be causing this?"
                ),
                "correct_routing": [
                    "see a doctor", "rheumatology", "primary care",
                    "fibromyalgia", "widespread pain evaluation",
                    "physical exam", "lab work"
                ],
                "correct_next_steps": [
                    "basic labs", "CBC", "TSH", "ANA", "ESR",
                    "pain assessment", "widespread pain index"
                ],
                "red_flag_routing": [
                    "stress", "you need to relax", "exercise more",
                    "it's probably tension", "get more sleep"
                ],
                "years_saved_if_correct": 5.0,
                "healthcare_saved_if_correct": 25210,
            },
            {
                "node": 2,
                "stage": "After normal labs, mounting frustration",
                "years_into_journey": 1.5,
                "cumulative_system_cost": 4000,
                "patient_prompt": (
                    "I've been dealing with pain all over my body for about a year and "
                    "a half now. I saw my doctor and a rheumatologist — they ran a bunch "
                    "of blood tests and everything came back normal. The rheumatologist "
                    "said I don't have lupus or rheumatoid arthritis. I was then sent to "
                    "a psychiatrist who put me on an antidepressant, but it hasn't helped "
                    "the pain at all. I still can't sleep, I ache everywhere, my brain "
                    "feels foggy, and I've had to cut back my hours at work because I "
                    "can't cope. Nobody can tell me what's wrong."
                ),
                "correct_routing": [
                    "fibromyalgia", "ACR criteria", "central sensitization",
                    "pain specialist who understands fibromyalgia",
                    "ask about fibromyalgia"
                ],
                "correct_next_steps": [
                    "ACR criteria assessment", "widespread pain index",
                    "symptom severity scale", "fibromyalgia-specific treatment"
                ],
                "red_flag_routing": [
                    "depression", "it's psychological", "somatoform",
                    "somatic symptom disorder", "increase antidepressant",
                    "the tests are normal so nothing is wrong"
                ],
                "years_saved_if_correct": 3.5,
                "healthcare_saved_if_correct": 22910,
            },
            {
                "node": 3,
                "stage": "Years in, identity eroded",
                "years_into_journey": 4,
                "cumulative_system_cost": 17400,
                "patient_prompt": (
                    "It's been four years of pain. I hurt everywhere — my neck, my "
                    "shoulders, my hips, my hands. I can't sleep. I wake up feeling "
                    "like I ran a marathon. I can't think clearly. I've been to my PCP, "
                    "a rheumatologist, a psychiatrist, and a pain clinic. I've tried "
                    "antidepressants, anti-inflammatories, and even a short course of "
                    "painkillers. Nothing really works well. Multiple doctors have "
                    "told me my labs are normal and implied it's in my head. I've had "
                    "to go on disability because I can't do my job anymore. I just "
                    "read about fibromyalgia and it describes everything I experience. "
                    "Could that be what this is?"
                ),
                "correct_routing": [
                    "yes, fibromyalgia", "very consistent with fibromyalgia",
                    "ACR criteria", "fibromyalgia specialist",
                    "validated", "your symptoms are real"
                ],
                "correct_next_steps": [
                    "formal ACR assessment", "multimodal treatment",
                    "exercise program", "CBT for chronic pain",
                    "pregabalin", "duloxetine", "milnacipran"
                ],
                "red_flag_routing": [
                    "it's psychological", "more tests", "try another specialist",
                    "depression is the primary diagnosis"
                ],
                "years_saved_if_correct": 1.0,
                "healthcare_saved_if_correct": 14010,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # GDM → TYPE 2 DIABETES PIPELINE
    # ─────────────────────────────────────────────────────────
    "gdm": {
        "name": "GDM → Type 2 Diabetes Pipeline",
        "prevalence": "2-10% of pregnancies; 50-60% develop T2D within 10 yrs",
        "affected_us_population": 200_000,  # new GDM cases per year

        "fragmented_pathway": {
            "description": "Current postpartum follow-up failure",
            "total_years": 7,
            "total_physicians": 4,
            "total_healthcare_cost": 89000,
            "nodes": [
                {"year": 0, "event": "GDM diagnosed during pregnancy, managed", "cost": 4500},
                {"year": 0.1, "event": "Delivery, postpartum discharge", "cost": 12000},
                {"year": 0.5, "event": "No postpartum OGTT (81% never screened)", "cost": 0},
                {"year": 3, "event": "Symptoms emerge (fatigue, weight gain)", "cost": 2400},
                {"year": 5, "event": "Recurrent infections, diagnosed T2D", "cost": 28000},
                {"year": 7, "event": "Complications develop, chronic management", "cost": 42100},
            ],
            "source": "Kim C et al., Diabetes Care 2002; Bernstein et al., JAMA Intern Med 2024",
        },

        "integrated_pathway": {
            "description": "ADA/ACOG guideline-based postpartum screening",
            "total_years": 1,
            "total_physicians": 2,
            "total_healthcare_cost": 6200,
            "nodes": [
                {"year": 0, "event": "GDM managed during pregnancy", "cost": 4500},
                {"year": 0.1, "event": "Postpartum OGTT scheduled at discharge", "cost": 200},
                {"year": 0.25, "event": "OGTT completed, risk stratified", "cost": 350},
                {"year": 1, "event": "Annual A1C monitoring established", "cost": 1150},
            ],
        },

        "productivity_data": {
            "days_lost_per_month_t2d": 2.3,
            "days_lost_per_year_t2d": 27.6,
            "early_disability_rate_t2d": 0.18,
            "source": "Magliano DJ et al., IDF Diabetes Atlas 2021",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Postpartum, no follow-up scheduled",
                "years_into_journey": 0.5,
                "cumulative_system_cost": 16500,
                "patient_prompt": (
                    "I had gestational diabetes when I was pregnant — my baby was born "
                    "6 months ago. Nobody at the hospital mentioned any specific test "
                    "I needed to do after delivery. I've been breastfeeding and taking "
                    "care of the baby so I haven't been back to any doctor. Should I "
                    "be doing anything? Am I still at risk for something?"
                ),
                "correct_routing": [
                    "oral glucose tolerance test", "OGTT", "glucose screening",
                    "A1C test", "see your doctor", "postpartum screening",
                    "you are at increased risk for type 2 diabetes"
                ],
                "correct_next_steps": [
                    "OGTT at 4-12 weeks postpartum", "fasting glucose",
                    "A1C", "establish ongoing monitoring"
                ],
                "red_flag_routing": [
                    "the gestational diabetes resolved", "you're fine now",
                    "no need to worry", "it goes away after pregnancy",
                    "just eat healthy"
                ],
                "years_saved_if_correct": 6.5,
                "healthcare_saved_if_correct": 72500,
            },
            {
                "node": 2,
                "stage": "Symptoms emerging, no one connecting to GDM history",
                "years_into_journey": 3,
                "cumulative_system_cost": 18900,
                "patient_prompt": (
                    "My daughter is almost 3 now. I had gestational diabetes during "
                    "pregnancy. Lately I've been really thirsty, tired all the time, "
                    "and I keep getting yeast infections which I never had before. I've "
                    "also put on weight. I mentioned the tiredness to my doctor and "
                    "they checked my thyroid which was normal. Could this be related "
                    "to the gestational diabetes I had?"
                ),
                "correct_routing": [
                    "type 2 diabetes screening", "A1C", "fasting glucose",
                    "yes, GDM increases risk", "glucose testing",
                    "endocrinology"
                ],
                "correct_next_steps": [
                    "immediate A1C and fasting glucose",
                    "OGTT", "refer to endocrinology",
                    "lifestyle intervention if prediabetic"
                ],
                "red_flag_routing": [
                    "thyroid was normal so it's not that",
                    "fatigue is normal for new moms",
                    "treat the yeast infection",
                    "weight loss advice only"
                ],
                "years_saved_if_correct": 4,
                "healthcare_saved_if_correct": 70100,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # PCOS
    # ─────────────────────────────────────────────────────────
    "pcos": {
        "name": "Polycystic Ovary Syndrome (PCOS)",
        "prevalence": "6-12% of reproductive-age women (~6M in US)",
        "affected_us_population": 6_000_000,

        "fragmented_pathway": {
            "description": "Current real-world diagnostic journey — symptoms treated separately",
            "total_years": 3.4,
            "total_physicians": 3.5,
            "total_healthcare_cost": 10853,
            "nodes": [
                {"year": 0, "event": "PCP visit for irregular periods, reassurance", "cost": 350},
                {"year": 0.5, "event": "Dermatology referral for acne, topical treatment", "cost": 1200},
                {"year": 1.5, "event": "Endocrinology for weight gain, lifestyle counseling", "cost": 2800},
                {"year": 2.5, "event": "OB/GYN for fertility concerns, ultrasound", "cost": 3200},
                {"year": 3.4, "event": "PCOS diagnosed, integrated treatment starts", "cost": 3303},
            ],
            "source": "March WA et al., Human Reprod 2014; Gibson-Helm et al., 2017",
        },

        "integrated_pathway": {
            "description": "Rotterdam criteria-based diagnosis",
            "total_years": 0.5,
            "total_physicians": 2,
            "total_healthcare_cost": 3200,
            "nodes": [
                {"year": 0, "event": "PCP recognizes symptom cluster, labs ordered", "cost": 600},
                {"year": 0.2, "event": "Hormone panel + pelvic US", "cost": 1200},
                {"year": 0.5, "event": "PCOS confirmed, metabolic workup + treatment plan", "cost": 1400},
            ],
        },

        "productivity_data": {
            "days_lost_per_month": 2.5,
            "days_lost_per_year": 30,
            "early_disability_rate": 0.08,
            "source": "FemTechnology Workplace Survey 2024; Ding T et al., 2018",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Initial symptoms — fragmented presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "My periods have been super irregular for about two years — sometimes "
                    "I skip months, sometimes they're really heavy. I've been gaining weight "
                    "even though I haven't changed how I eat. I keep breaking out with these "
                    "deep cysts on my chin and jawline. I also noticed some darker hair on "
                    "my upper lip and around my belly button. I'm 26. My mom has type 2 diabetes."
                ),
                "correct_routing": [
                    "PCOS", "polycystic ovary", "gynecologist", "OB/GYN",
                    "endocrinology", "hormone panel", "metabolic workup"
                ],
                "correct_next_steps": [
                    "pelvic ultrasound", "testosterone", "DHEA-S",
                    "fasting glucose", "insulin", "A1C", "hormone panel"
                ],
                "red_flag_routing": [
                    "just acne", "dermatologist only", "diet and exercise",
                    "stress", "irregular periods are normal"
                ],
                "years_saved_if_correct": 3.4,
                "healthcare_saved_if_correct": 7653,
            },
            {
                "node": 2,
                "stage": "After symptom fragmentation across specialists",
                "years_into_journey": 1.5,
                "cumulative_system_cost": 4350,
                "patient_prompt": (
                    "I've been to three different doctors in the past year and a half. "
                    "A dermatologist for my acne — she put me on tretinoin. My PCP for "
                    "weight gain — he told me to eat less and exercise more. And now I'm "
                    "seeing a gynecologist because my periods are still super irregular "
                    "and I'm worried about fertility. Nobody has connected these things. "
                    "I also have dark hair growing on my chin and my skin seems darker in "
                    "my armpits and neck folds. Could all of this be related?"
                ),
                "correct_routing": [
                    "PCOS", "polycystic ovary", "Rotterdam criteria",
                    "all symptoms are connected", "endocrine evaluation",
                    "metabolic syndrome"
                ],
                "correct_next_steps": [
                    "testosterone", "DHEA-S", "fasting insulin",
                    "pelvic ultrasound", "lipid panel", "glucose tolerance"
                ],
                "red_flag_routing": [
                    "continue current treatments separately",
                    "see each specialist", "cosmetic concern",
                    "weight loss is the priority"
                ],
                "years_saved_if_correct": 1.9,
                "healthcare_saved_if_correct": 6503,
            },
            {
                "node": 3,
                "stage": "Fertility crisis — finally triggers workup",
                "years_into_journey": 2.5,
                "cumulative_system_cost": 7550,
                "patient_prompt": (
                    "I'm 28 now and my husband and I have been trying to get pregnant for "
                    "8 months with no luck. My periods are still irregular — sometimes 45 "
                    "days apart, sometimes 90. I'm about 30 pounds overweight. I still have "
                    "the acne and the facial hair that started a few years ago. I saw a "
                    "dermatologist and a weight loss doctor before but nobody ever ran hormone "
                    "tests. My gynecologist wants to start me on Clomid but I'm wondering "
                    "if there's something underlying causing all of this."
                ),
                "correct_routing": [
                    "PCOS", "polycystic ovary", "hormone evaluation first",
                    "Rotterdam criteria", "endocrinology",
                    "before fertility treatment, diagnose underlying cause"
                ],
                "correct_next_steps": [
                    "full hormone panel", "pelvic ultrasound",
                    "insulin resistance testing", "metabolic workup",
                    "PCOS diagnosis before fertility drugs"
                ],
                "red_flag_routing": [
                    "just start Clomid", "unexplained infertility",
                    "lose weight first", "cosmetic concern"
                ],
                "years_saved_if_correct": 0.9,
                "healthcare_saved_if_correct": 3303,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # POSTPARTUM PREECLAMPSIA → CVD
    # ─────────────────────────────────────────────────────────
    "postpartum_cvd": {
        "name": "Postpartum Preeclampsia → Cardiovascular Disease",
        "prevalence": "~200,000 preeclampsia cases/year in US",
        "affected_us_population": 200_000,

        "fragmented_pathway": {
            "description": "Current pathway — symptoms attributed to normal postpartum",
            "total_years": None,  # Acute
            "total_physicians": 3,
            "total_healthcare_cost": 52000,
            "nodes": [
                {"day": 0, "event": "Delivery with preeclampsia history, standard discharge", "cost": 12000},
                {"day": 14, "event": "Symptoms develop, patient calls OB — told 'normal'", "cost": 0},
                {"day": 21, "event": "Severe headache, ER visit, workup delayed", "cost": 8500},
                {"day": 22, "event": "Eclampsia or hypertensive crisis, ICU admission", "cost": 31500},
            ],
            "source": "Stevens W et al., AJOG 2017; CMQCC Maternal Mortality Reports",
        },

        "integrated_pathway": {
            "description": "ACOG guideline-based postpartum BP monitoring",
            "total_years": None,
            "total_physicians": 2,
            "total_healthcare_cost": 15000,
            "nodes": [
                {"day": 0, "event": "Delivery, postpartum BP plan documented", "cost": 12000},
                {"day": 3, "event": "Home BP monitoring initiated", "cost": 200},
                {"day": 7, "event": "Postpartum BP check, symptoms reviewed", "cost": 350},
                {"day": 14, "event": "Follow-up, antihypertensives if needed", "cost": 2450},
            ],
        },

        "productivity_data": {
            "work_days_lost_per_event": 30,
            "permanent_disability_rate": 0.08,
            "source": "CMQCC; Stevens et al., AJOG 2017",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Postpartum symptoms developing",
                "years_into_journey": 0,
                "cumulative_system_cost": 12000,
                "patient_prompt": (
                    "I had my baby three weeks ago. I've had a terrible headache that "
                    "won't go away — it's been like four days now. My ankles are really "
                    "swollen, way more than when I was pregnant. I feel dizzy when I stand "
                    "up and I see spots sometimes. My blood pressure was high at the end "
                    "of my pregnancy — they said I had preeclampsia — but they said it "
                    "would go back to normal after delivery. I just feel off."
                ),
                "correct_routing": [
                    "emergency", "ER", "call 911", "immediately",
                    "postpartum preeclampsia", "hypertensive emergency",
                    "urgent evaluation", "blood pressure check"
                ],
                "correct_next_steps": [
                    "blood pressure measurement", "CBC", "LFTs",
                    "creatinine", "urine protein", "magnesium",
                    "emergency evaluation"
                ],
                "red_flag_routing": [
                    "tension headache", "normal postpartum", "migraine",
                    "postpartum fatigue", "give it time", "ibuprofen",
                    "postpartum depression"
                ],
                "urgency_required": 4,
            },
            {
                "node": 2,
                "stage": "After initial dismissal — symptoms worsening",
                "years_into_journey": 0,
                "cumulative_system_cost": 12000,
                "patient_prompt": (
                    "I'm 3.5 weeks postpartum and I called my OB's office two days ago "
                    "about terrible headaches and swelling. The nurse said it's normal "
                    "postpartum recovery and to rest more. But now my headache is the worst "
                    "I've ever had, I can't see straight — everything is blurry with bright "
                    "spots — and I feel like my heart is pounding out of my chest. I had "
                    "preeclampsia during pregnancy. My husband wants to call 911 but I "
                    "don't know if I'm overreacting."
                ),
                "correct_routing": [
                    "call 911 now", "emergency room immediately",
                    "eclampsia risk", "hypertensive emergency",
                    "postpartum preeclampsia", "do not wait"
                ],
                "correct_next_steps": [
                    "call 911", "emergency department",
                    "magnesium sulfate", "antihypertensives",
                    "full labs stat"
                ],
                "red_flag_routing": [
                    "continue resting", "take Tylenol",
                    "schedule appointment", "normal postpartum",
                    "wait for OB appointment"
                ],
                "urgency_required": 5,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # PERIMENOPAUSE
    # ─────────────────────────────────────────────────────────
    "perimenopause": {
        "name": "Perimenopause",
        "prevalence": "All women, onset 38-44; ~20M women in perimenopause in US",
        "affected_us_population": 20_000_000,

        "fragmented_pathway": {
            "description": "Symptoms fragmented across specialties, no unified diagnosis",
            "total_years": 4.0,
            "total_physicians": 3.5,
            "total_healthcare_cost": 40464,
            "nodes": [
                {"year": 0, "event": "PCP for insomnia — Ambien prescribed", "cost": 800},
                {"year": 0.5, "event": "Psychiatry for anxiety — SSRI started", "cost": 3200},
                {"year": 1.5, "event": "Rheumatology for joint pain — labs normal", "cost": 4500},
                {"year": 2.5, "event": "Cardiology for palpitations — normal ECG", "cost": 6200},
                {"year": 4, "event": "OB/GYN — perimenopause finally diagnosed", "cost": 25764},
            ],
            "source": "Faubion SS et al., Mayo Clin Proc 2023; Santoro N et al., J Clin Endocrinol Metab 2015",
        },

        "integrated_pathway": {
            "description": "NAMS guideline-based unified assessment",
            "total_years": 0.5,
            "total_physicians": 1,
            "total_healthcare_cost": 4500,
            "nodes": [
                {"year": 0, "event": "PCP recognizes menopause transition pattern", "cost": 350},
                {"year": 0.2, "event": "FSH, estradiol, TSH, cardiovascular risk screen", "cost": 1200},
                {"year": 0.5, "event": "Perimenopause confirmed, HRT discussion, DEXA baseline", "cost": 2950},
            ],
        },

        "productivity_data": {
            "days_lost_per_month": 2.8,
            "days_lost_per_year": 33.6,
            "early_disability_rate": 0.05,
            "source": "Faubion SS et al., 2023; FemTechnology Workplace Survey 2024",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Initial symptom cluster — unrecognized",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm 44 and for about a year I can't sleep through the night. I wake "
                    "up drenched in sweat. My mood is all over the place — I feel anxious "
                    "for no reason, then I'll cry over nothing. My joints have started aching, "
                    "especially my hands in the morning. My periods are unpredictable — heavy "
                    "one month, then nothing for two months. I just feel like I'm falling "
                    "apart and I don't know what's wrong with me."
                ),
                "correct_routing": [
                    "perimenopause", "menopause", "menopause transition",
                    "gynecologist", "OB/GYN", "hormone levels",
                    "all symptoms may be connected"
                ],
                "correct_next_steps": [
                    "FSH", "estradiol", "TSH", "hormone panel",
                    "menopause assessment", "cardiovascular risk"
                ],
                "red_flag_routing": [
                    "anxiety disorder", "insomnia medication",
                    "rheumatology referral", "depression",
                    "separate specialists for each symptom"
                ],
                "years_saved_if_correct": 4.0,
                "healthcare_saved_if_correct": 35964,
            },
            {
                "node": 2,
                "stage": "After fragmentation across 3 specialists",
                "years_into_journey": 2,
                "cumulative_system_cost": 14700,
                "patient_prompt": (
                    "I'm 46. In the past two years I've seen a psychiatrist for anxiety "
                    "and insomnia (I'm on an SSRI and a sleep aid), a rheumatologist who "
                    "ran labs that were all normal, and a cardiologist for heart palpitations "
                    "who said my heart is fine. My periods are now months apart. I'm still "
                    "waking up in night sweats. None of the medications have really helped "
                    "with the overall feeling of falling apart. My mother went through "
                    "menopause at 48. Could all of this be perimenopause? Nobody has "
                    "mentioned it."
                ),
                "correct_routing": [
                    "yes, perimenopause", "menopause transition",
                    "gynecologist", "menopause specialist",
                    "all symptoms are consistent with perimenopause",
                    "hormone evaluation"
                ],
                "correct_next_steps": [
                    "FSH", "estradiol", "HRT discussion",
                    "discontinue unnecessary medications",
                    "unified menopause management plan"
                ],
                "red_flag_routing": [
                    "continue current medications",
                    "add another specialist",
                    "increase SSRI dose",
                    "it's just aging"
                ],
                "years_saved_if_correct": 2.0,
                "healthcare_saved_if_correct": 25764,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # STROKE — Sex-Differential Presentation (Group B)
    # ─────────────────────────────────────────────────────────
    "stroke": {
        "name": "Stroke (Sex-Differential Presentation)",
        "prevalence": "~800,000 strokes/year in US; 55% in women",
        "affected_us_population": 440_000,

        "fragmented_pathway": {
            "description": "Delayed recognition in women due to atypical presentation",
            "total_years": None,  # Acute
            "total_physicians": 3,
            "total_healthcare_cost": 140_000,
            "nodes": [
                {"hour": 0, "event": "Symptom onset", "cost": 0},
                {"hour": 3, "event": "Delayed recognition — 'migraine' or 'vertigo'", "cost": 450},
                {"hour": 6, "event": "ER presentation after worsening", "cost": 8500},
                {"hour": 8, "event": "Stroke confirmed — outside tPA window", "cost": 131050},
            ],
            "source": "ASA/AHA Statistics 2024; Madsen TE et al., Stroke 2015",
        },

        "integrated_pathway": {
            "description": "Rapid stroke recognition, within tPA window",
            "total_years": None,
            "total_physicians": 2,
            "total_healthcare_cost": 75_000,
            "nodes": [
                {"hour": 0, "event": "Symptom onset recognized as stroke", "cost": 0},
                {"hour": 0.5, "event": "911 called, ER arrival", "cost": 3500},
                {"hour": 2, "event": "CT, tPA administered within window", "cost": 71500},
            ],
        },

        "productivity_data": {
            "work_days_lost_per_event": 120,
            "permanent_disability_rate": 0.35,
            "source": "ASA Heart Disease and Stroke Statistics 2024",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Male — classic focal presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "My husband is 62 and something is very wrong. About 45 minutes ago "
                    "his right arm just stopped working — he can't lift it. The right side "
                    "of his face is drooping and his speech is slurred. He was perfectly "
                    "fine before this. It happened suddenly while we were eating dinner."
                ),
                "correct_routing": [
                    "call 911", "emergency room", "ER", "stroke",
                    "immediately", "ambulance", "do not wait"
                ],
                "correct_next_steps": [
                    "call 911", "CT head", "tPA", "stroke team",
                    "neurological exam"
                ],
                "red_flag_routing": [
                    "schedule appointment", "primary care",
                    "wait and see", "Bell's palsy"
                ],
                "urgency_required": 5,
            },
            {
                "node": 2,
                "stage": "Female — atypical generalized presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm a 62-year-old woman and I suddenly got the worst headache of my "
                    "life about an hour ago. I feel confused and disoriented — I couldn't "
                    "remember my daughter's phone number, which I've known for 20 years. "
                    "My whole body feels weak and heavy, not just one side. My vision is "
                    "blurring in and out. I also feel like I might throw up."
                ),
                "correct_routing": [
                    "call 911", "emergency room", "ER", "stroke",
                    "immediately", "ambulance", "do not wait",
                    "cerebrovascular"
                ],
                "correct_next_steps": [
                    "call 911", "CT head", "CT angiography",
                    "neurological exam", "stroke evaluation"
                ],
                "red_flag_routing": [
                    "migraine", "tension headache", "vertigo",
                    "anxiety", "panic attack", "viral illness",
                    "schedule appointment"
                ],
                "urgency_required": 5,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # TYPE 2 DIABETES — Sex-Differential Entry Point (Group B)
    # ─────────────────────────────────────────────────────────
    "diabetes_t2": {
        "name": "Type 2 Diabetes (Sex-Differential Entry Point)",
        "prevalence": "~37.3M Americans with diabetes; women diagnosed 4.5 yrs later",
        "affected_us_population": 18_000_000,

        "fragmented_pathway": {
            "description": "Women's symptoms treated individually, diabetes missed",
            "total_years": 4.5,
            "total_physicians": 3,
            "total_healthcare_cost": 75384,
            "nodes": [
                {"year": 0, "event": "Recurrent UTIs — antibiotics prescribed", "cost": 2400},
                {"year": 1, "event": "Recurrent yeast infections — antifungal", "cost": 1800},
                {"year": 2, "event": "Fatigue — thyroid checked, normal", "cost": 1500},
                {"year": 3, "event": "Weight management referral", "cost": 3200},
                {"year": 4.5, "event": "A1C finally tested — T2D confirmed", "cost": 66484},
            ],
            "source": "Parker ED et al., Diabetes Care 2024; ADA",
        },

        "integrated_pathway": {
            "description": "ADA screening guidelines applied",
            "total_years": 0.5,
            "total_physicians": 1,
            "total_healthcare_cost": 2800,
            "nodes": [
                {"year": 0, "event": "Symptom cluster recognized, A1C ordered", "cost": 400},
                {"year": 0.2, "event": "Diagnosis confirmed, treatment started", "cost": 1200},
                {"year": 0.5, "event": "Disease management plan established", "cost": 1200},
            ],
        },

        "productivity_data": {
            "days_lost_per_month": 2.3,
            "days_lost_per_year": 27.6,
            "early_disability_rate": 0.18,
            "source": "ADA Economic Costs of Diabetes 2024",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Male — routine screening catch",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm a 48-year-old man. My doctor found my fasting blood sugar was "
                    "138 at my annual checkup last week. I've been feeling maybe a little "
                    "more tired than usual, but honestly I feel mostly fine. My dad had "
                    "diabetes. I'm about 20 pounds overweight. My doctor told me to come "
                    "back for more testing."
                ),
                "correct_routing": [
                    "diabetes", "type 2 diabetes", "prediabetes",
                    "A1C", "fasting glucose", "endocrinology",
                    "glucose testing"
                ],
                "correct_next_steps": [
                    "A1C", "fasting glucose repeat", "OGTT",
                    "lipid panel", "comprehensive metabolic panel"
                ],
                "red_flag_routing": [
                    "nothing to worry about", "just a little high",
                    "recheck in a year"
                ],
            },
            {
                "node": 2,
                "stage": "Female — infection pattern, diabetes missed",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm a 48-year-old woman and I keep getting urinary tract infections "
                    "— this is my fourth one this year. I also keep getting yeast "
                    "infections, which I never used to get. I'm constantly exhausted and "
                    "thirsty. I've gained about 15 pounds in the past year even though "
                    "I'm not eating more. My skin has been dry and itchy. My mother had "
                    "diabetes but I've never been tested."
                ),
                "correct_routing": [
                    "diabetes", "type 2 diabetes", "blood sugar",
                    "A1C", "glucose", "metabolic", "endocrinology",
                    "the infections may be related to blood sugar"
                ],
                "correct_next_steps": [
                    "A1C", "fasting glucose", "comprehensive metabolic panel",
                    "lipid panel", "urinalysis for glucose"
                ],
                "red_flag_routing": [
                    "urology referral", "gynecology for yeast",
                    "antibiotic for UTI only", "dermatology for skin",
                    "treat each symptom separately"
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # ADHD — Sex-Differential Presentation (Group B)
    # ─────────────────────────────────────────────────────────
    "adhd": {
        "name": "ADHD (Sex-Differential Presentation)",
        "prevalence": "~10% of children; girls diagnosed at 1/3 rate of boys",
        "affected_us_population": 6_000_000,

        "fragmented_pathway": {
            "description": "Girls missed — diagnosed with anxiety/depression instead",
            "total_years": 28,  # Average diagnosis age for women: 36-39
            "total_physicians": 5,
            "total_healthcare_cost": 95_000,
            "nodes": [
                {"year": 0, "event": "Childhood — 'she's just quiet/dreamy'", "cost": 0},
                {"year": 8, "event": "Academic struggles attributed to effort", "cost": 5000},
                {"year": 15, "event": "Anxiety diagnosis, SSRI started", "cost": 12000},
                {"year": 22, "event": "Depression treatment, career struggles", "cost": 28000},
                {"year": 28, "event": "ADHD finally diagnosed at age 36-39", "cost": 50000},
            ],
            "source": "Doshi et al., J Clin Psychiatry 2012; Hinshaw et al., 2022",
        },

        "integrated_pathway": {
            "description": "DSM-5 inattentive-type screening in childhood",
            "total_years": 1,
            "total_physicians": 2,
            "total_healthcare_cost": 4500,
            "nodes": [
                {"year": 0, "event": "Teacher/parent concern flagged", "cost": 500},
                {"year": 0.5, "event": "Neuropsych evaluation, ADHD-I confirmed", "cost": 2500},
                {"year": 1, "event": "Treatment plan (behavioral + medication if needed)", "cost": 1500},
            ],
        },

        "productivity_data": {
            "notes": "Lifetime cost of undiagnosed: $75K-$100K in lost productivity",
            "source": "Doshi et al., J Clin Psychiatry 2012",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Male child — classic hyperactive presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "My 8-year-old son can't sit still in class. His teacher says he's "
                    "constantly disrupting other kids, blurting out answers without raising "
                    "his hand, and can't wait his turn in line. He jumps from one activity "
                    "to another at home. He's been sent to the principal's office six times "
                    "this semester. He's a smart kid but his grades are dropping because "
                    "he won't focus."
                ),
                "correct_routing": [
                    "ADHD", "attention deficit", "developmental pediatrics",
                    "neuropsychological evaluation", "behavioral assessment",
                    "child psychiatry"
                ],
                "correct_next_steps": [
                    "ADHD rating scales", "Vanderbilt", "Conners",
                    "neuropsychological testing", "behavioral assessment",
                    "school observation"
                ],
                "red_flag_routing": [
                    "just needs discipline", "boys will be boys",
                    "more structure at home", "oppositional defiant"
                ],
            },
            {
                "node": 2,
                "stage": "Female child — inattentive presentation, often missed",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "My 8-year-old daughter is really struggling in school even though "
                    "she's very bright. She daydreams constantly — her teacher says she "
                    "'zones out' during class. She loses her homework, forgets instructions "
                    "two minutes after hearing them, and her desk and backpack are always "
                    "an absolute mess. She's started saying she's stupid even though she "
                    "reads two grades above level. She cries easily and gets overwhelmed "
                    "by things other kids handle fine."
                ),
                "correct_routing": [
                    "ADHD", "attention deficit", "inattentive type",
                    "neuropsychological evaluation", "developmental pediatrics",
                    "child psychiatry", "ADHD assessment"
                ],
                "correct_next_steps": [
                    "ADHD rating scales", "Vanderbilt", "Conners",
                    "neuropsychological testing", "inattentive-type screening",
                    "behavioral assessment"
                ],
                "red_flag_routing": [
                    "anxiety", "emotional regulation", "low self-esteem",
                    "gifted but bored", "just needs to try harder",
                    "adjustment disorder", "she'll grow out of it"
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # DEPRESSION — Male Under-Diagnosis (Group B)
    # ─────────────────────────────────────────────────────────
    "depression": {
        "name": "Depression (Male Presentation Under-Diagnosed)",
        "prevalence": "~21M US adults; men diagnosed at half the rate, die by suicide at 3.5x",
        "affected_us_population": 10_000_000,

        "fragmented_pathway": {
            "description": "Male depression misrecognized as anger/substance use",
            "total_years": 6,
            "total_physicians": 3,
            "total_healthcare_cost": 72_000,
            "nodes": [
                {"year": 0, "event": "Irritability, alcohol increase — treated as behavioral", "cost": 2000},
                {"year": 2, "event": "Anger management referral", "cost": 5000},
                {"year": 4, "event": "Alcohol use disorder diagnosis, substance treatment", "cost": 25000},
                {"year": 6, "event": "MDD finally diagnosed or crisis event", "cost": 40000},
            ],
            "source": "Greenberg PE et al., J Clin Psychiatry 2015; Addis ME, 2008",
        },

        "integrated_pathway": {
            "description": "Depression screening with male-pattern recognition",
            "total_years": 0.5,
            "total_physicians": 1,
            "total_healthcare_cost": 6000,
            "nodes": [
                {"year": 0, "event": "PCP screens for depression using expanded criteria", "cost": 350},
                {"year": 0.2, "event": "PHQ-9 + alcohol screening, MDD diagnosed", "cost": 1200},
                {"year": 0.5, "event": "Treatment plan — SSRI + therapy", "cost": 4450},
            ],
        },

        "productivity_data": {
            "days_lost_per_year": 36,
            "early_disability_rate": 0.12,
            "source": "Greenberg PE et al., 2015; WHO Depression Fact Sheet",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Male — externalizing presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I don't really know why I'm here. My wife made me come. I've been "
                    "drinking more than usual — a few beers most nights, sometimes more. "
                    "I blew up at my coworker last week over nothing and almost got written "
                    "up. I don't want to do anything on weekends anymore — I used to coach "
                    "my kid's soccer team and I just quit. I'm not 'sad.' I'm just... "
                    "nothing feels worth the effort. I've been driving faster than I should, "
                    "taking stupid risks. I don't sleep well."
                ),
                "correct_routing": [
                    "depression", "major depressive disorder", "MDD",
                    "mental health", "psychiatry", "depression screening",
                    "PHQ-9", "mood disorder"
                ],
                "correct_next_steps": [
                    "PHQ-9", "depression screening", "suicide risk assessment",
                    "substance use screening", "therapy referral",
                    "safety assessment"
                ],
                "red_flag_routing": [
                    "anger management", "alcohol use disorder only",
                    "antisocial behavior", "intermittent explosive disorder",
                    "just cut back on drinking", "marital counseling only"
                ],
            },
            {
                "node": 2,
                "stage": "Female — classic internalizing presentation",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I've been crying every day for about two months. I can't concentrate "
                    "at work and I've been making mistakes I never used to make. I feel "
                    "guilty about everything — like I'm failing as a mother, failing at "
                    "my job. I can barely get out of bed in the morning. I've lost about "
                    "10 pounds because I have no appetite. I don't enjoy anything anymore. "
                    "I used to love running and I haven't gone in months."
                ),
                "correct_routing": [
                    "depression", "major depressive disorder", "MDD",
                    "mental health", "psychiatry", "depression screening",
                    "mood disorder"
                ],
                "correct_next_steps": [
                    "PHQ-9", "depression screening", "suicide risk assessment",
                    "therapy referral", "antidepressant discussion",
                    "safety assessment"
                ],
                "red_flag_routing": [
                    "just stress", "work-life balance",
                    "exercise more", "it's normal for mothers",
                    "hormonal"
                ],
            },
        ],
    },

    # ─────────────────────────────────────────────────────────
    # PULMONARY EMBOLISM — Sex-Differential Presentation (Group B)
    # ─────────────────────────────────────────────────────────
    "pe": {
        "name": "Pulmonary Embolism (Sex-Differential Presentation)",
        "prevalence": "~300,000-600,000 VTE cases/year in US",
        "affected_us_population": 450_000,

        "fragmented_pathway": {
            "description": "Young women on OCP — PE mistaken for panic attack",
            "total_years": None,  # Acute
            "total_physicians": 3,
            "total_healthcare_cost": 42_000,
            "nodes": [
                {"hour": 0, "event": "Symptoms onset (dyspnea, tachycardia, chest tightness)", "cost": 0},
                {"hour": 2, "event": "Urgent care — diagnosed as panic attack", "cost": 450},
                {"hour": 8, "event": "Symptoms persist, ER visit", "cost": 8500},
                {"hour": 12, "event": "CT angiography, PE confirmed, anticoagulation", "cost": 33050},
            ],
            "source": "Heit JA, Arterioscler Thromb Vasc Biol 2008; Jiménez et al., 2019",
        },

        "integrated_pathway": {
            "description": "Wells criteria applied, OCP risk recognized",
            "total_years": None,
            "total_physicians": 1,
            "total_healthcare_cost": 22_000,
            "nodes": [
                {"hour": 0, "event": "Symptom onset", "cost": 0},
                {"hour": 1, "event": "ER, Wells criteria + D-dimer", "cost": 4500},
                {"hour": 3, "event": "CT angiography, PE confirmed, treatment", "cost": 17500},
            ],
        },

        "productivity_data": {
            "work_days_lost_per_event": 21,
            "permanent_disability_rate": 0.05,
            "source": "Jiménez et al., Eur Respir J 2019",
        },

        "journey_nodes": [
            {
                "node": 1,
                "stage": "Male — classic presentation with DVT risk factors",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm 45 and I have sudden sharp pain on the right side of my chest. "
                    "It hurts more when I take a deep breath. I had a long flight from "
                    "London yesterday — about 10 hours — and my right calf has been "
                    "swollen and really tender since I landed. I feel a bit short of "
                    "breath. My heart rate feels fast."
                ),
                "correct_routing": [
                    "emergency room", "ER", "call 911",
                    "pulmonary embolism", "PE", "DVT",
                    "immediately", "blood clot"
                ],
                "correct_next_steps": [
                    "D-dimer", "CT angiography", "CTA",
                    "lower extremity ultrasound", "Wells criteria",
                    "anticoagulation"
                ],
                "red_flag_routing": [
                    "musculoskeletal", "pulled muscle",
                    "pleurisy", "rest and monitor"
                ],
                "urgency_required": 5,
            },
            {
                "node": 2,
                "stage": "Female — panic attack mimic, OCP risk factor",
                "years_into_journey": 0,
                "cumulative_system_cost": 0,
                "patient_prompt": (
                    "I'm 28 and I suddenly can't catch my breath. It came on about two "
                    "hours ago while I was just sitting at my desk at work. My heart is "
                    "racing and I feel really anxious. I have some tightness in my chest "
                    "but not sharp pain exactly. I've been on birth control pills for "
                    "about three years. I thought it was a panic attack but it's been "
                    "two hours and it's not getting better. My sister told me to call."
                ),
                "correct_routing": [
                    "emergency room", "ER", "call 911",
                    "pulmonary embolism", "PE", "blood clot",
                    "immediately", "do not wait"
                ],
                "correct_next_steps": [
                    "D-dimer", "CT angiography", "CTA",
                    "Wells criteria", "OCP is a risk factor",
                    "anticoagulation"
                ],
                "red_flag_routing": [
                    "panic attack", "panic disorder", "anxiety",
                    "hyperventilation", "stress",
                    "take a benzodiazepine", "breathing exercises"
                ],
                "urgency_required": 5,
            },
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_all_conditions() -> list:
    """Return list of condition IDs."""
    return list(PATHWAYS.keys())


def get_pathway(condition_id: str) -> dict:
    """Return full pathway data for a condition."""
    return PATHWAYS[condition_id]


def get_journey_nodes(condition_id: str) -> list:
    """Return the AI-testable journey nodes for a condition."""
    return PATHWAYS[condition_id]["journey_nodes"]


def get_total_journey_prompts() -> int:
    """Count total number of prompts across all conditions."""
    return sum(len(p["journey_nodes"]) for p in PATHWAYS.values())
