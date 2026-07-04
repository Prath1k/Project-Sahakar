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
    
class ChatResponse(BaseModel):
    model_used: str
    provider: str
    latency_ms: float
    response: str
    is_safe: bool = True

@app.get("/")
def read_root():
    return {"message": "Welcome to ATLAS API"}

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
