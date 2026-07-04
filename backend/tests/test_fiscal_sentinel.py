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

def test_spending_anomaly():
    print("\n--- Testing spending_anomaly_detector ---")
    ledger = "Date,Description,Amount\n2023-01-01,Netflix,15.99\n2023-02-01,Netflix,15.99\n2023-03-01,Netflix,17.99\n2023-01-15,Gym,50.00\n2023-02-15,Gym,50.00\n2023-03-15,Gym,55.00"
    response = client.post(
        "/api/fiscal/spending-anomaly",
        json={"ledger_csv": ledger}
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_runway_projection():
    print("\n--- Testing runway_projection_engine ---")
    response = client.post(
        "/api/fiscal/runway-projection",
        json={
            "income": 5000.0,
            "burn_rate": 6500.0
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

def test_currency_arbitrage():
    print("\n--- Testing currency_arbitrage_fetcher ---")
    response = client.post(
        "/api/fiscal/currency-arbitrage",
        json={
            "base_currency": "USD",
            "target_currency": "EUR"
        }
    )
    print(f"Status: {response.status_code}")
    print(response.json().get("result", ""))

if __name__ == "__main__":
    print("Testing FiscalSentinel Endpoints (E2B Cloud Sandbox Integration)...")
    try:
        test_spending_anomaly()
        test_runway_projection()
        test_currency_arbitrage()
        print("\n=== FiscalSentinel Tests Complete ===")
    except Exception as e:
        print(f"Test failed: {e}")
