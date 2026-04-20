"""
Source vignettes from PubMed Central case reports.

Uses NCBI E-utilities API (no key needed for <3 requests/second).

WORKFLOW:
1. Run this script to search PubMed for candidate case reports
2. Manually review each case report
3. Extract: chief complaint, HPI, review of systems, vitals, PMH
4. Strip the diagnosis from the extracted text
5. Use the clinical language from the real case, not invented language
6. Record PMID, DOI, journal, year for citation
7. Populate data/vignettes.json with the extracted presentations
8. Create sex/age variants programmatically using generate_variants()
"""

import requests
import json
import time
import re
import copy
from pathlib import Path


PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Search queries designed to find open-access case reports with relevant presentations
CONDITION_QUERIES = {
    "acute_coronary_syndrome_atypical": (
        '"case report"[Title] AND ("acute coronary syndrome"[Title] OR '
        '"myocardial infarction"[Title]) AND ("atypical"[Title/Abstract] OR '
        '"unusual presentation"[Title/Abstract]) AND "female"[Title/Abstract]'
    ),
    "endometriosis": (
        '"case report"[Title] AND "endometriosis"[Title] AND '
        '("diagnostic delay"[Title/Abstract] OR "delayed diagnosis"[Title/Abstract])'
    ),
    "adhd_inattentive": (
        '"case report"[Title] AND ("ADHD"[Title] OR '
        '"attention deficit"[Title]) AND ("adult"[Title/Abstract] OR '
        '"woman"[Title/Abstract] OR "female"[Title/Abstract])'
    ),
    "autoimmune_lupus": (
        '"case report"[Title] AND ("systemic lupus"[Title] OR '
        '"SLE"[Title]) AND "diagnosis"[Title/Abstract]'
    ),
    "acute_mi_classic": (
        '"case report"[Title] AND "myocardial infarction"[Title] AND '
        '"chest pain"[Title/Abstract] AND "ST elevation"[Title/Abstract]'
    ),
}


def search_pubmed(query: str, max_results: int = 5) -> list:
    """Search PubMed Central and return PMC IDs."""
    params = {
        "db": "pmc",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
    }
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_article_summary(pmcid: str) -> dict:
    """Fetch article metadata from PubMed Central."""
    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "json",
    }
    response = requests.get(PUBMED_SUMMARY_URL, params=params)
    response.raise_for_status()
    data = response.json()
    result = data.get("result", {})
    if pmcid in result:
        article = result[pmcid]
        return {
            "pmcid": f"PMC{pmcid}",
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "pubdate": article.get("pubdate", ""),
            "doi": next(
                (aid["value"] for aid in article.get("articleids", [])
                 if aid.get("idtype") == "doi"),
                ""
            ),
        }
    return {"pmcid": f"PMC{pmcid}", "title": "Not found"}


def fetch_full_text(pmcid: str) -> str:
    """Fetch full text XML from PubMed Central."""
    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml",
        "rettype": "full",
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    response.raise_for_status()
    return response.text


def extract_case_presentation(xml_text: str) -> str:
    """
    Attempt to extract case presentation section from PMC XML.
    
    This is a rough extraction — manual review is REQUIRED.
    The function looks for common section headers like 
    'Case Report', 'Case Presentation', 'Case Description'.
    """
    # Look for case presentation/report sections
    patterns = [
        r'<title>Case\s*(?:Report|Presentation|Description)</title>(.*?)</sec>',
        r'<title>Clinical\s*(?:Presentation|Case)</title>(.*?)</sec>',
        r'<title>History\s*of\s*Present\s*Illness</title>(.*?)</sec>',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, xml_text, re.DOTALL | re.IGNORECASE)
        if match:
            # Strip XML tags for readable text
            text = re.sub(r'<[^>]+>', ' ', match.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:2000]  # Cap at 2000 chars
    
    return "Case presentation section not found — manual extraction required from full text."


def search_all_conditions(output_path: str = "data/pubmed_search_results.json"):
    """Run PubMed searches for all conditions and save results."""
    
    all_results = {}
    
    for condition, query in CONDITION_QUERIES.items():
        print(f"\n{'='*60}")
        print(f"Condition: {condition}")
        print(f"Query: {query}")
        
        pmcids = search_pubmed(query)
        print(f"Found {len(pmcids)} results")
        
        condition_results = []
        
        for pmcid in pmcids[:3]:  # Top 3 per condition
            time.sleep(0.4)  # Rate limit
            
            summary = fetch_article_summary(pmcid)
            print(f"\n  PMC{pmcid}: {summary.get('title', 'No title')[:80]}")
            print(f"  Journal: {summary.get('source', 'N/A')}")
            print(f"  Date: {summary.get('pubdate', 'N/A')}")
            print(f"  DOI: {summary.get('doi', 'N/A')}")
            
            time.sleep(0.4)  # Rate limit
            
            # Try to fetch and extract case presentation
            try:
                full_text = fetch_full_text(pmcid)
                presentation = extract_case_presentation(full_text)
                print(f"  Extracted presentation ({len(presentation)} chars):")
                print(f"    {presentation[:200]}...")
            except Exception as e:
                presentation = f"Error fetching: {e}"
                print(f"  Error: {e}")
            
            condition_results.append({
                **summary,
                "extracted_presentation": presentation,
                "status": "NEEDS_MANUAL_REVIEW",
            })
            
            time.sleep(0.4)  # Rate limit
        
        all_results[condition] = condition_results
    
    # Save results
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n\nSaved search results to {output_path}")
    print("NEXT STEP: Manually review each case report and extract presenting symptoms.")
    print("Then populate data/vignettes.json with the extracted presentations.")
    
    return all_results


