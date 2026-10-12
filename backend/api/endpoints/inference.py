import os
import sys
import time
import psutil
import asyncio
import logging
import traceback
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel

from ml.bonn.inference import predict_bonn
from ml.epieeg.inference import predict_epieeg as epieeg_predict
from core.logger import log_error, log_inference_performance, log_audit
from core.config import settings
from database.database import insert_analysis

logger = logging.getLogger("inference_logger")
router = APIRouter()

MAX_FILE_SIZE = settings.MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024  # Default 100 MB
DISALLOWED_MIME_PREFIXES = (
    "text/", "image/", "video/", "audio/",
    "application/x-msdownload", "application/javascript"
)

def _get_process_rss_mb() -> float:
    try:
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0

class InferenceResult(BaseModel):
    seizure_probability: float
    confidence_score: float
    prediction: str
    status: str
    dataset: str = "Bonn"
    explainability: Optional[dict] = None
    analysis_id: Optional[str] = None
    id: Optional[str] = None
    request_id: Optional[str] = None

async def _read_and_validate_edf(file: UploadFile) -> tuple[bytes, str, int]:
    """Securely reads and validates uploaded EDF file without blocking."""
    filename = file.filename or "recording.edf"
    
    # 1. Extension Validation
    if not filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="Only EDF files (.edf) are supported.")
        
    # 2. MIME Type Validation
    content_type = file.content_type or ""
    if content_type.startswith(DISALLOWED_MIME_PREFIXES):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # 3. Read bytes
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    # 4. Empty File Validation
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    # 5. File Size Limit
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Payload Too Large. Max size is {settings.MAX_UPLOAD_FILE_SIZE_MB}MB."
        )

    return file_bytes, filename, file_size

@router.post("/predict", response_model=InferenceResult)
async def predict_eeg(request: Request, file: UploadFile = File(...)):
    """
    Predict seizure probability from uploaded EEG file (.edf) using the Bonn dataset model.
    Runs asynchronously in thread pool with timeout and auto-persistence.
    """
    req_id = getattr(request.state, "request_id", "N/A")
    t0 = time.perf_counter()
    file_bytes, filename, file_size = await _read_and_validate_edf(file)
    t1 = time.perf_counter()
    read_time_ms = (t1 - t0) * 1000

    try:
        t2 = time.perf_counter()
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, predict_bonn, file_bytes),
            timeout=settings.INFERENCE_TIMEOUT_SECONDS
        )
        t3 = time.perf_counter()
        processing_time_ms = (t3 - t2) * 1000
        total_time_ms = (t3 - t0) * 1000

        # Auto-persistence and logging
        try:
            prediction = result.get("prediction", "Unknown")
            confidence = result.get("confidence_score", 0.0)
            
            saved_record = insert_analysis({
                "filename": filename,
                "file_size": f"{file_size / (1024*1024):.2f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.1f} KB",
                "prediction": prediction,
                "confidence_score": confidence,
                "seizure_probability": result.get("seizure_probability", 0.0),
                "dataset": "Bonn",
                "processing_time": f"{processing_time_ms / 1000:.2f}s",
                "explainability": None,
            })
            if saved_record and "id" in saved_record:
                result["analysis_id"] = saved_record["id"]
                result["id"] = saved_record["id"]
                
            result["request_id"] = req_id
            log_audit(filename, prediction, confidence, processing_time_ms, "success")
            log_inference_performance(
                filename, file_size, read_time_ms, 0.0, processing_time_ms, 0.0, total_time_ms, prediction, confidence
            )
        except Exception as ex:
            logger.error(f"Persistence error (Bonn): {ex}\n{traceback.format_exc()}")

        if 'dataset' not in result:
            result['dataset'] = "Bonn"
        return result

    except asyncio.TimeoutError as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, settings.INFERENCE_TIMEOUT_SECONDS * 1000, "timeout")
        except Exception:
            pass
        logger.error(f"[Req: {req_id}] Timeout processing Bonn file {filename}\n{traceback.format_exc()}")
        raise HTTPException(status_code=504, detail=f"Request timed out processing EDF file (Request ID: {req_id})")
    except HTTPException as he:
        raise he
    except Exception as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, 0.0, "error")
        except Exception:
            pass
        logger.error(f"[Req: {req_id}] Error processing Bonn EDF file {filename}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Unable to process EDF file: {str(e)} (Request ID: {req_id})")

@router.post("/epieeg", response_model=InferenceResult)
@router.post("/upload", response_model=InferenceResult)
@router.post("/analyze", response_model=InferenceResult)
async def predict_epieeg(request: Request, file: UploadFile = File(...)):
    """
    Predict seizure probability from uploaded EEG file (.edf) using the EpiEEG model.
    Includes security validations, timeout, and auto-persistence with stage telemetry.
    """
    req_id = getattr(request.state, "request_id", "N/A")
    t0 = time.perf_counter()
    ram_req_start = _get_process_rss_mb()
    logger.info(f"[Req: {req_id}] Endpoint /epieeg invoked | RAM: {ram_req_start:.1f}MB")

    file_bytes, filename, file_size = await _read_and_validate_edf(file)
    t1 = time.perf_counter()
    read_time_ms = (t1 - t0) * 1000
    ram_after_upload = _get_process_rss_mb()
    logger.info(f"[Req: {req_id}] File uploaded: {filename} ({file_size}B) | Read Time: {read_time_ms:.1f}ms | RAM: {ram_after_upload:.1f}MB")

    # Execute with Timeout in thread pool
    try:
        t2 = time.perf_counter()
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, epieeg_predict, file_bytes),
            timeout=settings.INFERENCE_TIMEOUT_SECONDS
        )
        t3 = time.perf_counter()
        processing_time_ms = (t3 - t2) * 1000

        # Stage 10: Database Auto-Persistence
        t_db_start = time.perf_counter()
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
                result["id"] = saved_record["id"]
                
            t_db = (time.perf_counter() - t_db_start) * 1000
            ram_db = _get_process_rss_mb()
            logger.info(f"[Stage 10] Database saved ID: {result.get('id')} | Time: {t_db:.1f}ms | RAM: {ram_db:.1f}MB")
            
            result["request_id"] = req_id
            log_audit(filename, prediction, confidence, processing_time_ms, "success")
            log_inference_performance(
                filename, file_size, read_time_ms, 0.0, processing_time_ms, 0.0, (t3 - t0) * 1000, prediction, confidence
            )
        except Exception as ex:
            logger.error(f"[Req: {req_id}] Persistence notice (EpiEEG): {ex}\n{traceback.format_exc()}")
            
        # Stage 11: Response return
        total_time_ms = (time.perf_counter() - t0) * 1000
        ram_final = _get_process_rss_mb()
        logger.info(f"[Stage 11] Response returned | Total: {total_time_ms:.1f}ms | RAM: {ram_final:.1f}MB")
        return result

    except asyncio.TimeoutError as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, settings.INFERENCE_TIMEOUT_SECONDS * 1000, "timeout")
        except Exception:
            pass
        logger.error(f"[Req: {req_id}] Timeout processing file {filename} after {settings.INFERENCE_TIMEOUT_SECONDS}s\n{traceback.format_exc()}")
        raise HTTPException(status_code=504, detail=f"Request timed out processing EDF file (Request ID: {req_id})")
    except HTTPException as he:
        raise he
    except Exception as e:
        try:
            log_error(e, filename)
            log_audit(filename, "N/A", 0.0, 0.0, "error")
        except Exception:
            pass
        logger.error(f"[Req: {req_id}] Error processing EDF file {filename}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Unable to process EDF file: {str(e)} (Request ID: {req_id})")
