"""
velocity_form.py — VelocityForm Agent Router
The Fitness & Physiological Optimization Agent of the ATLAS Operating System.

Blueprint: Stateful physiological optimization engineer with adaptive autoregulation.
Key innovation: Dynamically adjusts workouts based on fatigue signals (RPE, HRV, readiness score).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import urllib.request

router = APIRouter()


class FitnessQueryRequest(BaseModel):
    user_id: str = "user_sricharan_default"
    prompt: str
    rpe: Optional[float] = None              # Rate of Perceived Exertion (1-10)
    readiness_score: Optional[float] = None  # Readiness/HRV score (0-100)
    body_weight_kg: Optional[float] = None
    target_goals: Optional[str] = None       # e.g. "hypertrophy, fat loss"


class MacroRequest(BaseModel):
    user_id: str = "user_sricharan_default"
    target_goals: str       # e.g. "muscle gain", "fat loss", "maintenance"
    body_weight_kg: float
    activity_level: str = "moderate"  # sedentary, light, moderate, active, very_active


@router.post("/analyze", summary="Analyze workout and generate adaptive training plan")
async def analyze_fitness_endpoint(request: FitnessQueryRequest):
    """
    Routes fitness query through SCAAR memory + VelocityForm agent system prompt.
    Applies autoregulation if RPE or readiness score provided.
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
        memory_context = f"{fact_header}\n{doc_context}".strip() or "No historical fitness data recorded yet."

        # Augment the prompt with biometric context if provided
        augmented_prompt = request.prompt
        if request.rpe is not None:
            augmented_prompt += f"\n\n[BIOMETRIC_CONTEXT]: Current RPE: {request.rpe}/10"
        if request.readiness_score is not None:
            augmented_prompt += f" | Readiness Score: {request.readiness_score}/100"
        if request.body_weight_kg is not None:
            augmented_prompt += f" | Body Weight: {request.body_weight_kg}kg"
        if request.target_goals:
            augmented_prompt += f" | Goals: {request.target_goals}"

        full_prompt = build_full_prompt("velocity_form", memory_context, augmented_prompt)
        router_request = ChatRequest(
            prompt=full_prompt,
            has_image=False,
            is_complex_artifact=True,
            user_id=user_id
        )
        result = await route_query(router_request, target_model="llama-3.3-70b-versatile", target_provider="Groq")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/macros", summary="Calculate personalized macro-nutrient targets")
async def calculate_macros_endpoint(request: MacroRequest):
    """
    Uses the macro_nutrient_tailor tool to calculate TDEE-based macros
    adjusted for target goals and body metrics.
    """
    # Activity multipliers (Mifflin-St Jeor derived)
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }

    # Estimate BMR using a general formula (assumes average height/age)
    bmr = 10 * request.body_weight_kg + 6.25 * 170 - 5 * 25 + 5  # rough estimate
    tdee = bmr * multipliers.get(request.activity_level, 1.55)

    goal_lower = request.target_goals.lower()
    if "gain" in goal_lower or "bulk" in goal_lower or "hypertrophy" in goal_lower:
        calories = round(tdee + 300)
        protein_g = round(request.body_weight_kg * 2.2)
        fat_g = round(calories * 0.25 / 9)
        carb_g = round((calories - protein_g * 4 - fat_g * 9) / 4)
        phase = "Lean Bulk"
    elif "loss" in goal_lower or "cut" in goal_lower or "deficit" in goal_lower:
        calories = round(tdee - 400)
        protein_g = round(request.body_weight_kg * 2.4)
        fat_g = round(calories * 0.25 / 9)
        carb_g = round((calories - protein_g * 4 - fat_g * 9) / 4)
        phase = "Fat Loss"
    else:
        calories = round(tdee)
        protein_g = round(request.body_weight_kg * 2.0)
        fat_g = round(calories * 0.30 / 9)
        carb_g = round((calories - protein_g * 4 - fat_g * 9) / 4)
        phase = "Maintenance / Recomposition"

    return {
        "phase": phase,
        "target_calories": calories,
        "macros": {
            "protein_g": protein_g,
            "carbohydrates_g": carb_g,
            "fats_g": fat_g
        },
        "notes": [
            f"Protein: {protein_g}g ({round(protein_g*4)} kcal)",
            f"Carbs: {carb_g}g ({round(carb_g*4)} kcal)",
            f"Fats: {fat_g}g ({round(fat_g*9)} kcal)",
            f"Total: {calories} kcal/day",
            "Adjust by ±100 kcal after 2 weeks based on body composition response."
        ]
    }

class OverloadRequest(BaseModel):
    rpe: float
    load_history_json: str

class AutoregRequest(BaseModel):
    readiness_score: float
    fatigue_indicators: str

def get_groq_key_vf():
    for i in range(1, 8):
        k = os.environ.get(f"GROQ_API_KEY_{i}")
        if k: return k
    return None

def execute_llm_vf(prompt: str) -> str:
    key = get_groq_key_vf()
    if not key:
        raise HTTPException(status_code=500, detail="No Groq API keys configured.")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "ATLAS-OS/1.0"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are VelocityForm, an elite fitness and physiological optimization engineer. Wrap all structured outputs in <atlas_artifact> tags."},
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

@router.post("/progressive-overload")
def progressive_overload_calculator(req: OverloadRequest):
    prompt = f"Calculate the optimal weight/volume progression for the next workout based on current RPE ({req.rpe}/10) and load history:\n{req.load_history_json}\nWrap output in <atlas_artifact type=\"table\" title=\"Volume_Overload_Trajectory\">...</atlas_artifact>"
    return {"result": execute_llm_vf(prompt)}

@router.post("/autoregulation")
def autoregulation_engine(req: AutoregRequest):
    prompt = f"Evaluate current readiness score ({req.readiness_score}/100) and fatigue indicators ({req.fatigue_indicators}). Apply autoregulation principles to dynamically adjust training volume and intensity to prevent overtraining.\nWrap output in <atlas_artifact type=\"markdown\" title=\"Autoregulated_Workout_Prescription\">...</atlas_artifact>"
    return {"result": execute_llm_vf(prompt)}

