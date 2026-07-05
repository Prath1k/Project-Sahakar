"""
rag_router.py — FastAPI Router for SCAAR Memory Engine & RAG Endpoints

Exposes REST API endpoints for:
  - Adding and reconciling atomic facts (The Fact Brain)
  - Retrieving active memory context headers
  - Ingesting and chunking documents (The Document Ocean)
  - Ingesting large PDFs with per-page chunking and page-number pinpointing
  - Performing vector similarity searches with source location metadata
  - Running Deterministic Gateway validation
  - Executing cryptographic database wipes
"""

import io
import math
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from scaar_engine import (
    ReconciliationEngine,
    DocumentOceanEngine,
    DeterministicGateway,
    wipe_all_scaar_databases,
    AtomicFact,
    DocumentChunk,
    FactAddRequest,
    DocumentIngestRequest,
    RAGSearchRequest,
    DeterministicValidationRequest
)

router = APIRouter()


@router.get("/documents", summary="List all indexed documents in the RAG Document Ocean")
async def list_documents_endpoint(
    user_id: str = Query("user_sricharan_default", description="User ID")
):
    """
    Returns all documents currently indexed in ChromaDB for this user.
    Works even after container restarts because ChromaDB is on persistent /data volume.
    Shows document title, page count, chunk count, and ingest timestamp.
    """
    try:
        docs = DocumentOceanEngine.list_documents(user_id)
        return {
            "user_id": user_id,
            "document_count": len(docs),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")


@router.post("/fact", summary="Add or reconcile an atomic fact in The Fact Brain")
async def add_fact_endpoint(request: FactAddRequest):
    """
    Adds a new fact to Supabase/SQLite Fact Brain. Automatically triggers
    The Reconciliation Engine to detect contradictions and archive outdated facts.
    """
    try:
        fact, note = ReconciliationEngine.add_fact_with_reconciliation(request)
        return {
            "status": "SUCCESS",
            "fact": fact,
            "reconciliation_note": note
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact reconciliation error: {str(e)}")


@router.get("/facts", response_model=List[AtomicFact], summary="Get active reconciled facts for user")
async def get_facts_endpoint(
    user_id: str = Query("user_sricharan_default", description="User ID to retrieve facts for"),
    category: Optional[str] = Query(None, description="Optional category filter (location, study, finance, health)")
):
    """Retrieves all active, reconciled atomic facts for the specified user."""
    return ReconciliationEngine.get_active_facts(user_id, category)


@router.get("/context-header", summary="Get formatted [ACTIVE_MEMORY_CONTEXT] header")
async def get_context_header_endpoint(
    user_id: str = Query("user_sricharan_default", description="User ID")
):
    """Returns the clean, reconciled memory header ready for LLM prompt injection."""
    header = ReconciliationEngine.format_memory_header(user_id)
    return {
        "user_id": user_id,
        "active_memory_context": header
    }


@router.post("/ingest", summary="Ingest document or textbook into The Document Ocean")
async def ingest_document_endpoint(request: DocumentIngestRequest):
    """
    Chunks document content, computes high-dimensional vector embeddings,
    and indexes them in ChromaDB Document Ocean.
    """
    try:
        return DocumentOceanEngine.ingest_document(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document vectorization error: {str(e)}")


@router.post("/ingest-pdf", summary="Upload a PDF and ingest it page-by-page with semantic chunking")
async def ingest_pdf_endpoint(
    file: UploadFile = File(..., description="PDF file to ingest"),
    user_id: str = Form("user_sricharan_default"),
    title: str = Form(None)
):
    """
    Parses a PDF file page by page, splits each page into 500-token overlapping chunks,
    stores each chunk in ChromaDB with page_number + chunk_index metadata for
    precise semantic pinpointing when retrieving results.

    Supports PDFs up to 300+ pages.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise HTTPException(status_code=500, detail="pypdf is not installed. Run: pip install pypdf")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for this endpoint.")

    content = await file.read()
    doc_title = title or file.filename

    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse PDF: {str(e)}")

    total_chunks = 0
    total_pages = len(reader.pages)
    CHUNK_SIZE = 500     # characters per chunk
    CHUNK_OVERLAP = 80   # overlap between adjacent chunks

    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        if not page_text:
            continue  # skip empty/image-only pages

        # Split page text into overlapping chunks
        chunks = []
        start = 0
        while start < len(page_text):
            end = start + CHUNK_SIZE
            chunk = page_text[start:end]
            chunks.append(chunk)
            start += CHUNK_SIZE - CHUNK_OVERLAP
            if start >= len(page_text):
                break

        for chunk_idx, chunk_text in enumerate(chunks):
            ingest_req = DocumentIngestRequest(
                user_id=user_id,
                title=f"{doc_title} | Page {page_num} | Chunk {chunk_idx + 1}",
                text_content=chunk_text,
                category="pdf_document",
                source_page=page_num,
                chunk_index=chunk_idx
            )
            DocumentOceanEngine.ingest_document(ingest_req)
            total_chunks += 1

    return {
        "status": "SUCCESS",
        "document": doc_title,
        "total_pages": total_pages,
        "total_chunks_indexed": total_chunks,
        "message": f"Successfully indexed {total_chunks} semantic chunks from {total_pages} pages. The RAG engine can now pinpoint answers to the exact page and chunk location."
    }


@router.post("/search", summary="Semantic search across Document Ocean with page-level source pinpointing")
async def search_vectors_endpoint(request: RAGSearchRequest):
    """
    Performs cosine similarity search across vectorized document chunks.
    Returns results with page_number and chunk_index for precise source pinpointing.
    """
    try:
        results = DocumentOceanEngine.search_vectors(request)
        # Enrich results with source location metadata parsed from title
        enriched = []
        for chunk in results:
            enriched.append({
                "chunk_id": chunk.chunk_id,
                "title": chunk.title,
                "chunk_text": chunk.chunk_text,
                "category": chunk.category,
                "similarity_score": getattr(chunk, "similarity_score", None),
                "source_location": chunk.title  # title contains "Doc | Page X | Chunk Y"
            })
        return enriched
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search error: {str(e)}")


@router.post("/validate", summary="Run output through Deterministic Gateway")
async def validate_output_endpoint(request: DeterministicValidationRequest):
    """
    Validates LLM output formatting and self-corrects hallucinations or contradictions
    against known active facts.
    """
    return DeterministicGateway.validate_and_correct(request)


@router.delete("/wipe", summary="Granular deletion or full cryptographic database wipe")
async def wipe_database_endpoint(
    user_id: Optional[str] = Query(None, description="Optional user ID for granular wipe. If omitted, performs full cryptographic wipe.")
):
    """
    Executes line 401 of Project Sahakar blueprint: Granular deletion OR full cryptographic wipe.
    """
    return wipe_all_scaar_databases(user_id)
