"""
Unit and integration tests for TF-IDF + Cosine Retrieval Service and search API endpoint.
"""

import asyncio
import io
import unittest
import fitz
import httpx
from src.main import app
from src.services.retrieval_service import RetrievalService, get_retrieval_service
from src.storage.document_store import get_document_store


class TestRetrievalService(unittest.TestCase):
    def setUp(self):
        self.service = RetrievalService(default_threshold=0.15)
        self.clauses = [
            {
                "clause_id": 1,
                "original_text": "1. Confidentiality. The receiving party agrees to keep all trade secrets, financial records, and proprietary information confidential and shall not disclose them to any third party.",
                "predicted_category": "Confidentiality",
            },
            {
                "clause_id": 2,
                "original_text": "2. Payment Terms. The Client shall pay the Consultant a fee of $75,000 for services rendered. Invoices are due net 30 days from receipt. Late payments incur 1.5% monthly interest.",
                "predicted_category": "Payment",
            },
            {
                "clause_id": 3,
                "original_text": "3. Termination. Either party may terminate this agreement with 30 days written notice. In the event of a material breach, the non-breaching party may terminate immediately.",
                "predicted_category": "Termination",
            },
            {
                "clause_id": 4,
                "original_text": "4. Limitation of Liability. In no event shall either party be liable for any indirect, special, or consequential damages. Total liability is capped at fees paid.",
                "predicted_category": "Liability",
            },
        ]

    def test_search_termination_query(self):
        """Test retrieving termination details."""
        res = self.service.search_clauses(self.clauses, "When does this agreement terminate or expire?")
        self.assertTrue(res["found"])
        self.assertEqual(res["clause_category"], "Termination")
        self.assertEqual(res["clause_id"], 3)
        self.assertGreater(res["similarity_score"], 0.15)
        self.assertIn("terminate", res["answer"].lower())
        self.assertIn("3. Termination", res["source_clause"])

    def test_search_payment_query(self):
        """Test retrieving payment terms."""
        res = self.service.search_clauses(self.clauses, "What are the payment terms and invoice due dates?")
        self.assertTrue(res["found"])
        self.assertEqual(res["clause_category"], "Payment")
        self.assertEqual(res["clause_id"], 2)
        self.assertGreater(res["similarity_score"], 0.15)
        self.assertIn("Client shall pay", res["source_clause"])

    def test_search_confidentiality_query(self):
        """Test retrieving confidentiality obligations."""
        res = self.service.search_clauses(self.clauses, "What information is confidential?")
        self.assertTrue(res["found"])
        self.assertEqual(res["clause_category"], "Confidentiality")
        self.assertEqual(res["clause_id"], 1)
        self.assertGreater(res["similarity_score"], 0.15)

    def test_search_liability_query(self):
        """Test retrieving damages and liability info."""
        res = self.service.search_clauses(self.clauses, "Who is responsible for indirect damages?")
        self.assertTrue(res["found"])
        self.assertEqual(res["clause_category"], "Liability")
        self.assertEqual(res["clause_id"], 4)
        self.assertGreater(res["similarity_score"], 0.15)

    def test_threshold_fallback_for_unrelated_query(self):
        """Test that completely unrelated questions do not return random legal clauses."""
        unrelated_query = "What is the recipe for chocolate cake with strawberry frosting?"
        res = self.service.search_clauses(self.clauses, unrelated_query)
        self.assertFalse(res["found"])
        self.assertEqual(res["answer"], "No sufficiently relevant clause was found in this document.")
        self.assertIsNone(res["source_clause"])
        self.assertIsNone(res["clause_category"])
        self.assertIsNone(res["clause_id"])

    def test_empty_or_whitespace_query(self):
        """Test empty question returns fallback response cleanly."""
        res = self.service.search_clauses(self.clauses, "   ")
        self.assertFalse(res["found"])
        self.assertEqual(res["answer"], "No sufficiently relevant clause was found in this document.")

    def test_empty_clauses_list(self):
        """Test search with empty clause list."""
        res = self.service.search_clauses([], "When does contract expire?")
        self.assertFalse(res["found"])


class TestSearchAPIEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_test_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """SERVICE CONTRACT
1. Confidentiality.
All proprietary information disclosed under this agreement shall remain strictly confidential.

2. Invoicing and Payment.
The client agrees to pay invoices within 15 calendar days of receipt. Late charges will apply.

3. Notice and Termination.
Either party may terminate this agreement by providing 30 days written notice.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_search_endpoint_end_to_end(self):
        """Upload a PDF, then search it using POST /api/v1/documents/{document_id}/search."""
        pdf_bytes = self._create_test_pdf()

        async def _run_flow():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Upload & analyze document
                upload_res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("service_agreement.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(upload_res.status_code, 200)
                data = upload_res.json()
                doc_id = data["document_id"]
                self.assertTrue(len(doc_id) > 0)

                # 2. Search relevant question
                search_res = await client.post(
                    f"/api/v1/documents/{doc_id}/search",
                    json={"question": "What is the notice period to terminate?"},
                )
                self.assertEqual(search_res.status_code, 200)
                search_data = search_res.json()

                self.assertTrue(search_data["found"])
                self.assertIn("terminate", search_data["answer"].lower())
                self.assertEqual(search_data["clause_category"], "Termination")
                self.assertGreater(search_data["similarity_score"], 0.15)
                self.assertIsNotNone(search_data["clause_id"])
                self.assertIsNotNone(search_data["source_clause"])

                # 3. Search unrelated question (threshold check)
                unrelated_res = await client.post(
                    f"/api/v1/documents/{doc_id}/search",
                    json={"question": "How do you bake sourdough bread?"},
                )
                self.assertEqual(unrelated_res.status_code, 200)
                unrelated_data = unrelated_res.json()
                self.assertFalse(unrelated_data["found"])
                self.assertEqual(
                    unrelated_data["answer"],
                    "No sufficiently relevant clause was found in this document.",
                )
                self.assertIsNone(unrelated_data["source_clause"])

                # 4. Search non-existent document ID -> 404
                not_found_res = await client.post(
                    "/api/v1/documents/non-existent-uuid-12345/search",
                    json={"question": "When does this expire?"},
                )
                self.assertEqual(not_found_res.status_code, 404)

        asyncio.run(_run_flow())


if __name__ == "__main__":
    unittest.main()
