import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from api.router import api_router
from core.config import settings

# Set up safe centralized logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Production startup telemetry & resource verification:
    - Step 7: Deployment verification (Git version, timestamp, checksums, hardware, versions)
    - Verifies database connectivity and initializes tables/indices
    - Pre-warms PyTorch GNN-BiLSTM-BiGRU singleton model into memory
    """
    import os
    import psutil
    import platform
    import hashlib
    import datetime
    import torch
    import mne
    import numpy as np
    
    vm = psutil.virtual_memory()
    deploy_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    logger.info("=================================================================")
    logger.info(f"🚀 EpiDetect AI Backend Starting | Environment: {settings.ENVIRONMENT}")
    logger.info(f"📦 Version: {settings.APP_VERSION} | Deployment Timestamp: {deploy_time}")
    logger.info(f"⚙️  Worker PID: {os.getpid()} | Platform: {platform.platform()} | Python: {platform.python_version()}")
    logger.info(f"🧠 Runtimes: PyTorch={torch.__version__} (CUDA: {torch.cuda.is_available()}) | MNE={mne.__version__} | NumPy={np.__version__}")
    logger.info(f"💾 System RAM: Total={vm.total / (1024*1024):.1f}MB | Available={vm.available / (1024*1024):.1f}MB | Process RSS={psutil.Process(os.getpid()).memory_info().rss / (1024*1024):.1f}MB")
    logger.info(f"🔧 Config: Window={settings.ANALYSIS_WINDOW_SECONDS}s | XAI={settings.ENABLE_XAI} | Timeout={settings.INFERENCE_TIMEOUT_SECONDS}s | MaxUpload={settings.MAX_UPLOAD_FILE_SIZE_MB}MB")
    
    # 1. Database Check
    try:
        from database.database import init_db, get_dashboard_stats
        init_db()
        stats = get_dashboard_stats()
        logger.info(f"✅ Database connected successfully (Total Analyses: {stats.get('total_analyses', 0)})")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization notice: {e}")

    # 2. ML Model & Graph Pre-warming (Singleton) + Model Checksum
    try:
        from ml.epieeg.model import EpiEEGModelLoader, MODEL_PATH
        loader = EpiEEGModelLoader.load()
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as mf:
                md5_hash = hashlib.md5(mf.read()).hexdigest()
            logger.info(f"✅ EpiEEG GNN-BiLSTM-BiGRU Model pre-warmed | Checksum (MD5): {md5_hash}")
    except Exception as e:
        logger.warning(f"⚠️ EpiEEG model pre-warm notice: {e}")

    # 3. Bonn Model Pre-warming (Singleton)
    try:
        from ml.bonn.model import model_loader
        model_loader.get_model()
        logger.info("✅ Bonn PyTorch model pre-warmed successfully.")
    except Exception as e:
        logger.warning(f"⚠️ Bonn model pre-warm notice: {e}")

    # 4. PyTorch JIT / Kernel & Autograd Execution Pre-warming
    try:
        from ml.epieeg.model import EpiEEGModelLoader
        loader = EpiEEGModelLoader.load()
        synth_x = torch.zeros((1, 43, 17), dtype=torch.float32)
        with torch.inference_mode():
            _ = loader.model(synth_x, loader.adj_matrix)
        if settings.ENABLE_XAI:
            from ml.epieeg.explainability import generate_explanation
            _ = generate_explanation(loader, np.zeros((43, 17), dtype=np.float32), "Non-Epileptic")
        logger.info("✅ PyTorch execution graphs, MKL/oneDNN kernels, and autograd engines pre-warmed.")
    except Exception as e:
        logger.warning(f"⚠️ Synthetic forward pre-warm notice: {e}")

    logger.info("=================================================================")
    logger.info("✅ Application initialization complete. Ready for inference requests.")
    yield
    logger.info("🛑 Shutting down Epilepsy Detection AI backend services...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration supporting explicit origins and Vercel/Railway wildcard domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.up\.railway\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to prevent stack trace leaks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal Error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Unable to process the request due to an internal error."}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail, "detail": exc.detail}
    )

import uuid
import time

@app.middleware("http")
async def request_tracing_and_security_middleware(request: Request, call_next):
    # Generate or extract correlation Request ID
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    # Response Headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
    
    # Standard Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    
    # Apply CSP ONLY to non-documentation endpoints so Swagger UI/ReDoc loads smoothly
    path = request.url.path
    if not (path.startswith("/docs") or path.startswith("/redoc") or path.endswith("openapi.json")):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:;"
        )
    
    return response

import time
START_TIME = time.time()

# Include Versioned API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Welcome to Epilepsy Detection AI API",
        "version": "2.0.0"
    }

@app.get("/health")
def health():
    import os
    import psutil
    
    db_status = "connected"
    try:
        from database.database import get_dashboard_stats
        get_dashboard_stats()
    except Exception:
        db_status = "disconnected"

    model_status = "loaded"
    try:
        from ml.epieeg.model import EpiEEGModelLoader
        loader = EpiEEGModelLoader.load()
        if loader.model is None:
            model_status = "unloaded"
    except Exception:
        model_status = "unloaded"

    vm = psutil.virtual_memory()
    proc = psutil.Process(os.getpid())
    rss_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
    avail_ram_mb = round(vm.available / (1024 * 1024), 2)
    cpu_pct = proc.cpu_percent(interval=None)
    uptime = round(time.time() - START_TIME, 2)

    return {
        "status": "healthy" if db_status == "connected" and model_status == "loaded" else "degraded",
        "backend": "online",
        "database": db_status,
        "database_connectivity": db_status,
        "model": model_status,
        "model_loaded_status": model_status,
        "version": settings.APP_VERSION,
        "application_version": settings.APP_VERSION,
        "uptime_seconds": uptime,
        "worker_uptime": uptime,
        "worker_pid": os.getpid(),
        "process_rss": f"{rss_mb} MB",
        "process_rss_mb": rss_mb,
        "available_ram": f"{avail_ram_mb} MB",
        "available_ram_mb": avail_ram_mb,
        "cpu_usage": f"{cpu_pct}%",
        "cpu_usage_pct": cpu_pct
    }



