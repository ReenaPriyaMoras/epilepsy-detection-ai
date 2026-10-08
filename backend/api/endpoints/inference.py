import os
import sys
import time
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from ml.bonn.inference import predict as bonn_predict
from ml.epieeg.inference import predict_epieeg as epieeg_predict
from core.logger import log_error, log_inference_performance, log_audit
from database.database import insert_analysis

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

class InferenceResult(BaseModel):
    seizure_probability: float
    confidence_score: float
    prediction: str
    status: str
    dataset: str = "Bonn"
    explainability: Optional[dict] = None
    analysis_id: Optional[str] = None
    id: Optional[str] = None

@router.post("/predict", response_model=InferenceResult)
async def predict_eeg(file: UploadFile = File(...)):
    """
    Predict seizure probability from uploaded EEG file (.edf).
    Uses the trained TensorFlow/Keras model.
    """
    if not file.filename or not file.filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="Only EDF files are supported.")
        
    result = await bonn_predict(file)
    if 'dataset' not in result:
        result['dataset'] = "Bonn"
    return result

@router.post("/epieeg", response_model=InferenceResult)
@router.post("/upload", response_model=InferenceResult)
@router.post("/analyze", response_model=InferenceResult)
async def predict_epieeg(file: UploadFile = File(...)):
    """
    Predict seizure probability from uploaded EEG file (.edf) using the EpiEEG model.
    Includes security validations, timeout, and auto-persistence.
    """
    filename = file.filename or ""
    # 1. Extension Validation
    if not filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="Only EDF files are supported.")
        
    # 2. MIME Type Validation
    disallowed_prefixes = ("text/", "image/", "video/", "audio/", "application/x-msdownload", "application/javascript")
    content_type = file.content_type or ""
    if content_type.startswith(disallowed_prefixes):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    t0 = time.perf_counter()
    # Read bytes securely
    file_bytes = await file.read()
    file_size = len(file_bytes)
    t1 = time.perf_counter()
    read_time_ms = (t1 - t0) * 1000
    
    # 3. Empty File Validation
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    # 4. File Size Limit
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Payload Too Large. Max size is 100MB.")

    # 5. Execute with Timeout (30 seconds for complete MNE + GNN + XAI pipeline)
    try:
        t2 = time.perf_counter()
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, epieeg_predict, file_bytes),
            timeout=30.0
        )
        t3 = time.perf_counter()
        processing_time_ms = (t3 - t2) * 1000
        total_time_ms = (t3 - t0) * 1000

        # Invoke Logging and Database Auto-Persistence on Success
        try:
            prediction = result.get("prediction", "Unknown")
            confidence = result.get("confidence_score", 0.0)
            
            saved_record = insert_analysis({
                "filename": filename,
                "file_size": f"{file_size / (1024*1024):.2f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f} KB",
                "prediction": prediction,
                "confidence_score": confidence,
                "seizure_probability": result.get("seizure_probability", 0.0),
                "dataset": result.get("dataset", "EpiEEG"),
                "processing_time": f"{processing_time_ms / 1000:.2f}s",
                "explainability": result.get("explainability"),
            })
            if saved_record and "id" in saved_record:
                result["analysis_id"] = saved_record["id"]
                
            log_audit(filename, prediction, confidence, processing_time_ms, "success")
            log_inference_performance(
                filename, file_size, read_time_ms, 0.0, 0.0, 0.0, total_time_ms, prediction, confidence
            )
        except Exception as ex:
            logging.error(f"Persistence or logging exception: {ex}")
            
        return result
    except asyncio.TimeoutError as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, 15000.0, "timeout")
        except Exception:
            pass
        logging.error(f"Timeout processing file {filename}")
        raise HTTPException(status_code=504, detail="Request timed out while processing the EDF file.")
    except HTTPException as he:
        raise he
    except Exception as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, 0.0, "error")
        except Exception:
            pass
        logging.error(f"Error processing EDF file {filename}: {str(e)}")
        raise HTTPException(status_code=422, detail="Unable to process the uploaded EDF file. It may be corrupted or incorrectly formatted.")
