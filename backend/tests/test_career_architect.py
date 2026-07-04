import os
import json
from fastapi.testclient import TestClient

# Must load environment variables before importing main if not already set
def load_dotenv(dotenv_path):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                key, val = line.split("=", 1)
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                os.environ[key.strip()] = val.strip()

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, "../.env"))

from main import app
client = TestClient(app)

def test_analyze_role():
    print("\n--- Testing target_role_analyzer ---")
    response = client.post(
        "/api/career/analyze-role", 
        json={"job_url": "https://careers.google.com/jobs/results/senior-software-engineer-python-rust/"}
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_resume_gap():
    print("\n--- Testing resume_gap_assessor ---")
    response = client.post(
        "/api/career/resume-gap", 
        json={
            "resume_data": "I know JavaScript and React. I have 2 years of experience.",
            "job_requirements": "Requires Python, Rust, and 5+ years of distributed systems experience."
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_ats_tailor():
    print("\n--- Testing ats_resume_tailor ---")
    response = client.post(
        "/api/career/ats-tailor",
        json={
            "job_description": "We need a frontend developer skilled in React, Next.js, and Framer Motion.",
            "resume": "Web Developer with experience in HTML, CSS, JavaScript."
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_roadmap():
    print("\n--- Testing placement_roadmap_generator ---")
    response = client.post(
        "/api/career/roadmap",
        json={
            "target_role": "Backend Engineer",
            "current_skills": "Python basics, HTML, CSS"
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_adversarial():
    print("\n--- Testing adversarial_interviewer ---")
    response = client.post(
        "/api/career/adversarial-interview",
        json={
            "target_role": "Senior Cloud Architect",
            "context": "User says they have 6 months of AWS experience and took one online course."
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

if __name__ == "__main__":
    print("Testing CareerArchitect Endpoints via LLM integration...")
    try:
        import httpx
    except ImportError:
        print("Required library 'httpx' missing. Please 'pip install httpx'.")
        
    test_analyze_role()
    test_resume_gap()
    test_ats_tailor()
    test_roadmap()
    test_adversarial()
    print("\n=== CareerArchitect Tests Complete ===")
