# Production Multi-Layer Dockerfile for EpiDetect AI Backend
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PORT=8000

WORKDIR /app

# Install OS dependencies for C/C++ extensions, SciPy, MNE and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Layer 1: Python Dependencies (Cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: Application Source
COPY backend/ /app/backend/

# Layer 3: Security & Non-Root Execution
RUN useradd -m -u 10001 appuser && \
    mkdir -p /app/backend/logs && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app/backend

EXPOSE 8000

# Native Python Healthcheck (Zero external dependencies)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request, os; sys_port = os.environ.get('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{sys_port}/health', timeout=3)" || exit 1

# Start FastAPI server using uvicorn binding dynamically to $PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
