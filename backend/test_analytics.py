"""
Unit and integration tests for AnalyticsService and analytics API endpoints.
"""

import asyncio
import io
import unittest
import fitz
import httpx
from src.main import app
from src.services.analytics_service import AnalyticsService, get_analytics_service
from src.storage.document_store import get_document_store


class TestAnalyticsService(unittest.TestCase):
    def setUp(self):
        self.store = get_document_store()
        self.store.clear()
        self.service = AnalyticsService()

    def test_single_document_analytics_calculations(self):
        """Test 1-6: Single document analytics metrics (counts, risk, category, high-risk)."""
        doc_data = {
            "document_id": "doc-analytics-1",
            "filename": "vendor_contract.pdf",
            "total_clauses": 4,
            "clauses": [
                {
                    "clause_id": 1,
                    "original_text": "Payment clause",
                    "predicted_category": "Payment",
                    "risk_score": 20.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 2,
                    "original_text": "Confidentiality clause",
                    "predicted_category": "Confidentiality",
                    "risk_score": 40.0,
                    "risk_level": "MEDIUM",
                },
                {
                    "clause_id": 3,
                    "original_text": "Liability clause",
                    "predicted_category": "Liability",
                    "risk_score": 80.0,
                    "risk_level": "HIGH",
                },
                {
                    "clause_id": 4,
                    "original_text": "General clause",
                    "predicted_category": "General",
                    "risk_score": 30.0,
                    "risk_level": "LOW",
                },
            ],
            "document_risk": {
                "overall_score": 42.5,
                "overall_level": "MEDIUM",
            },
            "missing_clauses": {
                "missing_count": 1,
                "missing_clauses": [
                    {
                        "category": "Termination",
                        "title": "Potentially missing clause category",
                        "rationale": "No clause classified as Termination was detected.",
                        "risk_impact": "May lack termination terms.",
                    }
                ],
            },
        }
        self.store.save_document(doc_data)

        res = self.service.get_document_analytics("doc-analytics-1")
        self.assertIsNotNone(res)

        # 1. Document identity
        self.assertEqual(res["document_id"], "doc-analytics-1")
        self.assertEqual(res["filename"], "vendor_contract.pdf")
        self.assertEqual(res["overall_risk"], "MEDIUM")

        # 2. Total clauses
        self.assertEqual(res["total_clauses"], 4)

        # 3. Risk distribution
        self.assertEqual(res["risk_distribution"]["LOW"], 2)
        self.assertEqual(res["risk_distribution"]["MEDIUM"], 1)
        self.assertEqual(res["risk_distribution"]["HIGH"], 1)

        # 4. Average and highest risk scores
        # (20 + 40 + 80 + 30) / 4 = 170 / 4 = 42.5
        self.assertEqual(res["average_risk_score"], 42.5)
        self.assertEqual(res["highest_clause_risk_score"], 80.0)

        # 5. Category distribution
        self.assertEqual(res["category_distribution"]["Payment"], 1)
        self.assertEqual(res["category_distribution"]["Confidentiality"], 1)
        self.assertEqual(res["category_distribution"]["Liability"], 1)
        self.assertEqual(res["category_distribution"]["General"], 1)

        # 6. High-risk clause detection
        self.assertEqual(len(res["high_risk_clauses"]), 1)
        self.assertEqual(res["high_risk_clauses"][0]["clause_id"], 3)

        # 7. Missing clause information
        self.assertEqual(res["missing_clause_count"], 1)
        self.assertEqual(res["missing_clause_categories"], ["Termination"])

    def test_multiple_document_aggregation(self):
        """Test 7-8: System-wide aggregation over multiple stored documents."""
        # Doc 1: LOW risk
        self.store.save_document({
            "document_id": "doc-sys-1",
            "filename": "doc1.pdf",
            "clauses": [
                {"predicted_category": "Payment", "risk_level": "LOW", "risk_score": 15.0},
                {"predicted_category": "General", "risk_level": "LOW", "risk_score": 25.0},
            ],
            "document_risk": {"overall_score": 20.0, "overall_level": "LOW"},
            "missing_clauses": {
                "missing_count": 2,
                "missing_clauses": [{"category": "Liability"}, {"category": "Termination"}],
            },
        })

        # Doc 2: HIGH risk
        self.store.save_document({
            "document_id": "doc-sys-2",
            "filename": "doc2.pdf",
            "clauses": [
                {"predicted_category": "Liability", "risk_level": "HIGH", "risk_score": 85.0},
                {"predicted_category": "Payment", "risk_level": "MEDIUM", "risk_score": 55.0},
            ],
            "document_risk": {"overall_score": 70.0, "overall_level": "HIGH"},
            "missing_clauses": {
                "missing_count": 1,
                "missing_clauses": [{"category": "Liability"}],
            },
        })

        sys_res = self.service.get_system_analytics()

        self.assertEqual(sys_res["total_documents"], 2)
        self.assertEqual(sys_res["total_analyzed"], 2)
        self.assertEqual(sys_res["total_clauses"], 4)
        self.assertEqual(sys_res["average_clauses_per_document"], 2.0)
        # Avg doc risk: (20.0 + 70.0) / 2 = 45.0
        self.assertEqual(sys_res["average_risk_score"], 45.0)

        # Risk distribution (documents)
        self.assertEqual(sys_res["risk_distribution"]["LOW"], 1)
        self.assertEqual(sys_res["risk_distribution"]["HIGH"], 1)

        # High risk counts
        self.assertEqual(sys_res["high_risk_document_count"], 1)
        self.assertEqual(sys_res["high_risk_clause_count"], 1)

        # Category distribution
        self.assertEqual(sys_res["category_distribution"]["Payment"], 2)
        self.assertEqual(sys_res["category_distribution"]["Liability"], 1)
        self.assertEqual(sys_res["category_distribution"]["General"], 1)

        # Missing clause statistics
        stats = sys_res["missing_clause_statistics"]
        self.assertEqual(stats["documents_with_missing_clauses"], 2)
        self.assertEqual(stats["total_missing_categories"], 3)
        self.assertEqual(stats["most_common_missing_category"], "Liability")

    def test_empty_document_store(self):
        """Test 9: System analytics handles empty store with valid zero metrics."""
        self.store.clear()
        res = self.service.get_system_analytics()
        self.assertEqual(res["total_documents"], 0)
        self.assertEqual(res["total_analyzed"], 0)
        self.assertEqual(res["total_clauses"], 0)
        self.assertEqual(res["average_clauses_per_document"], 0.0)
        self.assertEqual(res["average_risk_score"], 0.0)
        self.assertEqual(res["high_risk_document_count"], 0)
        self.assertEqual(res["high_risk_clause_count"], 0)
        self.assertEqual(res["missing_clause_statistics"]["total_missing_categories"], 0)
        self.assertIsNone(res["missing_clause_statistics"]["most_common_missing_category"])

    def test_missing_or_invalid_risk_scores_safe_handling(self):
        """Test 13: Documents with missing/non-numeric risk scores do not crash."""
        doc_data = {
            "document_id": "doc-faulty-scores",
            "filename": "unusual.pdf",
            "clauses": [
                {"predicted_category": "Payment", "risk_level": "LOW", "risk_score": None},
                {"predicted_category": "General", "risk_level": "UNKNOWN", "risk_score": "not-a-number"},
                {"predicted_category": "Confidentiality"},  # No risk score key at all
            ],
            "document_risk": {"overall_score": None, "overall_level": "LOW"},
        }
        self.store.save_document(doc_data)

        # Should calculate without raising exceptions
        res = self.service.get_document_analytics("doc-faulty-scores")
        self.assertIsNotNone(res)
        self.assertEqual(res["total_clauses"], 3)
        self.assertEqual(res["average_risk_score"], 0.0)
        self.assertEqual(res["highest_clause_risk_score"], 0.0)


class TestAnalyticsEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_contract_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """ANALYTICS TEST CONTRACT
1. Confidentiality.
All information shall be kept secret.

2. Invoicing.
The client shall pay $3,000 net 30.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_analytics_endpoints_end_to_end(self):
        """Test 10-12: Document analytics and system analytics API endpoints."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Upload document
                res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("analytics_sample.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(res.status_code, 200)
                data = res.json()
                doc_id = data["document_id"]

                # 2. Test document analytics endpoint (GET /api/v1/documents/{document_id}/analytics)
                doc_an_res = await client.get(f"/api/v1/documents/{doc_id}/analytics")
                self.assertEqual(doc_an_res.status_code, 200)
                doc_an = doc_an_res.json()

                self.assertEqual(doc_an["document_id"], doc_id)
                self.assertEqual(doc_an["filename"], "analytics_sample.pdf")
                self.assertIn("total_clauses", doc_an)
                self.assertIn("risk_distribution", doc_an)
                self.assertIn("category_distribution", doc_an)
                self.assertIn("average_risk_score", doc_an)
                self.assertIn("highest_clause_risk_score", doc_an)
                self.assertIn("missing_clause_count", doc_an)

                # 3. Test invalid document ID -> 404
                not_found = await client.get("/api/v1/documents/non-existent-uuid-analytics/analytics")
                self.assertEqual(not_found.status_code, 404)

                # 4. Test system analytics endpoint (GET /api/v1/analytics)
                sys_an_res = await client.get("/api/v1/analytics")
                self.assertEqual(sys_an_res.status_code, 200)
                sys_an = sys_an_res.json()

                self.assertGreaterEqual(sys_an["total_documents"], 1)
                self.assertGreaterEqual(sys_an["total_clauses"], 1)
                self.assertIn("category_distribution", sys_an)
                self.assertIn("risk_distribution", sys_an)
                self.assertIn("missing_clause_statistics", sys_an)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
