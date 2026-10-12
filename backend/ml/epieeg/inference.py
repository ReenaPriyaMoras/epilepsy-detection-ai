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

def predict_epieeg(file_bytes: bytes) -> dict:
    """
    Handles EDF bytes, processes clinical EEG window,
    and returns a prediction payload with stage-by-stage telemetry.
    Stateless, leak-free, high-throughput.
    """
    t_start = time.perf_counter()
    ram_start = _get_process_rss_mb()
    logger.info(f"[Stage 1] Received upload | Bytes: {len(file_bytes)} | RAM: {ram_start:.1f}MB")
    
    try:
        loader = EpiEEGModelLoader.load()
        
        # 1. Preprocessing pipeline (EDF header -> Signal load -> Features -> Scaler)
        t0 = time.perf_counter()
        features = preprocess_edf(file_bytes, max_window_seconds=settings.ANALYSIS_WINDOW_SECONDS)
        t_pre = (time.perf_counter() - t0) * 1000
        ram_pre = _get_process_rss_mb()
        logger.info(f"[Stage 4/5] Preprocessing & Scaler complete | Time: {t_pre:.1f}ms | RAM: {ram_pre:.1f}MB")
        
        if features.shape != (43, 17):
            raise ValueError(f"Feature matrix shape mismatch: Expected (43, 17), got {features.shape}")
            
        # 2. PyTorch Tensor Creation & Forward Pass
        t0 = time.perf_counter()
        x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
        device = loader.model.bilstm.weight_ih_l0.device
        x = x.to(device)
        adj_matrix = loader.adj_matrix.to(device)
        logger.info(f"[Stage 6] Tensor created & moved to {device} | Shape: {x.shape}")
        
        with torch.inference_mode():
            output = loader.model(x, adj_matrix)
            raw_prob = output.item() if output.numel() == 1 else output[0].item()
            probability = float(np.clip(raw_prob, 0.0, 1.0))
            
        prediction = "Epileptic" if probability >= loader.threshold else "Non-Epileptic"
        confidence = probability if prediction == "Epileptic" else 1.0 - probability
        confidence = float(np.clip(confidence, 0.0, 1.0))
        t_inf = (time.perf_counter() - t0) * 1000
        ram_inf = _get_process_rss_mb()
        logger.info(f"[Stage 7] Model forward complete | Pred: {prediction} ({confidence:.4f}) | Time: {t_inf:.1f}ms | RAM: {ram_inf:.1f}MB")
        
        # Explicit cleanup of tensors
        del x, adj_matrix, output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # 3. Explainability layer (Step 6: ENABLE_XAI toggle)
        explainability_data = None
        t_xai = 0.0
        if settings.ENABLE_XAI:
            logger.info("[Stage 8] Explainability (Input x Gradient) started...")
            t0 = time.perf_counter()
            try:
                from .explainability import generate_explanation
                explainability_data = generate_explanation(loader, features, prediction)
                t_xai = (time.perf_counter() - t0) * 1000
                ram_xai = _get_process_rss_mb()
                logger.info(f"[Stage 9] Explainability finished | Time: {t_xai:.1f}ms | RAM: {ram_xai:.1f}MB")
            except Exception as e:
                logger.warning(f"Explainability execution error: {str(e)}\n{traceback.format_exc()}")
                explainability_data = None
        else:
            logger.info("[Stage 8/9] Explainability SKIPPED (ENABLE_XAI=False)")
        
        t_total = (time.perf_counter() - t_start) * 1000
        ram_end = _get_process_rss_mb()
        logger.info(
            f"EpiEEG Pipeline Complete: Preprocess={t_pre:.1f}ms | "
            f"Inference={t_inf:.1f}ms | XAI={t_xai:.1f}ms | Total={t_total:.1f}ms | "
            f"RAM: Start={ram_start:.1f}MB -> End={ram_end:.1f}MB (Net: {ram_end - ram_start:+.1f}MB)"
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
        logger.error(f"EpiEEG Validation Error: {str(ve)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=422, detail=f"Invalid EEG signal format: {str(ve)}")
    except Exception as e:
        logger.error(f"EpiEEG Inference Internal Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"EEG analysis failed: {str(e)}")