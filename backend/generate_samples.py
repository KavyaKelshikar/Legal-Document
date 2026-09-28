import fitz
import os

os.makedirs("sample_pdfs", exist_ok=True)

docs = [
    {
        "name": "Standard_Consulting_Agreement.pdf",
        "text": """CONSULTING AGREEMENT

This Consulting Services Agreement is entered into as of January 1, 2025.

1. Confidentiality.
The Consultant shall keep all business information, trade secrets, and client data strictly confidential. No information shall be shared without prior written consent.

2. Payment Terms.
The Client shall pay the Consultant a fixed fee of $50,000 for the completed project. Invoices must be paid within 30 days of receipt.

3. Termination.
Either party may terminate this agreement with 30 days written notice.

4. Limitation of Liability.
The Consultant shall not be liable for any indirect or consequential damages arising from this work.

5. General Provisions.
This agreement constitutes the entire understanding between parties. It is governed by the laws of the State of New York.
"""
    },
    {
        "name": "High_Risk_Vendor_Contract.pdf",
        "text": """VENDOR SERVICES AGREEMENT

1. Termination.
The Client may terminate this contract immediately at their sole discretion without any prior notice.

2. Liability and Indemnification.
The Vendor shall completely indemnify the Client against all third-party claims, damages, and severe penalties. The Vendor assumes full liability for any breach of this contract and any resulting losses.

3. Payment Terms.
Payment will be issued 90 days after delivery of services. Late payments from the Client do not accrue any interest or penalties.
"""
    },
    {
        "name": "Simple_NDA.pdf",
        "text": """NON-DISCLOSURE AGREEMENT

1. Confidential Information.
The Receiving Party agrees not to disclose any Trade Secrets, financial data, or source code to any unauthorized third parties. All proprietary data remains the property of the Disclosing Party.

2. General Provisions.
Any amendments to this document must be made in writing. This contract is governed by the State of Delaware.

3. Liability.
Neither party is held liable for failure to perform due to force majeure.
"""
    }
]

for d in docs:
    doc = fitz.open()
    page = doc.new_page()
    # Insert text with automatic word wrapping (width ~ 500)
    page.insert_textbox(fitz.Rect(50, 50, 550, 750), d["text"], fontsize=11, fontname="helv")
    doc.save(f"sample_pdfs/{d['name']}")
    doc.close()

print("Generated 3 sample PDFs in the 'sample_pdfs' directory.")
