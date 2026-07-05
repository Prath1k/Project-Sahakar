from fastapi import FastAPI, HTTPException
# Trigger reload to load new pip dependencies
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

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
    image_base64: Optional[str] = None
    override_model: Optional[str] = None

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
from agents.scholar_core import router as scholar_core_router
from agents.career_architect import router as career_architect_router
from agents.fiscal_sentinel import router as fiscal_sentinel_router
from agents.biometrics_pilot import router as biometrics_pilot_router
from agents.velocity_form import router as velocity_form_router
from agents.zenith_counsel import router as zenith_counsel_router
from agents.nexus_strategist import router as nexus_strategist_router
from image_gen_router import router as image_gen_router
from voice_service import router as voice_router
from stt_service import router as stt_router
from auth_service import router as auth_router
from rag_router import router as rag_router

app.include_router(scholar_core_router, prefix="/api/scholar", tags=["ScholarCore"])
app.include_router(career_architect_router, prefix="/api/career", tags=["CareerArchitect"])
app.include_router(fiscal_sentinel_router, prefix="/api/fiscal", tags=["FiscalSentinel"])
app.include_router(biometrics_pilot_router, prefix="/api/biometrics", tags=["BiometricsPilot"])
app.include_router(velocity_form_router, prefix="/api/fitness", tags=["VelocityForm"])
app.include_router(zenith_counsel_router, prefix="/api/zenith", tags=["ZenithCounsel"])
app.include_router(nexus_strategist_router, prefix="/api/nexus", tags=["NexusStrategist"])
app.include_router(image_gen_router, prefix="/api/image-gen", tags=["Image Generation"])
app.include_router(voice_router, prefix="/api/tts", tags=["Voice & TTS"])
app.include_router(stt_router, prefix="/api/stt", tags=["Speech-To-Text & Ears"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth & Identity"])
app.include_router(rag_router, prefix="/api/memory", tags=["SCAAR Memory & RAG"])





@app.get("/models")
def get_models():
    """Return the live model roster — matches actual routing in router_engine.py"""
    return {
        "models": [
            {"id": "auto", "name": "🌟 Auto Router", "provider": "ATLAS", "purpose": "Intelligent routing to best model", "is_default": True},
            {"id": "groq-llama-3-3", "name": "⚡ Groq Llama 3.3 70B", "provider": "Groq", "purpose": "Default chat, fast responses"},
            {"id": "sambanova-deepseek-r1", "name": "🧠 DeepSeek V3.2", "provider": "SambaNova", "purpose": "Complex reasoning & code"},
            {"id": "sambanova-maverick", "name": "📚 Llama-3.3-70B (SambaNova)", "provider": "SambaNova", "purpose": "Long context, multi-document analysis (128K tokens)"},
            {"id": "cerebras-llama", "name": "🚀 Cerebras Llama 3.3 70B", "provider": "Cerebras", "purpose": "High-speed batch processing"},
            {"id": "gemini-1-5-pro", "name": "✨ Gemini 1.5 Pro", "provider": "Google AI Studio", "purpose": "Complex artifacts, large documents"},
            {"id": "nvidia-nim-vision", "name": "👁️ NVIDIA NIM Vision", "provider": "NVIDIA NIM", "purpose": "Vision tasks, image understanding"},
            {"id": "openrouter-free", "name": "📡 OpenRouter", "provider": "OpenRouter", "purpose": "Multi-model showcase (Gemma, Mistral, Claude)"}
        ]
    }

def auto_ingest_user_memory(user_id: str, prompt: str):
    """
    Automatically detects declarative statements or user facts and ingests them into RAG memory.
    """
    try:
        from scaar_engine import ReconciliationEngine, DocumentOceanEngine, FactAddRequest, DocumentIngestRequest, FACT_DB_PATH
        import sqlite3
        prompt_lower = prompt.lower().strip()
        # Don't ingest simple questions or greetings
        if prompt_lower.startswith(("what ", "why ", "how ", "who ", "where ", "when ", "can you", "could you", "do you", "is there", "are there", "hello", "hi ", "hey")):
            return
            
        # Check if user is asking to forget/delete a fact
        if any(w in prompt_lower for w in ["forget ", "delete ", "remove ", "ignore ", "don't remember", "do not remember"]):
            conn = sqlite3.connect(FACT_DB_PATH)
            cursor = conn.cursor()
            words = [w for w in prompt_lower.replace("forget", "").replace("delete", "").replace("remove", "").replace("that", "").replace("my", "").replace("its", "").replace("it's", "").replace("is", "").replace("today", "").split() if len(w) > 2]
            if words:
                for w in words:
                    cursor.execute("UPDATE atomic_facts SET is_active = 0 WHERE user_id = ? AND LOWER(fact_text) LIKE ?", (user_id, f"%{w}%"))
                conn.commit()
            conn.close()
            print(f"🧠 [RAG Auto-Ingest] Deactivated/forgot facts matching '{words}' for user {user_id}")
            return

        fact_keywords = ["my ", "our ", "we ", "i am", "i'm", "remember", "note that", "is ", "code is", "region", "deploy", "study", "name is", "live in", "budget", "burn rate", "using", "project", "prefer", "favorite", "created", "built"]
        if any(kw in prompt_lower for kw in fact_keywords) and len(prompt) > 10:
            cat = "general"
            if any(w in prompt_lower for w in ["code", "region", "deploy", "server", "project", "using", "built"]):
                cat = "project"
            elif any(w in prompt_lower for w in ["name", "call me", "i am", "my", "prefer"]):
                cat = "personal"
            elif any(w in prompt_lower for w in ["live in", "from", "located"]):
                cat = "location"
            elif any(w in prompt_lower for w in ["study", "exam", "course", "grade"]):
                cat = "study"
            elif any(w in prompt_lower for w in ["burn rate", "budget", "salary", "cost"]):
                cat = "finance"
                
            # Record in SQLite Fact Brain (with contradiction reconciliation)
            ReconciliationEngine.add_fact_with_reconciliation(FactAddRequest(
                user_id=user_id, fact_text=prompt, category=cat, source="chat_auto_ingest"
            ))
            # Record in ChromaDB Document Ocean for semantic similarity search
            DocumentOceanEngine.ingest_document(DocumentIngestRequest(
                user_id=user_id, title=f"User Chat Note ({cat})", text_content=prompt, category=cat
            ))
            print(f"🧠 [RAG Auto-Ingest] Recorded new fact in category '{cat}': '{prompt}'")
    except Exception as e:
        print(f"[RAG Auto-Ingest Error]: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat queries using the Intelligent Brain Auto-Router.
    """
    try:
        from router_engine import route_query
        from scaar_engine import ReconciliationEngine, DocumentOceanEngine, RAGSearchRequest
        
        user_id = getattr(request, "user_id", "user_sricharan_default")
        
        # Auto-ingest new user facts before querying
        auto_ingest_user_memory(user_id, request.prompt)
        
        fact_header = ReconciliationEngine.format_memory_header(user_id)
        
        doc_chunks = DocumentOceanEngine.search_vectors(RAGSearchRequest(user_id=user_id, query=request.prompt, top_k=2))
        doc_context = "\n".join([f"- [DOC: {c.title}] {c.chunk_text}" for c in doc_chunks]) if doc_chunks else ""
        
        memory_context = f"{fact_header}\n{doc_context}".strip()
        
        if memory_context and memory_context != "No historical facts recorded yet.":
            request.prompt = f"""\
You are ATLAS, a helpful and dynamic AI assistant. Respond naturally and helpfully to the user's message. Be concise unless asked for detail. Do not reference any learning technique unless the user specifically asks about studying.

[ACTIVE_MEMORY_CONTEXT]:
{memory_context}

[USER MESSAGE]: {request.prompt}"""
        else:
            request.prompt = f"""You are ATLAS, a helpful and dynamic AI assistant. Respond naturally to the user.

[USER MESSAGE]: {request.prompt}"""
        
        target_model = None
        target_provider = None
        mo = getattr(request, 'override_model', None)
        if mo == "Groq":
            target_model = "llama-3.3-70b-versatile"
            target_provider = "Groq"
        elif mo == "SambaNova" or mo == "DeepSeek":
            target_model = "DeepSeek-V3.2"  # Blueprint: reasoning/code → DeepSeek-V3.2
            target_provider = "SambaNova"
        elif mo == "Maverick" or mo == "LongContext":
            target_model = "Meta-Llama-3.3-70B-Instruct"  # Blueprint: long context
            target_provider = "SambaNova"
        elif mo == "Nvidia":
            target_model = "meta/llama-3.2-11b-vision-instruct"  # Blueprint: NVIDIA NIM vision
            target_provider = "NVIDIA NIM"
        elif mo == "Cerebras":
            target_model = "gpt-oss-120b"  # Updated: active Cerebras flagship model
            target_provider = "Cerebras"
        elif mo == "OpenRouter":
            target_model = "meta-llama/llama-3.3-70b-instruct:free"  # OpenRouter free catalog
            target_provider = "OpenRouter"
        elif mo == "Gemini":
            target_model = "gemini-2.5-flash"
            target_provider = "Google AI Studio"
            
        result = await route_query(request, target_model=target_model, target_provider=target_provider)
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
        
        user_id = getattr(request, "user_id", "user_sricharan_default")
        
        # Auto-ingest new user facts before querying
        auto_ingest_user_memory(user_id, request.prompt)
        
        # 1. SCAAR RAG Layer: Dynamically retrieve reconciled atomic facts from The Fact Brain
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
        
        # 3. Router: Send to Groq (Llama-3.3-70B) for agent queries (fast + free)
        result = await route_query(
            router_request, 
            target_model="llama-3.3-70b-versatile", 
            target_provider="Groq"
        )
        
        # 4. Output: Validate real LLM response through Deterministic Gateway after ensuring wrapper
        llm_output = result['response']
        # Ensure it wraps the output in the <atlas_artifact> block if the LLM forgot
        if "<atlas_artifact" not in llm_output:
            llm_output = f"<atlas_artifact type=\"markdown\">\n{llm_output}\n</atlas_artifact>"
        
        gateway_res = DeterministicGateway.validate_and_correct(
            DeterministicValidationRequest(output_text=llm_output, expected_schema="markdown", user_id=user_id)
        )
        result["response"] = gateway_res.get("validated_output", llm_output)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
