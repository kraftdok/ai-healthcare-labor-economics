# Arm C — Condition Library (Methodology Validation)

Labor-economic cascade applied systematically across five drivers of health-related workforce exit, spanning both sexes, with Claude performing bottleneck classification per condition.

## Which file is canonical?

Read [`condition_library_findings.md`](condition_library_findings.md) **first** — it is the primary, more conservative analysis. The indirect recomputation is a companion that makes a separate methodological point about valuation choice.

| File | What it is | When to cite |
|---|---|---|
| [`condition_library_findings.md`](condition_library_findings.md) | **Primary.** Direct-wage cascade, BLS median × foregone hours only. Defensible lower bound. | When you need the conservative, reproducible baseline. $12–73B aggregate, 42% female. |
| [`condition_library_indirect_findings.md`](condition_library_indirect_findings.md) | **Companion.** Recomputation adding presenteeism, unpaid caregiving, and women's-health bias-tax channels. | When you want to make the methodological point that valuation choice matters. $77B aggregate, 48% female. |
| [`workforce_exit_endometriosis.md`](workforce_exit_endometriosis.md) | Single-condition pilot memo — the first application of the cascade, later generalized to the 5-condition library. | For historical context on how the methodology developed. |

**The finding that matters is the sign-change**, not either absolute number: direct-wage valuation reports the library as 42% female-accruing; once presenteeism, caregiving, and the bias-tax are included, the same five conditions flip to 48% female-accruing. Six percentage points is the methodological finding — direct-wage accounting systematically under-weights female-accruing AI-labor value, even across a library where three of five conditions are male-dominant in direct terms.

## Scripts

`src/pilot_condition_library.py` · `src/analyze_condition_library.py` · `src/analyze_condition_library_indirect.py`
