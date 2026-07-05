"""
zenith_counsel.py — ZenithCounsel Agent Router
The Mental Health & Cognitive Reframing Agent of the ATLAS Operating System.

Blueprint: Stateful emotional ballast and cognitive framing assistant using CBT frameworks.
Key innovation: Linguistic Sentiment Mapping + hard-coded crisis response protocol.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Hard-coded crisis keywords that MUST trigger immediate safety response
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "self-harm", "cutting", "want to die",
    "no reason to live", "better off dead", "hurt myself", "overdose"
]

CRISIS_RESPONSE = """
⚠️ **IMMEDIATE SUPPORT AVAILABLE** ⚠️

I've detected that you may be going through something very difficult. You are not alone.

**Emergency Resources:**
- 🆘 **iCall (India)**: 9152987821
- 🆘 **Vandrevala Foundation**: 1860-2662-345 (24/7)
- 🆘 **AASRA**: 9820466627
- 🆘 **International Crisis Lines**: https://www.findahelpline.com

Please reach out to a mental health professional or a trusted person in your life.
I'm here to support you, but these professionals are trained to help.

Would you like to talk about what you're feeling right now?
"""


class MentalHealthRequest(BaseModel):
    user_id: str = "user_sricharan_default"
    prompt: str
    session_context: Optional[str] = None  # Optional prior conversation context


@router.post("/counsel", summary="Mental health support and cognitive reframing session")
async def counsel_endpoint(request: MentalHealthRequest):
    """
    Routes mental health queries through ZenithCounsel's CBT-based agent.
    Includes hard-coded crisis detection with immediate emergency response.
    """
    # Hard-coded crisis check — runs BEFORE any LLM processing
    prompt_lower = request.prompt.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in prompt_lower:
            return {
                "model_used": "safety-override",
                "provider": "ATLAS Safety Protocol",
                "latency_ms": 0.0,
                "response": CRISIS_RESPONSE,
                "is_safe": True,
                "crisis_detected": True
            }

    try:
        from router_engine import route_query
        from agents.factory import build_full_prompt
        from scaar_engine import ReconciliationEngine, RAGSearchRequest, DocumentOceanEngine
        from main import ChatRequest, auto_ingest_user_memory

        user_id = request.user_id
        auto_ingest_user_memory(user_id, request.prompt)

        fact_header = ReconciliationEngine.format_memory_header(user_id)
        doc_chunks = DocumentOceanEngine.search_vectors(
            RAGSearchRequest(user_id=user_id, query=request.prompt, top_k=2)
        )
        doc_context = "\n".join([f"- [DOC: {c.title}] {c.chunk_text}" for c in doc_chunks]) if doc_chunks else ""
        memory_context = f"{fact_header}\n{doc_context}".strip() or "No historical emotional data recorded yet."

        augmented_prompt = request.prompt
        if request.session_context:
            augmented_prompt = f"[SESSION CONTEXT]: {request.session_context}\n\n{request.prompt}"

        full_prompt = build_full_prompt("zenith_counsel", memory_context, augmented_prompt)
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=False,
            is_complex_artifact=False,
            user_id=user_id
        )
        result = await route_query(router_request, target_model="llama-3.3-70b-versatile", target_provider="Groq")
        result["crisis_detected"] = False
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
