# Arm H — Women's AI-Healthcare Gap Taxonomy

A Clio-style taxonomy (Tamkin, Handa, Durmus et al., 2024) applied to 618 open-ended survey responses from 981 working women across 42 countries. Methodological homage to Anthropic's Clio conversation-clustering work, but applied to survey free-text rather than Claude conversations.

**Headline:** taxonomy of 16 distinct themes in how working women perceive AI-healthcare failure modes, with five novel findings that do not appear in the published literature.

## Files

| File | Purpose |
|---|---|
| [`findings.md`](findings.md) | Full writeup with tables, quotes, cross-country, novel findings |
| [`taxonomy.json`](taxonomy.json) | Machine-readable taxonomy + theme distributions |
| [`q49_labeled.csv`](q49_labeled.csv) | All 330 Q49 responses with country, primary theme, secondary themes |
| [`q50_labeled.csv`](q50_labeled.csv) | All 288 Q50 responses with country, primary theme, secondary themes |
| [`q49_raw.json`](q49_raw.json) | Raw Q49 responses (country-tagged, PII-stripped) |
| [`q50_raw.json`](q50_raw.json) | Raw Q50 responses (country-tagged, PII-stripped) |

## How to reproduce

```bash
pip install openpyxl
python3 src/taxonomy_analysis.py
```

Raw survey xlsx not included in repository (FemTechnology 2024 primary data; respondent consent terms cover aggregate publication only). Analysis regenerates from the committed `q49_raw.json` and `q50_raw.json`.

## Top finding in one sentence

*Working women across 42 countries name **symptom-presentation gaps** (29% of responses) and **menopause/perimenopause** (10%) as the dominant AI-healthcare failure modes — ahead of any specific disease — while simultaneously reporting a measurable AI-literacy gap (15–30%) that the literature has not surfaced.*
