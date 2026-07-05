from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import urllib.request
import urllib.error

router = APIRouter()

SYSTEM_PROMPT = """You are BiometricsPilot, the elite Preventative Health and Biometric Synthesis Agent within the ATLAS Operating System.
Your objective is to function as a data-driven health advisor. You analyze physiological strain, sleep architecture, and activity logs to identify hidden cross-domain health correlations.
You do not diagnose medical conditions.
If the user inputs any symptoms of acute distress, severe pain, or medical emergencies, you MUST instantly trigger the symptom_safety_filter. State clearly that you are an analytical AI, not a doctor, and advise immediate professional medical consultation.
Never dump raw numbers or plain text health statistics into the chat interface. All physiological data must be visualized using the ATLAS Artifact layout.
Do NOT output anything else outside the <atlas_artifact> tags."""

class TrendAnalyzerRequest(BaseModel):
    health_json_data: str

class LifestyleCorrelationRequest(BaseModel):
    health_metrics: str
    activity_logs: str

class SymptomSafetyRequest(BaseModel):
    symptom_statement: str

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
        "temperature": 0.2
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Execution Error: {e}")

@router.post("/trend-analyzer")
def biometric_trend_analyzer(req: TrendAnalyzerRequest):
    prompt = f"Analyze the following health metrics and output baseline health optimizations.\nData: {req.health_json_data}\nWrap your output strictly in <atlas_artifact type=\"table\" title=\"Biometric_Optimization_Matrix\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/lifestyle-correlation")
def lifestyle_correlation_engine(req: LifestyleCorrelationRequest):
    prompt = f"Identify hidden cross-domain health correlations between these health metrics and activity logs.\nMetrics: {req.health_metrics}\nActivity: {req.activity_logs}\nForecast the fatigue/strain trajectory and wrap your output strictly in <atlas_artifact type=\"chart\" title=\"Strain_Forecast_Trajectory\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/safety-filter")
def symptom_safety_filter(req: SymptomSafetyRequest):
    prompt = f"The user has stated the following symptoms: '{req.symptom_statement}'. Determine if this requires an acute distress warning. If so, clearly state you are an analytical AI, not a doctor, and advise immediate professional medical consultation. Output the warning formatted effectively using <atlas_artifact type=\"markdown\" title=\"Clinical_Safety_Protocol\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}
