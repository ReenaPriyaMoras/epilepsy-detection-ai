import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Base directory for logs
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Log file paths
INFERENCE_LOG_FILE = LOGS_DIR / "inference.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
AUDIT_LOG_FILE = LOGS_DIR / "audit.log"

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5
ENCODING = "utf-8"

def _setup_logger(name: str, log_file: Path, level=logging.INFO) -> logging.Logger:
    """Sets up a logger with a rotating file handler."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = RotatingFileHandler(
            str(log_file),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding=ENCODING
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

inference_logger = _setup_logger('inference_logger', INFERENCE_LOG_FILE, logging.INFO)
error_logger = _setup_logger('error_logger', ERROR_LOG_FILE, logging.ERROR)
audit_logger = _setup_logger('audit_logger', AUDIT_LOG_FILE, logging.INFO)

def log_error(exception: Exception, filename: str = "Unknown"):
    """Safely logs an error to the error file without interrupting execution."""
    try:
        error_logger.error(
            f"File: {filename} | Exception Type: {type(exception).__name__} | "
            f"Message: {str(exception)}",
            exc_info=True
        )
    except Exception:
        pass

def log_inference_performance(
    filename: str,
    file_size: int,
    read_time: float,
    preprocess_time: float,
    inference_time: float,
    xai_time: float,
    total_time: float,
    prediction: str,
    confidence: float
):
    """Safely logs performance metrics to the inference log."""
    try:
        inference_logger.info(
            f"File: {filename} | Size: {file_size}B | Prediction: {prediction} | Conf: {confidence:.4f} | "
            f"Times(ms) - Read: {read_time:.2f}, Preprocess: {preprocess_time:.2f}, "
            f"Inference: {inference_time:.2f}, XAI: {xai_time:.2f}, Total: {total_time:.2f}"
        )
    except Exception:
        pass

def log_audit(filename: str, prediction: str, confidence: float, processing_time: float, status: str = "success"):
    """Logs an audit record to the audit log."""
    try:
        audit_logger.info(
            f"AUDIT | File: {filename} | Prediction: {prediction} | "
            f"Confidence: {confidence:.4f} | Time(ms): {processing_time:.2f} | Status: {status}"
        )
    except Exception:
        pass
