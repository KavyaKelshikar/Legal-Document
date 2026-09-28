"""
Deterministic Missing Clause Category Detection Service.
Detects potentially absent clause categories from classified document clauses.
Academic document-analysis feature (not legal advice).
"""

import logging
from typing import Any, Dict, List, Optional
from src.storage.document_store import get_document_store

logger = logging.getLogger(__name__)

EXPECTED_CATEGORIES = [
    "Payment",
    "Confidentiality",
    "Termination",
    "Liability",
    "General",
]

CATEGORY_RISK_IMPACTS = {
    "Payment": "The document may lack explicitly identified payment amounts, invoicing terms, or payment schedules.",
    "Confidentiality": "The document may lack an explicitly identified confidentiality provision or proprietary information safeguards.",
    "Termination": "The document may lack an explicitly identified termination clause, notice period, or breach remedy.",
    "Liability": "The document may lack an explicitly identified liability provision, limitation of liability, or indemnification cap.",
    "General": "The document may lack standard general provisions such as governing law, entire agreement, or notice methods.",
}


class MissingClauseService:
    """Service to deterministically detect potentially missing clause categories."""

    def __init__(self, expected_categories: Optional[List[str]] = None):
        self.expected_categories = expected_categories or EXPECTED_CATEGORIES

    def analyze_document_missing_clauses(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves document by ID from DocumentStore and detects missing clause categories.

        Args:
            document_id: UUID of the document.

        Returns:
            Optional[Dict[str, Any]]: Missing clauses analysis, or None if document not found.
        """
        store = get_document_store()
        doc = store.get_document(document_id)
        if doc is None:
            return None

        clauses = doc.get("clauses", [])
        return self.detect_missing_clauses(clauses)

    def detect_missing_clauses(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compares detected clause categories against expected categories.

        Args:
            clauses: List of clause dictionaries with 'predicted_category'.

        Returns:
            Dict[str, Any]: Structured detection report with academic wording.
        """
        # Determine detected categories (preserve order of first appearance)
        detected_set = set()
        detected_ordered = []

        for clause in clauses:
            cat = clause.get("predicted_category")
            if cat and cat in self.expected_categories and cat not in detected_set:
                detected_set.add(cat)
                detected_ordered.append(cat)

        # Determine absent expected categories
        missing_findings = []
        for expected_cat in self.expected_categories:
            if expected_cat not in detected_set:
                impact = CATEGORY_RISK_IMPACTS.get(
                    expected_cat,
                    f"The document may lack an explicitly identified {expected_cat.lower()} provision.",
                )
                missing_findings.append({
                    "category": expected_cat,
                    "title": "Potentially missing clause category",
                    "rationale": f"No clause classified as {expected_cat} was detected in the analyzed document.",
                    "risk_impact": impact,
                })

        return {
            "expected_categories": list(self.expected_categories),
            "detected_categories": detected_ordered,
            "missing_count": len(missing_findings),
            "missing_clauses": missing_findings,
        }


# Global singleton instance
_missing_clause_instance: Optional[MissingClauseService] = None


def get_missing_clause_service() -> MissingClauseService:
    """Provides a singleton instance of MissingClauseService."""
    global _missing_clause_instance
    if _missing_clause_instance is None:
        _missing_clause_instance = MissingClauseService()
    return _missing_clause_instance
