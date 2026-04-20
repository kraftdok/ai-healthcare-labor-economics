"""Economic Cascade Model — see module docstring below."""
from __future__ import annotations

"""
Economic Cascade Model: Diagnosis timing → Lifetime labor productivity impact.

Maps the clinical pathway outcome to economic consequences:
  Diagnosis acceleration → Treatment cost saved → Work capacity restored
  → Productivity days recovered → Disability deferred → Pension extended
  → Lifetime earnings impact → Population-level GDP effect

All parameters sourced from published data (BLS, SSA, CBO, clinical literature).

The cascade computes a THEORETICAL MAXIMUM assuming 100% conversion at every
stage of the causal chain from AI output to realized labor recovery. In
reality there is substantial friction — adoption gaps, system gatekeeping,
insurance barriers, sustained-outcome attrition. The `system_friction_discount`
parameter (default 0.15) scales the theoretical max to a REALISTIC PROBABLE
estimate. Both values are emitted. See the "Funnel assumptions" sections in
the condition-library and enterprise-verticals findings memos for the
stage-by-stage multiplication that produced the default discount.
"""


# ═══════════════════════════════════════════════════════════════
# ECONOMIC PARAMETERS (US, 2024 dollars)
# ═══════════════════════════════════════════════════════════════

ECONOMIC_PARAMS = {
    # Labor market (BLS 2024)
    "median_hourly_wage": 29.76,
    "median_daily_earnings": 238.08,  # 8-hour day
    "median_annual_earnings": 59520,
    "working_days_per_year": 250,

    # Disability & pension (SSA 2024)
    "avg_annual_ssdi_benefit": 22_344,
    "avg_working_years_remaining_at_40": 27,
    "avg_working_years_remaining_at_50": 17,

    # Employer costs (DOL, SHRM)
    "avg_employer_cost_per_absence_day": 385,  # includes replacement, lost output
    "avg_annual_employer_healthcare_premium": 16_236,  # employer share

    # Friction discount: realistic_probable = theoretical_max × this factor.
    # Derived as the product of five realistic-range midpoints in the
    # condition-library funnel: adoption (0.4) × AI guideline-pass (0.9) ×
    # patient/clinician action (0.6) × system compliance (0.7) ×
    # treatment initiation × sustained outcome (0.8 × 0.75) ≈ 0.09.
    # For less complex enterprise flows the equivalent is ~0.18. We use a
    # midpoint default of 0.15; callers can override.
    "default_system_friction_discount": 0.15,

    # Sources
    "sources": {
        "wage": "BLS Occupational Employment and Wage Statistics, May 2024",
        "disability": "SSA Annual Statistical Supplement, 2024",
        "employer": "SHRM Employee Benefits Survey 2024; DOL Cost of Absenteeism",
        "presenteeism": (
            "Condition-specific multipliers: endometriosis 1.4× (Simoens et al., "
            "Hum Reprod 2012); depression 1.4–2.0× (Stewart et al., JAMA 2003; "
            "Goetzel et al., JOEM 2004); fibromyalgia 1.3–1.8× (Robinson et al., "
            "Pain Res Manag 2012); perimenopause 1.3–1.5× (Faubion et al., "
            "Menopause 2023); chronic pain/MSK 1.5–1.8× (Stewart 2003 meta)."
        ),
        "friction": (
            "Derived from multi-stage adoption/compliance funnel; see README "
            "'Known limitations' and findings-level 'Funnel assumptions' tables."
        ),
    },
}


