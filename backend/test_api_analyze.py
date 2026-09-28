"""
Integration test for /api/v1/analyze with DocumentStore.
"""

import io
import unittest
import fitz
import asyncio
import httpx
from src.main import app
from src.storage.document_store import get_document_store


class TestAnalyzeEndpointIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_sample_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """LEGAL SERVICES AGREEMENT
1. Confidentiality.
All proprietary information disclosed under this agreement shall be kept confidential.

2. Payment Terms.
The client agrees to pay the service provider $2,500 net 30.

3. Termination.
Either party may terminate this agreement with 30 days written notice.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_analyze_persists_and_returns_document_id(self):
        pdf_bytes = self._create_sample_pdf()

        async def _call():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                return await client.post(
                    "/api/v1/analyze",
                    files={"file": ("test_legal_doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )

        response = asyncio.run(_call())
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check document_id is present
        self.assertIn("document_id", data)
        doc_id = data["document_id"]
        self.assertTrue(len(doc_id) > 10)

        # Check all existing keys are strictly preserved
        self.assertEqual(data["filename"], "test_legal_doc.pdf")
        self.assertIn("metadata", data)
        self.assertIn("total_clauses", data)
        self.assertGreater(data["total_clauses"], 0)
        self.assertIn("clauses", data)
        self.assertIn("document_risk", data)

        # Check existing clause fields
        first_clause = data["clauses"][0]
        self.assertIn("clause_id", first_clause)
        self.assertIn("original_text", first_clause)
        self.assertIn("predicted_category", first_clause)
        self.assertIn("classification_confidence", first_clause)
        self.assertIn("fuzzy_inputs", first_clause)
        self.assertIn("risk_score", first_clause)
        self.assertIn("risk_level", first_clause)

        # Check existing document_risk fields
        doc_risk = data["document_risk"]
        self.assertIn("overall_score", doc_risk)
        self.assertIn("overall_level", doc_risk)
        self.assertIn("category_breakdown", doc_risk)

        # Check that it was saved into DocumentStore
        stored_doc = self.store.get_document(doc_id)
        self.assertIsNotNone(stored_doc)
        self.assertEqual(stored_doc["document_id"], doc_id)
        self.assertEqual(stored_doc["filename"], "test_legal_doc.pdf")
        self.assertEqual(stored_doc["total_clauses"], data["total_clauses"])

        # Check that get_latest_document returns this doc
        latest = self.store.get_latest_document()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["document_id"], doc_id)


if __name__ == "__main__":
    unittest.main()
