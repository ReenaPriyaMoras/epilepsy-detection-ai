import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from core.security import create_access_token, decode_access_token, verify_password, get_password_hash

client = TestClient(app)

def test_jwt_token_creation_and_decoding():
    payload = {"sub": "DOC-99", "role": "Neurologist", "email": "doc@hospital.org"}
    token = create_access_token(payload)
    assert isinstance(token, str)
    assert len(token) > 20

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "DOC-99"
    assert decoded["role"] == "Neurologist"
    assert "exp" in decoded

def test_invalid_jwt_token_decoding():
    invalid_token = "invalid.bearer.token.string"
    decoded = decode_access_token(invalid_token)
    assert decoded is None

def test_password_hashing():
    pwd = "SecureClinicalPassword2026!"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_auth_login_endpoint():
    res = client.post("/api/v1/auth/login", json={"doctorId": "TestNeurologist", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "token" in data
    assert "doctorName" in data
    
    # Verify token payload
    decoded = decode_access_token(data["token"])
    assert decoded is not None
    assert decoded["sub"] == "TestNeurologist"

def test_auth_register_endpoint():
    res = client.post("/api/v1/auth/register", json={
        "name": "Dr. Sarah Connor",
        "email": "sarah@neurology.org",
        "password": "ClinicalPassword2026"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "token" in data
    assert "userId" in data

def test_request_id_and_security_headers():
    res = client.get("/")
    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert "x-response-time-ms" in res.headers
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
    assert res.headers["referrer-policy"] == "no-referrer"