def compute_cascade(
    condition_name: str,
    diagnosis_acceleration_years: float,
    excess_annual_healthcare_cost: float,
    productivity_days_lost_per_year: float,
    affected_population: int,
    early_disability_rate: float = 0.15,
    avg_disability_acceleration_years: float = 5.0,
    presenteeism_factor: float = 1.3,
    system_friction_discount: float | None = None,
    is_acute: bool = False,
) -> dict:
    """
    Compute the full economic cascade of earlier diagnosis.

    Emits BOTH a theoretical-maximum projection (100% conversion at every
    stage) and a realistic-probable estimate (theoretical × friction_discount).
    The realistic_probable value is the one to cite in discussion of
    expected-value recovery; the theoretical_max is useful only as an upper
    bound for sensitivity analysis.

    Args:
        condition_name: Name of condition
        diagnosis_acceleration_years: Years of delay compressed by AI
        excess_annual_healthcare_cost: Per-patient annual excess cost during undiagnosed period
        productivity_days_lost_per_year: Work days lost per year due to undiagnosed condition
        affected_population: Number of affected individuals (US)
        early_disability_rate: Fraction who go on early disability due to delayed diagnosis
        avg_disability_acceleration_years: How many years earlier they enter disability
        presenteeism_factor: Multiplier for productivity loss while at work (1.0 = no presenteeism).
            Condition-specific values; see ECONOMIC_PARAMS['sources']['presenteeism'].
        system_friction_discount: Multiplier mapping theoretical max → realistic probable.
            Default (None) uses ECONOMIC_PARAMS['default_system_friction_discount'] = 0.15.
            Pass 1.0 to disable discounting and emit only the theoretical max.
        is_acute: If True, flags the cascade as outside the chronic-delay model
            scope. Caller is responsible for overriding the output appropriately.
            Emitted in the returned dict so downstream aggregations can exclude.

    Returns:
        Dict with per-patient and population-level economic impact, both
        theoretical_max and realistic_probable.
    """
    p = ECONOMIC_PARAMS
    if system_friction_discount is None:
        system_friction_discount = p["default_system_friction_discount"]

    # ── PER-PATIENT: Direct healthcare savings ──
    healthcare_saved = excess_annual_healthcare_cost * diagnosis_acceleration_years

    # ── PER-PATIENT: Productivity restored ──
    # Absenteeism (days not worked)
    absenteeism_days_restored = productivity_days_lost_per_year * diagnosis_acceleration_years
    absenteeism_earnings_restored = absenteeism_days_restored * p["median_daily_earnings"]

    # Presenteeism (reduced output while at work)
    presenteeism_cost_restored = (
        absenteeism_earnings_restored * (presenteeism_factor - 1.0)
    )

    total_productivity_restored = absenteeism_earnings_restored + presenteeism_cost_restored

    # ── PER-PATIENT: Employer cost savings ──
    employer_absence_savings = (
        absenteeism_days_restored * p["avg_employer_cost_per_absence_day"]
    )

    # ── PER-PATIENT: Disability cascade ──
    # If earlier diagnosis prevents/defers disability:
    disability_deferral_value = (
        early_disability_rate *
        avg_disability_acceleration_years *
        (p["median_annual_earnings"] - p["avg_annual_ssdi_benefit"])
    )
    # ^ The economic value = years of full earnings minus reduced disability payments

    pension_system_savings = (
        early_disability_rate *
        avg_disability_acceleration_years *
        p["avg_annual_ssdi_benefit"]
    )

    # ── PER-PATIENT: Total lifetime economic value ──
    per_patient_total = (
        healthcare_saved +
        total_productivity_restored +
        employer_absence_savings +
        disability_deferral_value +
        pension_system_savings
    )

    # ── POPULATION-LEVEL ──
    pop_healthcare = healthcare_saved * affected_population
    pop_productivity = total_productivity_restored * affected_population
    pop_employer = employer_absence_savings * affected_population
    pop_disability = disability_deferral_value * affected_population
    pop_pension = pension_system_savings * affected_population
    pop_total = per_patient_total * affected_population

    # ── FRICTION DISCOUNT → realistic probable ──
    per_patient_realistic = per_patient_total * system_friction_discount
    pop_total_realistic = pop_total * system_friction_discount

    return {
        "condition": condition_name,
        "diagnosis_acceleration_years": diagnosis_acceleration_years,
        "is_acute": is_acute,
        "system_friction_discount_applied": system_friction_discount,

        # Per-patient breakdown
        "per_patient": {
            "healthcare_saved": round(healthcare_saved),
            "absenteeism_days_restored": round(absenteeism_days_restored, 1),
            "absenteeism_earnings_restored": round(absenteeism_earnings_restored),
            "presenteeism_cost_restored": round(presenteeism_cost_restored),
            "total_productivity_restored": round(total_productivity_restored),
            "employer_absence_savings": round(employer_absence_savings),
            "disability_deferral_value": round(disability_deferral_value),
            "pension_system_savings": round(pension_system_savings),
            # THEORETICAL MAX — assumes 100% conversion at every stage
            "total_lifetime_economic_value": round(per_patient_total),
            # REALISTIC PROBABLE — theoretical max × friction discount
            "total_lifetime_economic_value_realistic": round(per_patient_realistic),
        },

        # Population-level
        "population": {
            "affected_population": affected_population,
            "healthcare_saved": round(pop_healthcare),
            "productivity_restored": round(pop_productivity),
            "employer_savings": round(pop_employer),
            "disability_savings": round(pop_disability),
            "pension_savings": round(pop_pension),
            # THEORETICAL MAX
            "total_economic_impact": round(pop_total),
            "total_billions": round(pop_total / 1_000_000_000, 2),
            # REALISTIC PROBABLE
            "total_economic_impact_realistic": round(pop_total_realistic),
            "total_billions_realistic": round(pop_total_realistic / 1_000_000_000, 2),
        },

        "sources": ECONOMIC_PARAMS["sources"],
    }


