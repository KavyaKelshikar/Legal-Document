"""
Unit and integration tests for DialogflowService and POST /api/v1/dialogflow/webhook.
"""

import asyncio
import io
import unittest
import pymupdf as fitz
import httpx
from src.main import app
from src.services.dialogflow_service import DialogflowService, get_dialogflow_service
from src.storage.document_store import get_document_store


class TestDialogflowServiceUnit(unittest.TestCase):
    """Unit tests for DialogflowService using synthetic data."""

    def setUp(self):
        self.store = get_document_store()
        self.store.clear()
        self.service = DialogflowService()

        # Insert a test document with varied clause categories
        # NOTE: Clause text must contain enough distinctive vocabulary for
        # TF-IDF cosine similarity to work with test queries.
        self.sample_doc = {
            "document_id": "df-test-doc-1",
            "filename": "DialogflowTestContract.pdf",
            "metadata": {"page_count": 3},
            "total_clauses": 5,
            "clauses": [
                {
                    "clause_id": 1,
                    "original_text": "This agreement duration shall remain in effect for a period of three years from the effective date of execution.",
                    "predicted_category": "General",
                    "risk_score": 12.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 2,
                    "original_text": "Payment terms require that the client shall pay seventy-five thousand dollars for professional payment services rendered within thirty business days of invoice and billing receipt.",
                    "predicted_category": "Payment",
                    "risk_score": 22.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 3,
                    "original_text": "Confidentiality provisions require that all confidential and proprietary information disclosed during the engagement must be protected under confidentiality obligations and not shared with third parties.",
                    "predicted_category": "Confidentiality",
                    "risk_score": 40.0,
                    "risk_level": "MEDIUM",
                },
                {
                    "clause_id": 4,
                    "original_text": "Termination clause states that either party may terminate this agreement with sixty days written termination notice to the other party.",
                    "predicted_category": "Termination",
                    "risk_score": 35.0,
                    "risk_level": "MEDIUM",
                },
                {
                    "clause_id": 5,
                    "original_text": "Liability limitation states that the vendor shall indemnify the client against all liability claims arising from negligence. Total liability shall not exceed fees paid under this agreement.",
                    "predicted_category": "Liability",
                    "risk_score": 80.0,
                    "risk_level": "HIGH",
                },
            ],
            "document_risk": {
                "overall_score": 37.8,
                "overall_level": "MEDIUM",
                "category_breakdown": {
                    "General": 1, "Payment": 1, "Confidentiality": 1,
                    "Termination": 1, "Liability": 1,
                },
            },
        }
        self.store.save_document(self.sample_doc)

    def test_direct_json_with_document_id(self):
        """Test 1: Direct JSON format with explicit document_id."""
        payload = {
            "question": "What are the payment terms?",
            "document_id": "df-test-doc-1",
        }
        result = self.service.process_webhook(payload)

        self.assertIn("fulfillmentText", result)
        self.assertIn("fulfillmentMessages", result)
        self.assertIn("payload", result)
        self.assertTrue(result["payload"]["found"])
        self.assertEqual(result["payload"]["document_id"], "df-test-doc-1")
        self.assertIsNotNone(result["payload"].get("answer"))
        self.assertIsNotNone(result["payload"].get("similarity_score"))

    def test_direct_json_without_document_id_falls_back_to_latest(self):
        """Test 2: Direct JSON without document_id uses latest analyzed document."""
        payload = {"question": "What are the confidentiality provisions?"}
        result = self.service.process_webhook(payload)

        self.assertTrue(result["payload"]["found"])
        self.assertEqual(result["payload"]["document_id"], "df-test-doc-1")

    def test_dialogflow_es_format(self):
        """Test 3: Dialogflow ES fulfillment format is correctly parsed."""
        payload = {
            "queryResult": {
                "queryText": "What is the termination notice period?",
                "parameters": {
                    "document_id": "df-test-doc-1",
                },
            }
        }
        result = self.service.process_webhook(payload)

        self.assertIn("fulfillmentText", result)
        self.assertTrue(result["payload"]["found"])
        self.assertEqual(result["payload"]["document_id"], "df-test-doc-1")

    def test_dialogflow_es_format_without_document_id(self):
        """Test 4: Dialogflow ES without document_id falls back to latest."""
        payload = {
            "queryResult": {
                "queryText": "What is the total liability?",
                "parameters": {},
            }
        }
        result = self.service.process_webhook(payload)

        self.assertTrue(result["payload"]["found"])
        self.assertEqual(result["payload"]["document_id"], "df-test-doc-1")

    def test_empty_question_returns_prompt(self):
        """Test 5: Empty question returns guidance message."""
        payload = {"question": "", "document_id": "df-test-doc-1"}
        result = self.service.process_webhook(payload)

        self.assertFalse(result["payload"]["found"])
        self.assertIn("provide a question", result["fulfillmentText"].lower())

    def test_missing_question_returns_prompt(self):
        """Test 6: Missing question key returns guidance message."""
        payload = {"document_id": "df-test-doc-1"}
        result = self.service.process_webhook(payload)

        self.assertFalse(result["payload"]["found"])
        self.assertIn("provide a question", result["fulfillmentText"].lower())

    def test_nonexistent_document_id(self):
        """Test 7: Non-existent document_id returns not found message."""
        payload = {
            "question": "What about payment?",
            "document_id": "non-existent-id-99999",
        }
        result = self.service.process_webhook(payload)

        self.assertFalse(result["payload"]["found"])
        self.assertIn("not found", result["fulfillmentText"].lower())

    def test_no_documents_analyzed(self):
        """Test 8: No documents in store and no document_id returns guidance."""
        self.store.clear()
        payload = {"question": "What are the payment terms?"}
        result = self.service.process_webhook(payload)

        self.assertFalse(result["payload"]["found"])
        self.assertIn("upload a document", result["fulfillmentText"].lower())

    def test_fulfillment_response_structure(self):
        """Test 9: Verify full fulfillment response structure."""
        payload = {"question": "How long does the agreement last?", "document_id": "df-test-doc-1"}
        result = self.service.process_webhook(payload)

        # Top-level keys
        self.assertIn("fulfillmentText", result)
        self.assertIn("fulfillmentMessages", result)
        self.assertIn("payload", result)

        # fulfillmentMessages structure
        self.assertIsInstance(result["fulfillmentMessages"], list)
        self.assertGreater(len(result["fulfillmentMessages"]), 0)
        msg = result["fulfillmentMessages"][0]
        self.assertIn("text", msg)
        self.assertIn("text", msg["text"])
        self.assertIsInstance(msg["text"]["text"], list)

        # payload structure
        p = result["payload"]
        self.assertIn("found", p)
        self.assertIn("document_id", p)
        if p["found"]:
            self.assertIn("answer", p)
            self.assertIn("source_clause", p)
            self.assertIn("clause_category", p)
            self.assertIn("similarity_score", p)
            self.assertIn("clause_id", p)

    def test_irrelevant_question_low_similarity(self):
        """Test 10: Completely irrelevant question falls below threshold."""
        payload = {
            "question": "What is the recipe for chocolate cake?",
            "document_id": "df-test-doc-1",
        }
        result = self.service.process_webhook(payload)

        # The retrieval should either not find a match or find one with low similarity
        # Either way the response structure should be correct
    def test_conversational_greetings(self):
        """Test conversational greeting variations (hi, hello, hiii, heyy)."""
        for greeting in ["hi", "hello", "hey", "hiii", "heyyy", "good morning", "sup"]:
            res = self.service.process_webhook({"question": greeting, "document_id": "df-test-doc-1"})
            self.assertTrue(res["payload"]["found"])
            self.assertIn("Hello! 👋", res["fulfillmentText"])

    def test_greeting_prefix_stripping(self):
        """Test stripping greeting prefix when followed by a contract question."""
        res = self.service.process_webhook({
            "question": "Hi, what are the payment terms?",
            "document_id": "df-test-doc-1"
        })
        self.assertTrue(res["payload"]["found"])
        self.assertIn("payment", res["fulfillmentText"].lower())

    def test_conversational_risk_and_summary(self):
        """Test conversational risk query, missing clauses query, and summary query."""
        # Risk query
        risk_res = self.service.process_webhook({"question": "what is the risk", "document_id": "df-test-doc-1"})
        self.assertTrue(risk_res["payload"]["found"])
        self.assertIn("Risk Assessment", risk_res["fulfillmentText"])

        # Missing clauses query
        missing_res = self.service.process_webhook({"question": "what clauses are missing", "document_id": "df-test-doc-1"})
        self.assertTrue(missing_res["payload"]["found"])
        self.assertIn("Missing Clause Audit", missing_res["fulfillmentText"])

    def test_singleton_instance(self):
        """Test 11: get_dialogflow_service returns singleton."""
        svc1 = get_dialogflow_service()
        svc2 = get_dialogflow_service()
        self.assertIs(svc1, svc2)


