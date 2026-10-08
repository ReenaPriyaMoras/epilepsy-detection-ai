import os
import glob
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Adjust path to import main app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_edfs(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("test_edfs")
    
    # Locate an existing valid EDF file from the dataset
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "epieeg", "dataset")
    discovered_edfs = glob.glob(os.path.join(dataset_dir, "**", "*.edf"), recursive=True)
    valid_edf = discovered_edfs[0] if discovered_edfs else None
    
    # Invalid file (not an EDF)
    invalid_edf = tmp_dir / "invalid.txt"
    invalid_edf.write_text("This is not an EDF file.")
    
    # Corrupted EDF (fake EDF extension but wrong bytes)
    corrupted_edf = tmp_dir / "corrupted.edf"
    corrupted_edf.write_bytes(b"0" * 1024)
    
    # Empty EDF
    empty_edf = tmp_dir / "empty.edf"
    empty_edf.write_bytes(b"")
    
    return {
        "valid": valid_edf,
        "invalid_ext": str(invalid_edf),
        "corrupted": str(corrupted_edf),
        "empty": str(empty_edf),
    }

def test_valid_edf(setup_edfs):
    if not setup_edfs["valid"] or not os.path.exists(setup_edfs["valid"]):
        pytest.skip("No sample EDF found in dataset directory for full inference test.")
    with open(setup_edfs["valid"], "rb") as f:
        response = client.post("/api/v1/inference/epieeg", files={"file": ("valid.edf", f, "application/octet-stream")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Success"
    assert "prediction" in data
    assert "confidence_score" in data
    assert "seizure_probability" in data
    assert data["dataset"] == "EpiEEG"

def test_invalid_extension(setup_edfs):
    with open(setup_edfs["invalid_ext"], "rb") as f:
        response = client.post("/api/v1/inference/epieeg", files={"file": ("invalid.txt", f, "text/plain")})
    assert response.status_code == 400

def test_corrupted_edf(setup_edfs):
    with open(setup_edfs["corrupted"], "rb") as f:
        response = client.post("/api/v1/inference/epieeg", files={"file": ("corrupted.edf", f, "application/octet-stream")})
    assert response.status_code in [400, 422, 500]

def test_empty_edf(setup_edfs):
    with open(setup_edfs["empty"], "rb") as f:
        response = client.post("/api/v1/inference/epieeg", files={"file": ("empty.edf", f, "application/octet-stream")})
    assert response.status_code in [400, 422, 500]

def test_missing_file():
    response = client.post("/api/v1/inference/epieeg")
    assert response.status_code in [400, 422]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "model" in data

