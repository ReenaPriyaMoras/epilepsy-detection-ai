from fastapi import APIRouter, HTTPException, Path, Body
from typing import Optional, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database.database import get_all_analyses, get_analysis_by_id, delete_analysis, insert_analysis

router = APIRouter()

@router.get("/")
def get_history():
    """
    Returns all stored analyses (newest first).
    """
    records = get_all_analyses()
    return {"status": "success", "data": records, "count": len(records)}

@router.get("/{analysis_id}")
def get_single_analysis(analysis_id: str = Path(...)):
    """
    Returns a single analysis by ID.
    """
    record = get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return {"status": "success", "data": record}

@router.delete("/{analysis_id}")
def delete_single_analysis(analysis_id: str = Path(...)):
    """
    Deletes an analysis record by ID.
    """
    success = delete_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found or already deleted.")
    return {"status": "success", "message": f"Analysis {analysis_id} deleted successfully."}

@router.post("/")
def save_analysis(payload: dict = Body(...)):
    """
    Saves an analysis record into SQLite database.
    """
    record = insert_analysis(payload)
    return {"status": "success", "data": record}
