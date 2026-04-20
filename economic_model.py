"""
Economic Cascade Model: Diagnosis timing → Lifetime labor productivity impact.

Maps the clinical pathway outcome to economic consequences:
  Diagnosis acceleration → Treatment cost saved → Work capacity restored
  → Productivity days recovered → Disability deferred → Pension extended
  → Lifetime earnings impact → Population-level GDP effect

All parameters sourced from published data (BLS, SSA, CBO, clinical literature).
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

    # Sources
    "sources": {
        "wage": "BLS Occupational Employment and Wage Statistics, May 2024",
        "disability": "SSA Annual Statistical Supplement, 2024",
        "employer": "SHRM Employee Benefits Survey 2024; DOL Cost of Absenteeism",
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
) -> dict:
    """
    Compute the full economic cascade of earlier diagnosis.

    Args:
        condition_name: Name of condition
        diagnosis_acceleration_years: Years of delay compressed by AI
        excess_annual_healthcare_cost: Per-patient annual excess cost during undiagnosed period
        productivity_days_lost_per_year: Work days lost per year due to undiagnosed condition
        affected_population: Number of affected individuals (US)
        early_disability_rate: Fraction who go on early disability due to delayed diagnosis
        avg_disability_acceleration_years: How many years earlier they enter disability
        presenteeism_factor: Multiplier for productivity loss while at work (1.0 = no presenteeism)

    Returns:
        Dict with per-patient and population-level economic impact
    """
    p = ECONOMIC_PARAMS

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

    return {
        "condition": condition_name,
        "diagnosis_acceleration_years": diagnosis_acceleration_years,

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
            "total_lifetime_economic_value": round(per_patient_total),
        },

        # Population-level
        "population": {
            "affected_population": affected_population,
            "healthcare_saved": round(pop_healthcare),
            "productivity_restored": round(pop_productivity),
            "employer_savings": round(pop_employer),
            "disability_savings": round(pop_disability),
            "pension_savings": round(pop_pension),
            "total_economic_impact": round(pop_total),
            "total_billions": round(pop_total / 1_000_000_000, 2),
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
        presenteeism_factor=1.4,
    )

    cascades["fibro"] = compute_cascade(
        condition_name="Fibromyalgia",
        diagnosis_acceleration_years=4.0,  # from 5 to ~1 year
        excess_annual_healthcare_cost=6_282,
        productivity_days_lost_per_year=50.4,
        affected_population=10_000_000,
        early_disability_rate=0.25,
        avg_disability_acceleration_years=8,
        presenteeism_factor=1.3,
    )

    cascades["gdm"] = compute_cascade(
        condition_name="GDM → Type 2 Diabetes Pipeline",
        diagnosis_acceleration_years=5.0,  # catching prediabetes 5 years earlier
        excess_annual_healthcare_cost=16_752,
        productivity_days_lost_per_year=27.6,
        affected_population=200_000,  # new cases per year
        early_disability_rate=0.18,
        avg_disability_acceleration_years=7,
        presenteeism_factor=1.2,
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
        presenteeism_factor=1.2,
    )

    cascades["perimenopause"] = compute_cascade(
        condition_name="Perimenopause",
        diagnosis_acceleration_years=3.5,  # from 4.0 to ~0.5 years
        excess_annual_healthcare_cost=10_116,
        productivity_days_lost_per_year=33.6,
        affected_population=20_000_000,
        early_disability_rate=0.05,
        avg_disability_acceleration_years=3,
        presenteeism_factor=1.3,
    )

    cascades["diabetes_t2"] = compute_cascade(
        condition_name="Type 2 Diabetes (Female delayed diagnosis)",
        diagnosis_acceleration_years=4.0,  # from 4.5 to ~0.5 years
        excess_annual_healthcare_cost=16_752,
        productivity_days_lost_per_year=27.6,
        affected_population=18_000_000,
        early_disability_rate=0.18,
        avg_disability_acceleration_years=7,
        presenteeism_factor=1.2,
    )

    cascades["depression"] = compute_cascade(
        condition_name="Depression (Male under-diagnosis)",
        diagnosis_acceleration_years=5.5,  # from 6 to ~0.5 years
        excess_annual_healthcare_cost=12_000,
        productivity_days_lost_per_year=36,
        affected_population=10_000_000,
        early_disability_rate=0.12,
        avg_disability_acceleration_years=5,
        presenteeism_factor=1.4,
    )

    return cascades


if __name__ == "__main__":
    """Print all cascades when run directly."""
    cascades = compute_all_cascades()
    for cid, cascade in cascades.items():
        print(format_cascade(cascade))
        print()
