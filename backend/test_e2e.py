"""
End-to-end integration test for the AI Legal Document Assistant pipeline.
Tests the full flow: PDF Upload → Extract → Preprocess → Segment → Classify → Risk → Document Score
"""
import os
import json
import fitz  # PyMuPDF

import requests

# ── Step 1: Generate a realistic multi-clause legal PDF ──
CONTRACT_TEXT = """CONSULTING SERVICES AGREEMENT

This Consulting Services Agreement ("Agreement") is entered into as of January 1, 2025.

1. Confidentiality.
The Consultant agrees to keep all proprietary information, trade secrets, and business
strategies strictly confidential. Neither party shall disclose any confidential information
to any third party without prior written consent.

2. Payment Terms.
The Client shall pay the Consultant a fee of $75,000 for services rendered under this
Agreement. Invoices are due net 30 from the date of receipt. Late payments will accrue
interest at a rate of 1.5% per month.

3. Termination.
Either party may terminate this Agreement with 60 days written notice. In the event of
a material breach, the non-breaching party may terminate immediately upon written notice.

4. Limitation of Liability.
In no event shall either party be liable for any indirect, incidental, or consequential
damages arising out of this Agreement. The Consultant shall indemnify the Client against
all claims related to breach of confidentiality. Any penalty for breach shall not exceed
the total fees paid.

5. General Provisions.
This Agreement constitutes the entire understanding between the parties. Any amendments
must be made in writing and signed by both parties. This contract shall be governed by
the laws of the State of California.
"""

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), CONTRACT_TEXT, fontsize=10)

os.makedirs("test_pdfs", exist_ok=True)
pdf_path = "test_pdfs/full_contract.pdf"
doc.save(pdf_path)
doc.close()
print(f"[OK] Created test PDF: {pdf_path}")

# ── Step 2: Send to the /api/v1/analyze endpoint ──
URL = "http://127.0.0.1:8000/api/v1/analyze"

print("\n" + "=" * 70)
print("  END-TO-END PIPELINE TEST: AI Legal Document Assistant")
print("=" * 70)

with open(pdf_path, 'rb') as f:
    files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
    response = requests.post(URL, files=files)

if response.status_code != 200:
    print(f"\n[FAIL] Server returned status {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()

# ── Step 3: Display Results ──
print(f"\nFilename: {data['filename']}")
print(f"Pages: {data['metadata'].get('page_count', 'N/A')}")
print(f"Total Clauses Extracted: {data['total_clauses']}")

print("\n" + "-" * 70)
print("  CLAUSE-LEVEL ANALYSIS")
print("-" * 70)

for c in data["clauses"]:
    fi = c["fuzzy_inputs"]
    print(f"\n[Clause {c['clause_id']}]")
    print(f"  Text:       {c['original_text'][:100]}...")
    print(f"  Category:   {c['predicted_category']}  (confidence: {c['classification_confidence']:.4f})")
    print(f"  Fuzzy In:   Importance={fi['importance']}, Ambiguity={fi['ambiguity']}, Risk Indicators={fi['risk_indicators']}")
    print(f"  Risk Score: {c['risk_score']}")
    print(f"  Risk Level: {c['risk_level']}")

print("\n" + "-" * 70)
print("  OVERALL DOCUMENT RISK")
print("-" * 70)

doc_risk = data["document_risk"]
print(f"\n  Overall Risk Score: {doc_risk['overall_score']}")
print(f"  Overall Risk Level: {doc_risk['overall_level']}")
print(f"  Category Breakdown: {json.dumps(doc_risk['category_breakdown'], indent=4)}")

print("\n" + "=" * 70)
print(f"  RESULT: {'PASS' if data['total_clauses'] > 0 else 'FAIL'}")
print("=" * 70)
