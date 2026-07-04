"""
rag_router.py — FastAPI Router for SCAAR Memory Engine & RAG Endpoints

Exposes REST API endpoints for:
  - Adding and reconciling atomic facts (The Fact Brain)
  - Retrieving active memory context headers
  - Ingesting and chunking documents (The Document Ocean)
  - Performing vector similarity searches
  - Running Deterministic Gateway validation
  - Executing cryptographic database wipes
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
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
    and indexes them in Pinecone / Qdrant / Local Document Ocean.
    """
    try:
        return DocumentOceanEngine.ingest_document(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document vectorization error: {str(e)}")


@router.post("/search", response_model=List[DocumentChunk], summary="Search Document Ocean vector store")
async def search_vectors_endpoint(request: RAGSearchRequest):
    """
    Performs cosine similarity search across vectorized document chunks
    to retrieve relevant context for queries.
    """
    try:
        return DocumentOceanEngine.search_vectors(request)
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