def format_cascade(result: dict) -> str:
    """Format economic cascade as readable text."""
    pp = result["per_patient"]
    pop = result["population"]
    lines = []

    lines.append(f"{'='*65}")
    lines.append(f"ECONOMIC CASCADE: {result['condition']}")
    lines.append(f"Diagnosis accelerated by {result['diagnosis_acceleration_years']} years")
    lines.append(f"{'='*65}")

    lines.append(f"\n  PER PATIENT:")
    lines.append(f"    Healthcare saved:           ${pp['healthcare_saved']:>10,}")
    lines.append(f"    Work days restored:          {pp['absenteeism_days_restored']:>10.0f} days")
    lines.append(f"    Earnings restored:          ${pp['absenteeism_earnings_restored']:>10,}")
    lines.append(f"    Presenteeism recovered:     ${pp['presenteeism_cost_restored']:>10,}")
    lines.append(f"    Employer absence savings:   ${pp['employer_absence_savings']:>10,}")
    lines.append(f"    Disability deferral value:  ${pp['disability_deferral_value']:>10,}")
    lines.append(f"    Pension system savings:     ${pp['pension_system_savings']:>10,}")
    lines.append(f"    {'─'*46}")
    lines.append(f"    TOTAL PER PATIENT:          ${pp['total_lifetime_economic_value']:>10,}")

    lines.append(f"\n  POPULATION ({pop['affected_population']:,} affected):")
    lines.append(f"    Healthcare:        ${pop['healthcare_saved']:>15,}")
    lines.append(f"    Productivity:      ${pop['productivity_restored']:>15,}")
    lines.append(f"    Employer savings:  ${pop['employer_savings']:>15,}")
    lines.append(f"    Disability:        ${pop['disability_savings']:>15,}")
    lines.append(f"    Pension:           ${pop['pension_savings']:>15,}")
    lines.append(f"    {'─'*46}")
    lines.append(f"    TOTAL:             ${pop['total_economic_impact']:>15,}")
    lines.append(f"                       (${pop['total_billions']}B)")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# PRECOMPUTED CASCADES FOR KNOWN CONDITIONS
# ═══════════════════════════════════════════════════════════════

