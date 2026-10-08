import os
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

# Rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5
ENCODING = "utf-8"