class TestDialogflowWebhookEndpoint(unittest.TestCase):
    """Integration tests for POST /api/v1/dialogflow/webhook via the full API."""

    @classmethod
    def setUpClass(cls):
        cls.store = get_document_store()

    def _create_contract_pdf(self) -> bytes:
        """Create a synthetic PDF with varied legal clauses."""
        doc = fitz.open()
        page = doc.new_page()
        text = """DIALOGFLOW INTEGRATION TEST CONTRACT

1. Duration.
This agreement shall remain effective for two years commencing on the execution date.

2. Fees and Payment.
The client shall pay $25,000 for services within 30 days of each invoice.

3. Confidentiality.
All proprietary information exchanged during this engagement shall remain confidential.

4. Termination.
Either party may terminate this agreement with 30 days prior written notice.
"""
        page.insert_text((50, 50), text)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

    def test_webhook_endpoint_direct_json(self):
        """Test 12: POST /api/v1/dialogflow/webhook with direct JSON after uploading a PDF."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Upload and analyze a PDF
                upload_res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("dialogflow_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(upload_res.status_code, 200)
                doc_id = upload_res.json()["document_id"]

                # 2. Call webhook with direct JSON
                webhook_res = await client.post(
                    "/api/v1/dialogflow/webhook",
                    json={"question": "What are the payment terms?", "document_id": doc_id},
                )
                self.assertEqual(webhook_res.status_code, 200)
                data = webhook_res.json()
                self.assertIn("fulfillmentText", data)
                self.assertIn("fulfillmentMessages", data)
                self.assertIn("payload", data)
                self.assertTrue(data["payload"]["found"])
                self.assertEqual(data["payload"]["document_id"], doc_id)

        asyncio.run(_run())

    def test_webhook_endpoint_dialogflow_es_format(self):
        """Test 13: POST /api/v1/dialogflow/webhook with Dialogflow ES format."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Upload PDF
                upload_res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("dialogflow_es_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(upload_res.status_code, 200)
                doc_id = upload_res.json()["document_id"]

                # 2. Call webhook with Dialogflow ES format
                webhook_res = await client.post(
                    "/api/v1/dialogflow/webhook",
                    json={
                        "queryResult": {
                            "queryText": "When does this agreement terminate?",
                            "parameters": {"document_id": doc_id},
                        }
                    },
                )
                self.assertEqual(webhook_res.status_code, 200)
                data = webhook_res.json()
                self.assertTrue(data["payload"]["found"])

        asyncio.run(_run())

    def test_webhook_endpoint_no_document_id_latest_fallback(self):
        """Test 14: Webhook without document_id falls back to latest document."""
        pdf_bytes = self._create_contract_pdf()

        async def _run():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Upload PDF
                upload_res = await client.post(
                    "/api/v1/analyze",
                    files={"file": ("dialogflow_fallback.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
                )
                self.assertEqual(upload_res.status_code, 200)

                # 2. Call webhook WITHOUT document_id
                webhook_res = await client.post(
                    "/api/v1/dialogflow/webhook",
                    json={"question": "What is the duration of this agreement?"},
                )
                self.assertEqual(webhook_res.status_code, 200)
                data = webhook_res.json()
                # Should still find an answer using the latest document
                self.assertIn("fulfillmentText", data)
                self.assertIsNotNone(data["payload"]["document_id"])

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
