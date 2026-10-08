# EpiDetect AI — Database Schema & Persistence Layer

## 1. Overview

EpiDetect AI employs a dual-engine persistence layer implemented in `backend/database/database.py`. It dynamically switches between **PostgreSQL 16** (production on Railway) and **SQLite 3** (local development and offline fallback).

## 2. Schema Definition

```sql
-- Analyses Record Table
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    prediction TEXT NOT NULL,
    confidence REAL NOT NULL,
    seizure_probability REAL NOT NULL,
    risk_level TEXT NOT NULL,
    channels_analyzed INTEGER NOT NULL,
    duration_seconds REAL NOT NULL,
    execution_time_ms REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    explainability_summary TEXT,
    notes TEXT
);

-- User Authentication Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'clinician',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patient Records Table
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Concurrency & Thread Safety

* **SQLite Engine:** SQLite connections are protected with a re-entrant `threading.Lock()` to prevent database locking errors during concurrent inference requests.
* **PostgreSQL Engine:** Leverages `psycopg2-binary` connection pooling with parameterized SQL queries to prevent SQL injection vulnerabilities.
