from src.classifiers.clause_classifier import get_clause_classifier

c = get_clause_classifier()

tests = [
    ("The vendor is not liable for damages", "Liability"),
    ("Cancel this contract at any time", "Termination"),
    ("Pay $5000 monthly", "Payment"),
    ("Keep all information secret", "Confidentiality"),
    ("Governed by the laws of Delaware", "General"),
    ("We are not responsible for broken software", "Liability"),
    ("Terminate immediately upon breach", "Termination"),
    ("Invoice due upon receipt", "Payment"),
]

correct = 0
for text, expected in tests:
    got, conf = c.predict(text)
    match = "CORRECT" if got == expected else "WRONG"
    if got == expected:
        correct += 1
    print(f"[{match}] Expected={expected}, Got={got}, Conf={conf:.3f} | \"{text}\"")

print(f"\nAccuracy: {correct}/{len(tests)} = {correct/len(tests)*100:.0f}%")
