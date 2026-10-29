import os
import time
import psutil
import threading
import logging
import traceback
from typing import Optional, Dict, Any

logger = logging.getLogger("inference_logger")

def get_telemetry_snapshot() -> Dict[str, Any]:
    """Captures instant process memory, CPU, PID, and Thread ID."""
    try:
        proc = psutil.Process(os.getpid())
        rss_mb = proc.memory_info().rss / (1024 * 1024)
        cpu_pct = proc.cpu_percent(interval=None)
    except Exception:
        rss_mb = 0.0
        cpu_pct = 0.0

    pid = os.getpid()
    try:
        tid = threading.get_native_id()
    except AttributeError:
        tid = threading.get_ident()

    return {
        "rss_mb": round(rss_mb, 2),
        "cpu_pct": round(cpu_pct, 1),
        "pid": pid,
        "tid": tid
    }

def log_stage_telemetry(
    stage: str,
    req_id: str = "N/A",
    duration_ms: float = 0.0,
    extra: str = "",
    error: Optional[Exception] = None
):
    """
    Standardized production telemetry logger for all inference stages.
    Logs: Stage, Request ID, Duration, RSS, CPU, PID, TID, Extra info, and Traceback if error.
    """
    snap = get_telemetry_snapshot()
    msg = (
        f"[Req: {req_id}] [Stage: {stage}] "
        f"PID={snap['pid']} TID={snap['tid']} "
        f"RSS={snap['rss_mb']:.1f}MB CPU={snap['cpu_pct']:.1f}% "
        f"Duration={duration_ms:.2f}ms"
    )
    if extra:
        msg += f" | {extra}"

    if error is not None:
        logger.error(f"{msg} | Exception: {str(error)}\n{traceback.format_exc()}")
    else:
        logger.info(msg)
