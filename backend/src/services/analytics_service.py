"""
Deterministic Contract Analytics Service.
Calculates document-level and system-wide aggregate metrics from stored documents.
No LLM used; consumes pre-computed analysis data safely.
"""

import logging
from collections import Counter
from typing import Any, Dict, List, Optional
from src.storage.document_store import get_document_store
from src.services.missing_clause_service import get_missing_clause_service

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for computing contract and portfolio analytics from DocumentStore."""

    def get_document_analytics(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Calculates analytics for a specific analyzed document.

        Args:
            document_id: UUID of the document.

        Returns:
            Optional[Dict[str, Any]]: Document analytics dict, or None if document not found.
        """
        store = get_document_store()
        doc = store.get_document(document_id)
        if doc is None:
            return None

        return self.calculate_document_analytics(doc)

    def calculate_document_analytics(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates clause-level metrics, category distribution, risk distribution,
        and missing clause info for an individual document.
        """
        document_id = doc.get("document_id")
        filename = doc.get("filename", "unknown.pdf")
        clauses = doc.get("clauses", [])
        total_clauses = len(clauses)

        doc_risk = doc.get("document_risk", {})
        overall_risk = str(doc_risk.get("overall_level", "LOW")).upper()

        # Collect numeric clause risk scores safely
        clause_scores: List[float] = []
        risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        category_distribution: Dict[str, int] = {}
        high_risk_clauses: List[Dict[str, Any]] = []

        for c in clauses:
            cat = c.get("predicted_category", "General")
            category_distribution[cat] = category_distribution.get(cat, 0) + 1

            # Risk level counts
            lvl = str(c.get("risk_level", "LOW")).upper()
            if lvl in risk_distribution:
                risk_distribution[lvl] += 1
            else:
                risk_distribution[lvl] = 1

            if lvl == "HIGH":
                high_risk_clauses.append(c)

            # Safely parse numeric risk score
            raw_score = c.get("risk_score")
            if isinstance(raw_score, (int, float)):
                clause_scores.append(float(raw_score))

        # Averages and extremes
        if clause_scores:
            avg_risk = round(sum(clause_scores) / len(clause_scores), 2)
            highest_risk = round(max(clause_scores), 2)
        else:
            # Fallback to overall doc score if available
            doc_score = doc_risk.get("overall_score")
            fallback = round(float(doc_score), 2) if isinstance(doc_score, (int, float)) else 0.0
            avg_risk = fallback
            highest_risk = fallback

        # Missing clause information
        missing_info = doc.get("missing_clauses")
        if not isinstance(missing_info, dict) or "missing_clauses" not in missing_info:
            missing_service = get_missing_clause_service()
            missing_info = missing_service.detect_missing_clauses(clauses)

        missing_count = missing_info.get("missing_count", 0)
        missing_categories = [
            item.get("category") if isinstance(item, dict) else str(item)
            for item in missing_info.get("missing_clauses", [])
        ]

        return {
            "document_id": document_id,
            "filename": filename,
            "total_clauses": total_clauses,
            "overall_risk": overall_risk,
            "average_risk_score": avg_risk,
            "highest_clause_risk_score": highest_risk,
            "risk_distribution": risk_distribution,
            "category_distribution": category_distribution,
            "high_risk_clauses": high_risk_clauses,
            "missing_clause_count": missing_count,
            "missing_clause_categories": missing_categories,
        }

    def get_system_analytics(self, user_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Aggregates analytics across documents in DocumentStore.
        Optionally filtered by user_email. Gracefully handles empty repository with zero-value output.
        """
        store = get_document_store()
        all_docs = store.get_all_documents(user_email=user_email)
        total_documents = len(all_docs)

        if total_documents == 0:
            return {
                "total_documents": 0,
                "total_analyzed": 0,
                "total_clauses": 0,
                "average_clauses_per_document": 0.0,
                "average_risk_score": 0.0,
                "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
                "category_distribution": {},
                "high_risk_document_count": 0,
                "high_risk_clause_count": 0,
                "missing_clause_statistics": {
                    "documents_with_missing_clauses": 0,
                    "total_missing_categories": 0,
                    "most_common_missing_category": None,
                },
            }

        total_clauses = 0
        doc_risk_scores: List[float] = []
        doc_risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        category_distribution: Dict[str, int] = {}
        high_risk_document_count = 0
        high_risk_clause_count = 0

        docs_with_missing_count = 0
        missing_category_counter: Counter = Counter()

        for doc in all_docs:
            doc_risk = doc.get("document_risk", {})
            doc_score = doc_risk.get("overall_score")
            if isinstance(doc_score, (int, float)):
                doc_risk_scores.append(float(doc_score))

            level = str(doc_risk.get("overall_level", "LOW")).upper()
            if level in doc_risk_distribution:
                doc_risk_distribution[level] += 1
            else:
                doc_risk_distribution[level] = 1

            if level == "HIGH":
                high_risk_document_count += 1

            clauses = doc.get("clauses", [])
            total_clauses += len(clauses)

            for c in clauses:
                cat = c.get("predicted_category", "General")
                category_distribution[cat] = category_distribution.get(cat, 0) + 1

                if str(c.get("risk_level", "")).upper() == "HIGH":
                    high_risk_clause_count += 1

            # Missing clauses tally
            missing_info = doc.get("missing_clauses")
            if not isinstance(missing_info, dict) or "missing_clauses" not in missing_info:
                missing_service = get_missing_clause_service()
                missing_info = missing_service.detect_missing_clauses(clauses)

            missing_items = missing_info.get("missing_clauses", [])
            if missing_items:
                docs_with_missing_count += 1
                for item in missing_items:
                    cat_name = item.get("category") if isinstance(item, dict) else str(item)
                    missing_category_counter[cat_name] += 1

        avg_clauses_per_doc = round(total_clauses / total_documents, 2)
        avg_doc_risk = round(sum(doc_risk_scores) / len(doc_risk_scores), 2) if doc_risk_scores else 0.0

        most_common_missing = (
            missing_category_counter.most_common(1)[0][0] if missing_category_counter else None
        )
        total_missing = sum(missing_category_counter.values())

        return {
            "total_documents": total_documents,
            "total_analyzed": total_documents,
            "total_clauses": total_clauses,
            "average_clauses_per_document": avg_clauses_per_doc,
            "average_risk_score": avg_doc_risk,
            "risk_distribution": doc_risk_distribution,
            "category_distribution": category_distribution,
            "high_risk_document_count": high_risk_document_count,
            "high_risk_clause_count": high_risk_clause_count,
            "missing_clause_statistics": {
                "documents_with_missing_clauses": docs_with_missing_count,
                "total_missing_categories": total_missing,
                "most_common_missing_category": most_common_missing,
            },
        }


# Global singleton instance
_analytics_instance: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Provides a singleton instance of AnalyticsService."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsService()
    return _analytics_instance
