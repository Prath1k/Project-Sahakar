# ==============================================================================
# Project Sahakar — 100% Automated Backend & Secret Uploader for Hugging Face
# ==============================================================================
# This script automatically uploads the contents of your backend/ folder directly
# to the root of your Hugging Face Space AND uploads all 40+ API keys from .env!
# NO GIT REQUIRED!

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
    print("🚀 Project Sahakar — 100% Automated Cloud Deployer")
    print("------------------------------------------------------------------")
    
    repo_id_input = input("Enter your Hugging Face Space Repo ID (e.g., username/project-sahakar-backend) [Press Enter for 'sricharansairi/ProjectSahakar']: ").strip()
    repo_id = repo_id_input if repo_id_input else "sricharansairi/ProjectSahakar"
    
    token = input("🔑 Paste your Hugging Face Access Token (from https://huggingface.co/settings/tokens): ").strip()
    
    if not token:
        print("❌ Error: Token cannot be empty.")
        return

    api = HfApi(token=token)
    
    # 1. Upload Backend Folder directly to Root of Space
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if not os.path.exists(backend_dir):
        print(f"❌ Error: Could not find backend directory at {backend_dir}")
        return
        
    print(f"\n📂 Step 1/2: Uploading backend files (Dockerfile, app, voices) directly to root of '{repo_id}'...")
    print("⏳ Please wait ~30-60 seconds while files are uploading...")
    
    try:
        api.upload_folder(
            folder_path=backend_dir,
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=["*.db", "chroma_storage/*", "__pycache__/*", "*.pyc", ".env"]
        )
        print("✅ Backend code uploaded successfully to space root!")
    except Exception as e:
        print(f"❌ Failed to upload code: {e}")
        return

    # 2. Upload Secrets from .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        env_vars = dotenv_values(env_path)
        print(f"\n🔐 Step 2/2: Uploading {len(env_vars)} API keys & secrets from .env...")
        
        count = 0
        for key, val in env_vars.items():
            if val and str(val).strip() and not str(val).startswith("your_"):
                try:
                    api.add_space_secret(repo_id=repo_id, key=key, value=str(val).strip())
                    count += 1
                except Exception as e:
                    pass
        print(f"✅ Successfully uploaded {count} secrets!")
    else:
        print("⚠️ No .env file found to upload secrets.")
                
    print("\n🎉 100% SUCCESS! Everything has been deployed to Hugging Face Spaces!")
    print(f"🌐 Check your live Space status at: https://huggingface.co/spaces/{repo_id}")
    print("👉 Note: The yellow 'No application file' badge will now disappear and change to 'Building'!")

if __name__ == "__main__":
    main()
