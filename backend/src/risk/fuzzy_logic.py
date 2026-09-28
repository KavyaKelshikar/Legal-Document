import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import re

# 1. DEFINE FUZZY VARIABLES (Antecedents & Consequents)
# Inputs (Ranges 0 to 10)
importance = ctrl.Antecedent(np.arange(0, 11, 1), 'importance')
ambiguity = ctrl.Antecedent(np.arange(0, 11, 1), 'ambiguity')
risk_indicators = ctrl.Antecedent(np.arange(0, 11, 1), 'risk_indicators')

# Output (Range 0 to 100)
risk_score = ctrl.Consequent(np.arange(0, 101, 1), 'risk_score')

# 2. DEFINE MEMBERSHIP FUNCTIONS (Triangular)
importance.automf(3, names=['low', 'medium', 'high'])
ambiguity.automf(3, names=['low', 'medium', 'high'])
risk_indicators.automf(3, names=['low', 'medium', 'high'])

# Custom membership functions for output to ensure sharp distinctions
risk_score['low'] = fuzz.trimf(risk_score.universe, [0, 0, 40])
risk_score['medium'] = fuzz.trimf(risk_score.universe, [20, 50, 80])
risk_score['high'] = fuzz.trimf(risk_score.universe, [60, 100, 100])

# 3. DEFINE FUZZY RULES
# Rule definitions based on legal risk logic
rule1 = ctrl.Rule(importance['high'] & risk_indicators['high'], risk_score['high'])
rule2 = ctrl.Rule(importance['high'] & ambiguity['high'], risk_score['high'])
rule3 = ctrl.Rule(risk_indicators['medium'] & importance['medium'], risk_score['medium'])
rule4 = ctrl.Rule(ambiguity['medium'] | risk_indicators['medium'], risk_score['medium'])
rule5 = ctrl.Rule(importance['low'] & risk_indicators['low'] & ambiguity['low'], risk_score['low'])
rule6 = ctrl.Rule(risk_indicators['low'] & importance['medium'], risk_score['low'])

# 4. BUILD CONTROL SYSTEM
risk_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6])
risk_sim = ctrl.ControlSystemSimulation(risk_ctrl)

def extract_fuzzy_inputs(text: str, category: str) -> dict:
    """Calculates numerical fuzzy inputs based on text analysis."""
    text_lower = text.lower()
    
    # Base importance based on category
    importance_map = {
        "Liability": 9.0,
        "Termination": 8.0,
        "Payment": 7.0,
        "Confidentiality": 6.0,
        "General": 3.0
    }
    imp_val = importance_map.get(category, 5.0)
    
    # Ambiguity calculation (count of vague words)
    vague_words = ["reasonable", "may", "approximate", "customary", "subject to", "sole discretion", "good faith"]
    ambig_count = sum(len(re.findall(r'\b' + vw + r'\b', text_lower)) for vw in vague_words)
    ambig_val = min(10.0, ambig_count * 2.5) # Scale to 0-10
    
    # Risk indicator calculation (count of severe terms)
    severe_words = ["indemnify", "breach", "penalty", "damage", "liable", "void", "immediate", "lawsuit", "sue"]
    risk_count = sum(len(re.findall(r'\b' + sw + r'\b', text_lower)) for sw in severe_words)
    risk_val = min(10.0, risk_count * 3.0) # Scale to 0-10
    
    return {
        "importance": imp_val,
        "ambiguity": ambig_val,
        "risk_indicators": risk_val
    }

def assess_contract_risk(text: str, category: str) -> dict:
    """
    Executes the fuzzy logic inference system to calculate contract risk.
    """
    inputs = extract_fuzzy_inputs(text, category)
    
    # Load inputs into simulation
    risk_sim.input['importance'] = inputs['importance']
    risk_sim.input['ambiguity'] = inputs['ambiguity']
    risk_sim.input['risk_indicators'] = inputs['risk_indicators']
    
    # Compute output (Defuzzification happens internally using centroid method)
    try:
        risk_sim.compute()
        score = float(risk_sim.output['risk_score'])
    except ValueError:
        # If no rules fire, default to medium
        score = 50.0
        
    # Classify into discrete label
    if score >= 65:
        level = "HIGH"
    elif score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
        
    return {
        "fuzzy_inputs": inputs,
        "risk_score": round(score, 2),
        "risk_level": level,
        "activated_rules_summary": "Fuzzy rules fired based on scikit-fuzzy ControlSystemSimulation centroid defuzzification."
    }
