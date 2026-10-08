import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.logger import (
    INFERENCE_LOG_FILE,
    ERROR_LOG_FILE,
    AUDIT_LOG_FILE,
    inference_logger,
    error_logger,
    audit_logger
)

client = TestClient(app)

def test_log_files_created():
    # Trigger an inference request with empty file to test validation
    response = client.post("/api/v1/inference/epieeg", files={"file": ("test.edf", b"", "application/octet-stream")})
    assert response.status_code == 400
    
    assert Path(ERROR_LOG_FILE).parent.exists()
    assert Path(INFERENCE_LOG_FILE).parent.exists()
    assert Path(AUDIT_LOG_FILE).parent.exists()

def test_rotation_configuration():
    from logging.handlers import RotatingFileHandler
    
    # Check if a RotatingFileHandler exists on inference_logger
    has_rotating_handler = any(isinstance(h, RotatingFileHandler) for h in inference_logger.handlers)
    assert has_rotating_handler, "RotatingFileHandler is not configured properly."
    
    # Check maxBytes and backupCount
    for h in inference_logger.handlers:
        if isinstance(h, RotatingFileHandler):
            assert h.maxBytes == 10 * 1024 * 1024
            assert h.backupCount == 5

def test_prediction_unaffected():
    # Health endpoint verification
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "model" in data

def test_error_logging_works():
    # Trigger a 422 with corrupt EDF
    response = client.post("/api/v1/inference/epieeg", files={"file": ("corrupt.edf", b"corrupted_bytes_that_fail_mne", "application/octet-stream")})
    assert response.status_code == 422
    
    # Check if ERROR_LOG_FILE exists
    assert Path(ERROR_LOG_FILE).exists()

def test_audit_logging_works():
    # Check if AUDIT_LOG_FILE exists
    assert Path(AUDIT_LOG_FILE).exists()
