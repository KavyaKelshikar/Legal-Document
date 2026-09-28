"""
Unit and integration tests for SummaryService and the Summary API endpoint.
"""

import asyncio
import io
import unittest
import fitz
import httpx
from src.main import app
from src.services.summary_service import SummaryService, get_summary_service
from src.storage.document_store import get_document_store


class TestSummaryService(unittest.TestCase):
    def setUp(self):
        self.service = SummaryService()
        self.clauses = [
            {
                "clause_id": 1,
                "original_text": "This Agreement is entered into as of January 1, 2025. The term of this agreement shall remain in effect for two years.",
                "predicted_category": "General",
            },
            {
                "clause_id": 2,
                "original_text": "The receiving party shall keep all proprietary information and trade secrets strictly confidential and shall not disclose them to third parties without prior written consent.",
                "predicted_category": "Confidentiality",
            },
            {
                "clause_id": 3,
                "original_text": "The Client shall pay the Consultant a fee of $75,000 for services rendered. Invoices are due net 30 days from the date of receipt. Late payments accrue interest at 1.5% per month.",
                "predicted_category": "Payment",
            },
            {
                "clause_id": 4,
                "original_text": "Either party may terminate this agreement with 60 days written notice. In the event of a material breach, the non-breaching party may terminate immediately.",
                "predicted_category": "Termination",
            },
            {
                "clause_id": 5,
                "original_text": "In no event shall either party be liable for any indirect, special, or consequential damages. Total liability of the vendor shall not exceed the total fees paid.",
                "predicted_category": "Liability",
            },
        ]

    def test_duration_extraction(self):
        """Test 1: Duration extraction finds term and effective dates."""
        summary = self.service.extract_summary(self.clauses)
        dur = summary["duration"]
        self.assertEqual(dur["status"], "detected")
        self.assertIsNotNone(dur["text"])
        self.assertIn("term of this agreement", dur["text"].lower())
        self.assertEqual(dur["clause_category"], "General")

    def test_payment_terms_extraction(self):
        """Test 2: Payment terms extraction finds fees and due dates."""
        summary = self.service.extract_summary(self.clauses)
        pay = summary["payment_terms"]
        self.assertEqual(pay["status"], "detected")
        self.assertIsNotNone(pay["text"])
        self.assertTrue("$75,000" in pay["text"] or "due net 30" in pay["text"])
        self.assertEqual(pay["clause_category"], "Payment")

    def test_termination_extraction(self):
        """Test 3: Termination extraction finds notice period and conditions."""
        summary = self.service.extract_summary(self.clauses)
        term = summary["termination"]
        self.assertEqual(term["status"], "detected")
        self.assertIsNotNone(term["text"])
        self.assertIn("written notice", term["text"].lower())
        self.assertEqual(term["clause_category"], "Termination")

    def test_confidentiality_extraction(self):
        """Test 4: Confidentiality extraction captures protection obligations."""
        summary = self.service.extract_summary(self.clauses)
        conf = summary["confidentiality"]
        self.assertEqual(conf["status"], "detected")
        self.assertIsNotNone(conf["text"])
        self.assertIn("confidential", conf["text"].lower())
        self.assertEqual(conf["clause_category"], "Confidentiality")

    def test_liability_extraction(self):
        """Test 5: Liability extraction captures caps and indemnification."""
        summary = self.service.extract_summary(self.clauses)
        liab = summary["liability"]
        self.assertEqual(liab["status"], "detected")
        self.assertIsNotNone(liab["text"])
        self.assertIn("liability", liab["text"].lower())
        self.assertEqual(liab["clause_category"], "Liability")

    def test_correct_source_clause_and_category(self):
        """Test 6: Each detected category contains valid source clause and category."""
        summary = self.service.extract_summary(self.clauses)
        for cat_name in ["duration", "payment_terms", "termination", "confidentiality", "liability"]:
            cat_data = summary[cat_name]
            self.assertEqual(cat_data["status"], "detected")
            self.assertIn(cat_data["text"], cat_data["source_clause"])
            self.assertIsNotNone(cat_data["clause_category"])

    def test_missing_category_returns_not_detected(self):
        """Test 7: Missing category returns 'not_detected' without hallucinating."""
        # Only Payment and Confidentiality present
        partial_clauses = [
            {
                "clause_id": 1,
                "original_text": "The party agrees to pay the fee of $1,000 due net 30 days.",
                "predicted_category": "Payment",
            },
            {
                "clause_id": 2,
                "original_text": "All proprietary information shall remain strictly confidential.",
                "predicted_category": "Confidentiality",
            },
        ]
        summary = self.service.extract_summary(partial_clauses)

        self.assertEqual(summary["payment_terms"]["status"], "detected")
        self.assertEqual(summary["confidentiality"]["status"], "detected")

        # Missing categories must be not_detected
        self.assertEqual(summary["duration"]["status"], "not_detected")
        self.assertIsNone(summary["duration"]["text"])
        self.assertIsNone(summary["duration"]["source_clause"])
        self.assertIsNone(summary["duration"]["clause_category"])

        self.assertEqual(summary["termination"]["status"], "not_detected")
        self.assertIsNone(summary["termination"]["text"])
        self.assertIsNone(summary["termination"]["source_clause"])

        self.assertEqual(summary["liability"]["status"], "not_detected")
        self.assertIsNone(summary["liability"]["text"])
        self.assertIsNone(summary["liability"]["source_clause"])

    def test_no_hallucination_on_empty_clauses(self):
        """Test 8: Empty clauses list produces all not_detected and no invented text."""
        summary = self.service.extract_summary([])
        for cat in ["duration", "payment_terms", "termination", "confidentiality", "liability"]:
            self.assertEqual(summary[cat]["status"], "not_detected")
            self.assertIsNone(summary[cat]["text"])
            self.assertIsNone(summary[cat]["source_clause"])
            self.assertIsNone(summary[cat]["clause_category"])


class TestSummaryEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_contract_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """STANDARD CONSULTING CONTRACT

This Agreement is entered into as of January 1, 2025 for a period of one year.

1. Confidentiality.
The parties agree to keep all trade secrets and proprietary information confidential.

2. Payment Terms.
The client shall pay the fee of $15,000 payable within 30 days of invoice receipt.

3. Termination.
Either party may terminate this agreement with 30 days written notice.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_summary_endpoint_end_to_end(self):
        """Test 9: End-to-end PDF upload and summary endpoint retrieval."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Analyze PDF
                res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("consulting_summary.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(res.status_code, 200)
                data = res.json()
                doc_id = data["document_id"]

                # Ensure summary is in the analyze response
                self.assertIn("summary", data)
                self.assertEqual(data["summary"]["confidentiality"]["status"], "detected")
                self.assertEqual(data["summary"]["payment_terms"]["status"], "detected")
                self.assertEqual(data["summary"]["termination"]["status"], "detected")

                # 2. Query GET /api/v1/documents/{document_id}/summary
                sum_res = await client.get(f"/api/v1/documents/{doc_id}/summary")
                self.assertEqual(sum_res.status_code, 200)
                sum_data = sum_res.json()

                self.assertIn("duration", sum_data)
                self.assertIn("payment_terms", sum_data)
                self.assertIn("termination", sum_data)
                self.assertIn("confidentiality", sum_data)
                self.assertIn("liability", sum_data)

                self.assertEqual(sum_data["payment_terms"]["status"], "detected")
                self.assertIn("$15,000", sum_data["payment_terms"]["text"])

                # 3. Test 10: Invalid document ID returns 404
                not_found = await client.get("/api/v1/documents/non-existent-uuid-9999/summary")
                self.assertEqual(not_found.status_code, 404)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
