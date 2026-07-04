import os
import json
import urllib.request
import urllib.error
import time

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

def test_sambanova_completion(key_name, key_value):
    url = "https://api.sambanova.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key_value}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    payload = {
        "model": "DeepSeek-R1-Distill-Llama-70B",
        "messages": [{"role": "user", "content": "Respond with OK"}],
        "max_tokens": 10
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            text = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return True, f"SUCCESS: '{text}'"
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode('utf-8'))
            err_msg = err.get("error", {}).get("message", str(e))
        except Exception:
            err_msg = f"HTTP Error {e.code}"
        return False, f"FAILED: {err_msg}"
    except Exception as e:
        return False, f"FAILED: {e}"

def main():
    print("Testing all SambaNova keys for completions...")
    for i in range(1, 9):
        key_name = f"SAMBANOVA_API_KEY_{i}"
        key_val = os.environ.get(key_name)
        if key_val:
            success, msg = test_sambanova_completion(key_name, key_val)
            status = "🟢" if success else "🔴"
            print(f"{status} {key_name}: {msg}")
        else:
            print(f"⚪ {key_name}: Not configured")

if __name__ == "__main__":
    main()
