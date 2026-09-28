"""
Unit and integration tests for ReportService and GET /api/v1/documents/{id}/report.
"""

import asyncio
import io
import unittest
import pymupdf as fitz
import httpx
from src.main import app
from src.services.report_service import ReportService, get_report_service
from src.storage.document_store import get_document_store


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.store = get_document_store()
        self.store.clear()
        self.service = ReportService()

        # Sample test document data
        self.sample_doc = {
            "document_id": "test-doc-report-1",
            "filename": "Sample_Contract.pdf",
            "upload_timestamp": "2026-09-23T01:00:00+00:00",
            "metadata": {"page_count": 2},
            "total_clauses": 4,
            "clauses": [
                {
                    "clause_id": 1,
                    "original_text": "This agreement shall remain in effect for two years from the effective date.",
                    "predicted_category": "General",
                    "risk_score": 15.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 2,
                    "original_text": "The client shall pay $50,000 for consulting services rendered within 15 days.",
                    "predicted_category": "Payment",
                    "risk_score": 25.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 3,
                    "original_text": "Either party may terminate this agreement with 30 days written notice.",
                    "predicted_category": "Termination",
                    "risk_score": 45.0,
                    "risk_level": "MEDIUM",
                },
                {
                    "clause_id": 4,
                    "original_text": "The vendor shall indemnify client against claims. Total liability shall not exceed fees paid.",
                    "predicted_category": "Liability",
                    "risk_score": 85.0,
                    "risk_level": "HIGH",
                },
            ],
            "document_risk": {
                "overall_score": 42.5,
                "overall_level": "MEDIUM",
                "category_breakdown": {
                    "General": 1,
                    "Payment": 1,
                    "Termination": 1,
                    "Liability": 1,
                },
            },
            "summary": {
                "duration": {"status": "detected", "text": "This agreement shall remain in effect for two years."},
                "payment_terms": {"status": "detected", "text": "The client shall pay $50,000."},
                "termination": {"status": "detected", "text": "Either party may terminate this agreement with 30 days written notice."},
                "confidentiality": {"status": "not_detected", "text": None},
                "liability": {"status": "detected", "text": "Total liability shall not exceed fees paid."},
            },
            "missing_clauses": {
                "missing_count": 1,
                "missing_clauses": [
                    {
                        "category": "Confidentiality",
                        "title": "Potentially missing clause category",
                        "rationale": "No clause classified as Confidentiality was detected.",
                        "risk_impact": "The document may lack an explicitly identified confidentiality provision.",
                    }
                ],
            },
        }
        self.store.save_document(self.sample_doc)

    def test_pdf_generation_bytes_and_header(self):
        """Test 1 & 2: PDF generation returns valid bytes beginning with %PDF-."""
        pdf_bytes = self.service.build_pdf(self.sample_doc)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_pdf_reopen_and_text_content(self):
        """Test 3-9, 13: Generated PDF can be reopened with PyMuPDF and contains all required sections."""
        pdf_bytes = self.service.build_pdf(self.sample_doc)

        # Open generated PDF with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreater(doc.page_count, 0)

        # Combine text across all pages
        full_text = ""
        for i in range(doc.page_count):
            full_text += doc.load_page(i).get_text() + "\n"

        doc.close()

        # 3. Expected report title
        self.assertIn("AI Legal Document Analysis Report", full_text)

        # 4. Document information
        self.assertIn("Sample_Contract.pdf", full_text)
        self.assertIn("test-doc-report-1", full_text)
        self.assertIn("Total Clauses", full_text)

        # 5. Risk information
        self.assertIn("RISK: MEDIUM", full_text)
        self.assertIn("42.5", full_text)

        # 6. Summary information
        self.assertIn("Contract Duration", full_text)
        self.assertIn("two years", full_text)
        self.assertIn("Payment Terms", full_text)
        self.assertIn("Not detected", full_text)  # Confidentiality is not detected

        # 7. Clause classification breakdown
        self.assertIn("Clause Classification Breakdown", full_text)
        self.assertIn("Payment", full_text)
        self.assertIn("Liability", full_text)

        # 8. Missing clause information
        self.assertIn("Potentially missing clause category", full_text)
        self.assertIn("Confidentiality", full_text)

        # 9. Disclaimer
        norm_text = " ".join(full_text.split())
        self.assertIn("does not constitute legal advice", norm_text)
        self.assertIn("academic and informational purposes", norm_text)

    def test_long_clause_text_does_not_crash(self):
        """Test 10: Documents with long, multi-paragraph clauses layout cleanly without error."""
        long_text = "This is a very detailed legal provision containing extensive clauses. " * 40
        doc_long = {
            "document_id": "doc-long-clauses",
            "filename": "long_contract.pdf",
            "clauses": [
                {
                    "clause_id": i,
                    "original_text": f"Clause {i}: {long_text}",
                    "predicted_category": "Liability" if i % 2 == 0 else "General",
                    "risk_score": 75.0,
                    "risk_level": "HIGH",
                }
                for i in range(1, 15)
            ],
            "document_risk": {"overall_score": 75.0, "overall_level": "HIGH"},
        }

        pdf_bytes = self.service.build_pdf(doc_long)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        # Check that it generates multi-page document cleanly
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.assertGreater(doc.page_count, 1)
        doc.close()


class TestReportEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_contract_pdf(self) -> bytes:
        doc = fitz.open()
        page = doc.new_page()
        text = """REPORT INTEGRATION TEST
1. Confidentiality.
All information shall be kept strictly secret.

2. Invoicing.
The client shall pay $10,000 within 30 days.

3. Termination.
May terminate with 30 days notice.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_report_endpoint_end_to_end(self):
        """Test 11 & 12: Downloadable report endpoint returns 200 and application/pdf."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Analyze PDF
                upload_res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("contract_for_report.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(upload_res.status_code, 200)
                data = upload_res.json()
                doc_id = data["document_id"]

                # 2. Test GET /api/v1/documents/{document_id}/report
                report_res = await client.get(f"/api/v1/documents/{doc_id}/report")
                self.assertEqual(report_res.status_code, 200)
                self.assertEqual(report_res.headers.get("content-type"), "application/pdf")
                self.assertIn("attachment; filename=", report_res.headers.get("content-disposition", ""))
                self.assertIn("contract_for_report", report_res.headers.get("content-disposition", ""))

                # Verify payload is a valid PDF
                report_bytes = report_res.content
                self.assertTrue(report_bytes.startswith(b"%PDF-"))
                doc = fitz.open(stream=report_bytes, filetype="pdf")
                self.assertGreater(doc.page_count, 0)
                doc.close()

                # 3. Test invalid document ID -> 404
                not_found = await client.get("/api/v1/documents/non-existent-report-uuid-5555/report")
                self.assertEqual(not_found.status_code, 404)

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
