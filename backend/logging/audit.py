import json
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os
import sys
sys.path.append(os.path.dirname(__file__))
from config import AUDIT_LOG_FILE, MAX_BYTES, BACKUP_COUNT, ENCODING

def setup_audit_logger() -> logging.Logger:
    """Sets up the audit logger to output pure JSON strings without standard formatting."""
    logger = logging.getLogger("audit_logger")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = RotatingFileHandler(
            str(AUDIT_LOG_FILE),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding=ENCODING
        )
        # Just the message so we can log pure JSON
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

audit_logger = setup_audit_logger()

def log_audit(
    filename: str,
    prediction: str,
    confidence: float,
    processing_time_ms: float,
    status: str
):
    """
    Safely logs a JSON audit record.
    Keys must not contain patient PII.
    """
    try:
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "filename": filename,
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "processing_time_ms": round(processing_time_ms, 2),
            "status": status
        }
        audit_logger.info(json.dumps(record))
    except Exception:
        pass  # Never interrupt execution for logging failures
