"""
Thread-safe in-memory document repository for storing and retrieving
analyzed legal documents and their extracted analysis.
"""

import copy
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DocumentStore:
    """Thread-safe in-memory repository for analyzed legal contracts."""

    def __init__(self):
        self._lock = threading.RLock()
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._ordered_ids: List[str] = []

    def save_document(self, data: Dict[str, Any]) -> str:
        """
        Stores an analyzed document record. Generates a UUID if none is provided.

        Args:
            data: Dictionary containing document details and analysis results.

        Returns:
            str: The unique document_id assigned to this document.
        """
        with self._lock:
            doc_id = data.get("document_id") or str(uuid.uuid4())
            timestamp = data.get("upload_timestamp") or datetime.now(timezone.utc).isoformat()

            clauses = copy.deepcopy(data.get("clauses", []))
            total_clauses = data.get("total_clauses", len(clauses))

            user_email = (data.get("user_email") or "").strip().lower() or None

            doc_record: Dict[str, Any] = {
                "document_id": doc_id,
                "filename": data.get("filename", "document.pdf"),
                "upload_timestamp": timestamp,
                "user_email": user_email,
                "metadata": copy.deepcopy(data.get("metadata", {})),
                "raw_text": data.get("raw_text", ""),
                "total_clauses": total_clauses,
                "clauses": clauses,
                "document_risk": copy.deepcopy(data.get("document_risk", {})),
                "summary": copy.deepcopy(data.get("summary")),
                "missing_clauses": copy.deepcopy(data.get("missing_clauses")),
            }

            self._documents[doc_id] = doc_record

            if doc_id in self._ordered_ids:
                self._ordered_ids.remove(doc_id)
            self._ordered_ids.append(doc_id)

            logger.info("Saved document %s (%s) for user %s with %d clauses", doc_id, doc_record["filename"], user_email or "public", total_clauses)
            return doc_id

    def _matches_user(self, doc: Dict[str, Any], user_email: Optional[str]) -> bool:
        if not user_email:
            return True
        norm = user_email.strip().lower()
        if norm in ("admin@lexicore.ai", "admin", "demo"):
            # Demo / admin sees sample preloaded documents and demo docs
            doc_user = (doc.get("user_email") or "").lower()
            return doc_user in ("", "admin@lexicore.ai", "admin", "demo")
        doc_user = (doc.get("user_email") or "").lower()
        return doc_user == norm

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves an analyzed document by its ID.

        Args:
            document_id: The UUID of the document.

        Returns:
            Optional[Dict[str, Any]]: A deep copy of the document data, or None if not found.
        """
        with self._lock:
            doc = self._documents.get(document_id)
            if doc is None:
                return None
            return copy.deepcopy(doc)

    def get_latest_document(self, user_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most recently analyzed document matching the user filter.

        Returns:
            Optional[Dict[str, Any]]: The latest document record or None if the store is empty.
        """
        with self._lock:
            if not self._ordered_ids:
                return None
            for doc_id in reversed(self._ordered_ids):
                doc = self._documents.get(doc_id)
                if doc and self._matches_user(doc, user_email):
                    return copy.deepcopy(doc)
            return None

    def list_documents(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns a list of summary records for stored documents (newest first),
        optionally filtered by user_email.

        Returns:
            List[Dict[str, Any]]: List of document summaries.
        """
        with self._lock:
            summaries = []
            for doc_id in reversed(self._ordered_ids):
                doc = self._documents.get(doc_id)
                if not doc:
                    continue
                if not self._matches_user(doc, user_email):
                    continue
                risk_info = doc.get("document_risk", {})
                summaries.append({
                    "document_id": doc["document_id"],
                    "filename": doc["filename"],
                    "upload_timestamp": doc["upload_timestamp"],
                    "user_email": doc.get("user_email"),
                    "total_clauses": doc.get("total_clauses", len(doc.get("clauses", []))),
                    "overall_score": risk_info.get("overall_score", 0.0),
                    "overall_level": risk_info.get("overall_level", "LOW"),
                })
            return summaries

    def get_all_documents(self, user_email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns deep copies of stored documents (newest first), filtered by user_email.

        Returns:
            List[Dict[str, Any]]: List of full document records.
        """
        with self._lock:
            return [
                copy.deepcopy(self._documents[doc_id])
                for doc_id in reversed(self._ordered_ids)
                if doc_id in self._documents and self._matches_user(self._documents[doc_id], user_email)
            ]

    def get_all_analytics(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Aggregates analytics across all stored documents for a specific user.

        Returns:
            Dict[str, Any]: Overall metrics for the contract analytics dashboard.
        """
        with self._lock:
            target_docs = [
                d for d in self._documents.values()
                if self._matches_user(d, user_email)
            ]
            total_documents = len(target_docs)
            if total_documents == 0:
                return {
                    "total_documents": 0,
                    "total_analyzed_documents": 0,
                    "total_clauses": 0,
                    "clause_category_counts": {},
                    "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
                    "average_risk_score": 0.0,
                    "high_risk_clause_count": 0,
                    "missing_clause_count": 0,
                    "document_risk_breakdown": [],
                }

            total_clauses = 0
            category_counts: Dict[str, int] = {}
            risk_counts: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            total_doc_scores = 0.0
            high_risk_clause_count = 0
            missing_clause_count = 0
            doc_summaries: List[Dict[str, Any]] = []

            for doc in target_docs:
                doc_risk = doc.get("document_risk", {})
                score = float(doc_risk.get("overall_score", 0.0))
                level = str(doc_risk.get("overall_level", "LOW")).upper()
                total_doc_scores += score

                if level in risk_counts:
                    risk_counts[level] += 1
                else:
                    risk_counts[level] = 1

                clauses = doc.get("clauses", [])
                total_clauses += len(clauses)

                for c in clauses:
                    cat = c.get("predicted_category", "General")
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    if str(c.get("risk_level", "")).upper() == "HIGH":
                        high_risk_clause_count += 1

                missing_info = doc.get("missing_clauses")
                if isinstance(missing_info, dict):
                    missing_list = missing_info.get("missing", [])
                    missing_clause_count += len(missing_list)

                doc_summaries.append({
                    "document_id": doc["document_id"],
                    "filename": doc["filename"],
                    "overall_score": score,
                    "overall_level": level,
                    "timestamp": doc["upload_timestamp"],
                })

            avg_score = round(total_doc_scores / total_documents, 2)

            return {
                "total_documents": total_documents,
                "total_analyzed_documents": total_documents,
                "total_clauses": total_clauses,
                "clause_category_counts": category_counts,
                "risk_distribution": risk_counts,
                "average_risk_score": avg_score,
                "high_risk_clause_count": high_risk_clause_count,
                "missing_clause_count": missing_clause_count,
                "document_risk_breakdown": doc_summaries,
            }

    def clear(self) -> None:
        """Clears all stored documents. Useful for test isolation."""
        with self._lock:
            self._documents.clear()
            self._ordered_ids.clear()


# ── Global Singleton Instance ──
_store_instance: Optional[DocumentStore] = None
_store_lock = threading.Lock()


def get_document_store() -> DocumentStore:
    """Provides a singleton instance of the DocumentStore."""
    global _store_instance
    if _store_instance is None:
        with _store_lock:
            if _store_instance is None:
                _store_instance = DocumentStore()
    return _store_instance
