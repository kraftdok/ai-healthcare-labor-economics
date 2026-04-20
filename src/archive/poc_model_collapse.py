import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in .env")
    exit(1)

client = Anthropic(api_key=api_key)

MAX_BUDGET_USD = 3.00

def test_model_collapse():
    print("=" * 80)
    print("🧬 POC 2: SYNTHETIC DATA 'MODEL COLLAPSE' TEST")
    print("Testing if recursive AI data generation progressively erases female-specific symptom profiles.")
    print("=" * 80)

    total_input_tokens = 0
    total_output_tokens = 0
    iterations = 5
    
    # Ground Truth Initial Instruction (representing what happens when you start with a narrow seed of Endometriosis-like pain)
    current_knowledge = """
Generate 3 short, realistic clinical vignettes of women presenting to the emergency room. 
Key requirements: They must be complaining of severe cyclical pelvic pain, dyschezia (painful bowel movements), and dyspareunia (painful intercourse).
Format each as a quick 2-sentence ER triage note.
"""

    for i in range(1, iterations + 1):
        print(f"\n[GENERATION {i}]")
        
        # Financial Kill Switch
        current_cost = ((total_input_tokens / 1_000_000) * 3.00) + ((total_output_tokens / 1_000_000) * 15.00)
        if current_cost >= MAX_BUDGET_USD:
            print(f"!!! CRITICAL HALT: Budget of ${MAX_BUDGET_USD:.2f} exceeded. Halting.")
            break
            
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=400,
            temperature=0.5, # Some variance to allow drift
            messages=[{"role": "user", "content": current_knowledge}]
        )
        
        # Tracking
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens
        
        generation_output = response.content[0].text.strip()
        print(generation_output)
        
        # The crucial step: In the next iteration, the model is asked to generate NEW records 
        # using ONLY the previous generation as its source of "What ER pelvic pain looks like".
        # This simulates a model training exclusively on the synthetic outputs of the previous model.
        current_knowledge = f"""
You are an AI generating synthetic ER records. 
Here are 3 training examples of patients presenting with pelvic pain:
{generation_output}

Based ONLY on the clinical patterns in these 3 examples, generate 3 NEW distinct ER triage notes for women presenting with pelvic pain. 
Make them sound like typical ER presentations that fit the pattern of the training examples. Format as 2-sentence notes.
"""

    # Final Cost Calculation
    total_cost = ((total_input_tokens / 1_000_000) * 3.00) + ((total_output_tokens / 1_000_000) * 15.00)
    print("\n💰 FINANCIAL SAFETY REPORT:")
    print(f"Total Input: {total_input_tokens} | Total Output: {total_output_tokens}")
    print(f"Actual Cost: ${total_cost:.4f}")

if __name__ == "__main__":
    test_model_collapse()
