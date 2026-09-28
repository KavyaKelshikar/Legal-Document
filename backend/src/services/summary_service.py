"""
Deterministic extractive contract summary service.
Extracts duration, payment terms, termination, confidentiality, and liability
directly from classified clauses without using LLMs.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from src.storage.document_store import get_document_store

logger = logging.getLogger(__name__)

# Keyword patterns for category detection and sentence ranking
CATEGORY_PATTERNS = {
    "duration": {
        "primary_categories": ["General", "Termination"],
        "strong_patterns": [
            r"\beffective\s+date\b",
            r"\bcommenc(?:ing|es?)\s+(?:on|as\s+of)\b",
            r"\bentered\s+into\s+as\s+of\b",
            r"\bterm\s+of\s+(?:this\s+agreement|\d+)\b",
            r"\bshall\s+remain\s+in\s+effect\b",
            r"\bexpir(?:es|ation|y)\s+(?:on|date)\b",
            r"\b(?:one|two|three|five|\d+)\s+(?:years?|months?)\s+(?:term|period)\b",
        ],
        "keywords": [
            r"\bterm\b",
            r"\beffective\s+date\b",
            r"\bexpir(?:es|ation|y)\b",
            r"\brenew(?:al|s|ed)?\b",
            r"\bduration\b",
            r"\bperiod\b",
            r"\bcalendar\s+days\b",
        ],
    },
    "payment_terms": {
        "primary_categories": ["Payment"],
        "strong_patterns": [
            r"\$\s*[\d,]+(?:\.\d{2})?",
            r"\b(?:fee|sum)\s+of\s+\$\s*[\d,]+",
            r"\bdue\s+net\s+\d+\b",
            r"\bnet\s+\d+\s+days\b",
            r"\bwithin\s+\d+\s+(?:calendar\s+)?days\b",
            r"\binvoices?\s+(?:are\s+)?due\b",
            r"\bpayable\s+(?:in|within|monthly|annually)\b",
            r"\binterest\s+at\s+(?:a\s+rate\s+of\s+)?[\d\.]+\s*%",
        ],
        "keywords": [
            r"\bpay(?:ment|s|able|ing)?\b",
            r"\bfee\b",
            r"\bfees\b",
            r"\binvoice\b",
            r"\binvoices\b",
            r"\bdue\s+date\b",
            r"\bretainer\b",
            r"\bcompensation\b",
        ],
    },
    "termination": {
        "primary_categories": ["Termination"],
        "strong_patterns": [
            r"\b\d+\s+(?:calendar\s+)?days\s+(?:prior\s+)?written\s+notice\b",
            r"\bwritten\s+notice\s+of\s+\d+\s+days\b",
            r"\bterminate\s+immediately\b",
            r"\bmaterial\s+breach\b",
            r"\bterminate\s+for\s+convenience\b",
            r"\beither\s+party\s+may\s+terminate\b",
            r"\bupon\s+termination\b",
        ],
        "keywords": [
            r"\bterminat(?:e|es|ed|ion|ing)\b",
            r"\bnotice\b",
            r"\bbreach\b",
            r"\bcancel(?:lation)?\b",
            r"\bend\s+this\s+contract\b",
        ],
    },
    "confidentiality": {
        "primary_categories": ["Confidentiality"],
        "strong_patterns": [
            r"\bproprietary\s+information\b",
            r"\btrade\s+secrets?\b",
            r"\bkeep\s+(?:all\s+)?(?:information\s+)?confidential\b",
            r"\bnot\s+disclose\b",
            r"\bwithout\s+prior\s+written\s+consent\b",
            r"\bshall\s+not\s+(?:use|disclose)\b",
            r"\bconfidential\s+information\s+includes\b",
        ],
        "keywords": [
            r"\bconfidenti(?:al|ality)\b",
            r"\bdisclos(?:e|ure|ing)\b",
            r"\bproprietary\b",
            r"\bsecret\b",
            r"\bnon-disclosure\b",
        ],
    },
    "liability": {
        "primary_categories": ["Liability"],
        "strong_patterns": [
            r"\blimitation\s+of\s+liability\b",
            r"\bindemnif(?:y|ies|ication)\b",
            r"\bhold\s+harmless\b",
            r"\bindirect[,\s]+incidental[,\s]+or\s+consequential\s+damages\b",
            r"\bconsequential\s+damages\b",
            r"\bnot\s+exceed\s+the\s+total\s+fees\b",
            r"\bpenalty\s+for\s+breach\b",
            r"\btotal\s+liability\b",
        ],
        "keywords": [
            r"\bliab(?:ility|le)\b",
            r"\bdamage\b",
            r"\bdamages\b",
            r"\bindemn(?:ify|ity)\b",
            r"\bpenalty\b",
            r"\blawsuit\b",
            r"\bclaims?\b",
        ],
    },
}


class SummaryService:
    """Service to deterministically generate extractive contract summaries."""

    def summarize_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves document by ID from DocumentStore and generates extractive summary.

        Args:
            document_id: UUID of the document.

        Returns:
            Optional[Dict[str, Any]]: Summary dictionary, or None if document not found.
        """
        store = get_document_store()
        doc = store.get_document(document_id)
        if doc is None:
            return None

        clauses = doc.get("clauses", [])
        return self.extract_summary(clauses)

    def extract_summary(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extracts summary information for the 5 legal categories from given clauses.

        Args:
            clauses: List of clause dictionaries with 'original_text' and 'predicted_category'.

        Returns:
            Dict[str, Any]: Structured summary dictionary.
        """
        summary: Dict[str, Any] = {}

        for category_name in ["duration", "payment_terms", "termination", "confidentiality", "liability"]:
            extracted = self._extract_category_summary(clauses, category_name)
            summary[category_name] = extracted

        return summary

    def _extract_category_summary(
        self, clauses: List[Dict[str, Any]], category_key: str
    ) -> Dict[str, Any]:
        """
        Scans clauses and extracts the single most informative sentence for the target category.
        """
        config = CATEGORY_PATTERNS.get(category_key, {})
        primary_categories = config.get("primary_categories", [])
        strong_patterns = [re.compile(p, re.IGNORECASE) for p in config.get("strong_patterns", [])]
        keywords = [re.compile(k, re.IGNORECASE) for k in config.get("keywords", [])]

        best_score = 0.0
        best_sentence: Optional[str] = None
        best_clause_text: Optional[str] = None
        best_category: Optional[str] = None

        for clause in clauses:
            clause_text = clause.get("original_text", "").strip()
            if not clause_text:
                continue

            clause_cat = clause.get("predicted_category", "General")
            is_primary_cat = clause_cat in primary_categories

            # Break clause into sentences
            sentences = self._split_into_sentences(clause_text)

            for sentence in sentences:
                score = 0.0

                # Match strong multi-word patterns
                for sp in strong_patterns:
                    if sp.search(sentence):
                        score += 3.0

                # Match general category keywords
                for kw in keywords:
                    if kw.search(sentence):
                        score += 1.0

                # Add category alignment boost if clause ML classification matches
                if score > 0 and is_primary_cat:
                    score += 2.0

                if score > best_score:
                    best_score = score
                    best_sentence = sentence
                    best_clause_text = clause_text
                    best_category = clause_cat

        # Threshold check: requires a minimum score of 2.0 to avoid weak false positives
        if best_score >= 2.0 and best_sentence:
            return {
                "status": "detected",
                "text": best_sentence,
                "source_clause": best_clause_text,
                "clause_category": best_category,
            }

        return {
            "status": "not_detected",
            "text": None,
            "source_clause": None,
            "clause_category": None,
        }

    def _split_into_sentences(self, text: str) -> List[str]:
        """Splits raw clause text into clean sentence units."""
        # Split on terminal punctuation followed by space or newline
        raw = re.split(r"(?<=[.!?])\s+", text)
        sentences = []
        for s in raw:
            s_clean = s.strip()
            # Exclude very short header snippets like "1. Payment Terms." unless followed by content
            if len(s_clean) > 15:
                sentences.append(s_clean)
        if not sentences and text.strip():
            sentences.append(text.strip())
        return sentences


# Global singleton instance
_summary_instance: Optional[SummaryService] = None


def get_summary_service() -> SummaryService:
    """Provides a singleton instance of SummaryService."""
    global _summary_instance
    if _summary_instance is None:
        _summary_instance = SummaryService()
    return _summary_instance
