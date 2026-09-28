"""
Unit and integration tests for MissingClauseService and GET /api/v1/documents/{id}/missing-clauses.
"""

import asyncio
import io
import unittest
import fitz
import httpx
from src.main import app
from src.services.missing_clause_service import (
    MissingClauseService,
    get_missing_clause_service,
    EXPECTED_CATEGORIES,
)
from src.storage.document_store import get_document_store


class TestMissingClauseService(unittest.TestCase):
    def setUp(self):
        self.service = MissingClauseService()

    def test_all_categories_present(self):
        """Test 1: When all 5 categories are present, missing_count is 0."""
        clauses = [
            {"clause_id": 1, "predicted_category": "Payment"},
            {"clause_id": 2, "predicted_category": "Confidentiality"},
            {"clause_id": 3, "predicted_category": "Termination"},
            {"clause_id": 4, "predicted_category": "Liability"},
            {"clause_id": 5, "predicted_category": "General"},
        ]
        res = self.service.detect_missing_clauses(clauses)
        self.assertEqual(res["missing_count"], 0)
        self.assertEqual(len(res["missing_clauses"]), 0)
        self.assertEqual(len(res["detected_categories"]), 5)

    def test_missing_single_category(self):
        """Test 2: When Liability is missing, exactly 1 missing finding is created."""
        clauses = [
            {"clause_id": 1, "predicted_category": "Payment"},
            {"clause_id": 2, "predicted_category": "Confidentiality"},
            {"clause_id": 3, "predicted_category": "Termination"},
            {"clause_id": 4, "predicted_category": "General"},
        ]
        res = self.service.detect_missing_clauses(clauses)
        self.assertEqual(res["missing_count"], 1)
        self.assertIn("Liability", [f["category"] for f in res["missing_clauses"]])
        self.assertNotIn("Liability", res["detected_categories"])

    def test_empty_clauses_all_missing(self):
        """Test 3: Empty clauses list marks all 5 expected categories as missing."""
        res = self.service.detect_missing_clauses([])
        self.assertEqual(res["missing_count"], 5)
        self.assertEqual(len(res["detected_categories"]), 0)
        categories_flagged = [f["category"] for f in res["missing_clauses"]]
        for cat in EXPECTED_CATEGORIES:
            self.assertIn(cat, categories_flagged)

    def test_only_general_clauses(self):
        """Test 4: When only General clauses exist, 4 specific categories are missing."""
        clauses = [
            {"clause_id": 1, "predicted_category": "General"},
            {"clause_id": 2, "predicted_category": "General"},
        ]
        res = self.service.detect_missing_clauses(clauses)
        self.assertEqual(res["missing_count"], 4)
        self.assertEqual(res["detected_categories"], ["General"])
        missing_cats = [f["category"] for f in res["missing_clauses"]]
        self.assertIn("Payment", missing_cats)
        self.assertIn("Confidentiality", missing_cats)
        self.assertIn("Termination", missing_cats)
        self.assertIn("Liability", missing_cats)
        self.assertNotIn("General", missing_cats)

    def test_duplicate_categories(self):
        """Test 5: Multiple clauses with the same category are counted once in detected."""
        clauses = [
            {"clause_id": 1, "predicted_category": "Payment"},
            {"clause_id": 2, "predicted_category": "Payment"},
            {"clause_id": 3, "predicted_category": "Termination"},
        ]
        res = self.service.detect_missing_clauses(clauses)
        self.assertEqual(res["detected_categories"], ["Payment", "Termination"])
        self.assertEqual(res["missing_count"], 3)

    def test_unexpected_or_unknown_category(self):
        """Test 6: Clauses with unknown/custom categories do not crash detection."""
        clauses = [
            {"clause_id": 1, "predicted_category": "Payment"},
            {"clause_id": 2, "predicted_category": "CustomIntellectualProperty"},
        ]
        res = self.service.detect_missing_clauses(clauses)
        self.assertEqual(res["detected_categories"], ["Payment"])
        self.assertEqual(res["missing_count"], 4)

    def test_academic_wording(self):
        """Test 7: Findings use academic phrasing without claiming legal requirement."""
        clauses = [{"clause_id": 1, "predicted_category": "Payment"}]
        res = self.service.detect_missing_clauses(clauses)
        for finding in res["missing_clauses"]:
            self.assertEqual(finding["title"], "Potentially missing clause category")
            self.assertIn("was detected", finding["rationale"])
            self.assertIn("may lack", finding["risk_impact"])


class TestMissingClausesEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_contract_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """SIMPLE NDA
1. Confidentiality.
All proprietary information disclosed under this agreement shall remain strictly confidential.

2. Termination.
This agreement shall terminate automatically after one year.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_missing_clauses_endpoint_end_to_end(self):
        """Test 8: End-to-end PDF upload and missing-clauses endpoint retrieval."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Analyze PDF
                res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("nda_missing.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(res.status_code, 200)
                data = res.json()
                doc_id = data["document_id"]

                # Ensure missing_clauses is in the analyze response
                self.assertIn("missing_clauses", data)
                self.assertIn("missing_count", data["missing_clauses"])
                self.assertGreater(data["missing_clauses"]["missing_count"], 0)

                # 2. Query GET /api/v1/documents/{document_id}/missing-clauses
                mc_res = await client.get(f"/api/v1/documents/{doc_id}/missing-clauses")
                self.assertEqual(mc_res.status_code, 200)
                mc_data = mc_res.json()

                self.assertIn("expected_categories", mc_data)
                self.assertIn("detected_categories", mc_data)
                self.assertIn("missing_count", mc_data)
                self.assertIn("missing_clauses", mc_data)

                # Payment and Liability should be potentially missing in this NDA
                missing_cats = [item["category"] for item in mc_data["missing_clauses"]]
                self.assertIn("Payment", missing_cats)
                self.assertIn("Liability", missing_cats)

                # 3. Invalid document ID returns 404
                not_found = await client.get("/api/v1/documents/non-existent-uuid-7777/missing-clauses")
                self.assertEqual(not_found.status_code, 404)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
