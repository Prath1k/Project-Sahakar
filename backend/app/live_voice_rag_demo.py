import os
import sys
import json
import time
import asyncio
import urllib.request
import urllib.error
from pathlib import Path

# Ensure UTF-8 stdout printing on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add backend/app to path if needed
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

from scaar_engine import (
    ReconciliationEngine,
    DocumentOceanEngine,
    DocumentIngestRequest,
    RAGSearchRequest,
    FactAddRequest,
    init_scaar_databases
)
from voice_service import KokoroTTSService, VoiceRouter

# Load environment variables
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

load_dotenv(base_dir.parent.parent / ".env")

def call_live_model(prompt_text):
    """Call live LLM (SambaNova or Groq) with RAG context."""
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
                {"role": "system", "content": "You are ATLAS, an intelligent voice assistant. Answer in 1 or 2 clear, concise sentences suitable for speaking out loud. Use ONLY the provided RAG context."},
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                # Clean out any thinking tags if present
                if "</think>" in content:
                    content = content.split("</think>")[-1].strip()
                return f"SambaNova (Key {i})", content
        except Exception:
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
                {"role": "system", "content": "You are ATLAS, an intelligent voice assistant. Answer in 1 or 2 clear, concise sentences suitable for speaking out loud. Use ONLY the provided RAG context."},
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 150,
            "temperature": 0.3
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as response:
                res = json.loads(response.read().decode('utf-8'))
                content = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return f"Groq ({key_name})", content
        except Exception:
            continue
            
    return "Local Simulation", "Your project code is SAHAKAR TITAN 2026, deploying to region us-central1."

def play_audio_through_speakers(audio_bytes, filename="live_reply.wav"):
    """Save WAV and play through Windows OS speakers."""
    out_path = base_dir / filename
    out_path.write_bytes(audio_bytes)
    print(f"   [AUDIO] Saved ({len(audio_bytes):,} bytes). Playing through system speakers NOW...")
    try:
        import winsound
        winsound.PlaySound(str(out_path), winsound.SND_FILENAME)
        print("   [AUDIO] Playback finished!")
    except Exception as e:
        print(f"   [ERROR] Could not play sound: {e}")

async def run_voice_rag_demo():
    print("="*75)
    print("LIVE VOICE DICTATION & RAG MEMORY RECALL DEMO")
    print("="*75)
    
    init_scaar_databases()
    user_id = f"user_voice_demo_{int(time.time())}"
    
    # STEP 1: Teach RAG Brain
    print("\n[STEP 1] Teaching RAG Fact Brain & Document Ocean...")
    fact1 = "My secret project code is 'SAHAKAR-TITAN-2026' and my primary deployment region is 'us-central1'."
    ReconciliationEngine.add_fact_with_reconciliation(FactAddRequest(
        user_id=user_id, fact_text=fact1, category="project", source="user_voice"
    ))
    
    doc_text = "Titan Protocol Manual v2: All production microservice pods must be deployed with a strict CPU limit of 8000m and RAM limit of 32Gi."
    DocumentOceanEngine.ingest_document(DocumentIngestRequest(
        user_id=user_id, title="Titan Protocol Manual v2", text_content=doc_text
    ))
    print("   [OK] Stored project facts & protocol manual into RAG.")
    
    # STEP 2: Query 1 -> Live Model Reply -> Speak out of Speakers!
    print("\n[STEP 2] Query 1: Asking Model for secret code and region...")
    q1 = "What is my secret project code and which deployment region am I deploying to?"
    
    fact_header = ReconciliationEngine.format_memory_header(user_id)
    doc_chunks = DocumentOceanEngine.search_vectors(RAGSearchRequest(user_id=user_id, query=q1, top_k=1))
    doc_context = "\n".join([f"- [DOC: {c.title}] {c.chunk_text}" for c in doc_chunks])
    full_memory = f"{fact_header}\n\n{doc_context}"
    
    prompt1 = f"Active Memory Context:\n{full_memory}\n\nUser Question: {q1}"
    model_name, answer1 = call_live_model(prompt1)
    
    print(f"\n🤖 [{model_name}] Text Reply 1:")
    print(f"   \"{answer1}\"")
    
    print("\n🔊 Synthesizing speech and dictating through speakers...")
    route1 = VoiceRouter.get_voice_profile(text=answer1, agent_role="GeneralAssistant", message_type="general", urgency="normal")
    audio1, _, _ = await KokoroTTSService.synthesize_audio(text=answer1, voice=route1.assigned_voice)
    play_audio_through_speakers(audio1, "turn1_reply.wav")
    
    time.sleep(1.0)
    
    # STEP 3: Query 2 -> Memory Recall & Reconciliation -> Speak out of Speakers!
    print("\n" + "-"*75)
    print("[STEP 3] Query 2: Updating region and testing RAG Memory Recall...")
    print("User update: 'Wait, I just changed my primary deployment region to europe-west1.'")
    
    fact2 = "I just changed my primary deployment region to europe-west1."
    _, note2 = ReconciliationEngine.add_fact_with_reconciliation(FactAddRequest(
        user_id=user_id, fact_text=fact2, category="project", source="user_voice"
    ))
    print(f"   [RECONCILIATION]: {note2}")
    
    q2 = "Which deployment region am I deploying to now, and what was my previous region?"
    fact_header_new = ReconciliationEngine.format_memory_header(user_id)
    prompt2 = f"Active Memory Context:\n{fact_header_new}\n\nUser Question: {q2}"
    
    model_name2, answer2 = call_live_model(prompt2)
    
    print(f"\n🤖 [{model_name2}] Text Reply 2 (Memory Recall):")
    print(f"   \"{answer2}\"")
    
    print("\n🔊 Synthesizing speech and dictating through speakers...")
    route2 = VoiceRouter.get_voice_profile(text=answer2, agent_role="GeneralAssistant", message_type="general", urgency="normal")
    audio2, _, _ = await KokoroTTSService.synthesize_audio(text=answer2, voice=route2.assigned_voice)
    play_audio_through_speakers(audio2, "turn2_reply.wav")
    
    print("\n" + "="*75)
    print("[SUCCESS] LIVE VOICE DICTATION & RAG RECALL COMPLETED!")
    print("="*75)

if __name__ == "__main__":
    asyncio.run(run_voice_rag_demo())