def generate_sex_variant(vignette: dict, target_sex: str) -> dict:
    """
    Generate a sex variant of a vignette by changing sex markers.
    
    IMPORTANT: This only handles pronoun/sex-marker substitution.
    For endometriosis male variants, dysmenorrhea must be manually
    removed from the presentation text.
    """
    variant = copy.deepcopy(vignette)
    presentation = variant["presentation"]
    
    # Get original sex for replacement direction
    original_sex = variant["patient_sex"]
    
    if target_sex == "female":
        variant["patient_sex"] = "female"
        # These replacements are idempotent if already female
        
    elif target_sex == "male":
        variant["patient_sex"] = "male"
        replacements = [
            (r'\bwoman\b', 'man'),
            (r'\bWoman\b', 'Man'),
            (r'\bfemale\b', 'male'),
            (r'\bFemale\b', 'Male'),
            (r'\b[Ss]he\b', lambda m: 'He' if m.group()[0].isupper() else 'he'),
            (r'\b[Hh]er\b(?!\s+(?:own|self))', lambda m: 'His' if m.group()[0].isupper() else 'his'),
            (r'\bherself\b', 'himself'),
            (r'\bHerself\b', 'Himself'),
            (r'\bMs\.\b', 'Mr.'),
        ]
        for pattern, replacement in replacements:
            if callable(replacement):
                presentation = re.sub(pattern, replacement, presentation)
            else:
                presentation = re.sub(pattern, replacement, presentation)
    
    elif target_sex == "unspecified":
        variant["patient_sex"] = "unspecified"
        replacements = [
            (r'\b(?:woman|man)\b', 'patient'),
            (r'\b(?:Woman|Man)\b', 'Patient'),
            (r'\b(?:female|male)\b', 'patient'),
            (r'\b(?:Female|Male)\b', 'Patient'),
            (r'\b[Ss]he\b', lambda m: 'They' if m.group()[0].isupper() else 'they'),
            (r'\b[Hh]is\b', lambda m: 'Their' if m.group()[0].isupper() else 'their'),
            (r'\b[Hh]er\b', lambda m: 'Their' if m.group()[0].isupper() else 'their'),
            (r'\b(?:himself|herself)\b', 'themselves'),
            (r'\b(?:Himself|Herself)\b', 'Themselves'),
            (r'\b(?:Ms\.|Mr\.)\b', 'Mx.'),
        ]
        for pattern, replacement in replacements:
            if callable(replacement):
                presentation = re.sub(pattern, replacement, presentation)
            else:
                presentation = re.sub(pattern, replacement, presentation)
    
    variant["presentation"] = presentation
    
    # Update vignette_id
    old_sex = original_sex
    variant["vignette_id"] = variant["vignette_id"].replace(
        f"_{old_sex}", f"_{target_sex}"
    )
    
    return variant


def generate_age_variant(vignette: dict, target_age: int) -> dict:
    """Generate an age variant of a vignette."""
    variant = copy.deepcopy(vignette)
    original_age = variant["patient_age"]
    
    # Update age in presentation text
    variant["presentation"] = re.sub(
        rf'\b{original_age}-year-old\b',
        f'{target_age}-year-old',
        variant["presentation"]
    )
    variant["patient_age"] = target_age
    
    # Update vignette_id
    variant["vignette_id"] = variant["vignette_id"].replace(
        f"_age{original_age}_", f"_age{target_age}_"
    )
    
    return variant


def generate_all_variants(base_vignettes_path: str = "data/vignettes.json",
                          output_path: str = "data/vignettes_full.json"):
    """
    Generate the full 45-vignette set from base vignettes.
    
    Takes the base vignettes (age 42, one per sex per condition)
    and generates age variants at 32 and 55.
    
    5 conditions × 3 sexes × 3 ages = 45 vignettes
    """
    with open(base_vignettes_path) as f:
        base_vignettes = json.load(f)
    
    # Filter out the instruction comment entry
    base_vignettes = [v for v in base_vignettes if "vignette_id" in v]
    
    all_vignettes = []
    ages = [32, 42, 55]
    
    for vignette in base_vignettes:
        # The base vignette is age 42 — keep it
        all_vignettes.append(vignette)
        
        # Generate age variants
        for age in ages:
            if age == vignette["patient_age"]:
                continue  # Skip — already have this one
            variant = generate_age_variant(vignette, age)
            all_vignettes.append(variant)
    
    # Sort by condition, then sex, then age
    all_vignettes.sort(key=lambda v: (
        v["condition"],
        {"female": 0, "male": 1, "unspecified": 2}.get(v["patient_sex"], 3),
        v["patient_age"]
    ))
    
    with open(output_path, "w") as f:
        json.dump(all_vignettes, f, indent=2)
    
    print(f"Generated {len(all_vignettes)} vignettes from {len(base_vignettes)} base vignettes")
    print(f"Saved to {output_path}")
    
    # Summary
    from collections import Counter
    conditions = Counter(v["condition"] for v in all_vignettes)
    sexes = Counter(v["patient_sex"] for v in all_vignettes)
    ages_count = Counter(v["patient_age"] for v in all_vignettes)
    
    print(f"\nBy condition: {dict(conditions)}")
    print(f"By sex: {dict(sexes)}")
    print(f"By age: {dict(ages_count)}")
    
    return all_vignettes


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        # Generate all variants from populated base vignettes
        generate_all_variants()
    else:
        # Default: search PubMed for candidate case reports
        search_all_conditions()
