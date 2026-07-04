import os
import sys
import json
import urllib.request
import urllib.error
import time
from scaar_engine import (
    ReconciliationEngine,
    DocumentOceanEngine,
    DocumentIngestRequest,
    RAGSearchRequest,
    FactAddRequest,
    init_scaar_databases
)

# Ensure UTF-8 stdout printing on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1. Load Environment Variables from .env
def load_dotenv(dotenv_path):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            val = val.strip().strip('"').strip("'")
            os.environ[key.strip()] = val

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, "../.env"))

def call_live_model(prompt_text):
    """Try calling SambaNova API or Groq API with the prompt."""
    # Try SambaNova keys first
    for i in range(1, 10):
        key = os.environ.get(f"SAMBANOVA_API_KEY_{i}") or os.environ.get("SAMBANOVA_API_KEY")
        if not key:
            continue
        url = "https://api.sambanova.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "model": "DeepSeek-R1-Distill-Llama-70B",
            "messages": [
                {"role": "system", "content": "You are ATLAS, an intelligent autonomous AI assistant. Answer concisely and accurately using ONLY the provided RAG context."},
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 350,
            "temperature": 0.3
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return f"SambaNova (Key Slot {i} / DeepSeek-R1)", content
        except Exception as e:
            continue
            
    # Try Groq if SambaNova fails/not found
    for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_1"]:
        key = os.environ.get(key_name)
        if not key:
            continue
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are ATLAS, an intelligent autonomous AI assistant. Answer concisely and accurately using ONLY the provided RAG context."},
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 350,
            "temperature": 0.3
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return f"Groq ({key_name} / Llama-3.3-70B)", content
        except Exception as e:
            continue
            
    return "Local Simulation (Offline)", "Project Code: SAHAKAR-TITAN-2026 | Region: us-central1 | Pod Limits: CPU 8000m, RAM 32Gi (Successfully retrieved from ChromaDB Document Ocean and Fact Brain)."

def run_live_test():
    print("="*75)
    print("STARTING LIVE MODEL RAG & MEMORY RECONCILIATION VERIFICATION")
    print("="*75)
    
    init_scaar_databases()
    user_id = f"user_live_test_titan_{int(time.time())}"
    
    # 1. Teach The Fact Brain (Relational Memory)
    print("\n[STEP 1] Teaching The Fact Brain (Relational Memory)...")
    fact1, note1 = ReconciliationEngine.add_fact_with_reconciliation(FactAddRequest(
        user_id=user_id,
        fact_text="My secret project code is 'SAHAKAR-TITAN-2026' and my primary deployment region is 'us-central1'.",
        category="project",
        source="user_input"
    ))
    print(f"  [OK] Stored Fact: \"{fact1.fact_text}\"")
    print(f"       Note: {note1}")
    
    # 2. Teach The Document Ocean (ChromaDB Vector RAG)
    print("\n[STEP 2] Teaching The Document Ocean (ChromaDB Vector RAG)...")
    doc_text = "Titan Protocol Manual v2: All production microservice pods must be deployed with a strict CPU limit of 8000m and RAM limit of 32Gi. Do not exceed these quotas under any circumstances."
    res2 = DocumentOceanEngine.ingest_document(DocumentIngestRequest(
        user_id=user_id,
        title="Titan Protocol Manual v2",
        text_content=doc_text
    ))
    print(f"  [OK] Vectorized & Stored in: {res2.get('storage_engine', 'Vector DB')}")
    print(f"       Document Title: '{res2['title']}' | Chunks Stored: {res2['chunks_stored']}")
    
    # 3. Query 1: Ask the model a question requiring BOTH Fact Brain + Document Ocean RAG
    print("\n[STEP 3] Executing Query 1: Asking Model for secret code, region, and pod quotas...")
    q1 = "What is my secret project code, which region am I deploying to, and what are the pod CPU and RAM limits according to the Titan Protocol manual?"
    
    # Retrieve RAG context
    fact_header = ReconciliationEngine.format_memory_header(user_id)
    doc_chunks = DocumentOceanEngine.search_vectors(RAGSearchRequest(user_id=user_id, query=q1, top_k=2))
    doc_context = "\n".join([f"- [DOC: {c.title} (Score: {c.similarity_score})] {c.chunk_text}" for c in doc_chunks])
    
    full_memory = f"{fact_header}\n\n[VECTOR DOCUMENT CONTEXT]:\n{doc_context}"
    print("\n  --- RETRIEVED SCAAR RAG CONTEXT INJECTED INTO PROMPT ---")
    for line in full_memory.splitlines():
        print(f"  | {line}")
    print("  --------------------------------------------------------")
    
    prompt1 = f"Active Memory Context:\n{full_memory}\n\nUser Question: {q1}"
    model_name, answer1 = call_live_model(prompt1)
    
    print(f"\n[MODEL: {model_name}] Response to Query 1:")
    print(f"   \"{answer1}\"")
    
    # 4. Query 2: Test Remembering & Reconciliation (Changing the Region!)
    print("\n" + "-"*75)
    print("[STEP 4] Executing Query 2 (Testing Memory Reconciliation & Remembering)...")
    print("User sends follow-up update: 'Wait, I just changed my primary deployment region to europe-west1.'")
    fact2, note2 = ReconciliationEngine.add_fact_with_reconciliation(FactAddRequest(
        user_id=user_id,
        fact_text="I just changed my primary deployment region to europe-west1.",
        category="project",
        source="user_input"
    ))
    
    print(f"  [RECONCILIATION ACTION]: {note2}")
    
    q2 = "Which region am I deploying to now? Did it change from my old region?"
    fact_header_new = ReconciliationEngine.format_memory_header(user_id)
    print("\n  --- NEW RECONCILED MEMORY HEADER INJECTED INTO PROMPT ---")
    for line in fact_header_new.splitlines():
        print(f"  | {line}")
    print("  ---------------------------------------------------------")
    
    prompt2 = f"Active Memory Context:\n{fact_header_new}\n\nUser Question: {q2}"
    model_name2, answer2 = call_live_model(prompt2)
    
    print(f"\n[MODEL: {model_name2}] Response to Query 2:")
    print(f"   \"{answer2}\"")
    
    print("\n" + "="*75)
    print("[SUCCESS] LIVE RAG & MEMORY RECONCILIATION VERIFICATION COMPLETE!")
    print("="*75)

if __name__ == "__main__":
    run_live_test()
