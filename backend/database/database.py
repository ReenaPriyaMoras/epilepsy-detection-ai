import sqlite3
import os
import json
import uuid
import datetime
import threading
from typing import Optional, List, Dict, Any

from core.config import settings

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_PATH = os.path.join(DB_DIR, "epilepsy_ai.db")

_lock = threading.Lock()

def get_database_url() -> str:
    """Returns DATABASE_URL from settings or defaults to local SQLite file path."""
    return settings.DATABASE_URL or f"sqlite:///{DEFAULT_SQLITE_PATH}"

def get_connection():
    """
    Creates and returns a thread-safe connection to the configured database.
    Supports SQLite locally and PostgreSQL via DATABASE_URL.
    """
    db_url = get_database_url()
    
    if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
        try:
            import psycopg2
            import psycopg2.extras
            # Handle Railway/Render 'postgres://' -> 'postgresql://' if needed
            cleaned_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(cleaned_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except Exception as e:
            # Fallback to local SQLite if PostgreSQL connection fails
            conn = sqlite3.connect(DEFAULT_SQLITE_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
    else:
        # Extract SQLite path
        sqlite_path = db_url.replace("sqlite:///", "") if db_url.startswith("sqlite:///") else DEFAULT_SQLITE_PATH
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initializes the analyses table and required search indices."""
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            
            if is_postgres:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id VARCHAR(64) PRIMARY KEY,
                    patient_id VARCHAR(64),
                    patient_name VARCHAR(255),
                    filename VARCHAR(255) NOT NULL,
                    file_size VARCHAR(64),
                    prediction VARCHAR(64) NOT NULL,
                    confidence_score DOUBLE PRECISION NOT NULL,
                    seizure_probability DOUBLE PRECISION NOT NULL,
                    risk_level VARCHAR(32),
                    timestamp VARCHAR(64) NOT NULL,
                    dataset VARCHAR(64) DEFAULT 'EpiEEG',
                    processing_time VARCHAR(64),
                    pdf_path TEXT,
                    xai_summary TEXT,
                    doctor_recommendation TEXT,
                    explainability_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
            else:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    patient_name TEXT,
                    filename TEXT NOT NULL,
                    file_size TEXT,
                    prediction TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    seizure_probability REAL NOT NULL,
                    risk_level TEXT,
                    timestamp TEXT NOT NULL,
                    dataset TEXT DEFAULT 'EpiEEG',
                    processing_time TEXT,
                    pdf_path TEXT,
                    xai_summary TEXT,
                    doctor_recommendation TEXT,
                    explainability_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_filename ON analyses(filename);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_patient ON analyses(patient_id);")
            conn.commit()
        finally:
            conn.close()

# Auto-initialize database on import
init_db()

def insert_analysis(record: dict) -> dict:
    """Inserts or updates an EEG analysis record into the database."""
    analysis_id = record.get("id") or f"ANL-{uuid.uuid4().hex[:8].upper()}"
    patient_id = record.get("patient_id") or "PT-2026-0942"
    patient_name = record.get("patient_name") or "Anonymous Patient"
    filename = record.get("filename") or "eeg_recording.edf"
    file_size = record.get("file_size") or "N/A"
    prediction = record.get("prediction") or "Unknown"
    confidence_score = float(record.get("confidence_score") or 0.0)
    seizure_probability = float(record.get("seizure_probability") or 0.0)
    
    if seizure_probability > 0.75:
        risk_level = "High"
    elif seizure_probability > 0.40:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    timestamp = record.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dataset = record.get("dataset") or "EpiEEG"
    processing_time = str(record.get("processing_time") or "0.12s")
    pdf_path = record.get("pdf_path") or ""
    
    explainability = record.get("explainability")
    if isinstance(explainability, dict):
        xai_summary = explainability.get("summary", "")
        explainability_json = json.dumps(explainability)
    else:
        xai_summary = ""
        explainability_json = ""
        
    if prediction.lower() == "epileptic":
        doctor_recommendation = "High epileptiform activity detected. Prompt neurological consultation and 24-hr continuous video-EEG recommended."
    else:
        doctor_recommendation = "Normal baseline EEG profile without paroxysmal epileptiform discharges. Routine follow-up."

    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            
            if is_postgres:
                cursor.execute("""
                INSERT INTO analyses (
                    id, patient_id, patient_name, filename, file_size, prediction,
                    confidence_score, seizure_probability, risk_level, timestamp,
                    dataset, processing_time, pdf_path, xai_summary,
                    doctor_recommendation, explainability_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    patient_id = EXCLUDED.patient_id,
                    patient_name = EXCLUDED.patient_name,
                    filename = EXCLUDED.filename,
                    file_size = EXCLUDED.file_size,
                    prediction = EXCLUDED.prediction,
                    confidence_score = EXCLUDED.confidence_score,
                    seizure_probability = EXCLUDED.seizure_probability,
                    risk_level = EXCLUDED.risk_level,
                    timestamp = EXCLUDED.timestamp,
                    dataset = EXCLUDED.dataset,
                    processing_time = EXCLUDED.processing_time,
                    pdf_path = EXCLUDED.pdf_path,
                    xai_summary = EXCLUDED.xai_summary,
                    doctor_recommendation = EXCLUDED.doctor_recommendation,
                    explainability_json = EXCLUDED.explainability_json;
                """, (
                    analysis_id, patient_id, patient_name, filename, file_size, prediction,
                    confidence_score, seizure_probability, risk_level, timestamp,
                    dataset, processing_time, pdf_path, xai_summary,
                    doctor_recommendation, explainability_json
                ))
            else:
                cursor.execute("""
                INSERT OR REPLACE INTO analyses (
                    id, patient_id, patient_name, filename, file_size, prediction,
                    confidence_score, seizure_probability, risk_level, timestamp,
                    dataset, processing_time, pdf_path, xai_summary,
                    doctor_recommendation, explainability_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id, patient_id, patient_name, filename, file_size, prediction,
                    confidence_score, seizure_probability, risk_level, timestamp,
                    dataset, processing_time, pdf_path, xai_summary,
                    doctor_recommendation, explainability_json
                ))
            conn.commit()
        finally:
            conn.close()

    return get_analysis_by_id(analysis_id)

def get_all_analyses(limit: int = 100, offset: int = 0) -> list:
    """Retrieves all analyses ordered by created_at DESC with pagination."""
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            placeholder = "%s" if is_postgres else "?"
            
            cursor.execute(f"SELECT * FROM analyses ORDER BY created_at DESC LIMIT {placeholder} OFFSET {placeholder}", (limit, offset))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                if item.get("explainability_json"):
                    try:
                        item["explainability"] = json.loads(item["explainability_json"])
                    except Exception:
                        item["explainability"] = None
                else:
                    item["explainability"] = None
                results.append(item)
            return results
        finally:
            conn.close()

def get_analysis_by_id(analysis_id: str) -> dict | None:
    """Retrieves a single analysis by its unique ID."""
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            placeholder = "%s" if is_postgres else "?"
            
            cursor.execute(f"SELECT * FROM analyses WHERE id = {placeholder} LIMIT 1", (analysis_id,))
            row = cursor.fetchone()
            if not row:
                return None
            item = dict(row)
            if item.get("explainability_json"):
                try:
                    item["explainability"] = json.loads(item["explainability_json"])
                except Exception:
                    item["explainability"] = None
            else:
                item["explainability"] = None
            return item
        finally:
            conn.close()

def delete_analysis(analysis_id: str) -> bool:
    """Deletes an analysis record by ID."""
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            placeholder = "%s" if is_postgres else "?"
            
            cursor.execute(f"DELETE FROM analyses WHERE id = {placeholder}", (analysis_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

def search_analyses(query: str) -> list:
    """Performs case-insensitive search across ID, patient, filename, and prediction."""
    if not query or not query.strip():
        return get_all_analyses()
        
    term = f"%{query.strip().lower()}%"
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            placeholder = "%s" if is_postgres else "?"
            
            cursor.execute(f"""
            SELECT * FROM analyses
            WHERE LOWER(id) LIKE {placeholder}
               OR LOWER(patient_id) LIKE {placeholder}
               OR LOWER(patient_name) LIKE {placeholder}
               OR LOWER(filename) LIKE {placeholder}
               OR LOWER(prediction) LIKE {placeholder}
            ORDER BY created_at DESC
            """, (term, term, term, term, term))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                if item.get("explainability_json"):
                    try:
                        item["explainability"] = json.loads(item["explainability_json"])
                    except Exception:
                        item["explainability"] = None
                else:
                    item["explainability"] = None
                results.append(item)
            return results
        finally:
            conn.close()

def get_dashboard_stats() -> dict:
    """Aggregates real-time metrics and diagnostic counters for the dashboard."""
    with _lock:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Total analyses
            cursor.execute("SELECT COUNT(*) FROM analyses")
            row = cursor.fetchone()
            total_analyses = (list(row.values())[0] if isinstance(row, dict) else row[0]) if row else 0
            
            # Epileptic cases
            cursor.execute("SELECT COUNT(*) FROM analyses WHERE LOWER(prediction) = 'epileptic'")
            row = cursor.fetchone()
            epileptic_cases = (list(row.values())[0] if isinstance(row, dict) else row[0]) if row else 0
            
            # Healthy cases
            cursor.execute("SELECT COUNT(*) FROM analyses WHERE LOWER(prediction) != 'epileptic'")
            row = cursor.fetchone()
            healthy_cases = (list(row.values())[0] if isinstance(row, dict) else row[0]) if row else 0
            
            # Average confidence
            cursor.execute("SELECT AVG(confidence_score) FROM analyses")
            row = cursor.fetchone()
            avg_conf = (list(row.values())[0] if isinstance(row, dict) else row[0]) if row else None
            avg_confidence_pct = round(avg_conf * 100, 1) if avg_conf is not None else 0.0
            
            # Today's analyses
            today_str = datetime.date.today().isoformat()
            is_postgres = hasattr(conn, 'cursor_factory') and not isinstance(conn, sqlite3.Connection)
            if is_postgres:
                cursor.execute("SELECT COUNT(*) FROM analyses WHERE DATE(created_at) = %s", (today_str,))
            else:
                cursor.execute("SELECT COUNT(*) FROM analyses WHERE DATE(created_at) = DATE(?)", (today_str,))
            row = cursor.fetchone()
            today_analyses = (list(row.values())[0] if isinstance(row, dict) else row[0]) if row else 0
            
            # Last analysis time
            cursor.execute("SELECT timestamp FROM analyses ORDER BY created_at DESC LIMIT 1")
            last_row = cursor.fetchone()
            if last_row:
                last_analysis_time = list(last_row.values())[0] if isinstance(last_row, dict) else last_row[0]
            else:
                last_analysis_time = "None"
            
            return {
                "status": "success",
                "total_analyses": total_analyses,
                "epileptic_cases": epileptic_cases,
                "healthy_cases": healthy_cases,
                "average_confidence": f"{avg_confidence_pct}%" if total_analyses > 0 else "--",
                "average_confidence_val": avg_confidence_pct,
                "today_analyses": today_analyses,
                "total_reports_generated": total_analyses,
                "backend_status": "Connected",
                "last_analysis_time": last_analysis_time
            }
        finally:
            conn.close()
