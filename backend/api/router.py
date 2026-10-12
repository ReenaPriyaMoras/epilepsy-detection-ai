from fastapi import APIRouter
from api.endpoints import inference, history, clinical, dashboard, search, debug

api_router = APIRouter()
api_router.include_router(inference.router, prefix="/inference", tags=["inference"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(debug.router, prefix="/debug", tags=["debug"])
api_router.include_router(clinical.router, tags=["clinical"])
