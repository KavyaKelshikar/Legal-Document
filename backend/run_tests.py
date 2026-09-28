import os
import requests
import fitz

# Create a valid PDF using PyMuPDF with multiple clauses
doc = fitz.open()
page = doc.new_page()

text = """NON-DISCLOSURE AGREEMENT

1. Confidentiality.
The parties agree not to disclose any confidential information to third parties. All proprietary data shall remain the property of the disclosing party.

2. Termination.
This agreement may be terminated by either party with a 30-day written notice. Upon termination, all confidential materials must be returned immediately.

3. Payment Terms.
The receiving party agrees to pay the sum of $50,000 for the consulting services rendered. Payment is due within 15 days of invoice receipt.
"""

page.insert_text((50, 50), text)
if not os.path.exists("test_pdfs"):
    os.makedirs("test_pdfs")
doc.save("test_pdfs/valid_multi_clause.pdf")
doc.close()

URL = "http://127.0.0.1:8000/api/v1/extract"

def test_upload(filepath, name):
    print(f"\n--- Testing: {name} ---")
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'application/pdf')}
            response = requests.post(URL, files=files)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                clauses = data.get("clauses", [])
                print(f"Extracted {len(clauses)} clauses.\n")
                for c in clauses:
                    print(f"[Clause {c['clause_id']}]")
                    print(f"  Text: {c['text']}")
                    print(f"  Category: {c.get('category')} (confidence: {c.get('confidence', 0.0):.2f})")
                    fi = c.get('fuzzy_inputs', {})
                    print(f"  Fuzzy Inputs -> Importance: {fi.get('importance')}, Ambiguity: {fi.get('ambiguity')}, Risk Indicators: {fi.get('risk_indicators')}")
                    print(f"  Risk Score: {c.get('risk_score')}  |  Risk Level: {c.get('risk_level')}")
                    print()
            else:
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

print("Running tests...")
test_upload("test_pdfs/valid_multi_clause.pdf", "Multi-clause PDF")
