import os
import json
import urllib.request

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

def main():
    # 1. Print Cerebras Models List
    cerebras_key = os.environ.get("CEREBRAS_API_KEY_1")
    if cerebras_key:
        print("\n--- Cerebras Models ---")
        try:
            req = urllib.request.Request(
                "https://api.cerebras.ai/v1/models",
                headers={
                    "Authorization": f"Bearer {cerebras_key}",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"Failed: {e}")
            
    # 2. Print Gemini Raw Response
    gemini_key = os.environ.get("GEMINI_API_KEY_1")
    if gemini_key:
        print("\n--- Gemini Raw Response ---")
        try:
            query_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": "Explain quantum computing in one sentence."}]}],
                "generationConfig": {"maxOutputTokens": 60}
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
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                print(json.dumps(res, indent=2))
        except Exception as e:
            print(f"Failed: {e}")
            
    # 3. Print OpenRouter Free Models
    openrouter_key = os.environ.get("OPENROUTER_API_KEY_1")
    if openrouter_key:
        print("\n--- OpenRouter Free Models ---")
        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {openrouter_key}"},
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res = json.loads(response.read().decode('utf-8'))
                free_models = [m["id"] for m in res.get("data", []) if m["id"].endswith(":free")]
                print(free_models[:10])
        except Exception as e:
            print(f"Failed: {e}")

if __name__ == "__main__":
    main()
