import logging
from logging.handlers import RotatingFileHandler
import os
import sys
sys.path.append(os.path.dirname(__file__))
from config import INFERENCE_LOG_FILE, ERROR_LOG_FILE, MAX_BYTES, BACKUP_COUNT, ENCODING

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Sets up a logger with a rotating file handler."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent adding multiple handlers if logger is already configured
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_file,
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

inference_logger = setup_logger('inference_logger', str(INFERENCE_LOG_FILE), logging.INFO)
error_logger = setup_logger('error_logger', str(ERROR_LOG_FILE), logging.ERROR)

def log_error(exception: Exception, filename: str = "Unknown"):
    """Safely logs an error to the error file without interrupting execution."""
    try:
        error_logger.error(
            f"File: {filename} | Exception Type: {type(exception).__name__} | "
            f"Message: {str(exception)}",
            exc_info=True
        )
    except Exception:
        pass  # Never interrupt execution for logging failures

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
