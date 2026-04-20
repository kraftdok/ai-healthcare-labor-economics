import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

# Load API key
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in .env")
    exit(1)

client = Anthropic(api_key=api_key)

# The Clinical Scenario
# Markedly elevated Alkaline Phosphatase (ALP) is pathological in a non-pregnant adult (biliary/liver/bone issues).
# However, during the 3rd trimester, the placenta produces high amounts of ALP, making elevated levels physiological.
# Postpartum, it takes weeks to return to baseline.
base_clinical_vignette = """
The patient is a 32-year-old female. 
Recent routine labs show a markedly elevated Alkaline Phosphatase (ALP) at 320 U/L (reference range 44-147 U/L). 
AST and ALT are within normal limits. GGT is normal. Bilirubin is normal. 
Patient reports mild fatigue and mild ankle edema. No abdominal pain.
"""

# The three dynamic states
states = {
    "Not Pregnant": "The patient is not pregnant and has no relevant medical history.",
    "3rd Trimester": "The patient is currently in her 3rd trimester of pregnancy (34 weeks gestation).",
    "Postpartum": "The patient gave birth 4 weeks ago and is currently postpartum."
}

def analyze_life_stage():
    print("=" * 80)
    print("🧪 POC 1: LIFE-STAGE INTERPRETATION TEST")
    print("Testing if Claude contextualizes borderline labs dynamically based on reproductive state.")
    print("=" * 80)
    
    total_input_tokens = 0
    total_output_tokens = 0

    MAX_BUDGET_USD = 3.00
    
    for state_name, state_desc in states.items():
        print(f"\nEvaluating State: {state_name}")
        
        # Calculate current real-time cost before making the next call
        current_cost = ((total_input_tokens / 1_000_000) * 3.00) + ((total_output_tokens / 1_000_000) * 15.00)
        if current_cost >= MAX_BUDGET_USD:
            print(f"!!! CRITICAL HALT: Current cost (${current_cost:.4f}) has exceeded the hard-coded budget of ${MAX_BUDGET_USD:.2f}. Halting execution immediately.")
            break
            
        prompt = f"""
{base_clinical_vignette}
{state_desc}

Provide a brief 2-sentence clinical assessment. 
Then, provide a rigid severity score from 1 to 10 (where 1 is perfectly normal physiology requiring no intervention, and 10 is an acute emergency).
Format output as:
Assessment: [2 sentences]
Severity: [1-10]
"""
        
        # Hard limit enforced via explicit max_tokens
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Cost tracking
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
        
        reply = response.content[0].text.strip()
        print(reply)
        print("-" * 50)

    # Final Cost Calculation
    input_cost = (total_input_tokens / 1_000_000) * 3.00
    output_cost = (total_output_tokens / 1_000_000) * 15.00
    total_cost = input_cost + output_cost

    print("\n💰 FINANCIAL SAFETY REPORT:")
    print(f"Total Input Tokens:  {total_input_tokens}")
    print(f"Total Output Tokens: {total_output_tokens}")
    print(f"Actual Cost: ${total_cost:.4f}")
    if total_cost < MAX_BUDGET_USD:
        print(f"Status: Safely under ${MAX_BUDGET_USD:.2f} limit.")

if __name__ == "__main__":
    analyze_life_stage()
