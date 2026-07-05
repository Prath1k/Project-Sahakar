"""
nexus_strategist.py — NexusStrategist Agent Router
The High-Density Logistics Optimizer & Constraint-Based Scheduler of ATLAS.

Blueprint: Multi-constraint hyper-routing agent that optimizes around time, location, budget, fatigue.
Key innovation: Spatiotemporal graph mapping + dynamic re-routing on disruption.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import urllib.request

router = APIRouter()


class StrategyRequest(BaseModel):
    user_id: str = "user_sricharan_default"
    prompt: str
    budget_cap: Optional[float] = None          # Budget constraint in USD/INR
    locations: Optional[List[str]] = None       # List of location strings
    time_available_hours: Optional[float] = None  # Total time budget


class ItineraryRequest(BaseModel):
    user_id: str = "user_sricharan_default"
    destination: str
    duration_days: int
    budget_inr: Optional[float] = None
    preferences: Optional[str] = None          # e.g., "adventure, food, culture"
    starting_location: Optional[str] = None


@router.post("/plan", summary="Generate high-density constraint-optimized strategy or schedule")
async def plan_strategy_endpoint(request: StrategyRequest):
    """
    Routes logistics query through NexusStrategist's multi-constraint optimizer.
    Handles travel itineraries, complex schedules, event planning, and task ordering.
    """
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
        memory_context = f"{fact_header}\n{doc_context}".strip() or "No historical planning data recorded yet."

        # Augment prompt with constraint parameters
        augmented_prompt = request.prompt
        if request.budget_cap is not None:
            augmented_prompt += f"\n\n[CONSTRAINTS]: Budget Cap: {request.budget_cap}"
        if request.locations:
            augmented_prompt += f" | Locations: {', '.join(request.locations)}"
        if request.time_available_hours is not None:
            augmented_prompt += f" | Time Available: {request.time_available_hours} hours"

        full_prompt = build_full_prompt("nexus_strategist", memory_context, augmented_prompt)
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=False,
            is_complex_artifact=True,   # Itineraries are complex artifacts
            user_id=user_id
        )
        result = await route_query(router_request, target_model="llama-3.3-70b-versatile", target_provider="Groq")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/itinerary", summary="Generate a full travel itinerary with day-by-day optimization")
async def itinerary_endpoint(request: ItineraryRequest):
    """
    Generates a detailed, constraint-optimized travel itinerary.
    Factors in budget, duration, preferences, and starting location.
    """
    try:
        from router_engine import route_query
        from agents.factory import build_full_prompt
        from scaar_engine import ReconciliationEngine, format_memory_header
        from main import ChatRequest

        itinerary_prompt = f"""Generate a detailed {request.duration_days}-day travel itinerary for {request.destination}.

Constraints:
- Budget: {f'₹{request.budget_inr:,.0f}' if request.budget_inr else 'flexible'}
- Preferences: {request.preferences or 'balanced mix of culture, food, and adventure'}
- Starting from: {request.starting_location or 'to be determined'}

Include:
1. Day-by-day schedule with times
2. Recommended accommodations per budget tier
3. Local food must-tries with estimated costs
4. Transport between locations with time estimates
5. Buffer time for rest/unexpected delays
6. Total estimated cost breakdown"""

        full_prompt = build_full_prompt("nexus_strategist", "No historical travel data.", itinerary_prompt)
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=False,
            is_complex_artifact=True,
            user_id=request.user_id
        )
        result = await route_query(
            router_request,
            target_model="Meta-Llama-3.3-70B-Instruct",  # Long context for itineraries
            target_provider="SambaNova"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RouteRequest(BaseModel):
    locations_list: str
    budget_cap: float

class TemporalRequest(BaseModel):
    calendar_json: str

class BundleRequest(BaseModel):
    itinerary_specs: str

def get_groq_key_ns():
    for i in range(1, 8):
        k = os.environ.get(f"GROQ_API_KEY_{i}")
        if k: return k
    return None

def execute_llm_ns(prompt: str) -> str:
    key = get_groq_key_ns()
    if not key:
        raise HTTPException(status_code=500, detail="No Groq API keys configured.")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "ATLAS-OS/1.0"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are NexusStrategist, an elite high-density logistics optimizer and constraint scheduler. Wrap all structured outputs in <atlas_artifact> tags."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.2
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Execution Error: {e}")

@router.post("/route-optimizer")
def logistic_route_optimizer(req: RouteRequest):
    prompt = f"Optimize the travel route and sequence across these locations: {req.locations_list} under a budget cap of {req.budget_cap}. Minimize transit time and cost.\nWrap output in <atlas_artifact type=\"table\" title=\"Logistic_Route_Optimization\">...</atlas_artifact>"
    return {"result": execute_llm_ns(prompt)}

@router.post("/temporal-gap")
def temporal_gap_analyzer(req: TemporalRequest):
    prompt = f"Analyze this calendar schedule data for temporal gaps, inefficiencies, and fatigue bottlenecks:\n{req.calendar_json}\nWrap output in <atlas_artifact type=\"timeline\" title=\"Temporal_Gap_Analysis\">...</atlas_artifact>"
    return {"result": execute_llm_ns(prompt)}

@router.post("/itinerary-bundle")
def itinerary_bundle_compiler(req: BundleRequest):
    prompt = f"Compile a comprehensive itinerary bundle (accommodations, transit, dining, activities) for these specifications: {req.itinerary_specs}.\nWrap output in <atlas_artifact type=\"markdown\" title=\"Itinerary_Bundle_Compilation\">...</atlas_artifact>"
    return {"result": execute_llm_ns(prompt)}

