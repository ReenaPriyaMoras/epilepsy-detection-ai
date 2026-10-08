from fastapi import APIRouter
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.database import get_dashboard_stats

router = APIRouter()

@router.get("/")
@router.get("/stats")
def dashboard_stats():
    """
    Computes and returns real-time statistics from the SQLite database.
    """
    return get_dashboard_stats()
