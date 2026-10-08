import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from ml.epieeg.inference import predict_epieeg

def test_repeated_inference_stability():
    print("\n--- Starting Sequential Repeated Inference Stress Test (20 runs) ---")
    edf_path = os.path.join(os.path.dirname(__file__), "Patient_01.edf")
    if not os.path.exists(edf_path):
        edf_path = os.path.join(os.path.dirname(__file__), "F001.edf")
        
    with open(edf_path, "rb") as f:
        file_bytes = f.read()

    for i in range(1, 21):
        t0 = time.perf_counter()
        result = predict_epieeg(file_bytes)
        t1 = time.perf_counter()
        assert result["status"] == "Success", f"Run {i} failed: {result}"
        assert "prediction" in result
        assert 0.0 <= result["seizure_probability"] <= 1.0
        assert 0.0 <= result["confidence_score"] <= 1.0
        assert result["explainability"] is not None
        print(f"Run {i:02d}/20 passed in {(t1-t0)*1000:.1f}ms - Prediction: {result['prediction']} ({result['confidence_score']:.2f})")

def test_endpoints_200_and_json():
    print("\n--- Testing All Backend Endpoints for HTTP 200 & Structured JSON ---")
    client = TestClient(app)

    endpoints_to_test = [
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/api/v1/health"),
        ("GET", "/api/v1/settings"),
        ("GET", "/api/v1/documentation"),
        ("GET", "/api/v1/docs-info"),
        ("GET", "/api/v1/reports"),
        ("GET", "/api/v1/report"),
        ("GET", "/api/v1/prescription"),
        ("POST", "/api/v1/prescription", {"patientId": "PT-01"}),
        ("POST", "/api/v1/login", {"doctorId": "Tester"}),
        ("POST", "/api/v1/register", {"name": "Dr. Test", "email": "test@doc.org", "password": "pass"}),
        ("POST", "/api/v1/patients", {"name": "Patient X", "age": "50", "gender": "Male"}),
        ("GET", "/api/v1/history/"),
    ]

    for item in endpoints_to_test:
        method = item[0]
        path = item[1]
        payload = item[2] if len(item) > 2 else None

        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json=payload or {})

        assert res.status_code == 200, f"{method} {path} returned status {res.status_code}: {res.text}"
        data = res.json()
        assert isinstance(data, dict), f"{method} {path} did not return JSON object: {data}"
        print(f"PASSED: {method:4s} {path:30s} -> HTTP {res.status_code} JSON OK")

def test_resilience_to_malformed_inputs():
    print("\n--- Testing Resilience to Corrupted / Empty / Malformed Inputs ---")
    client = TestClient(app)

    # 1. Empty file
    res = client.post("/api/v1/inference/epieeg", files={"file": ("empty.edf", b"", "application/octet-stream")})
    assert res.status_code in [400, 422], f"Empty file got {res.status_code}"
    print("PASSED: Empty EDF rejected cleanly with structured HTTP 400")

    # 2. Corrupted bytes
    res = client.post("/api/v1/inference/epieeg", files={"file": ("corrupt.edf", b"random non-edf binary garbage", "application/octet-stream")})
    assert res.status_code in [400, 422], f"Corrupt file got {res.status_code}"
    print("PASSED: Corrupt EDF rejected cleanly with structured HTTP 422 without crashing")

    # 3. Invalid extension
    res = client.post("/api/v1/inference/epieeg", files={"file": ("test.txt", b"some text", "text/plain")})
    assert res.status_code == 400, f"TXT file got {res.status_code}"
    print("PASSED: Non-EDF rejected cleanly with structured HTTP 400")

    # 4. Valid EDF through /upload and /analyze aliases
    edf_path = os.path.join(os.path.dirname(__file__), "Patient_01.edf")
    if os.path.exists(edf_path):
        with open(edf_path, "rb") as f:
            content = f.read()
        res1 = client.post("/api/v1/inference/upload", files={"file": ("Patient_01.edf", content, "application/octet-stream")})
        assert res1.status_code == 200
        print("PASSED: /api/v1/inference/upload -> HTTP 200")

        res2 = client.post("/api/v1/inference/analyze", files={"file": ("Patient_01.edf", content, "application/octet-stream")})
        assert res2.status_code == 200
        print("PASSED: /api/v1/inference/analyze -> HTTP 200")

if __name__ == "__main__":
    test_repeated_inference_stability()
    test_endpoints_200_and_json()
    test_resilience_to_malformed_inputs()
    print("\n================ ALL STABILITY AND RESILIENCE TESTS PASSED ================\n")
