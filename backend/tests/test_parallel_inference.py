import os
import sys
import time
import concurrent.futures
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def run_single_inference(endpoint, edf_bytes):
    res = client.post(
        endpoint,
        files={"file": ("test.edf", edf_bytes, "application/octet-stream")}
    )
    return res.status_code, res.json()

def test_concurrent_inferences():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f001_path = os.path.join(backend_dir, "F001.edf")
    if not os.path.exists(f001_path):
        pytest.skip("Sample EDF not found.")

    edf_bytes = open(f001_path, "rb").read()

    # Launch 4 concurrent requests (2 EpiEEG, 2 Bonn) across threads
    tasks = [
        ("/api/v1/inference/epieeg", edf_bytes),
        ("/api/v1/inference/predict", edf_bytes),
        ("/api/v1/inference/epieeg", edf_bytes),
        ("/api/v1/inference/predict", edf_bytes),
    ]

    t0 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_single_inference, ep, b) for ep, b in tasks]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    t1 = time.perf_counter()

    for status_code, data in results:
        assert status_code == 200
        assert data["status"] == "Success"
        assert "prediction" in data
        assert "seizure_probability" in data

    print(f"\n4 concurrent inference requests completed in {t1-t0:.2f}s")
