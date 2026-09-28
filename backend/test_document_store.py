"""
Unit and integration tests for DocumentStore and /api/v1/analyze integration.
"""

import concurrent.futures
import unittest
import uuid
from src.storage.document_store import DocumentStore, get_document_store


class TestDocumentStore(unittest.TestCase):
    def setUp(self):
        """Set up a fresh DocumentStore instance for each test."""
        self.store = DocumentStore()

    def test_save_and_retrieve_document(self):
        """Test 1: Saving a document and retrieving it by document_id."""
        sample_doc = {
            "filename": "nda_agreement.pdf",
            "metadata": {"page_count": 2},
            "raw_text": "This is an NDA between Party A and Party B.",
            "total_clauses": 2,
            "clauses": [
                {
                    "clause_id": 1,
                    "original_text": "Party A shall keep information secret.",
                    "predicted_category": "Confidentiality",
                    "classification_confidence": 0.95,
                    "fuzzy_inputs": {"importance": 6.0, "ambiguity": 0.0, "risk_indicators": 0.0},
                    "risk_score": 25.0,
                    "risk_level": "LOW",
                },
                {
                    "clause_id": 2,
                    "original_text": "Agreement terminates in 30 days.",
                    "predicted_category": "Termination",
                    "classification_confidence": 0.88,
                    "fuzzy_inputs": {"importance": 8.0, "ambiguity": 0.0, "risk_indicators": 0.0},
                    "risk_score": 35.0,
                    "risk_level": "MEDIUM",
                },
            ],
            "document_risk": {
                "overall_score": 30.7,
                "overall_level": "LOW",
                "category_breakdown": {"Confidentiality": 1, "Termination": 1},
            },
        }

        doc_id = self.store.save_document(sample_doc)
        self.assertIsNotNone(doc_id)
        self.assertTrue(len(doc_id) > 0)

        # Retrieve document
        retrieved = self.store.get_document(doc_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["document_id"], doc_id)
        self.assertEqual(retrieved["filename"], "nda_agreement.pdf")
        self.assertEqual(retrieved["total_clauses"], 2)
        self.assertEqual(len(retrieved["clauses"]), 2)
        self.assertEqual(retrieved["document_risk"]["overall_level"], "LOW")
        self.assertIn("upload_timestamp", retrieved)

    def test_retrieve_invalid_document_id(self):
        """Test 2: Handling an invalid/non-existent document_id returns None."""
        random_id = str(uuid.uuid4())
        retrieved = self.store.get_document(random_id)
        self.assertIsNone(retrieved)

        # Empty string / None check
        self.assertIsNone(self.store.get_document(""))
        self.assertIsNone(self.store.get_document("invalid-id-12345"))

    def test_retrieve_latest_document(self):
        """Test 3: Retrieving latest document returns the most recently saved document."""
        # Empty store returns None
        self.assertIsNone(self.store.get_latest_document())

        doc1_id = self.store.save_document({"filename": "contract_1.pdf", "clauses": []})
        latest = self.store.get_latest_document()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["document_id"], doc1_id)
        self.assertEqual(latest["filename"], "contract_1.pdf")

        doc2_id = self.store.save_document({"filename": "contract_2.pdf", "clauses": []})
        latest2 = self.store.get_latest_document()
        self.assertIsNotNone(latest2)
        self.assertEqual(latest2["document_id"], doc2_id)
        self.assertEqual(latest2["filename"], "contract_2.pdf")

    def test_list_documents(self):
        """Test 4: Listing documents returns ordered summaries (newest first)."""
        self.assertEqual(len(self.store.list_documents()), 0)

        self.store.save_document({
            "filename": "doc_first.pdf",
            "document_risk": {"overall_score": 40.0, "overall_level": "MEDIUM"},
            "clauses": [{"clause_id": 1}],
        })
        self.store.save_document({
            "filename": "doc_second.pdf",
            "document_risk": {"overall_score": 80.0, "overall_level": "HIGH"},
            "clauses": [{"clause_id": 1}, {"clause_id": 2}],
        })

        summaries = self.store.list_documents()
        self.assertEqual(len(summaries), 2)
        # Newest first
        self.assertEqual(summaries[0]["filename"], "doc_second.pdf")
        self.assertEqual(summaries[0]["overall_level"], "HIGH")
        self.assertEqual(summaries[1]["filename"], "doc_first.pdf")
        self.assertEqual(summaries[1]["overall_level"], "MEDIUM")

    def test_immutability_and_deep_copy(self):
        """Test 5: Modifying retrieved document doesn't alter internal store state."""
        doc_id = self.store.save_document({
            "filename": "original.pdf",
            "clauses": [{"clause_id": 1, "text": "Confidential"}],
        })

        retrieved1 = self.store.get_document(doc_id)
        retrieved1["clauses"].append({"clause_id": 2, "text": "Tampered"})

        retrieved2 = self.store.get_document(doc_id)
        self.assertEqual(len(retrieved2["clauses"]), 1)

    def test_concurrent_access(self):
        """Test 6: Thread-safe concurrent writes and reads."""
        num_threads = 20
        doc_ids = []

        def worker(idx):
            doc = {
                "filename": f"contract_{idx}.pdf",
                "clauses": [{"clause_id": i} for i in range(idx % 5 + 1)],
                "document_risk": {"overall_score": float(idx * 4), "overall_level": "LOW"},
            }
            d_id = self.store.save_document(doc)
            # Read back immediately
            fetched = self.store.get_document(d_id)
            assert fetched is not None
            assert fetched["filename"] == f"contract_{idx}.pdf"
            return d_id

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for fut in concurrent.futures.as_completed(futures):
                doc_ids.append(fut.result())

        self.assertEqual(len(doc_ids), num_threads)
        self.assertEqual(len(self.store.list_documents()), num_threads)

    def test_singleton_accessor(self):
        """Test 7: get_document_store() returns singleton instance."""
        s1 = get_document_store()
        s2 = get_document_store()
        self.assertIs(s1, s2)

    def test_analytics_aggregation(self):
        """Test 8: get_all_analytics calculates aggregate metrics properly."""
        self.store.clear()
        empty_analytics = self.store.get_all_analytics()
        self.assertEqual(empty_analytics["total_documents"], 0)

        self.store.save_document({
            "filename": "doc_1.pdf",
            "clauses": [
                {"predicted_category": "Payment", "risk_level": "LOW"},
                {"predicted_category": "Termination", "risk_level": "HIGH"},
            ],
            "document_risk": {"overall_score": 60.0, "overall_level": "MEDIUM"},
        })
        self.store.save_document({
            "filename": "doc_2.pdf",
            "clauses": [
                {"predicted_category": "Payment", "risk_level": "LOW"},
                {"predicted_category": "Liability", "risk_level": "HIGH"},
            ],
            "document_risk": {"overall_score": 80.0, "overall_level": "HIGH"},
        })

        analytics = self.store.get_all_analytics()
        self.assertEqual(analytics["total_documents"], 2)
        self.assertEqual(analytics["total_clauses"], 4)
        self.assertEqual(analytics["clause_category_counts"]["Payment"], 2)
        self.assertEqual(analytics["clause_category_counts"]["Termination"], 1)
        self.assertEqual(analytics["clause_category_counts"]["Liability"], 1)
        self.assertEqual(analytics["high_risk_clause_count"], 2)
        self.assertEqual(analytics["average_risk_score"], 70.0)


if __name__ == "__main__":
    unittest.main()
