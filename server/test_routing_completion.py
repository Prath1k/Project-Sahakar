import os
import json
import urllib.request
import urllib.error
import time

# Manual env loading helper
def load_dotenv(dotenv_path):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                os.environ[key.strip()] = val.strip()

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, "../.env"))

def check_gemini(key):
    # 1. Get model list first to find exact name
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        req = urllib.request.Request(
            list_url, 
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            models = [m["name"].split("/")[-1] for m in res.get("models", [])]
    except Exception as e:
        return f"Failed to list models: {e}"
        
    target_model = "gemini-1.5-flash"
    # Fallback to first available model if gemini-1.5-flash is not found
    if "gemini-1.5-flash" not in models and "gemini-2.5-flash" in models:
        target_model = "gemini-2.5-flash"
    elif models:
        target_model = models[0]
        
    # 2. Query model
    query_url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": "Explain quantum computing in one sentence."}]}],
        "generationConfig": {"maxOutputTokens": 500}
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        query_url, 
        data=data, 
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }, 
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode('utf-8'))
            candidates = res.get("candidates", [{}])
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            return f"SUCCESS: Routed to Gemini model: {target_model}.\n      Reply: \"{text}\""
    except Exception as e:
        return f"Query failed for {target_model}: {e}"

def check_openai_compatible(provider, url, key, model):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Explain quantum computing in one sentence."}],
        "max_tokens": 100
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode('utf-8'))
            responded_model = res.get("model", "unknown")
            choices = res.get("choices", [{}])
            message = choices[0].get("message", {}) if choices else {}
            text = (message.get("content") or "").strip().replace("\n", " ")
            
            status = "SUCCESS" if responded_model.lower().replace("_", "-").replace("/", "-") in model.lower().replace("_", "-").replace("/", "-") or model.lower().replace("_", "-").replace("/", "-") in responded_model.lower().replace("_", "-").replace("/", "-") else "PARTIAL (Model mismatch)"
            
            return f"{status}: Routed to {provider} model: {responded_model}.\n      Reply: \"{text}\""
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode('utf-8'))
            return f"FAILED: {provider} error: {err.get('error', {}).get('message', str(e))}"
        except Exception:
            return f"FAILED: {provider} HTTP Error {e.code}"
    except Exception as e:
        return f"FAILED: {provider} error: {e}"

def main():
    print("=" * 60)
    print("ATLAS Live Model Response Verification")
    print("=" * 60)
    
    # 1. Test Groq using GROQ_API_KEY_1
    groq_key = os.environ.get("GROQ_API_KEY_1")
    if groq_key:
        print("\nChecking Groq Routing...")
        res = check_openai_compatible(
            "Groq", 
            "https://api.groq.com/openai/v1/chat/completions", 
            groq_key, 
            "llama-3.3-70b-versatile"
        )
        print(f"-> {res}")
    else:
        print("\nGroq key not found.")

    # 2. Test Cerebras using CEREBRAS_API_KEY_1
    cerebras_key = os.environ.get("CEREBRAS_API_KEY_1")
    if cerebras_key:
        print("\nChecking Cerebras Routing...")
        res = check_openai_compatible(
            "Cerebras", 
            "https://api.cerebras.ai/v1/chat/completions", 
            cerebras_key, 
            "gemma-4-31b"
        )
        print(f"-> {res}")
    else:
        print("\nCerebras key not found.")
        
    # 3. Test Gemini using GEMINI_API_KEY_1
    gemini_key = os.environ.get("GEMINI_API_KEY_1")
    if gemini_key:
        print("\nChecking Google AI Studio Routing...")
        res = check_gemini(gemini_key)
        print(f"-> {res}")
    else:
        print("\nGemini key not found.")
        
    # 4. Test NVIDIA NIM using NVIDIA_API_KEY_1
    nvidia_key = os.environ.get("NVIDIA_API_KEY_1")
    if nvidia_key:
        print("\nChecking NVIDIA NIM Routing...")
        res = check_openai_compatible(
            "NVIDIA NIM", 
            "https://integrate.api.nvidia.com/v1/chat/completions", 
            nvidia_key, 
            "meta/llama-3.2-11b-vision-instruct"
        )
        print(f"-> {res}")
    else:
        print("\nNVIDIA NIM key not found.")
        
    # 5. Test OpenRouter using OPENROUTER_API_KEY_1
    openrouter_key = os.environ.get("OPENROUTER_API_KEY_1")
    if openrouter_key:
        print("\nChecking OpenRouter Routing...")
        # We will try a few model options dynamically
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {openrouter_key}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_models = json.loads(response.read().decode('utf-8')).get("data", [])
                free_models = [m["id"] for m in res_models if m["id"].endswith(":free")]
                
            # Filter model candidates
            test_model = "meta-llama/llama-3.1-8b-instruct"  # Paid fallback
            for model_id in ["google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free", "qwen/qwen-2.5-7b-instruct:free", "google/gemma-2-9b-it:free", "mistralai/mistral-7b-instruct:free"]:
                if model_id in free_models:
                    test_model = model_id
                    break
            if test_model == "meta-llama/llama-3.1-8b-instruct" and free_models:
                test_model = free_models[0]
                
            print(f"Selected OpenRouter Model to test: {test_model}")
            res = check_openai_compatible(
                "OpenRouter", 
                "https://openrouter.ai/api/v1/chat/completions", 
                openrouter_key, 
                test_model
            )
            print(f"-> {res}")
        except Exception as e:
            print(f"-> FAILED: OpenRouter model test error: {e}")
    else:
        print("\nOpenRouter key not found.")

    # 6. Test SambaNova using SAMBANOVA_API_KEY_8
    sambanova_key = os.environ.get("SAMBANOVA_API_KEY_8")
    if sambanova_key:
        print("\nChecking SambaNova Routing...")
        res = check_openai_compatible(
            "SambaNova", 
            "https://api.sambanova.ai/v1/chat/completions", 
            sambanova_key, 
            "DeepSeek-R1-Distill-Llama-70B"
        )
        print(f"-> {res}")
    else:
        print("\nSambaNova key not found.")

if __name__ == "__main__":
    main()
