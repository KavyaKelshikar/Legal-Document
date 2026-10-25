"""
TF-IDF + Cosine Similarity Question Retrieval Service.
Extracts relevant answers from analyzed contract clauses without using LLMs.
"""

import logging
import re
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.storage.document_store import get_document_store

logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = "No sufficiently relevant clause was found in this document."
DEFAULT_THRESHOLD = 0.12

# Domain-specific synonym expansions to bridge conversational questions with formal legalese
SYNONYM_MAP = {
    "rent": ["rent", "monthly base rent", "payment", "lease fee", "amount", "dollars"],
    "payment": ["pay", "payment", "invoicing", "due", "fee", "compensation", "billing"],
    "pay": ["pay", "payment", "fee", "compensation", "remuneration", "deposit", "invoice"],
    "cost": ["cost", "price", "fee", "expenses", "payment", "rent"],
    "money": ["payment", "fee", "rent", "dollars", "deposit"],
    "deposit": ["security deposit", "deposit", "escrow", "performance", "funds"],
    "terminate": ["terminate", "termination", "default", "breach", "remedies", "cancel", "surrender", "exit", "notice"],
    "termination": ["terminate", "termination", "default", "remedies", "written notice", "cancellation"],
    "cancel": ["cancel", "cancellation", "terminate", "termination", "default", "notice"],
    "default": ["default", "breach", "remedy", "remedies", "cure", "terminate", "eviction"],
    "breach": ["breach", "default", "remedies", "violation", "cure"],
    "penalty": ["penalty", "liquidated damages", "interest", "late charge", "fine", "remedies"],
    "liability": ["liability", "indemnify", "indemnification", "damages", "claims", "loss", "hold harmless"],
    "liable": ["liability", "indemnify", "damages", "claims", "responsible"],
    "indemnity": ["indemnify", "indemnity", "hold harmless", "defense", "damages"],
    "damage": ["damages", "liability", "indirect", "special", "consequential"],
    "confidential": ["confidential", "proprietary", "trade secrets", "non-disclosure", "privacy", "disclosure"],
    "secret": ["trade secrets", "proprietary", "confidential", "confidentiality"],
    "nda": ["confidentiality", "proprietary", "disclosure", "trade secrets"],
    "law": ["governing law", "jurisdiction", "court", "arbitration", "dispute", "venue"],
    "court": ["governing law", "jurisdiction", "court", "arbitration", "venue"],
    "dispute": ["dispute resolution", "arbitration", "governing law", "court", "litigation"],
    "parties": ["landlord", "tenant", "client", "consultant", "vendor", "parties", "between", "lessor", "lessee"],
    "who": ["landlord", "tenant", "parties", "client", "consultant", "contractor", "vendor"],
    "duration": ["duration", "term", "commencement", "expiration", "period", "years", "months", "effective date"],
    "term": ["term", "duration", "commencement", "period", "renewal", "expiration"],
    "expire": ["expiration", "expire", "term", "duration", "end date"],
    "maintenance": ["common area maintenance", "operating expenses", "cam", "repairs", "alterations", "upkeep"],
    "cam": ["common area maintenance", "operating expenses", "cam", "proportionate share"],
    "use": ["permitted use", "premises", "occupancy"],
}


