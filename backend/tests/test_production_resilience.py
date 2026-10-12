import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.database import get_dashboard_stats, get_all_analyses

client = TestClient(app)

@pytest.fixture(scope="module")
def sample_edfs():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f001_path = os.path.join(backend_dir, "F001.edf")
    patient01_path = os.path.join(backend_dir, "Patient_01.edf")
    
    f001_bytes = open(f001_path, "rb").read() if os.path.exists(f001_path) else None
    patient01_bytes = open(patient01_path, "rb").read() if os.path.exists(patient01_path) else None
    
    return {
        "f001": f001_bytes,
        "patient01": patient01_bytes,
    }

# 1. Root and Health Endpoints
def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "version" in data

def test_health_endpoints():
    res1 = client.get("/health")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] in ["healthy", "degraded"]
    assert data1["backend"] == "online"
    assert "uptime_seconds" in data1

    res2 = client.get("/api/v1/health")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "healthy"

# 2. Dashboard and History Endpoints
def test_dashboard_stats():
    res = client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "total_analyses" in data
    assert "epileptic_cases" in data
    assert "healthy_cases" in data
    assert "average_confidence" in data

def test_history_crud():
    res = client.get("/api/v1/history/")
    assert res.status_code == 200
    data = res.json()
    assert "data" in data
    assert "count" in data

# 3. EpiEEG Inference Endpoint
def test_epieeg_inference_success(sample_edfs):
    edf_data = sample_edfs["f001"] or sample_edfs["patient01"]
    if not edf_data:
        pytest.skip("No sample EDF found.")

    res = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("test_recording.edf", edf_data, "application/octet-stream")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Success"
    assert data["prediction"] in ["Epileptic", "Non-Epileptic"]
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert 0.0 <= data["seizure_probability"] <= 1.0
    assert data["dataset"] == "EpiEEG"
    assert "analysis_id" in data

def test_epieeg_inference_aliases(sample_edfs):
    edf_data = sample_edfs["f001"] or sample_edfs["patient01"]
    if not edf_data:
        pytest.skip("No sample EDF found.")

    res_upload = client.post(
        "/api/v1/inference/upload",
        files={"file": ("test_recording.edf", edf_data, "application/octet-stream")}
    )
    assert res_upload.status_code == 200
    assert res_upload.json()["status"] == "Success"

    res_analyze = client.post(
        "/api/v1/inference/analyze",
        files={"file": ("test_recording.edf", edf_data, "application/octet-stream")}
    )
    assert res_analyze.status_code == 200
    assert res_analyze.json()["status"] == "Success"

# 4. Bonn Inference Endpoint
def test_bonn_inference_success(sample_edfs):
    edf_data = sample_edfs["f001"] or sample_edfs["patient01"]
    if not edf_data:
        pytest.skip("No sample EDF found.")

    res = client.post(
        "/api/v1/inference/predict",
        files={"file": ("bonn_test.edf", edf_data, "application/octet-stream")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "Success"
    assert data["prediction"] in ["Epileptic", "Non-Epileptic"]
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert 0.0 <= data["seizure_probability"] <= 1.0
    assert data["dataset"] == "Bonn"
    assert "analysis_id" in data

# 5. Invalid / Malformed / Empty Inputs
def test_invalid_extension():
    res = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("document.pdf", b"%PDF-1.4 dummy content", "application/pdf")}
    )
    assert res.status_code == 400
    assert "Only EDF files" in res.json()["message"]

def test_invalid_extension_bonn():
    res = client.post(
        "/api/v1/inference/predict",
        files={"file": ("data.csv", b"col1,col2\n1,2", "text/csv")}
    )
    assert res.status_code == 400

def test_empty_file():
    res = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("empty.edf", b"", "application/octet-stream")}
    )
    assert res.status_code == 400
    assert "empty" in res.json()["message"].lower()

def test_corrupted_edf_bytes():
    res = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("corrupt.edf", b"random junk non-edf header bytes", "application/octet-stream")}
    )
    assert res.status_code == 422
    assert "Invalid EEG" in res.json()["message"] or "Unable to process" in res.json()["message"]


def test_missing_file_payload():
    res = client.post("/api/v1/inference/epieeg")
    assert res.status_code in [400, 422]

# 6. Large File Inference & Performance
def test_large_edf_inference_performance(sample_edfs):
    patient01 = sample_edfs["patient01"]
    if not patient01:
        pytest.skip("Patient_01.edf (56MB) not found.")

    t0 = time.perf_counter()
    res = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("Patient_01.edf", patient01, "application/octet-stream")}
    )
    t1 = time.perf_counter()
    elapsed = t1 - t0

    assert res.status_code == 200
    assert res.json()["status"] == "Success"
    assert elapsed < 30.0, f"Inference took too long: {elapsed:.2f}s"
    print(f"\nPatient_01.edf (56MB) processed in {elapsed:.2f}s")
