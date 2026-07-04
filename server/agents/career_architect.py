from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import urllib.request
import urllib.error

router = APIRouter()

SYSTEM_PROMPT = """You are CareerArchitect, the elite full-lifecycle Career Strategy and Market Intelligence Agent within the ATLAS Operating System.
Your mission is to map user competencies, optimize application materials for applicant tracking systems (ATS), engineer targeted professional roadmaps, and execute high-fidelity behavioral/technical interview simulations.
You must wrap all operational outputs inside the strict `<atlas_artifact>` system layout as requested.
Do NOT output anything else outside the <atlas_artifact> tags."""

class RoleAnalyzerRequest(BaseModel):
    job_url: str

class ResumeGapRequest(BaseModel):
    resume_data: str
    job_requirements: str

class ATSTailorRequest(BaseModel):
    job_description: str
    resume: str

class RoadmapRequest(BaseModel):
    target_role: str
    current_skills: str

class SchedulerRequest(BaseModel):
    application_goals: str

class MarketIntelRequest(BaseModel):
    role_name: str

class AdversarialRequest(BaseModel):
    target_role: str
    context: str

def get_groq_key():
    # Attempt to grab one of the available Groq keys
    for i in range(1, 8):
        k = os.environ.get(f"GROQ_API_KEY_{i}")
        if k: return k
    return None

def execute_llm(prompt: str) -> str:
    # We use Groq (Llama 3.3 70B) for ultra-fast artifact generation during demo
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

@router.post("/analyze-role")
def target_role_analyzer(req: RoleAnalyzerRequest):
    prompt = f"Analyze the following job URL or description and extract key requirements, tools, and traits needed.\nJob: {req.job_url}\nWrap your output in <atlas_artifact type=\"markdown\" title=\"Job_Analysis\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/resume-gap")
def resume_gap_assessor(req: ResumeGapRequest):
    prompt = f"Assess the gaps between this resume and the job requirements.\nResume: {req.resume_data}\nJob Requirements: {req.job_requirements}\nWrap your output in <atlas_artifact type=\"markdown\" title=\"Gap_Analysis\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/ats-tailor")
def ats_resume_tailor(req: ATSTailorRequest):
    prompt = f"Tailor this resume to pass ATS for the given job description. Provide explicit compatibility percentages and missing keywords.\nJob: {req.job_description}\nResume: {req.resume}\nWrap output in <atlas_artifact type=\"markdown\" title=\"ATS_Scorecard\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/roadmap")
def placement_roadmap_generator(req: RoadmapRequest):
    prompt = f"Create a 30/60/90-day placement roadmap to bridge the skills needed for {req.target_role} given current skills: {req.current_skills}.\nOutput MUST be wrapped in <atlas_artifact type=\"table\" title=\"Placement_Roadmap\">...</atlas_artifact>. Do not include markdown tables, strictly use HTML tables if needed, or follow the ATLAS format."
    return {"result": execute_llm(prompt)}

@router.post("/schedule")
def strategic_scheduler(req: SchedulerRequest):
    prompt = f"Create a structured application timeline for these goals: {req.application_goals}.\nWrap output in <atlas_artifact type=\"table\" title=\"Application_Timeline\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/market-intel")
def job_market_intelligence(req: MarketIntelRequest):
    prompt = f"Provide salary benchmarks, market trends, and growth trajectory for: {req.role_name}.\nWrap output in <atlas_artifact type=\"markdown\" title=\"Market_Intelligence\">...</atlas_artifact>"
    return {"result": execute_llm(prompt)}

@router.post("/adversarial-interview")
def adversarial_interviewer(req: AdversarialRequest):
    prompt = f"Enter ADVERSARIAL MODE. Act as a ruthless, hyper-critical technical recruiter for {req.target_role}. The user's context is: {req.context}. Ask a brutal technical question and provide your hyper-critical feedback on their context.\nWrap your output in <atlas_artifact type=\"json\" title=\"Interview_Performance_Report\">...</atlas_artifact> containing fields for question, critique, and severity."
    return {"result": execute_llm(prompt)}
