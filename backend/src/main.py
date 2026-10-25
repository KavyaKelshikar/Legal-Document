import logging
import os
from contextlib import asynccontextmanager

from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.config import settings
from src.extractors.pdf_extractor import extract_text_from_pdf
from src.extractors.preprocessor import segment_clauses
from src.classifiers.clause_classifier import get_clause_classifier
from src.risk.fuzzy_logic import assess_contract_risk
from src.storage.document_store import get_document_store
from src.services.retrieval_service import get_retrieval_service
from src.services.summary_service import get_summary_service
from src.services.missing_clause_service import get_missing_clause_service
from src.services.analytics_service import get_analytics_service
from src.services.report_service import get_report_service
from src.services.dialogflow_service import get_dialogflow_service

logger = logging.getLogger(__name__)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle for the FastAPI application."""
    # ── Startup ──
    logger.info("Starting up AI Legal Document Assistant Service")
    # Pre-train the classifier on startup
    get_clause_classifier()
    # Document store starts empty; users upload their own documents
    yield
    # ── Shutdown ──
    logger.info("Shutting down AI Service")


app = FastAPI(title="AI Legal Document Assistant", lifespan=lifespan)

# Serve static assets (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_login():
    """Serve the login page."""
    return FileResponse(os.path.join(STATIC_DIR, "login.html"))

@app.get("/app")
async def serve_frontend():
    """Serve the main HTML frontend."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/health")
async def health_check():
    return {
        "status": "AI Service Running",
        "environment": settings.ENV,
    }

