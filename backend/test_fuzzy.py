from src.risk.fuzzy_logic import assess_contract_risk

def run_test(name, text, category):
    print(f"\n--- Testing: {name} ---")
    print(f"Clause: {text}")
    print(f"Type: {category}")
    
    result = assess_contract_risk(text, category)
    
    print("\nFuzzy Inputs:")
    inputs = result["fuzzy_inputs"]
    print(f"Importance: {inputs['importance']}")
    print(f"Ambiguity: {inputs['ambiguity']}")
    print(f"Risk Indicators: {inputs['risk_indicators']}")
    
    print("\nFuzzy Output:")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Notes: {result['activated_rules_summary']}")

# Low Risk
run_test(
    "Low Risk Clause",
    "This agreement constitutes the entire understanding between the parties.",
    "General"
)

# Medium Risk
run_test(
    "Medium Risk Clause",
    "We may cancel this contract at our sole discretion with a customary notice period.",
    "Termination"
)

# High Risk
run_test(
    "High Risk Clause",
    "The client shall indemnify and hold harmless the contractor from any lawsuit, penalty, or damage. The client is liable for any breach.",
    "Liability"
)
