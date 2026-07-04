from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Initialize FastAPI
app = FastAPI(title="ATLAS Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    has_image: bool = False
    is_complex_artifact: bool = False
    user_id: str = "user_sricharan_default"

class AgentChatRequest(BaseModel):
    agent_id: str = "scholar_core"
    prompt: str
    has_image: bool = False
    is_complex_artifact: bool = False
    user_id: str = "user_sricharan_default"
    
class ChatResponse(BaseModel):
    model_used: str
    provider: str
    latency_ms: float
    response: str
    is_safe: bool = True

@app.get("/")
def read_root():
    return {"message": "Welcome to ATLAS API"}

# Import Agent Routers
from agents.career_architect import router as career_architect_router
from agents.fiscal_sentinel import router as fiscal_sentinel_router
from agents.biometrics_pilot import router as biometrics_pilot_router
from voice_service import router as voice_router
from auth_service import router as auth_router
from rag_router import router as rag_router

app.include_router(career_architect_router, prefix="/api/career", tags=["CareerArchitect"])
app.include_router(fiscal_sentinel_router, prefix="/api/fiscal", tags=["FiscalSentinel"])
app.include_router(biometrics_pilot_router, prefix="/api/biometrics", tags=["BiometricsPilot"])
app.include_router(voice_router, prefix="/api/tts", tags=["Voice & TTS"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth & Identity"])
app.include_router(rag_router, prefix="/api/memory", tags=["SCAAR Memory & RAG"])



@app.get("/models")
def get_models():
    """Return available models in the roster"""
    return {
        "models": [
            {"id": "groq-llama-3-3", "name": "Groq Llama 3.3 70B", "provider": "Groq", "purpose": "Default chat, UI scripting"},
            {"id": "sambanova-deepseek-r1", "name": "DeepSeek R1", "provider": "SambaNova", "purpose": "Complex code, reasoning"},
            {"id": "sambanova-llama-4-maverick", "name": "Llama-4-Maverick", "provider": "SambaNova", "purpose": "Long context, multi-document"},
            {"id": "cerebras-qwen", "name": "Qwen 3-235B", "provider": "Cerebras", "purpose": "High-throughput batch"},
            {"id": "gemini-1-5-pro", "name": "Gemini 1.5 Pro", "provider": "Google AI Studio", "purpose": "Complex artifacts"},
            {"id": "nvidia-nim-vision", "name": "Vision Models", "provider": "NVIDIA NIM", "purpose": "Vision tasks"}
        ]
    }

# We will import the router engine later once it is created
# from router_engine import route_query

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat queries using the Intelligent Brain Auto-Router.
    """
    try:
        from router_engine import route_query
        result = await route_query(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/chat", response_model=ChatResponse)
async def agent_chat_endpoint(request: AgentChatRequest):
    """
    Handle agent chat queries with "First Interaction" Logic using the Agent Factory.
    """
    try:
        from router_engine import route_query
        from agents.factory import build_full_prompt
        from scaar_engine import ReconciliationEngine, DocumentOceanEngine, RAGSearchRequest, DeterministicGateway, DeterministicValidationRequest
        
        # 1. SCAAR RAG Layer: Dynamically retrieve reconciled atomic facts from The Fact Brain
        user_id = getattr(request, "user_id", "user_sricharan_default")
        fact_header = ReconciliationEngine.format_memory_header(user_id)
        
        # Also perform cosine similarity search across vectorized textbooks & study guides in The Document Ocean
        doc_chunks = DocumentOceanEngine.search_vectors(RAGSearchRequest(user_id=user_id, query=request.prompt, top_k=2))
        doc_context = "\n".join([f"- [DOC: {c.title}] {c.chunk_text}" for c in doc_chunks]) if doc_chunks else ""
        
        memory_context = f"{fact_header}\n{doc_context}".strip()
        if not memory_context:
            memory_context = "No historical facts or document chunks found."
        
        # 2. Prompt Builder: Grab agent prompt and inject facts and user input
        full_prompt = build_full_prompt(request.agent_id, memory_context, request.prompt)
        
        # Create a ChatRequest for the router with the newly built full prompt
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=request.has_image,
            is_complex_artifact=request.is_complex_artifact,
            user_id=user_id
        )
        
        # 3. Router: Send to SambaNova (Llama-4-Maverick) as requested
        result = await route_query(
            router_request, 
            target_model="sambanova-llama-4-maverick", 
            target_provider="SambaNova"
        )
        
        # 4. Output & Deterministic Gateway Validation:
        # We wrap the response and pass it through the Deterministic Gateway for zero-hallucination verification
        simulated_llm_output = (
            f"<atlas_artifact type=\"markdown\">\n"
            f"# {request.agent_id.replace('_', ' ').title()} Response\n\n"
            f"Here is a step-by-step breakdown based on your active SCAAR memory context:\n{memory_context}\n\n"
            f"**Your Request:** {request.prompt}\n\n"
            f"Shall I proceed to step two?\n"
            f"</atlas_artifact>\n\n"
            f"*(Debug: {result['response']})*"
        )
        
        gateway_res = DeterministicGateway.validate_and_correct(
            DeterministicValidationRequest(output_text=simulated_llm_output, expected_schema="markdown", user_id=user_id)
        )
        result["response"] = gateway_res["validated_output"]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
