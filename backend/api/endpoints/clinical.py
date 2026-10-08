from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
import datetime

router = APIRouter()

class LoginRequest(BaseModel):
    doctorId: Optional[str] = "Doctor"
    email: Optional[str] = None
    password: Optional[str] = ""

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class PatientRecord(BaseModel):
    name: str
    age: Optional[str] = None
    gender: Optional[str] = None
    notes: Optional[str] = None

class PrescriptionRequest(BaseModel):
    patientId: Optional[str] = "PT-001"
    diagnosis: Optional[str] = "Epileptic"
    notes: Optional[str] = ""

@router.get("/health")
@router.get("/status")
def get_health():
    return {
        "status": "healthy",
        "service": "Epilepsy Detection AI",
        "version": "2.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@router.get("/settings")
def get_settings():
    return {
        "status": "success",
        "model_architecture": "GNN-BiLSTM-BiGRU",
        "model_version": "v2.0.0-clinical",
        "sampling_rate": 256,
        "supported_formats": ["EDF", "EDF+"],
        "max_channels": 43,
        "threshold": 0.5,
        "explainability_engine": "Input*Gradient"
    }

@router.get("/documentation")
@router.get("/docs-info")
def get_documentation():
    return {
        "status": "success",
        "overview": "Clinical AI decision support system for EEG-based epilepsy diagnosis.",
        "pipeline": [
            "EDF File Ingestion",
            "Vectorized Preprocessing (43 Channels)",
            "17-Statistical Feature Extraction",
            "Standard Normalization",
            "GNN-BiLSTM-BiGRU Inference",
            "Input*Gradient Explainability",
            "Clinical PDF & Report Generation"
        ]
    }

@router.get("/reports")
@router.get("/report")
def get_reports():
    return {
        "status": "success",
        "data": [
            {
                "id": "RPT-001",
                "patientId": "PT-2026-0942",
                "date": datetime.date.today().isoformat(),
                "prediction": "Seizure Detected",
                "risk": "High",
                "status": "Reviewed"
            },
            {
                "id": "RPT-002",
                "patientId": "PT-2026-0811",
                "date": datetime.date.today().isoformat(),
                "prediction": "Normal EEG",
                "risk": "Low",
                "status": "Pending"
            }
        ]
    }

@router.post("/prescription")
@router.get("/prescription")
def handle_prescription(data: Optional[PrescriptionRequest] = None):
    return {
        "status": "success",
        "message": "Prescription recommendations generated based on neurological guidelines.",
        "guidelines": [
            "Review full EEG multichannel traces before pharmacological intervention.",
            "Consider standard AED therapeutic titration (e.g. Levetiracetam / Lamotrigine) as clinically indicated.",
            "Schedule follow-up ambulatory video-EEG monitoring within 30 days."
        ]
    }

@router.post("/login")
@router.post("/auth/login")
def login(req: Optional[LoginRequest] = None):
    doc_id = req.doctorId if req and req.doctorId else "Doctor"
    return {
        "status": "success",
        "token": "clinical-jwt-token-demo",
        "doctorName": f"Dr. {doc_id}",
        "role": "Neurologist"
    }

@router.post("/register")
@router.post("/auth/register")
def register(req: Optional[RegisterRequest] = None):
    return {
        "status": "success",
        "message": "Clinical account created successfully.",
        "userId": "usr-2026-01"
    }

@router.post("/patients")
@router.post("/patient")
def register_patient(patient: Optional[PatientRecord] = None):
    name = patient.name if patient else "New Patient"
    return {
        "status": "success",
        "message": f"Patient profile for {name} saved successfully.",
        "patientId": "PT-2026-0942"
    }
