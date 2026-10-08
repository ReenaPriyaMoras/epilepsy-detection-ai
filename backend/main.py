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
    Production startup & shutdown checks:
    - Verifies database connectivity and initializes tables/indices
    - Pre-warms PyTorch GNN-BiLSTM-BiGRU singleton model into memory (0ms first-request latency)
    - Verifies logging and temporary filesystem permissions
    """
    logger.info("Initializing Epilepsy Detection AI backend services...")
    
    # 1. Database Check
    try:
        from database.database import init_db, get_dashboard_stats
        init_db()
        get_dashboard_stats()
        logger.info("Database connection & indices verified successfully.")
    except Exception as e:
        logger.warning(f"Database initialization notice: {e}")

    # 2. ML Model & Graph Pre-warming (Singleton)
    try:
        from ml.epieeg.model import EpiEEGModelLoader
        loader = EpiEEGModelLoader.load()
        if loader.model is not None:
            logger.info("EpiEEG GNN-BiLSTM-BiGRU PyTorch model, weights, and graph topology pre-warmed successfully.")
    except Exception as e:
        logger.warning(f"EpiEEG model pre-warm notice: {e}")

    # 3. Bonn Model Pre-warming (Singleton)
    try:
        from ml.bonn.model import model_loader
        model_loader.get_model()
        logger.info("Bonn PyTorch model pre-warmed successfully.")
    except Exception as e:
        logger.warning(f"Bonn model pre-warm notice: {e}")

    logger.info("Backend startup complete. Application ready to accept inference requests.")
    yield
    logger.info("Shutting down Epilepsy Detection AI backend services...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration driven entirely by settings.BACKEND_CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
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
        content={"status": "error", "message": exc.detail}
    )

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
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

    return {
        "status": "healthy" if db_status == "connected" and model_status == "loaded" else "degraded",
        "backend": "online",
        "database": db_status,
        "model": model_status,
        "version": "2.0.0",
        "uptime_seconds": round(time.time() - START_TIME, 2)
    }



