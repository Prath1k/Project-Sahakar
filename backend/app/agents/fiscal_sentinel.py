from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import urllib.request
import re
from e2b_code_interpreter import Sandbox

router = APIRouter()

SYSTEM_PROMPT = """You are FiscalSentinel, the elite Financial Defense and Capital Allocation Agent within the ATLAS Operating System.
Your mission is predictive net-worth defense, subscription anomaly detection, and budget optimization. You operate strictly on mathematical verification and data execution.
You must NEVER attempt to manually calculate large datasets, compound interest, or CSV bank ledgers. 
Instead, you must autonomously generate a Python script using pandas/numpy to analyze the data.
OUTPUT REQUIREMENT: Output ONLY valid Python code inside ```python ... ``` blocks. Do not explain the code. Do not include markdown other than the code block."""

class AnomalyRequest(BaseModel):
    ledger_csv: str

class RunwayRequest(BaseModel):
    income: float
    burn_rate: float

class ArbitrageRequest(BaseModel):
    base_currency: str
    target_currency: str

def get_groq_key():
    for i in range(1, 8):
        k = os.environ.get(f"GROQ_API_KEY_{i}")
        if k: return k
    return None

def generate_python_code(prompt: str) -> str:
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
        "temperature": 0.1
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=35) as response:
            res = json.loads(response.read().decode('utf-8'))
            content = res["choices"][0]["message"]["content"]
            # Extract code from markdown block
            match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
            if match:
                return match.group(1)
            # Fallback
            return content.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Execution Error: {e}")

def execute_in_e2b(code: str, artifact_type: str, title: str) -> str:
    e2b_key = os.environ.get("E2B_API_KEY")
    if not e2b_key:
        raise HTTPException(status_code=500, detail="E2B_API_KEY not configured.")
        
    try:
        os.environ["E2B_API_KEY"] = e2b_key
        with Sandbox.create() as sandbox:
            execution = sandbox.run_code(code)
            
            output = ""
            if execution.logs.stdout:
                output += "\n".join(execution.logs.stdout)
            if execution.logs.stderr:
                output += "\nERROR:\n" + "\n".join(execution.logs.stderr)
            if execution.error:
                output += f"\nRUNTIME ERROR: {execution.error.name}: {execution.error.value}"
                
            if not output:
                output = "Code executed successfully but returned no output."
                
            return f'<atlas_artifact type="{artifact_type}" title="{title}">\n{output}\n</atlas_artifact>'
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox Execution Error: {e}")

@router.post("/spending-anomaly")
def spending_anomaly_detector(req: AnomalyRequest):
    prompt = f"Write a Python script using pandas. Read this CSV data into a DataFrame using io.StringIO: {repr(req.ledger_csv)}. Find any recurring subscriptions that have increased in price month-over-month (subscription creep). Print the results formatted as a clean ascii table."
    code = generate_python_code(prompt)
    return {"result": execute_in_e2b(code, "table", "Capital_Leakage_Matrix")}

@router.post("/runway-projection")
def runway_projection_engine(req: RunwayRequest):
    prompt = f"Write a Python script to calculate the financial runway (in months) if a user has a monthly income of {req.income} and a burn rate of {req.burn_rate}. Assume they start with 10000 in savings. Print a simple 12-month projection table."
    code = generate_python_code(prompt)
    return {"result": execute_in_e2b(code, "chart", "Runway_Forecast")}

@router.post("/currency-arbitrage")
def currency_arbitrage_fetcher(req: ArbitrageRequest):
    # This would typically fetch an API, but for the sandbox demo we'll mock the exchange rates in the script
    prompt = f"Write a Python script that mocks checking the currency arbitrage between {req.base_currency} and {req.target_currency}. Use some hardcoded random exchange rates to simulate the API response, calculate the spread, and print if an arbitrage opportunity exists."
    code = generate_python_code(prompt)
    return {"result": execute_in_e2b(code, "code_execution", "Sandbox_Output")}