@app.post("/api/v1/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    user_email: Optional[str] = Form(None),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """
    Full end-to-end analysis pipeline:
    PDF Upload → Text Extraction → Preprocessing → Clause Segmentation
    → AI Classification → Fuzzy Logic Risk Assessment → Final Result
    """
    resolved_user_email = (user_email or x_user_email or "").strip().lower() or None
    # ── Step 1: Validate Upload ──
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file provided.")
            
        # ── Step 2: Extract Text (PyMuPDF) ──
        result = extract_text_from_pdf(contents)
        if not result["success"]:
            raise HTTPException(status_code=422, detail=result["error"])
            
        full_text = result.get("text", "")
        metadata = result.get("metadata", {})
        
        # ── Step 3 & 4: Preprocess + Segment Clauses (spaCy / NLTK) ──
        clauses = segment_clauses(full_text)
        
        # ── Step 5 & 6: Classify (Naive Bayes) + Risk Assessment (Fuzzy Logic) ──
        classifier = get_clause_classifier()
        analyzed_clauses = []
        
        for clause in clauses:
            # Naive Bayes classification
            category, confidence = classifier.predict(clause["text"], clause["clean_text"])
            
            # Fuzzy logic risk assessment
            risk_result = assess_contract_risk(clause["text"], category)
            
            analyzed_clauses.append({
                "clause_id": clause["clause_id"],
                "original_text": clause["text"],
                "predicted_category": category,
                "classification_confidence": round(confidence, 4),
                "fuzzy_inputs": risk_result["fuzzy_inputs"],
                "risk_score": risk_result["risk_score"],
                "risk_level": risk_result["risk_level"],
            })
        
        # ── Step 7: Overall Document Risk Score ──
        doc_risk = _calculate_document_risk(analyzed_clauses)

        # ── Step 8: Extractive Contract Summary ──
        summary_service = get_summary_service()
        contract_summary = summary_service.extract_summary(analyzed_clauses)

        # ── Step 9: Missing Clause Detection ──
        missing_service = get_missing_clause_service()
        missing_clauses = missing_service.detect_missing_clauses(analyzed_clauses)

        # ── Step 10: Save to Document Store ──
        store = get_document_store()
        doc_id = store.save_document({
            "filename": file.filename,
            "user_email": resolved_user_email,
            "metadata": metadata,
            "raw_text": full_text,
            "total_clauses": len(analyzed_clauses),
            "clauses": analyzed_clauses,
            "document_risk": doc_risk,
            "summary": contract_summary,
            "missing_clauses": missing_clauses,
        })
            
        return JSONResponse(content={
            "document_id": doc_id,
            "filename": file.filename,
            "metadata": metadata,
            "total_clauses": len(analyzed_clauses),
            "clauses": analyzed_clauses,
            "document_risk": doc_risk,
            "summary": contract_summary,
            "missing_clauses": missing_clauses,
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Failed to process upload")
        raise HTTPException(status_code=500, detail="An error occurred while processing the PDF file.")


def _calculate_document_risk(clauses: list) -> dict:
    """
    Calculates an overall document risk score from clause-level results.
    Uses a weighted average where clause importance acts as the weight,
    so higher-importance clauses influence the total score more.
    """
    if not clauses:
        return {"overall_score": 0.0, "overall_level": "LOW", "category_breakdown": {}}
    
    # Weighted average: weight = fuzzy importance input for each clause
    total_weight = 0.0
    weighted_sum = 0.0
    category_counts = {}
    
    for c in clauses:
        weight = c["fuzzy_inputs"]["importance"]
        weighted_sum += c["risk_score"] * weight
        total_weight += weight
        
        cat = c["predicted_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    overall_score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
    
    if overall_score >= 65:
        overall_level = "HIGH"
    elif overall_score >= 35:
        overall_level = "MEDIUM"
    else:
        overall_level = "LOW"
    
    return {
        "overall_score": overall_score,
        "overall_level": overall_level,
        "category_breakdown": category_counts,
    }






class SearchRequest(BaseModel):
    question: str


@app.post("/api/v1/documents/{document_id}/search")
async def search_document(document_id: str, request: SearchRequest):
    """
    Search document clauses using TF-IDF + Cosine Similarity retrieval.
    Extracts the most relevant clause and deterministic answer sentence.
    """
    retrieval_service = get_retrieval_service()
    result = retrieval_service.search_document(document_id, request.question)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return JSONResponse(content=result)


@app.get("/api/v1/documents/{document_id}/search")
async def search_document_get(document_id: str, question: str = ""):
    """
    Search document clauses using TF-IDF + Cosine Similarity retrieval (GET).
    """
    retrieval_service = get_retrieval_service()
    result = retrieval_service.search_document(document_id, question)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return JSONResponse(content=result)


@app.get("/api/v1/documents")
async def list_documents(
    user_email: Optional[str] = None,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """
    List analyzed documents stored in the DocumentStore, optionally filtered by user_email.
    """
    resolved_email = (user_email or x_user_email or "").strip().lower() or None
    store = get_document_store()
    return JSONResponse(content=store.list_documents(user_email=resolved_email))


@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str):
    """
    Retrieve full record of a single analyzed document.
    """
    store = get_document_store()
    doc = store.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found.")
    return JSONResponse(content=doc)


@app.get("/api/v1/documents/{document_id}/summary")
async def get_document_summary(document_id: str):
    """
    Retrieve the deterministic extractive summary for an analyzed document.
    """
    store = get_document_store()
    doc = store.get_document(document_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    summary = doc.get("summary")
    if summary is None:
        summary_service = get_summary_service()
        summary = summary_service.extract_summary(doc.get("clauses", []))
    return JSONResponse(content=summary)


@app.get("/api/v1/documents/{document_id}/missing-clauses")
async def get_document_missing_clauses(document_id: str):
    """
    Retrieve potentially missing clause categories for an analyzed document.
    """
    store = get_document_store()
    doc = store.get_document(document_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    missing_info = doc.get("missing_clauses")
    if missing_info is None:
        missing_service = get_missing_clause_service()
        missing_info = missing_service.detect_missing_clauses(doc.get("clauses", []))
    return JSONResponse(content=missing_info)


@app.get("/api/v1/documents/{document_id}/analytics")
async def get_document_analytics(document_id: str):
    """
    Retrieve document-level analytics for an analyzed document.
    """
    analytics_service = get_analytics_service()
    analytics = analytics_service.get_document_analytics(document_id)
    if analytics is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    return JSONResponse(content=analytics)


@app.get("/api/v1/analytics")
async def get_system_analytics(
    user_email: Optional[str] = None,
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
):
    """
    Retrieve system-wide analytics across analyzed documents for the given user.
    """
    resolved_email = (user_email or x_user_email or "").strip().lower() or None
    analytics_service = get_analytics_service()
    system_analytics = analytics_service.get_system_analytics(user_email=resolved_email)
    return JSONResponse(content=system_analytics)


@app.get("/api/v1/documents/{document_id}/report")
async def download_document_report(document_id: str):
    """
    Download the deterministic PDF analysis report for an analyzed document.
    """
    report_service = get_report_service()
    result = report_service.generate_report_bytes(document_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID '{document_id}' not found.",
        )
    pdf_bytes, filename = result
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/v1/dialogflow/webhook")
async def dialogflow_webhook(request_body: dict):
    """
    Dialogflow fulfillment webhook endpoint.
    Accepts both Dialogflow ES format and direct JSON:
      - Dialogflow ES: {"queryResult": {"queryText": "...", "parameters": {"document_id": "..."}}}
      - Direct JSON:   {"question": "...", "document_id": "..."}
    Falls back to the most recently analyzed document if document_id is omitted.
    """
    dialogflow_service = get_dialogflow_service()
    result = dialogflow_service.process_webhook(request_body)
    return JSONResponse(content=result)
