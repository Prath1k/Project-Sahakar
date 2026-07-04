import os
import json
from fastapi.testclient import TestClient

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

def test_trend_analyzer():
    print("\n--- Testing biometric_trend_analyzer ---")
    response = client.post(
        "/api/biometrics/trend-analyzer",
        json={"health_json_data": '{"avg_hrv": 45, "sleep_score": 62, "caloric_deficit": 500}'}
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_lifestyle_correlation():
    print("\n--- Testing lifestyle_correlation_engine ---")
    response = client.post(
        "/api/biometrics/lifestyle-correlation",
        json={
            "health_metrics": "Resting Heart Rate: 68bpm, Deep Sleep: 45m",
            "activity_logs": "Worked until 2 AM, drank 3 cups of coffee after 4 PM, 0 minutes active time."
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_safety_filter():
    print("\n--- Testing symptom_safety_filter ---")
    response = client.post(
        "/api/biometrics/safety-filter",
        json={"symptom_statement": "I'm having a sudden sharp pain in my chest and my left arm feels numb."}
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

if __name__ == "__main__":
    print("Testing BiometricsPilot Endpoints...")
    try:
        test_trend_analyzer()
        test_lifestyle_correlation()
        test_safety_filter()
        print("\n=== BiometricsPilot Tests Complete ===")
    except Exception as e:
        print(f"Test failed: {e}")
