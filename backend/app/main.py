from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional
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
    image_base64: Optional[str] = None
    override_model: Optional[str] = None

class AgentChatRequest(BaseModel):
    agent_id: str = "scholar_core"
    prompt: str
    has_image: bool = False
    is_complex_artifact: bool = False
    
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
from app.agents.career_architect import router as career_architect_router
from app.agents.fiscal_sentinel import router as fiscal_sentinel_router
from app.agents.biometrics_pilot import router as biometrics_pilot_router
from app.voice_service import router as voice_router

app.include_router(career_architect_router, prefix="/api/career", tags=["CareerArchitect"])
app.include_router(fiscal_sentinel_router, prefix="/api/fiscal", tags=["FiscalSentinel"])
app.include_router(biometrics_pilot_router, prefix="/api/biometrics", tags=["BiometricsPilot"])
app.include_router(voice_router, prefix="/api/tts", tags=["Voice & TTS"])



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
        from app.router_engine import route_query
        
        target_model = None
        target_provider = None
        mo = getattr(request, 'override_model', None)
        if mo == "Groq":
            target_model = "llama-3.3-70b-versatile"
            target_provider = "Groq"
        elif mo == "SambaNova":
            target_model = "Meta-Llama-3.1-405B-Instruct"
            target_provider = "SambaNova"
        elif mo == "Nvidia":
            target_model = "meta/llama-3.2-90b-vision-instruct"
            target_provider = "NVIDIA NIM"
        elif mo == "Cerebras":
            target_model = "llama3.1-8b"
            target_provider = "Cerebras"
            
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
        from app.router_engine import route_query
        from app.agents.factory import build_full_prompt
        
        # 1. RAG Layer: Mock querying Supabase for facts
        memory_context = "User is currently studying Networking 101. Exam is in 2 weeks."
        
        # 2. Prompt Builder: Grab agent prompt and inject facts and user input
        full_prompt = build_full_prompt(request.agent_id, memory_context, request.prompt)
        
        # Create a ChatRequest for the router with the newly built full prompt
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=request.has_image,
            is_complex_artifact=request.is_complex_artifact
        )
        
        # 3. Router: Send to SambaNova (Llama-4-Maverick) as requested
        result = await route_query(
            router_request, 
            target_model="sambanova-llama-4-maverick", 
            target_provider="SambaNova"
        )
        
        # 4. Output: The router engine returns the REAL LLM response.
        llm_output = result['response']
        
        # Ensure it wraps the output in the <atlas_artifact> block if the LLM forgot
        if "<atlas_artifact" not in llm_output:
            llm_output = f"<atlas_artifact type=\"markdown\">\n{llm_output}\n</atlas_artifact>"
            
        result["response"] = llm_output
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
