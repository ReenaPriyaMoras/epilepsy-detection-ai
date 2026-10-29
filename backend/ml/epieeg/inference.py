import os
import time
import psutil
import logging
import traceback
import torch
import numpy as np
from fastapi import HTTPException

from core.config import settings
from .model import EpiEEGModelLoader
from .preprocessing import preprocess_edf

logger = logging.getLogger("inference_logger")

def _get_process_rss_mb() -> float:
    try:
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0

from core.telemetry import log_stage_telemetry

def predict_epieeg(file_bytes: bytes, req_id: str = "N/A") -> dict:
    """
    Handles EDF bytes, processes clinical EEG window,
    and returns a prediction payload with stage-by-stage telemetry.
    Stateless, leak-free, high-throughput.
    """
    t_start = time.perf_counter()
    
    try:
        loader = EpiEEGModelLoader.load()
        
        # 1. Preprocessing pipeline (EDF header -> Signal load -> Features -> Scaler)
        t0 = time.perf_counter()
        features = preprocess_edf(
            file_bytes,
            max_window_seconds=settings.ANALYSIS_WINDOW_SECONDS,
            req_id=req_id
        )
        t_pre = (time.perf_counter() - t0) * 1000
        
        if features.shape != (43, 17):
            raise ValueError(f"Feature matrix shape mismatch: Expected (43, 17), got {features.shape}")
            
        # 2. PyTorch Tensor Creation & Forward Pass
        t0 = time.perf_counter()
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        device = loader.model.bilstm.weight_ih_l0.device
        x = x.to(device)
        adj_matrix = loader.adj_matrix.to(device)
        t_tensor = (time.perf_counter() - t0) * 1000
        log_stage_telemetry(
            "Tensor creation",
            req_id=req_id,
            duration_ms=t_tensor,
            extra=f"Shape={x.shape} | Device={device}"
        )
        
        t0 = time.perf_counter()
        with torch.inference_mode():
            output = loader.model(x, adj_matrix)
            raw_prob = output.item() if output.numel() == 1 else output[0].item()
            probability = float(np.clip(raw_prob, 0.0, 1.0))
            
        prediction = "Epileptic" if probability >= loader.threshold else "Non-Epileptic"
        confidence = probability if prediction == "Epileptic" else 1.0 - probability
        confidence = float(np.clip(confidence, 0.0, 1.0))
        t_inf = (time.perf_counter() - t0) * 1000
        log_stage_telemetry(
            "Model inference",
            req_id=req_id,
            duration_ms=t_inf,
            extra=f"Pred={prediction} | Prob={probability:.4f} | Conf={confidence:.4f}"
        )
        
        # Explicit cleanup of tensors
        del x, adj_matrix, output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # 3. Explainability layer (Step 6: ENABLE_XAI toggle)
        explainability_data = None
        t_xai = 0.0
        if settings.ENABLE_XAI:
            t0 = time.perf_counter()
            try:
                from .explainability import generate_explanation
                explainability_data = generate_explanation(loader, features, prediction)
                t_xai = (time.perf_counter() - t0) * 1000
                top_ch = explainability_data.get("top_channels", [{}])[0].get("name", "N/A") if explainability_data else "N/A"
                top_ft = explainability_data.get("top_features", [{}])[0].get("name", "N/A") if explainability_data else "N/A"
                log_stage_telemetry(
                    "Explainability",
                    req_id=req_id,
                    duration_ms=t_xai,
                    extra=f"TopChannel={top_ch} | TopFeature={top_ft}"
                )
            except Exception as e:
                log_stage_telemetry("Explainability error", req_id=req_id, error=e)
                explainability_data = None
        else:
            log_stage_telemetry(
                "Explainability",
                req_id=req_id,
                duration_ms=0.0,
                extra="Skipped (ENABLE_XAI=False)"
            )
        
        t_total = (time.perf_counter() - t_start) * 1000
        log_stage_telemetry(
            "Inference pipeline complete",
            req_id=req_id,
            duration_ms=t_total,
            extra=f"Pre={t_pre:.1f}ms | Inf={t_inf:.1f}ms | XAI={t_xai:.1f}ms | Total={t_total:.1f}ms"
        )
            
        return {
            "status": "Success",
            "prediction": prediction,
            "confidence_score": float(round(confidence, 4)),
            "seizure_probability": float(round(probability, 4)),
            "dataset": "EpiEEG",
            "explainability": explainability_data
        }
    except ValueError as ve:
        log_stage_telemetry("EpiEEG Validation Error", req_id=req_id, error=ve)
        raise HTTPException(status_code=422, detail=f"Invalid EEG signal format: {str(ve)}")
    except Exception as e:
        log_stage_telemetry("EpiEEG Inference Internal Error", req_id=req_id, error=e)
        raise HTTPException(status_code=500, detail=f"EEG analysis failed: {str(e)}")