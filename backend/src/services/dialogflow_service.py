"""
Dialogflow Webhook Integration Service for AI Legal Document Assistant.
Handles both Dialogflow ES fulfillment payloads and direct JSON format.
Routes natural-language questions to flexible intent handlers and TF-IDF
semantic retrieval without using any LLM.
"""

import logging
import re
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
        """
        question, document_id = self._extract_params(payload)

        if not question or not question.strip():
            return self._build_fulfillment(
                text="Please provide a question about the legal document.",
                found=False,
            )

        question = question.strip()

        # Strip common greeting prefixes if accompanied by a real query
        stripped_prefix = re.sub(
            r'^(hi|hello|hey|greetings|dear assistant|assistant|lawlens|lexi)\b[,!\s-]*',
            '',
            question,
            flags=re.IGNORECASE,
        ).strip()
        if stripped_prefix and len(stripped_prefix) > 3:
            question = stripped_prefix

        norm = question.lower().strip()
        norm_clean = re.sub(r'^[^\w]+|[^\w]+$', '', norm)
        norm_collapsed = re.sub(r'(.)\1{2,}', r'\1', norm_clean)

        greeting_words = {
            "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
            "good evening", "namaste", "howdy", "hi there", "hello there",
            "sup", "yo", "what's up", "whats up", "how are you", "how are u",
            "how do you do", "hiya", "welcome", "hey lexi", "hi lexi", "hello lexi",
            "hola", "bonjour",
        }

        # ── Conversational Intent 1: Greetings ──
        if norm_clean in greeting_words or norm_collapsed in greeting_words:
            greeting_msg = (
                "Hello! 👋 I am your **LawLens AI Legal Assistant**.\n\n"
                "I analyze legal contracts deterministically without using an LLM. You can ask me:\n"
                "• **\"What is the rent or payment terms?\"** — billing schedule & fee details\n"
                "• **\"Can you explain this contract?\"** — executive summary of the agreement\n"
                "• **\"What happens if I terminate or default?\"** — default remedies & notice periods\n"
                "• **\"What is the contract risk?\"** — Fuzzy Logic risk evaluation & scores\n"
                "• **\"Are there any missing clauses?\"** — audit of standard commercial safeguards\n"
                "• **\"Show all clauses\"** — complete clause breakdown\n\n"
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
            "what are your features", "commands", "guide", "info",
        } or re.search(r"^(who are you|what can you do|how do i use|how does this work)\b", norm_clean):
            help_msg = (
                "I am **LawLens AI**, a deterministic AI Legal Assistant built with:\n"
                "1. 🔍 **TF-IDF & Cosine Similarity Retrieval**: Answers legal questions with exact sentence extraction.\n"
                "2. ⚖️ **Mamdani Fuzzy Logic Risk Assessment**: Evaluates ambiguity, indemnity, and termination penalties (0-100 score).\n"
                "3. 🏷️ **Naive Bayes Classification**: Automatically categorizes clauses into *Payment, Confidentiality, Termination, Liability, or General*.\n"
                "4. 📋 **Extractive Contract Summary**: Highlights duration, consideration, and obligations.\n"
                "5. ⚠️ **Missing Clause Audit**: Flags omitted standard protections.\n\n"
                "Try asking: *\"What are the payment terms?\"*, *\"Explain this contract\"*, or *\"What is the risk?\"*."
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

        filename = doc.get("filename", "document.pdf")

        # ── Conversational Intent 4: Overall Risk Query ──
        if re.search(r"\b(risk|risky|risk score|overall risk|how risky|contract risk|danger|safe to sign|is this safe)\b", norm_clean):
            doc_risk = doc.get("document_risk", {})
            score = round(doc_risk.get("overall_score", 0))
            level = str(doc_risk.get("overall_level", "MODERATE")).upper()
            risk_msg = (
                f"📊 **Contract Risk Assessment** for *{filename}*:\n\n"
                f"• Overall Risk Rating: **{level} ({score}/100)**\n"
                f"• Evaluation Engine: **Mamdani Fuzzy Logic Inference** (Triangular/Trapezoidal Membership Functions)\n\n"
                f"Key risk factors evaluated:\n"
                f"1. **Clause Importance**: High-impact obligations (e.g. Liability, Termination, Payment)\n"
                f"2. **Linguistic Ambiguity**: Vague terms (e.g., 'reasonable efforts', 'as deemed fit')\n"
                f"3. **Aggressive Keywords**: Penalty, indemnification, unilateral covenants\n\n"
                f"💡 *Tip: Check the **Analysis** tab to view the interactive radial gauge and clause breakdown.*"
            )
            return self._build_fulfillment(
                text=risk_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 5: Missing Clauses Query ──
        if re.search(r"\b(missing|omit|omitted|absent|lacking|safeguard|safeguards|missing clauses|what is missing|what clauses are missing)\b", norm_clean):
            missing_data = doc.get("missing_clauses", {})
            missing_list = missing_data.get("missing_clauses", []) if isinstance(missing_data, dict) else (missing_data or [])
            if missing_list:
                items_text = "\n".join(
                    f"• ⚠️ **{m.get('category', 'Clause')}** ({m.get('severity', 'HIGH')} Severity): {m.get('recommendation', 'Standard commercial safeguard.')}"
                    for m in missing_list
                )
                missing_msg = (
                    f"⚠️ **Missing Clause Audit Results** for *{filename}*:\n\n"
                    f"The following standard commercial safeguards are absent:\n\n{items_text}\n\n"
                    f"💡 *Recommendation: Inserting these protections mitigates unilateral liability risk.*"
                )
            else:
                missing_msg = f"✅ **Missing Clause Audit**: All standard commercial clauses (Payment, Confidentiality, Termination, and Liability) are present in *{filename}*."
            return self._build_fulfillment(
                text=missing_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 6: Extractive Summary & Explanation Query ──
        if re.search(r"\b(summary|summarize|explain\s+(the|this)?\s*(contract|agreement|document)|overview|contract\s*overview|what\s+is\s+this\s+(contract|agreement|document)|give\s+me\s+a\s+summary)\b", norm_clean) or norm_clean in {"brief", "key points", "summary", "overview", "contract summary"}:
            summary_data = doc.get("summary", {})

            def _fmt_summary_item(item: Any, fallback: str) -> str:
                if isinstance(item, dict):
                    text = item.get("text")
                    if text and str(text).strip():
                        return str(text).strip()
                    return fallback
                if item and str(item).strip():
                    return str(item).strip()
                return fallback

            duration = _fmt_summary_item(summary_data.get("duration"), "Standard contract duration applies.")
            payment = _fmt_summary_item(summary_data.get("payment_terms"), "Commercial payment and fee schedule apply.")
            termination = _fmt_summary_item(summary_data.get("termination"), "Standard notice and default remedy provisions.")
            confidentiality = _fmt_summary_item(summary_data.get("confidentiality"), "Mutual non-disclosure and proprietary covenants.")
            liability = _fmt_summary_item(summary_data.get("liability"), "Standard limitation of liability and damages clause.")

            summary_msg = (
                f"📋 **Executive Contract Summary** for *{filename}*:\n\n"
                f"• ⏳ **Duration & Term**: {duration}\n"
                f"• 💰 **Financial / Payment Terms**: {payment}\n"
                f"• 🛑 **Termination & Default**: {termination}\n"
                f"• 🔒 **Confidentiality**: {confidentiality}\n"
                f"• ⚖️ **Liability & Indemnity**: {liability}\n\n"
                f"💡 *Extracted deterministically from analyzed clauses without LLM generation.*"
            )
            return self._build_fulfillment(
                text=summary_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 7: List All Clauses / Structure ──
        if re.search(r"\b(how many clauses|list clauses|show clauses|all clauses|what clauses|structure|table of contents)\b", norm_clean):
            clauses = doc.get("clauses", [])
            total = len(clauses)
            clause_lines = []
            for c in clauses[:10]:
                cid = c.get("clause_id", "?")
                cat = c.get("predicted_category", "General")
                score = round(c.get("risk_score", 0))
                level = c.get("risk_level", "LOW")
                snippet = c.get("original_text", "").strip()[:85].replace("\n", " ")
                clause_lines.append(f"• **Clause #{cid} [{cat}]** ({level} - {score}/100): *\"{snippet}...\"*")

            more_text = f"\n*...and {total - 10} more clauses.*" if total > 10 else ""
            clauses_msg = (
                f"📑 **Contract Clause Breakdown** for *{filename}* ({total} total clauses):\n\n"
                + "\n".join(clause_lines)
                + more_text
                + f"\n\n💡 *Ask me specifically about any clause (e.g. \"What are the payment terms in Clause #3?\").*"
            )
            return self._build_fulfillment(
                text=clauses_msg,
                found=True,
                document_id=document_id,
            )

        # ── Conversational Intent 8: Parties / Preamble ──
        if re.search(r"\b(parties|who are the parties|who is involved|who signed|between whom|who is landlord|who is tenant)\b", norm_clean):
            clauses = doc.get("clauses", [])
            preamble = clauses[0]["original_text"] if clauses else "Parties defined in contract preamble."
            parties_msg = (
                f"👥 **Contract Parties & Identification** from *{filename}*:\n\n"
                f"{preamble[:400]}...\n\n"
                f"💡 *Source: Clause #1 (Preamble & Identification)*"
            )
            return self._build_fulfillment(
                text=parties_msg,
                found=True,
                document_id=document_id,
            )

        # ── Semantic Retrieval Search ──
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
            # Helpful fallback when query didn't match a specific clause
            full_text = (
                f"I couldn't locate a clause specifically addressing that phrasing in *{filename}*.\n\n"
                f"💡 **Key questions you can ask me about this document:**\n"
                f"• **Payment / Rent**: *\"What is the base rent and payment schedule?\"*\n"
                f"• **Termination / Default**: *\"What happens upon default or breach?\"*\n"
                f"• **Security Deposit**: *\"Tell me about the security deposit\"*\n"
                f"• **Summary**: *\"Can you explain this contract?\"*\n"
                f"• **Risk**: *\"What is the contract risk score?\"*\n"
                f"• **All Clauses**: *\"Show all clauses\"*"
            )

        return self._build_fulfillment(
            text=full_text,
            found=result.get("found", False),
            retrieval_result=result,
            document_id=document_id,
        )

    def _extract_params(self, payload: Dict[str, Any]) -> tuple:
        """
        Extracts question and document_id from either Dialogflow ES or direct format.
        """
        question = None
        document_id = None

        query_result = payload.get("queryResult")
        if isinstance(query_result, dict):
            question = query_result.get("queryText", "")
            params = query_result.get("parameters", {})
            if isinstance(params, dict):
                document_id = params.get("document_id") or None
            logger.info("Parsed Dialogflow ES payload: question='%s', doc_id='%s'", question, document_id)
            return question, document_id

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
