"""
Dialogflow Webhook Integration Service for AI Legal Document Assistant.
Handles both Dialogflow ES fulfillment payloads and direct JSON format.
Routes natural-language questions to TF-IDF + Cosine Similarity retrieval
without using any LLM.
"""

import logging
from typing import Any, Dict, Optional

from src.services.retrieval_service import get_retrieval_service
from src.storage.document_store import get_document_store

logger = logging.getLogger(__name__)


class DialogflowService:
    """
    Adapter service for processing Dialogflow webhook requests
    and direct JSON question payloads.

    Supported input formats:
    1. Direct JSON: {"question": "...", "document_id": "..."}
    2. Dialogflow ES: {"queryResult": {"queryText": "...", "parameters": {"document_id": "..."}}}
    """

    def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes an incoming webhook payload from Dialogflow or direct JSON.

        Extracts the question and optional document_id, performs TF-IDF
        retrieval, and returns a Dialogflow-compatible fulfillment response.

        Args:
            payload: The raw webhook request body.

        Returns:
            Dict[str, Any]: Dialogflow fulfillment response with
            fulfillmentText, fulfillmentMessages, and payload fields.
        """
        question, document_id = self._extract_params(payload)

        if not question or not question.strip():
            return self._build_fulfillment(
                text="Please provide a question about the legal document.",
                found=False,
            )

        question = question.strip()
        import re

        # Strip common greeting prefixes if accompanied by a real query
        stripped_prefix = re.sub(
            r'^(hi|hello|hey|greetings|dear assistant|assistant|lexicore|lexi)\b[,!\s-]*',
            '',
            question,
            flags=re.IGNORECASE
        ).strip()
        if stripped_prefix and len(stripped_prefix) > 3:
            # Query has substantive question following greeting
            question = stripped_prefix

        norm = question.lower().strip()
        norm_clean = re.sub(r'^[^\w]+|[^\w]+$', '', norm)
        # Collapse repeated characters (e.g. "hiii" -> "hi", "heyyy" -> "hey")
        norm_collapsed = re.sub(r'(.)\1{2,}', r'\1', norm_clean)

        greeting_words = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "namaste", "howdy", "hi there", "hello there",
            "sup", "yo", "what's up", "whats up", "how are you", "how are u",
            "how do you do", "hiya", "welcome", "hey lexi", "hi lexi", "hello lexi",
            "hola", "bonjour"
        }

        # ── Conversational Intent 1: Greetings ──
        if norm_clean in greeting_words or norm_collapsed in greeting_words:
            greeting_msg = (
                "Hello! 👋 I am your **LexiCore AI Legal Assistant**.\n\n"
                "I analyze legal contracts deterministically without using an LLM. You can ask me:\n"
                "• **\"What are the payment terms?\"** — billing schedule & milestone terms\n"
                "• **\"When does this contract expire?\"** — effective dates & duration\n"
                "• **\"What happens if I terminate early?\"** — notice periods & early penalties\n"
                "• **\"What is the contract risk?\"** — Mamdani fuzzy logic risk breakdown\n"
                "• **\"Are there any missing clauses?\"** — audit of standard commercial safeguards\n\n"
                "How can I help you review your legal document today?"
            )
            return self._build_fulfillment(
                text=greeting_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 2: Identity & Help ──
        if norm_clean in {
            "who are you", "what can you do", "help", "what is this", "how does this work",
            "what are your features", "commands", "guide", "info"
        }:
            help_msg = (
                "I am **LexiCore**, a deterministic AI Legal Assistant built with:\n"
                "1. 🔍 **TF-IDF & Cosine Similarity Retrieval**: Answers legal questions with exact sentence extraction.\n"
                "2. ⚖️ **Mamdani Fuzzy Logic Risk Assessment**: Evaluates ambiguity, indemnity, and termination penalties (0-100 score).\n"
                "3. 🏷️ **Naive Bayes Classification**: Automatically categorizes clauses into *Payment, Confidentiality, Termination, Liability, or General*.\n"
                "4. 📋 **Extractive Contract Summary**: Highlights duration, consideration, and obligations.\n"
                "5. ⚠️ **Missing Clause Audit**: Flags omitted standard protections.\n\n"
                "Try asking: *\"What are the payment terms?\"* or *\"Show termination clauses\"*."
            )
            return self._build_fulfillment(
                text=help_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 3: Gratitude ──
        if norm_clean in {"thanks", "thank you", "great", "awesome", "perfect", "good job", "ok", "okay", "thank you so much", "thx"}:
            return self._build_fulfillment(
                text="You're very welcome! Let me know if you need to review any other clauses or download the PDF analysis report.",
                found=True,
                document_id=document_id,
            )

        # Resolve document_id: use provided value or fall back to latest
        store = get_document_store()
        doc = None
        if document_id:
            doc = store.get_document(document_id)
            if not doc:
                return self._build_fulfillment(
                    text=f"Document with ID '{document_id}' was not found.",
                    found=False,
                )
        else:
            doc = store.get_latest_document()
            if doc:
                document_id = doc["document_id"]
            else:
                return self._build_fulfillment(
                    text="No documents have been analyzed yet. Please upload a document first.",
                    found=False,
                )

        # ── Conversational Intent 4: Overall Risk Query ──
        if norm_clean in {
            "risk", "what is the risk", "contract risk", "overall risk",
            "is this contract risky", "how risky is this", "risk score", "show risk"
        }:
            doc_risk = doc.get("document_risk", {})
            score = round(doc_risk.get("overall_score", 0))
            level = str(doc_risk.get("overall_level", "MODERATE")).upper()
            risk_msg = (
                f"📊 **Contract Risk Assessment** for *{doc.get('filename', 'document.pdf')}*:\n\n"
                f"• Overall Risk: **{level} ({score}/100)**\n"
                f"• Engine: **Mamdani Fuzzy Logic Inference** (Triangular/Trapezoidal Membership Functions)\n\n"
                f"Key risk drivers evaluated: Clause Importance, Linguistic Ambiguity, and Consequential Indemnity/Liability terms.\n\n"
                f"💡 *Tip: Check the **Analysis** tab to view the radial risk gauge and individual clause risk scores.*"
            )
            return self._build_fulfillment(
                text=risk_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 5: Missing Clauses Query ──
        if norm_clean in {
            "missing", "missing clauses", "what is missing", "what clauses are missing",
            "are there any missing clauses", "omitted clauses", "check missing", "missing terms"
        }:
            missing_data = doc.get("missing_clauses", {})
            missing_list = missing_data.get("missing_clauses", []) if isinstance(missing_data, dict) else (missing_data or [])
            if missing_list:
                items_text = "\n".join(
                    f"• ⚠️ **{m.get('category', 'Clause')}** ({m.get('severity', 'HIGH')} Severity): {m.get('recommendation', 'Standard commercial safeguard.')}"
                    for m in missing_list
                )
                missing_msg = (
                    f"⚠️ **Missing Clause Audit Results** for *{doc.get('filename', 'document.pdf')}*:\n\n"
                    f"The following standard commercial safeguards are absent:\n\n{items_text}\n\n"
                    f"💡 *Recommendation: Inserting these clauses protects against unilateral risk.*"
                )
            else:
                missing_msg = f"✅ **Missing Clause Audit**: All standard commercial clauses (Payment, Confidentiality, Termination, and Liability) are present in *{doc.get('filename', 'document.pdf')}*."
            return self._build_fulfillment(
                text=missing_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 6: Extractive Summary Query ──
        if norm_clean in {
            "summary", "summarize", "contract summary", "give me a summary",
            "overview", "what is this contract about", "brief", "key points"
        }:
            summary_data = doc.get("summary", {})
            if summary_data:
                summary_msg = (
                    f"📋 **Extractive Contract Summary** for *{doc.get('filename', 'document.pdf')}*:\n\n"
                    f"• ⏳ **Duration & Term**: {summary_data.get('duration', 'No explicit term detected.')}\n"
                    f"• 💰 **Payment Terms**: {summary_data.get('payment_terms', 'Standard commercial invoicing.')}\n"
                    f"• 🛑 **Termination**: {summary_data.get('termination', 'Notice requirements apply.')}\n"
                    f"• 🔒 **Confidentiality**: {summary_data.get('confidentiality', 'Mutual non-disclosure terms.')}\n"
                    f"• ⚖️ **Liability**: {summary_data.get('liability', 'Standard limitation provisions.')}\n\n"
                    f"💡 *Extracted deterministically from key clause headings without LLM generation.*"
                )
                return self._build_fulfillment(
                    text=summary_msg,
                    found=True,
                    document_id=document_id,
                )

        # Use RetrievalService to search
        retrieval = get_retrieval_service()
        result = retrieval.search_document(document_id, question)

        if result is None:
            return self._build_fulfillment(
                text=f"Document with ID '{document_id}' was not found.",
                found=False,
            )

        if result.get("found"):
            answer_text = result["answer"]
            source_info = (
                f"\n\n📄 Source: {result.get('clause_category', 'Unknown')} clause "
                f"(Clause #{result.get('clause_id', '?')}, "
                f"Similarity: {result.get('similarity_score', 0):.2%})"
            )
            full_text = answer_text + source_info
        else:
            full_text = result.get("answer", "No relevant clause was found.")

        return self._build_fulfillment(
            text=full_text,
            found=result.get("found", False),
            retrieval_result=result,
            document_id=document_id,
        )

    def _extract_params(self, payload: Dict[str, Any]) -> tuple:
        """
        Extracts question and document_id from either Dialogflow ES or direct format.

        Returns:
            tuple: (question, document_id) — document_id may be None.
        """
        question = None
        document_id = None

        # ── Format 1: Dialogflow ES fulfillment ──
        query_result = payload.get("queryResult")
        if isinstance(query_result, dict):
            question = query_result.get("queryText", "")
            params = query_result.get("parameters", {})
            if isinstance(params, dict):
                document_id = params.get("document_id") or None
            logger.info("Parsed Dialogflow ES payload: question='%s', doc_id='%s'", question, document_id)
            return question, document_id

        # ── Format 2: Direct JSON ──
        question = payload.get("question", "")
        document_id = payload.get("document_id") or None
        logger.info("Parsed direct JSON payload: question='%s', doc_id='%s'", question, document_id)
        return question, document_id

    def _build_fulfillment(
        self,
        text: str,
        found: bool = False,
        retrieval_result: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Constructs a Dialogflow-compatible fulfillment response.

        Args:
            text: The main response text.
            found: Whether a relevant clause was found.
            retrieval_result: The full retrieval result dictionary (optional).
            document_id: The resolved document_id (optional).

        Returns:
            Dict[str, Any]: Dialogflow fulfillment response.
        """
        response = {
            "fulfillmentText": text,
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [text],
                    }
                }
            ],
            "payload": {
                "found": found,
                "document_id": document_id,
            },
        }

        if retrieval_result is not None:
            response["payload"]["answer"] = retrieval_result.get("answer")
            response["payload"]["source_clause"] = retrieval_result.get("source_clause")
            response["payload"]["clause_category"] = retrieval_result.get("clause_category")
            response["payload"]["similarity_score"] = retrieval_result.get("similarity_score")
            response["payload"]["clause_id"] = retrieval_result.get("clause_id")

        return response


# ── Global Singleton Instance ──
_dialogflow_instance: Optional[DialogflowService] = None


def get_dialogflow_service() -> DialogflowService:
    """Provides a singleton instance of the DialogflowService."""
    global _dialogflow_instance
    if _dialogflow_instance is None:
        _dialogflow_instance = DialogflowService()
    return _dialogflow_instance
