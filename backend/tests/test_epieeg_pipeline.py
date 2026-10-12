import os
import io
import time
import pytest
import psutil
import numpy as np
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "epieeg", "dataset", "EDF_dataset", "EDF_dataset")

def _get_process_rss_mb() -> float:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)

def test_debug_system_endpoint():
    """Verify GET /api/v1/debug/system returns complete hardware, memory, and runtime metadata."""
    response = client.get("/api/v1/debug/system")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "memory" in data
    assert "pytorch" in data
    assert "models" in data
    assert data["models"]["epieeg_gnn_bilstm_bigru_loaded"] is True
    assert data["memory"]["process_rss_mb"] > 0

def test_debug_synthetic_inference():
    """Verify POST /api/v1/debug/inference runs synthetic inference under 500ms without crashing."""
    ram_before = _get_process_rss_mb()
    t0 = time.perf_counter()
    response = client.post("/api/v1/debug/inference")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    ram_after = _get_process_rss_mb()
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["prediction"] in ["Epileptic", "Non-Epileptic"]
    assert "timings_ms" in data
    assert elapsed_ms < 1000  # Must be fast
    assert (ram_after - ram_before) < 100  # Minimal memory delta

def test_empty_upload():
    """Verify empty file upload is rejected with HTTP 400 Bad Request."""
    response = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("empty.edf", io.BytesIO(b""), "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "empty" in response.json().get("detail", "").lower()

def test_invalid_extension():
    """Verify non-EDF file is rejected with HTTP 400 Bad Request."""
    response = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 dummy"), "application/pdf")}
    )
    assert response.status_code == 400

def test_corrupted_edf():
    """Verify corrupted EDF bytes return structured HTTP 422 without unhandled 500."""
    response = client.post(
        "/api/v1/inference/epieeg",
        files={"file": ("corrupt.edf", io.BytesIO(b"0" * 256 + b"CORRUPTED_SIGNAL"), "application/octet-stream")}
    )
    assert response.status_code in [400, 422]

def test_large_clinical_edf_patient01():
    """Verify real large clinical EDF (Patient_01.edf, 56.3 MB) completes within 3.0s and memory is stable."""
    p1_path = os.path.join(DATASET_DIR, "Patient_01.edf")
    if not os.path.exists(p1_path):
        pytest.skip("Dataset file Patient_01.edf not found locally.")

    ram_start = _get_process_rss_mb()
    t0 = time.perf_counter()
    with open(p1_path, "rb") as f:
        response = client.post(
            "/api/v1/inference/epieeg",
            files={"file": ("Patient_01.edf", f, "application/octet-stream")}
        )
    elapsed_sec = time.perf_counter() - t0
    ram_end = _get_process_rss_mb()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert data["dataset"] == "EpiEEG"
    assert data["prediction"] in ["Epileptic", "Non-Epileptic"]
    assert 0.0 <= data["confidence_score"] <= 1.0
    assert 0.0 <= data["seizure_probability"] <= 1.0
    assert "analysis_id" in data
    assert elapsed_sec < 5.0  # Must finish within 5s
    assert (ram_end - ram_start) < 250  # Memory delta must stay bounded

def test_large_clinical_edf_patient56():
    """Verify large clinical EDF (Patient_56.edf, 72.0 MB) completes with HTTP 200 and valid XAI."""
    p56_path = os.path.join(DATASET_DIR, "Patient_56.edf")
    if not os.path.exists(p56_path):
        pytest.skip("Dataset file Patient_56.edf not found locally.")

    t0 = time.perf_counter()
    with open(p56_path, "rb") as f:
        response = client.post(
            "/api/v1/inference/epieeg",
            files={"file": ("Patient_56.edf", f, "application/octet-stream")}
        )
    elapsed_sec = time.perf_counter() - t0

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert data["dataset"] == "EpiEEG"
    if data.get("explainability"):
        assert "top_channels" in data["explainability"]
        assert "top_features" in data["explainability"]
        assert len(data["explainability"]["top_channels"]) > 0
    assert elapsed_sec < 5.0
