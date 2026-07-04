import os
import json
import urllib.request
import urllib.error
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                # Strip quotes if present
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                os.environ[key.strip()] = val.strip()

# Ensure environment variables are loaded relative to file directory
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, "../.env")
load_dotenv(dotenv_path)

# Define the providers and models to test
TEST_CONFIGS = {
    "Groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "env_prefix": "GROQ_API_KEY"
    },
    "SambaNova": {
        "url": "https://api.sambanova.ai/v1/chat/completions",
        "model": "DeepSeek-R1",  # We can fall back to DeepSeek-R1-Distill-Llama-70B if needed
        "env_prefix": "SAMBANOVA_API_KEY"
    },
    "Google AI Studio": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-1.5-flash",
        "env_prefix": "GEMINI_API_KEY"
    },
    "NVIDIA NIM": {
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model": "meta/llama-3.2-11b-vision-instruct",
        "env_prefix": "NVIDIA_API_KEY"  # The env keys are named NVIDIA_API_KEY_X
    },
    "OpenRouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "google/gemma-2-9b-it:free",
        "env_prefix": "OPENROUTER_API_KEY"
    },
    "Cerebras": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama3.1-8b",
        "env_prefix": "CEREBRAS_API_KEY"
    }
}

def test_single_key(provider, key_name, key_value, config):
    url = config["url"]
    
    # If checking via GET models
    if provider in ["OpenRouter", "SambaNova", "Cerebras", "Groq"]:
        # We test the key by calling the models endpoint
        if provider == "OpenRouter":
            models_url = "https://openrouter.ai/api/v1/models"
        elif provider == "SambaNova":
            models_url = "https://api.sambanova.ai/v1/models"
        elif provider == "Cerebras":
            models_url = "https://api.cerebras.ai/v1/models"
        else: # Groq
            models_url = "https://api.groq.com/openai/v1/models"
            
        req = urllib.request.Request(
            models_url,
            headers={
                "Authorization": f"Bearer {key_value}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            method="GET"
        )
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                latency = round((time.time() - start_time) * 1000, 2)
                # Just check if we got a list of models
                models = res_json.get("data", [])
                return {
                    "provider": provider,
                    "key_name": key_name,
                    "status": "SUCCESS",
                    "latency_ms": latency,
                    "model_requested": "GET /v1/models",
                    "model_responded": f"Retrieved {len(models)} models",
                    "response": "Authentication Successful",
                    "error": None
                }
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = f"HTTP Error {e.code}: {e.reason}"
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": "GET /v1/models",
                "model_responded": None,
                "response": None,
                "error": err_msg
            }
        except Exception as e:
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": "GET /v1/models",
                "model_responded": None,
                "response": None,
                "error": str(e)
            }
            
    elif provider == "Google AI Studio":
        # Call the models list endpoint to test key validity
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key_value}"
        req = urllib.request.Request(
            gemini_url, 
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            method='GET'
        )
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                latency = round((time.time() - start_time) * 1000, 2)
                models = res_json.get("models", [])
                return {
                    "provider": provider,
                    "key_name": key_name,
                    "status": "SUCCESS",
                    "latency_ms": latency,
                    "model_requested": "GET /v1beta/models",
                    "model_responded": f"Retrieved {len(models)} models",
                    "response": "Authentication Successful",
                    "error": None
                }
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = f"HTTP Error {e.code}: {e.reason}"
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": "GET /v1beta/models",
                "model_responded": None,
                "response": None,
                "error": err_msg
            }
        except Exception as e:
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": "GET /v1beta/models",
                "model_responded": None,
                "response": None,
                "error": str(e)
            }
            
    else:
        # Standard chat completions (NVIDIA NIM)
        url = config["url"]
        model = config["model"]
        headers = {
            "Authorization": f"Bearer {key_value}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Respond with the single word: OK"}],
            "max_tokens": 5
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                latency = round((time.time() - start_time) * 1000, 2)
                responded_model = res_json.get("model", "unknown")
                response_text = res_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                return {
                    "provider": provider,
                    "key_name": key_name,
                    "status": "SUCCESS",
                    "latency_ms": latency,
                    "model_requested": model,
                    "model_responded": responded_model,
                    "response": response_text,
                    "error": None
                }
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", {}).get("message", err_body)
            except Exception:
                err_msg = f"HTTP Error {e.code}: {e.reason}"
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": model,
                "model_responded": None,
                "response": None,
                "error": err_msg
            }
        except Exception as e:
            return {
                "provider": provider,
                "key_name": key_name,
                "status": "FAILED",
                "latency_ms": round((time.time() - start_time) * 1000, 2),
                "model_requested": model,
                "model_responded": None,
                "response": None,
                "error": str(e)
            }

def main():
    print("=" * 60)
    print("ATLAS Multi-Model API Key Validation Script")
    print("=" * 60)
    
    # Gather all keys from environment
    keys_to_test = []
    for provider, config in TEST_CONFIGS.items():
        prefix = config["env_prefix"]
        for k, v in os.environ.items():
            if k == prefix or k.startswith(f"{prefix}_"):
                val = v.strip()
                if val and val != '""' and val != "''":
                    keys_to_test.append((provider, k, val, config))
                    
    print(f"Found {len(keys_to_test)} configured keys to test.")
    if not keys_to_test:
        print("No keys found! Please populate your .env file.")
        return
        
    results = []
    
    # Execute tests in parallel to save time
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(test_single_key, p, kn, kv, conf): (p, kn) for p, kn, kv, conf in keys_to_test}
        
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            # Live progress output
            status_indicator = "✅" if res["status"] == "SUCCESS" else "❌"
            print(f"{status_indicator} Tested {res['provider']} key {res['key_name']} -> {res['status']}")
            if res["error"]:
                print(f"   Error: {res['error']}")
                
    # Group results by provider for final report
    print("\n" + "=" * 60)
    print("FINAL API VALIDATION REPORT")
    print("=" * 60)
    
    for provider in TEST_CONFIGS.keys():
        provider_results = [r for r in results if r["provider"] == provider]
        if not provider_results:
            continue
            
        print(f"\n📁 Provider: {provider}")
        success_count = sum(1 for r in provider_results if r["status"] == "SUCCESS")
        print(f"Status: {success_count}/{len(provider_results)} keys active")
        
        for res in sorted(provider_results, key=lambda x: x["key_name"]):
            if res["status"] == "SUCCESS":
                print(f"  🟢 {res['key_name']}: SUCCESS")
                print(f"     Latency: {res['latency_ms']} ms")
                print(f"     Model Requested: {res['model_requested']}")
                print(f"     Model Responded: {res['model_responded']}")
                print(f"     Response: '{res['response']}'")
            else:
                print(f"  🔴 {res['key_name']}: FAILED")
                print(f"     Error: {res['error']}")
                
if __name__ == "__main__":
    main()
