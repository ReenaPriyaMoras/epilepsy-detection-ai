import os
import sys
import time
import psutil
import platform
import logging
import traceback
import torch
import numpy as np
from fastapi import APIRouter, HTTPException

from core.config import settings

logger = logging.getLogger("inference_logger")
router = APIRouter()

START_TIME = time.time()

def _get_process_rss_mb() -> float:
    try:
        return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    except Exception:
        return 0.0

@router.get("/system")
def debug_system():
    """
    Returns live system diagnostics, hardware memory, versions, and configuration.
    """
    vm = psutil.virtual_memory()
    epieeg_loaded = False
    bonn_loaded = False
    
    try:
        from ml.epieeg.model import EpiEEGModelLoader
        loader = EpiEEGModelLoader.load()
        epieeg_loaded = loader.model is not None
    except Exception:
        pass
        
    try:
        from ml.bonn.model import model_loader
        bonn_loaded = model_loader.get_model() is not None
    except Exception:
        pass

    db_status = "connected"
    try:
        from database.database import get_dashboard_stats
        get_dashboard_stats()
    except Exception:
        db_status = "disconnected"

    proc_rss = round(_get_process_rss_mb(), 2)
    avail_ram = round(vm.available / (1024 * 1024), 2)
    cpu_usage = psutil.cpu_percent()
    uptime = round(time.time() - START_TIME, 2)

    return {
        "status": "online",
        "worker_uptime": uptime,
        "uptime_seconds": uptime,
        "worker_pid": os.getpid(),
        "application_version": settings.APP_VERSION,
        "app_version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database_connectivity": db_status,
        "model_loaded_status": {
            "epieeg_gnn_bilstm_bigru": epieeg_loaded,
            "bonn": bonn_loaded,
            "all_loaded": epieeg_loaded and bonn_loaded
        },
        "process_rss": f"{proc_rss} MB",
        "process_rss_mb": proc_rss,
        "available_ram": f"{avail_ram} MB",
        "available_ram_mb": avail_ram,
        "cpu_usage": f"{cpu_usage}%",
        "cpu_usage_pct": cpu_usage,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "memory": {
            "process_rss_mb": proc_rss,
            "system_total_mb": round(vm.total / (1024 * 1024), 2),
            "system_available_mb": avail_ram,
            "system_used_percent": vm.percent,
        },
        "cpu": {
            "cpu_percent": cpu_usage,
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False),
        },
        "pytorch": {
            "torch_version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        },
        "models": {
            "epieeg_gnn_bilstm_bigru_loaded": epieeg_loaded,
            "bonn_model_loaded": bonn_loaded,
        },
        "config": {
            "ENABLE_XAI": settings.ENABLE_XAI,
            "ANALYSIS_WINDOW_SECONDS": settings.ANALYSIS_WINDOW_SECONDS,
            "INFERENCE_TIMEOUT_SECONDS": settings.INFERENCE_TIMEOUT_SECONDS,
            "MAX_UPLOAD_FILE_SIZE_MB": settings.MAX_UPLOAD_FILE_SIZE_MB,
            "DATABASE_CONFIGURED": settings.DATABASE_URL is not None,
        }
    }

@router.get("/inference")
@router.post("/inference")
def debug_inference():
    """
    Executes a synthetic synthetic inference without requiring an EDF file.
    Measures tensor allocation, forward pass, explainability, and memory deltas.
    """
    ram_start = _get_process_rss_mb()
    t_start = time.perf_counter()
    
    try:
        from ml.epieeg.model import EpiEEGModelLoader
        loader = EpiEEGModelLoader.load()
        
        # 1. Synthetic 43-channel, 17-feature tensor
        t0 = time.perf_counter()
        synthetic_features = np.random.randn(43, 17).astype(np.float32)
        x = torch.tensor(synthetic_features, dtype=torch.float32).unsqueeze(0)
        device = loader.model.bilstm.weight_ih_l0.device
        x = x.to(device)
        adj_matrix = loader.adj_matrix.to(device)
        t_tensor = (time.perf_counter() - t0) * 1000
        
        # 2. Forward pass
        t0 = time.perf_counter()
        with torch.inference_mode():
            output = loader.model(x, adj_matrix)
            prob = float(output.item() if output.numel() == 1 else output[0].item())
        pred = "Epileptic" if prob >= loader.threshold else "Non-Epileptic"
        t_forward = (time.perf_counter() - t0) * 1000
        
        # 3. Explainability
        t_xai = 0.0
        xai_result = None
        if settings.ENABLE_XAI:
            t0 = time.perf_counter()
            from ml.epieeg.explainability import generate_explanation
            xai_result = generate_explanation(loader, synthetic_features, pred)
            t_xai = (time.perf_counter() - t0) * 1000
            
        t_total = (time.perf_counter() - t_start) * 1000
        ram_end = _get_process_rss_mb()
        
        # Clean up
        del x, adj_matrix, output
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return {
            "status": "success",
            "test_type": "synthetic_epieeg_inference",
            "prediction": pred,
            "probability": round(prob, 4),
            "timings_ms": {
                "tensor_creation_ms": round(t_tensor, 2),
                "model_forward_ms": round(t_forward, 2),
                "explainability_ms": round(t_xai, 2),
                "total_inference_ms": round(t_total, 2)
            },
            "memory_mb": {
                "ram_start_mb": round(ram_start, 2),
                "ram_end_mb": round(ram_end, 2),
                "ram_delta_mb": round(ram_end - ram_start, 2)
            },
            "explainability_executed": xai_result is not None
        }
    except Exception as e:
        logger.error(f"Debug synthetic inference failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Synthetic inference failed: {str(e)}")
