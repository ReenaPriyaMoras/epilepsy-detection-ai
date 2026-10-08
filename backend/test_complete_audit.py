import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import app
from database.database import get_dashboard_stats, get_all_analyses, search_analyses

def run_audit():
    client = TestClient(app)
    
    print("--- 1. Testing Root & Health Endpoints ---")
    r = client.get("/")
    assert r.status_code == 200 and r.json()["status"] == "online"
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"
    r = client.get("/api/v1/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"
    print("OK: Health & root endpoints verified.")

    print("--- 2. Testing Inference & Auto-save to SQLite ---")
    edf_path = os.path.join(os.path.dirname(__file__), "Patient_01.edf")
    if not os.path.exists(edf_path):
        edf_path = os.path.join(os.path.dirname(__file__), "F001.edf")

    with open(edf_path, "rb") as f:
        content = f.read()

    r = client.post("/api/v1/inference/epieeg", files={"file": ("Patient_01.edf", content, "application/octet-stream")})
    assert r.status_code == 200
    res_data = r.json()
    assert res_data["status"] == "Success"
    assert "prediction" in res_data
    assert "analysis_id" in res_data
    analysis_id = res_data["analysis_id"]
    print(f"OK: Inference succeeded and generated record ID: {analysis_id}")

    print("--- 3. Testing Dashboard Dynamic Metrics ---")
    r = client.get("/api/v1/dashboard/stats")
    assert r.status_code == 200
    stats = r.json()
    assert stats["total_analyses"] >= 1
    assert stats["backend_status"] == "Connected"
    print(f"OK: Dashboard stats: Total Analyses = {stats['total_analyses']}, Avg Conf = {stats['average_confidence']}")

    print("--- 4. Testing History Retrieval ---")
    r = client.get("/api/v1/history/")
    assert r.status_code == 200
    hist = r.json()
    assert hist["count"] >= 1
    assert any(item["id"] == analysis_id for item in hist["data"])
    print(f"OK: History contains {hist['count']} analyses.")

    print("--- 5. Testing Global Search ---")
    # Search by filename
    r = client.get("/api/v1/search/?q=Patient_01")
    assert r.status_code == 200
    search_res = r.json()
    assert search_res["count"] >= 1
    print(f"OK: Search 'Patient_01' found {search_res['count']} match(es).")

    # Search by analysis ID
    r = client.get(f"/api/v1/search/?q={analysis_id}")
    assert r.status_code == 200
    assert r.json()["count"] == 1
    print(f"OK: Search ID '{analysis_id}' exact match verified.")

    # Search non-existent
    r = client.get("/api/v1/search/?q=NonExistent999XYZ")
    assert r.status_code == 200
    assert r.json()["count"] == 0
    print("OK: Search non-existent query returned 0 matches cleanly.")

    print("--- 6. Testing Delete Analysis ---")
    r = client.delete(f"/api/v1/history/{analysis_id}")
    assert r.status_code == 200
    print("OK: Analysis deleted from database cleanly.")

    print("\n================ FULL CLINICAL AUDIT SUITE PASSED ================\n")

if __name__ == "__main__":
    run_audit()
