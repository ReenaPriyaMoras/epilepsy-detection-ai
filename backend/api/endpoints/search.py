from fastapi import APIRouter, Query
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.database import search_analyses

router = APIRouter()

@router.get("/")
def search(q: str = Query(..., description="Search query by patient ID, filename, analysis ID, or prediction")):
    """
    Search analyses across patient_id, filename, analysis_id, patient_name, and prediction.
    """
    results = search_analyses(q)
    return {"status": "success", "query": q, "count": len(results), "data": results}
