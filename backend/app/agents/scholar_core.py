from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import urllib.request
import urllib.error

router = APIRouter()

SYSTEM_PROMPT = """You are ScholarCore, the elite Academic Mastery and Learning Synthesis Agent within the ATLAS Operating System.
Your mission is to curate structured learning experiences, break complex topics into intuitive step-by-step analogies, generate Anki-compatible flashcards, and map conceptual relationships between documents.
You must wrap all operational outputs inside the strict `<atlas_artifact>` system layout as requested.
Do NOT output anything else outside the <atlas_artifact> tags."""

class FeynmanRequest(BaseModel):
    concept: str
    depth: str = "intermediate"

class FlashcardRequest(BaseModel):
    knowledge_nodes: str

class ConceptMapRequest(BaseModel):
    documents: str

def get_groq_key():
    for i in range(1, 8):
        k = os.environ.get(f"GROQ_API_KEY_{i}")
        if k: return k
    return None

def execute_llm(prompt: str) -> str:
    key = get_groq_key()
    if not key:
        raise HTTPException(status_code=500, detail="No Groq API keys configured.")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "ATLAS-OS/1.0"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.3
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Execution Error: {e}")

@router.post("/feynman-synthesizer")
def feynman_synthesizer(req: FeynmanRequest):
    prompt = f"Break down the concept '{req.concept}' at a '{req.depth}' level using simple intuitive analogies and step-wise explanations.\nWrap your output in <atlas_artifact type=\"markdown\" title=\"Concept_Synthesis\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/flashcard-generator")
def flashcard_generator(req: FlashcardRequest):
    prompt = f"Generate a set of high-yield Anki-compatible flashcards (Front/Back) from these knowledge nodes: {req.knowledge_nodes}.\nWrap your output in <atlas_artifact type=\"table\" title=\"Flashcard_Deck\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/concept-mapper")
def concept_mapper(req: ConceptMapRequest):
    prompt = f"Build a conceptual relationship graph and topic mapping between the core ideas in these documents:\n{req.documents}\nWrap your output in <atlas_artifact type=\"markdown\" title=\"Concept_Relationship_Map\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}
