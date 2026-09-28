from src.classifiers.clause_classifier import get_clause_classifier

classifier = get_clause_classifier()

print("--- 1. Testing 5 Known Example Clauses ---")
examples = [
    "The client will pay 50 dollars.", # Payment
    "No information will be shared with the press.", # Confidentiality
    "We can cancel this contract at any time.", # Termination
    "We are not responsible for any broken software.", # Liability
    "This agreement constitutes the entire understanding." # General
]

for ex in examples:
    cat, conf = classifier.predict(ex)
    print(f"[{cat} - {conf:.2f}] {ex}")

print("\n--- 3. Testing Unknown/General Clause ---")
unknown = "The weather today is exceptionally sunny and bright."
cat, conf = classifier.predict(unknown)
print(f"[{cat} - {conf:.2f}] {unknown}")
