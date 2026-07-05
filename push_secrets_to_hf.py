# ==============================================================================
# Project Sahakar — Bulk Secret Uploader for Hugging Face Spaces
# ==============================================================================
# This script reads all 40+ keys from your local .env file and automatically
# uploads them to your Hugging Face Space secrets in 3 seconds!

import os
import sys
from dotenv import dotenv_values

try:
    from huggingface_hub import HfApi
except ImportError:
    print("❌ 'huggingface_hub' library is not installed.")
    print("👉 Run: pip install huggingface_hub python-dotenv")
    sys.exit(1)

def main():
    print("🔑 Project Sahakar — Bulk Secret Uploader to Hugging Face Spaces")
    print("------------------------------------------------------------------")
    
    repo_id = "sricharansairi/ProjectSahakar"
    token = input("Paste your Hugging Face Access Token (from https://huggingface.co/settings/tokens): ").strip()
    
    if not token:
        print("❌ Error: Token cannot be empty.")
        return

    api = HfApi(token=token)
    
    # Read .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        print(f"❌ Error: Could not find .env file at {env_path}")
        return
        
    env_vars = dotenv_values(env_path)
    print(f"\n📂 Found {len(env_vars)} variables in .env file. Starting upload to '{repo_id}'...\n")
    
    count = 0
    for key, val in env_vars.items():
        if val and str(val).strip() and not str(val).startswith("your_"):
            print(f"⬆️ Uploading secret: {key}...")
            try:
                api.add_space_secret(repo_id=repo_id, key=key, value=str(val).strip())
                count += 1
            except Exception as e:
                print(f"⚠️ Could not upload {key}: {e}")
                
    print(f"\n🎉 SUCCESS! Uploaded {count} API keys and secrets to your Hugging Face Space!")
    print(f"👉 Now go to https://huggingface.co/spaces/{repo_id}/settings and click 'Restart Space'!")

if __name__ == "__main__":
    main()
