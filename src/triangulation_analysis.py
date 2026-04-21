#!/usr/bin/env python3
"""
Supply-demand triangulation: where do physicians (N=200 × 6 countries) and
patients (N=981 × 42 countries) INDEPENDENTLY name the same gaps in women's
health AI/research — and where do they diverge?

Inputs:
    findings/08_womens_ai_gap_taxonomy/taxonomy.json  (patient-side Q49 themes)
    findings/09_physician_patient_triangulation/physician_survey_data.json

Outputs:
    findings/09_physician_patient_triangulation/triangulation.json
    (+ printed summary of convergent / divergent / patient-only / physician-only gaps)
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PATIENT_TAX = HERE / "findings" / "08_womens_ai_gap_taxonomy" / "taxonomy.json"
PHYS_DATA = HERE / "findings" / "09_physician_patient_triangulation" / "physician_survey_data.json"
OUT_JSON = HERE / "findings" / "09_physician_patient_triangulation" / "triangulation.json"


def average_across_countries(country_condition_dict: dict, condition_key: str) -> float:
    """Average physician % across countries for a single condition."""
    vals = []
    for country, conds in country_condition_dict.items():
        if isinstance(conds, dict) and condition_key in conds and isinstance(conds[condition_key], (int, float)):
            vals.append(conds[condition_key])
    return sum(vals) / len(vals) if vals else 0


def main():
    patient = json.loads(PATIENT_TAX.read_text())
    physician = json.loads(PHYS_DATA.read_text())

    # Patient-side: primary-theme percentages from Q49
    p_primary = patient["q49"]["primary_theme_distribution"]
    p_any = patient["q49"]["any_theme_distribution"]
    p_n = patient["q49"]["n_responses"]

    # Physician-side: average % across countries for each condition
    onc = physician["data"]["oncology_conditions_needing_more_research_pct"]
    endo = physician["data"]["endocrinology_conditions_needing_more_research_pct"]
    card = physician["data"]["cardiology_conditions_needing_more_research_pct"]
    neuro = physician["data"]["neurology_conditions_needing_more_research_pct"]
    oph = physician["data"]["ophthalmology_conditions_needing_more_research_pct"]

    phys_averages = {
        "breast_cancer": average_across_countries(onc, "breast"),
        "ovarian_cancer": average_across_countries(onc, "ovarian"),
        "cervical_cancer": average_across_countries(onc, "cervical"),
        "endometrial_cancer": average_across_countries(onc, "endometrial"),
        "pcos": average_across_countries(endo, "pcos"),
        "osteoporosis": average_across_countries(endo, "osteoporosis"),
        "thyroid": average_across_countries(endo, "thyroid"),
        "heart_attack_female": average_across_countries(card, "heart_attack_symptoms"),
        "heart_failure": average_across_countries(card, "heart_failure"),
        "stroke": average_across_countries(card, "stroke"),
        "hypertension": average_across_countries(card, "hypertension"),
        "migraines": average_across_countries(neuro, "migraines"),
        "ms": average_across_countries(neuro, "ms"),
        "alzheimers": average_across_countries(neuro, "alzheimers"),
        "amd": average_across_countries(oph, "amd"),
        "diabetic_retinopathy": average_across_countries(oph, "dr"),
    }

    # Map patient themes → physician condition categories where possible
    # (Unmappable patient themes are explicitly listed as "patient_only")
    MAPPING = {
        "cardiovascular_female_presentation": ["heart_attack_female", "heart_failure", "stroke"],
        "endometriosis_pcos_fibroids": ["pcos"],
        "cancer_female_specific": ["breast_cancer", "ovarian_cancer", "cervical_cancer", "endometrial_cancer"],
        "menopause_perimenopause": [],  # NO physician track
        "medical_dismissal_gaslighting": [],  # NO physician track
        "autoimmune": [],  # NO physician track (no rheumatology)
        "mental_health_neurodiversity": [],  # NO physician track (no psychiatry)
        "pharmacokinetics_dosing": [],  # NO physician track (cross-cutting)
        "pain_management": [],  # NO physician track
        "fertility_pregnancy_postpartum": [],  # NO physician track (no OB/GYN tier 1)
        "caregiver_burden_maternal_load": [],  # NO physician track
        "clinical_trials_representation": [],  # NO physician track
        "intersectional_woc_lmic_age": [],  # cross-cutting, no direct
        "symptoms_presentation": [],  # too generic to map
    }

    triangulation = []
    for patient_theme, phys_conds in MAPPING.items():
        p_rate = p_primary.get(patient_theme, 0) / p_n * 100
        p_any_rate = p_any.get(patient_theme, 0) / p_n * 100
        if phys_conds:
            # Convergent — both sides have a signal
            phys_rate = sum(phys_averages[c] for c in phys_conds) / len(phys_conds)
            row = {
                "patient_theme": patient_theme,
                "patient_primary_pct": round(p_rate, 1),
                "patient_any_pct": round(p_any_rate, 1),
                "physician_conditions": phys_conds,
                "physician_avg_across_countries_pct": round(phys_rate, 1),
                "category": "convergent" if p_any_rate > 1 and phys_rate > 30 else "weakly_convergent",
            }
        else:
            # Patient-only (no physician specialty track)
            row = {
                "patient_theme": patient_theme,
                "patient_primary_pct": round(p_rate, 1),
                "patient_any_pct": round(p_any_rate, 1),
                "physician_conditions": None,
                "physician_avg_across_countries_pct": None,
                "category": "patient_only_no_physician_track",
            }
        triangulation.append(row)

    # Physician-only conditions (specialty-specific research gaps that patients don't name)
    patient_any_themes = set(p_any.keys())
    physician_only = []
    phys_only_map = {
        "lung_cancer": ("oncology", "lung"),
        "hematological_cancer": ("oncology", "hematological"),
        "diabetes_type2": ("endocrinology", "diabetes"),
        "hypertension_cv": ("cardiology", "hypertension"),
        "epilepsy": ("neurology", "epilepsy"),
        "amd_eye": ("ophthalmology", "amd"),
        "diabetic_retinopathy": ("ophthalmology", "dr"),
        "dme_eye": ("ophthalmology", "dme"),
        "rvo_eye": ("ophthalmology", "rvo"),
        "uveitis": ("ophthalmology", "uveitis"),
        "ms_neurology": ("neurology", "ms"),
        "alzheimers_neurology": ("neurology", "alzheimers"),
        "osteoporosis_endo": ("endocrinology", "osteoporosis"),
    }
    spec_lookup = {
        "oncology": onc, "endocrinology": endo, "cardiology": card,
        "neurology": neuro, "ophthalmology": oph,
    }
    for label, (spec, cond) in phys_only_map.items():
        rate = average_across_countries(spec_lookup[spec], cond)
        physician_only.append({
            "physician_condition": label,
            "specialty": spec,
            "avg_pct_across_countries": round(rate, 1),
        })
    physician_only.sort(key=lambda r: -r["avg_pct_across_countries"])

    out = {
        "patient_data_source": "FemTechnology Workplace Survey 2024, N=981 × 42 countries (primary data by author)",
        "physician_data_source": "Roche/HBA/FemTechnology Women's Health Physician Survey 2024, N=200 × 6 countries (primary data by author)",
        "triangulation_mapping": triangulation,
        "patient_only_themes_no_physician_specialty": [
            r for r in triangulation if r["category"] == "patient_only_no_physician_track"
        ],
        "convergent_themes": [
            r for r in triangulation if r["category"] == "convergent"
        ],
        "physician_identified_condition_priorities_no_direct_patient_theme": physician_only,
        "design_blind_spot_note": physician["data"]["design_blind_spot"]["description"],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2))

    # Console summary
    print("=" * 76)
    print("TRIANGULATION: patient (N=981 × 42 countries) × physician (N=200 × 6 countries)")
    print("=" * 76)
    print()
    print("--- CONVERGENT themes (both sides flag the same gap) ---")
    for r in triangulation:
        if r["category"] in ("convergent", "weakly_convergent"):
            print(f"  {r['patient_theme']:<40}")
            print(f"    patient primary: {r['patient_primary_pct']:>5.1f}% · any-label: {r['patient_any_pct']:>5.1f}%")
            print(f"    physician avg:   {r['physician_avg_across_countries_pct']:>5.1f}%  ({', '.join(r['physician_conditions'])})")
            ratio = r['physician_avg_across_countries_pct'] / max(r['patient_any_pct'], 0.1)
            print(f"    physician/patient intensity ratio: {ratio:.1f}×")
            print()

    print("\n--- PATIENT-ONLY themes (no physician-specialty track in this survey) ---")
    for r in triangulation:
        if r["category"] == "patient_only_no_physician_track":
            print(f"  {r['patient_theme']:<40}  primary: {r['patient_primary_pct']:>5.1f}% · any: {r['patient_any_pct']:>5.1f}%")

    print("\n--- PHYSICIAN-IDENTIFIED priorities with no direct patient theme ---")
    for r in physician_only[:10]:
        print(f"  {r['physician_condition']:<30} ({r['specialty']:<15}) {r['avg_pct_across_countries']:>5.1f}%")


if __name__ == "__main__":
    main()