def compute_all_cascades() -> dict:
    """Compute economic cascades for all conditions at max pathway compression."""
    cascades = {}

    cascades["endo"] = compute_cascade(
        condition_name="Endometriosis",
        diagnosis_acceleration_years=5.2,  # from 6.7 to ~1.5 years
        excess_annual_healthcare_cost=10_002,
        productivity_days_lost_per_year=45.6,
        affected_population=6_500_000,
        early_disability_rate=0.12,
        avg_disability_acceleration_years=6,
        presenteeism_factor=1.4,  # Simoens et al., Hum Reprod 2012
    )

    cascades["fibro"] = compute_cascade(
        condition_name="Fibromyalgia",
        diagnosis_acceleration_years=4.0,  # from 5 to ~1 year
        excess_annual_healthcare_cost=6_282,
        productivity_days_lost_per_year=50.4,
        affected_population=10_000_000,
        early_disability_rate=0.25,
        avg_disability_acceleration_years=8,
        presenteeism_factor=1.5,  # Robinson et al., Pain Res Manag 2012 (midpoint 1.3–1.8)
    )

    cascades["gdm"] = compute_cascade(
        condition_name="GDM → Type 2 Diabetes Pipeline",
        diagnosis_acceleration_years=5.0,  # catching prediabetes 5 years earlier
        excess_annual_healthcare_cost=16_752,
        productivity_days_lost_per_year=27.6,
        affected_population=200_000,  # new cases per year
        early_disability_rate=0.18,
        avg_disability_acceleration_years=7,
        presenteeism_factor=1.2,  # Goetzel et al., JOEM 2004 (diabetes cohort)
    )

    # -------------------------------------------------------------------------
    # ACS (acute coronary syndrome) — KNOWN METHODOLOGICAL COMPROMISE
    #
    # ACS does not fit the chronic diagnostic-delay cascade this function
    # implements. For chronic conditions, the cascade computes labor recovery
    # as (diagnosis-acceleration years × annual productivity/healthcare
    # parameters). For ACS, the relevant cost is the acute event itself (PCI
    # delay, post-MI disability deferral), which is a one-time event, not an
    # annualized flow.
    #
    # This pilot inserts ACS using an acute-event override rather than
    # building a separate acute-event model. The override parameters below
    # are sourced from AHA post-MI rehab guidelines (~45-day recovery median)
    # and published PCI-delay cost literature (~$20K excess healthcare cost
    # for delayed vs. timely intervention). The cascade-model output is
    # overwritten post-hoc.
    #
    # Readers should treat the ACS projection as ILLUSTRATIVE ONLY. A proper
    # acute-event cost model (chained with probability of progression to
    # disability) is extension-phase work. This override is called out in
    # the README's "Known limitations" section.
    # -------------------------------------------------------------------------
    cascades["acs_female"] = compute_cascade(
        condition_name="ACS — Female Presentation (Acute)",
        diagnosis_acceleration_years=0.03,  # ~12 hours saved (measured in year fraction)
        excess_annual_healthcare_cost=0,  # Not annual — one-time event
        productivity_days_lost_per_year=0,
        affected_population=400_000,
        early_disability_rate=0.22,
        avg_disability_acceleration_years=10,
        presenteeism_factor=1.0,
        is_acute=True,  # flag: exclude from chronic-cascade aggregates
    )
    # Override ACS with acute-event economics (cascade model does not apply — see header block).
    cascades["acs_female"]["per_patient"]["healthcare_saved"] = 20_000  # delayed vs. timely PCI
    cascades["acs_female"]["per_patient"]["total_lifetime_economic_value"] = (
        20_000 +  # healthcare
        45 * ECONOMIC_PARAMS["median_daily_earnings"] +  # reduced recovery time
        0.22 * 10 * (ECONOMIC_PARAMS["median_annual_earnings"] -
                      ECONOMIC_PARAMS["avg_annual_ssdi_benefit"])  # disability deferral
    )
    cascades["acs_female"]["population"]["total_economic_impact"] = round(
        cascades["acs_female"]["per_patient"]["total_lifetime_economic_value"] * 400_000
    )
    cascades["acs_female"]["population"]["total_billions"] = round(
        cascades["acs_female"]["population"]["total_economic_impact"] / 1e9, 2
    )
    cascades["acs_female"]["notes"] = (
        "Override: cascade model does not apply to acute events; parameters sourced "
        "from AHA post-MI rehab guidelines + published PCI-delay cost literature. "
        "Treat as illustrative only. See header comment block above."
    )

    cascades["pcos"] = compute_cascade(
        condition_name="PCOS",
        diagnosis_acceleration_years=2.9,  # from 3.4 to ~0.5 years
        excess_annual_healthcare_cost=3_192,
        productivity_days_lost_per_year=30,
        affected_population=6_000_000,
        early_disability_rate=0.08,
        avg_disability_acceleration_years=4,
        presenteeism_factor=1.2,  # Goetzel et al., JOEM 2004 (hormonal cohort)
    )

    cascades["perimenopause"] = compute_cascade(
        condition_name="Perimenopause",
        diagnosis_acceleration_years=3.5,  # from 4.0 to ~0.5 years
        excess_annual_healthcare_cost=10_116,
        productivity_days_lost_per_year=33.6,
        affected_population=20_000_000,
        early_disability_rate=0.05,
        avg_disability_acceleration_years=3,
        presenteeism_factor=1.4,  # Faubion et al., Menopause 2023 (midpoint 1.3–1.5)
    )

    cascades["diabetes_t2"] = compute_cascade(
        condition_name="Type 2 Diabetes (Female delayed diagnosis)",
        diagnosis_acceleration_years=4.0,  # from 4.5 to ~0.5 years
        excess_annual_healthcare_cost=16_752,
        productivity_days_lost_per_year=27.6,
        affected_population=18_000_000,
        early_disability_rate=0.18,
        avg_disability_acceleration_years=7,
        presenteeism_factor=1.2,  # Goetzel et al., JOEM 2004 (diabetes cohort)
    )

    cascades["depression"] = compute_cascade(
        condition_name="Depression (Male under-diagnosis)",
        diagnosis_acceleration_years=5.5,  # from 6 to ~0.5 years
        excess_annual_healthcare_cost=12_000,
        productivity_days_lost_per_year=36,
        affected_population=10_000_000,
        early_disability_rate=0.12,
        avg_disability_acceleration_years=5,
        presenteeism_factor=1.9,  # Stewart et al., JAMA 2003; Goetzel JOEM 2004 (midpoint 1.4–2.0)
    )

    return cascades


