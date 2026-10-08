# EpiDetect AI — Backend Architecture & Engineering

## 1. Overview

The backend service is implemented using **FastAPI** on Python 3.11. It provides asynchronous endpoints for file ingestion, signal processing, neural network inference, explainability attribution, and clinical report management.

## 2. Core Modules

```text
backend/
├── main.py                     # FastAPI application entrypoint & Lifespan manager
├── core/
│   ├── config.py               # Pydantic-settings v2 environment configuration
│   └── logger.py               # Rotating multi-handler structured logging
├── database/
│   └── database.py             # Dual-engine PostgreSQL / SQLite adapter
├── api/
│   └── endpoints/
│       ├── inference.py        # /api/v1/inference/epieeg EDF analysis endpoint
│       ├── history.py          # /api/v1/history/ analysis records CRUD
│       ├── dashboard.py        # /api/v1/dashboard/ aggregated clinical telemetry
│       └── auth.py             # JWT token issuance and authentication
└── ml/
    └── epieeg/
        ├── model.py            # PyTorch Hybrid GNN-BiLSTM architecture & singleton
        ├── preprocessing.py    # 43-channel EDF reader & feature extractor
        └── inference.py        # Complete inference execution & XAI attribution
```

## 3. Lifespan & Startup Pre-Warming

During server boot, the FastAPI `lifespan` event handler executes pre-warming routines:
1. Instantiates the PyTorch model singleton and loads weights (`backend/ml/epieeg/weights/gnn_bilstm_epieeg.pt`).
2. Computes the electrode topology adjacency matrix ($A \in \mathbb{R}^{43 \times 43}$).
3. Initializes the database schema (`init_db()`), provisioning required tables if missing.
4. Initializes rotating log handlers (`inference.log`, `errors.log`, `audit.log`).

## 4. Error Handling & Security Sanitization

* **500 Internal Server Errors:** Sanitized to `{ "detail": "An internal processing error occurred." }`. Raw stack traces are isolated to `backend/logs/errors.log`.
* **422 Unprocessable Entity:** Returned when uploaded EDF files are malformed or contain corrupt headers.
* **400 Bad Request:** Returned when file format is not `.edf` or file size is 0 bytes.
* **504 Gateway Timeout:** Enforced if EEG signal processing exceeds the 30.0-second safety window.