class RetrievalService:
    """Reusable service for searching and retrieving clauses by question similarity."""

    def __init__(self, default_threshold: float = DEFAULT_THRESHOLD):
        self.default_threshold = default_threshold

    def search_document(
        self,
        document_id: str,
        question: str,
        threshold: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the document from DocumentStore and executes question search.

        Args:
            document_id: UUID of the document in DocumentStore.
            question: User's natural-language query.
            threshold: Optional custom similarity threshold.

        Returns:
            Optional[Dict[str, Any]]: Structured search response, or None if document_id does not exist.
        """
        store = get_document_store()
        document = store.get_document(document_id)
        if document is None:
            return None

        clauses = document.get("clauses", [])
        return self.search_clauses(clauses, question, threshold=threshold)

    def _expand_query(self, query: str) -> str:
        """Enriches the user query with domain-specific legal synonyms."""
        words = re.findall(r"\w+", query.lower())
        expansions = set(words)
        for w in words:
            if w in SYNONYM_MAP:
                expansions.update(SYNONYM_MAP[w])
        return " ".join(expansions)

    def search_clauses(
        self,
        clauses: List[Dict[str, Any]],
        question: str,
        threshold: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Builds TF-IDF vectors for clauses, computes cosine similarity against the question,
        and extracts the best-matching clause and specific answer sentence.

        Args:
            clauses: List of clause dictionaries containing 'original_text' and 'clause_id'.
            question: User's query string.
            threshold: Cosine similarity threshold (defaults to 0.12).

        Returns:
            Dict[str, Any]: Structured search result matching project specifications.
        """
        eff_threshold = threshold if threshold is not None else self.default_threshold
        cleaned_question = question.strip() if question else ""

        # Validate input
        if not cleaned_question or not clauses:
            return self._build_empty_response(cleaned_question)

        # Prepare corpus of clause texts
        corpus = [c.get("original_text", "").strip() for c in clauses]

        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            clause_vectors = vectorizer.fit_transform(corpus)

            # Transform original query
            question_vector = vectorizer.transform([cleaned_question])
            similarities = cosine_similarity(question_vector, clause_vectors)[0]

            # Also check expanded query with legal synonyms
            expanded_q = self._expand_query(cleaned_question)
            if expanded_q != cleaned_question.lower():
                expanded_vec = vectorizer.transform([expanded_q])
                expanded_sims = cosine_similarity(expanded_vec, clause_vectors)[0]
                # Combine original and expanded with weighting
                similarities = np.maximum(similarities, expanded_sims * 0.95)
        except ValueError as err:
            logger.debug("TF-IDF vectorizer encountered empty vocabulary: %s", err)
            return self._build_empty_response(cleaned_question)

        best_idx = int(np.argmax(similarities))
        top_score = float(similarities[best_idx])

        # Enforce similarity threshold to reject unrelated queries
        if top_score < eff_threshold:
            logger.info(
                "Query '%s' top similarity %.4f below threshold %.4f",
                cleaned_question,
                top_score,
                eff_threshold,
            )
            return self._build_empty_response(cleaned_question, similarity_score=round(top_score, 4))

        best_clause = clauses[best_idx]
        clause_text = best_clause.get("original_text", "")
        best_sentence = self._extract_best_sentence(clause_text, cleaned_question)

        return {
            "question": cleaned_question,
            "answer": best_sentence,
            "source_clause": clause_text,
            "clause_category": best_clause.get("predicted_category"),
            "similarity_score": round(top_score, 4),
            "clause_id": best_clause.get("clause_id"),
            "found": True,
        }

    def _extract_best_sentence(self, clause_text: str, question: str) -> str:
        """
        Extracts the most relevant sentence from the selected clause to provide
        a concise, informative, deterministic answer.
        """
        # Split clause into sentences
        raw_sentences = [
            s.strip() for s in re.split(r"(?<=[.!?])\s+", clause_text.strip()) if len(s.strip()) > 3
        ]

        if not raw_sentences:
            return clause_text.strip()

        if len(raw_sentences) == 1:
            return raw_sentences[0]

        try:
            sent_vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            sent_matrix = sent_vec.fit_transform(raw_sentences)
            q_vec = sent_vec.transform([question])
            sent_sims = cosine_similarity(q_vec, sent_matrix)[0]

            best_sent_idx = int(np.argmax(sent_sims))
            chosen = raw_sentences[best_sent_idx]

            # If the selected sentence looks like a short heading/section number
            # (e.g. "2.1 Monthly Base Rent." or under 50 chars), append the following sentence
            # so the user receives the full explanation/amount.
            is_heading = (
                len(chosen) < 60
                or re.match(r"^(\d+(\.\d+)*\s+[A-Z\s]+|\d+\.\s+[A-Z])", chosen)
                or not re.search(r"[a-z]", chosen)
            )
            if is_heading and (best_sent_idx + 1) < len(raw_sentences):
                return f"{chosen} {raw_sentences[best_sent_idx + 1]}"

            return chosen
        except Exception as e:
            logger.debug("Sentence extraction fallback due to: %s", e)

        # Fallback: if first sentence is short header, combine with second
        if len(raw_sentences) > 1 and len(raw_sentences[0]) < 60:
            return f"{raw_sentences[0]} {raw_sentences[1]}"
        return raw_sentences[0]

    def _build_empty_response(
        self, question: str, similarity_score: float = 0.0
    ) -> Dict[str, Any]:
        """Constructs standardized empty response when no clause meets the threshold."""
        return {
            "question": question,
            "answer": NOT_FOUND_MESSAGE,
            "source_clause": None,
            "clause_category": None,
            "similarity_score": similarity_score,
            "clause_id": None,
            "found": False,
        }


# Global singleton instance
_retrieval_instance: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    """Provides a singleton instance of the RetrievalService."""
    global _retrieval_instance
    if _retrieval_instance is None:
        _retrieval_instance = RetrievalService()
    return _retrieval_instance