def aggregate_chronic_only(cascades: dict) -> dict:
    """Sum theoretical and realistic totals across chronic conditions, EXCLUDING
    conditions flagged as acute (is_acute=True). Keeps ACS and any other acute
    overrides out of headline aggregates, since the chronic cascade model does
    not apply to acute events."""
    chronic_theoretical = 0
    chronic_realistic = 0
    excluded = []
    for cid, c in cascades.items():
        if c.get("is_acute"):
            excluded.append(cid)
            continue
        chronic_theoretical += c["population"]["total_economic_impact"]
        chronic_realistic += c["population"].get(
            "total_economic_impact_realistic",
            c["population"]["total_economic_impact"]
            * ECONOMIC_PARAMS["default_system_friction_discount"],
        )
    return {
        "chronic_conditions_included": [
            cid for cid in cascades if not cascades[cid].get("is_acute")
        ],
        "acute_excluded": excluded,
        "theoretical_max_total_usd": round(chronic_theoretical),
        "theoretical_max_total_billions": round(chronic_theoretical / 1e9, 2),
        "realistic_probable_total_usd": round(chronic_realistic),
        "realistic_probable_total_billions": round(chronic_realistic / 1e9, 2),
        "friction_discount_applied": ECONOMIC_PARAMS["default_system_friction_discount"],
    }


if __name__ == "__main__":
    """Print all cascades when run directly."""
    cascades = compute_all_cascades()
    for cid, cascade in cascades.items():
        print(format_cascade(cascade))
        print()
    print("═" * 65)
    print("CHRONIC-ONLY AGGREGATE (acute conditions excluded)")
    print("═" * 65)
    agg = aggregate_chronic_only(cascades)
    print(f"  Theoretical max:    ${agg['theoretical_max_total_billions']:>8.2f}B")
    print(f"  Realistic probable: ${agg['realistic_probable_total_billions']:>8.2f}B "
          f"(× {agg['friction_discount_applied']:.2f} friction discount)")
    print(f"  Excluded (acute):   {agg['acute_excluded']}")
