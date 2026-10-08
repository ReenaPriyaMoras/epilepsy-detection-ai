# 🧠 EpiDetect AI — Clinical Epilepsy Detection Using AI Techniques

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.13+-EE4C2C.svg?style=flat&logo=PyTorch&logoColor=white)](https://pytorch.org)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF.svg?style=flat&logo=Vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **EpiDetect AI** is an enterprise-grade, clinical-grade artificial intelligence platform for automated seizure detection and neurological biomarker extraction from electroencephalogram (EEG) recordings. Combining spatial Graph Neural Networks (GNN) and temporal Bidirectional LSTM/GRU networks with Explainable AI (SHAP & LIME), it provides neurologists with fast, transparent, and accurate diagnostic support.

---

## 📑 Table of Contents
1. [Clinical Motivation & Overview](#-clinical-motivation--overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Technology Stack](#-technology-stack)
5. [Machine Learning & Signal Processing](#-machine-learning--signal-processing)
6. [Explainable AI (XAI)](#-explainable-ai-xai)
7. [Repository Structure](#-repository-structure)
8. [Installation & Local Setup](#-installation--local-setup)
9. [Deployment Guide](#-deployment-guide)
   * [Docker & Docker Compose](#docker--docker-compose)
   * [Railway (Backend & PostgreSQL)](#railway-backend--postgresql)
   * [Vercel (Frontend SPA)](#vercel-frontend-spa)
10. [Environment Variables](#-environment-variables)
11. [REST API Overview](#-rest-api-overview)
12. [Testing & Quality Assurance](#-testing--quality-assurance)
13. [Future Roadmap](#-future-roadmap)
14. [License & Authors](#-license--authors)
15. [Citation](#-citation)

---

## 🏥 Clinical Motivation & Overview

Epilepsy affects over 50 million individuals worldwide. Standard diagnostic workflows rely on continuous multi-channel scalp EEG monitoring lasting hours to days. Manual visual inspection of these recordings by certified epileptologists is:
* **Time-Intensive:** A 24-hour recording contains millions of signal datapoints across 40+ channels.
* **Prone to Fatigue & Inter-Rater Variability:** Subtle epileptiform discharges can be masked by physiological artifacts (muscle, cardiac, ocular).
* **Resource Constrained:** Specialized neurological centers face significant backlogs.

**EpiDetect AI** addresses these challenges by offering automated, high-precision European Data Format (EDF) ingestion, signal pre-filtering, spatio-temporal deep feature learning, and explainability attributions in seconds.

---

## ✨ Key Features

* **Multi-Channel EDF Ingestion:** Supports up to 43 scalp EEG channels conforming to the international 10–20 electrode montage system.
* **Dual-Stage Signal Preprocessing:** Butterworth bandpass filtering (0.5–70 Hz), notch filtering (50/60 Hz), and multi-resolution wavelet decomposition.
* **Hybrid Deep Learning Model:** Graph Convolutional Networks (GNN) for spatial cortical topology combined with Bidirectional LSTM/GRU for temporal dynamics.
* **Transparent Explainability:** SHAP and LIME attribution maps highlighting the dominant electrode channels and frequency bands contributing to each diagnosis.
* **Interactive Waveform Visualizer:** Plotly-powered high-performance multi-channel EEG viewer with pan, zoom, channel filtering, and snapshot export.
* **Dual-Engine Persistence:** Automatic runtime switching between managed PostgreSQL 16 (cloud) and SQLite 3 (local development).
* **Hardened Cloud Infrastructure:** Docker containerization, dynamic port binding, sanitized error masking, and non-root execution.

---

## 🏛 System Architecture

```mermaid
flowchart TD
    subgraph Client Layer
        A[React 19 + Vite SPA] -->|HTTPS / Bearer JWT| B[API Gateway / CORS]
    end

    subgraph Application Tier
        B --> C[FastAPI ASGI Server]
        C --> D[Pydantic v2 Config]
        C --> E[Rotating Log Engine]
        C --> F[Lifespan Pre-Warming]
    end

    subgraph AI Engine
        F --> G[PyTorch GNN-BiLSTM Singleton]
        C --> H[43-Ch EDF Preprocessor]
        H --> G
        G --> I[HistGradientBoosting Classifier]
        I --> J[SHAP / LIME Attribution Engine]
    end

    subgraph Database Tier
        C --> K[Dual-Engine DB Adapter]
        K -->|Cloud Production| L[(Railway PostgreSQL 16)]
        K -->|Local Offline| M[(SQLite3 Local DB)]
    end
```

---

## 💻 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, Tailwind CSS, Plotly.js, Recharts, Lucide Icons, Axios |
| **Backend** | Python 3.11, FastAPI, Pydantic v2, Uvicorn, Python-JOSE (JWT), Passlib |
| **AI / ML** | PyTorch 2.13, Scikit-learn, MNE-Python, PyWavelets, SHAP, LIME |
| **Database** | PostgreSQL 16, SQLite 3, SQLAlchemy 2.0, Psycopg2 |
| **DevOps & Cloud** | Docker, Docker Compose, Railway, Vercel Edge CDN |

---

## 🧠 Machine Learning & Signal Processing

For each EEG channel, the feature extraction module calculates 17 multi-domain metrics ($43 \times 17 = 731$ dimensional representation):
* **Spectral Band Power:** $\delta$ (0.5–4 Hz), $\theta$ (4–8 Hz), $\alpha$ (8–13 Hz), $\beta$ (13–30 Hz), $\gamma$ (30–70 Hz).
* **Time-Domain Statistics:** Mean, Variance, Skewness, Kurtosis, Peak-to-Peak, RMS.
* **Non-Linear Dynamics:** Approximate Entropy, Sample Entropy, Spectral Entropy, Petrosian & Higuchi Fractal Dimensions, Hurst Exponent.

The spatial graph $G = (V, E, A)$ models electrode proximity, passing spatial embeddings into recurrent BiLSTM units to detect transient paroxysmal spikes.

---

## 🔍 Explainable AI (XAI)

EpiDetect AI integrates **SHAP (SHapley Additive exPlanations)** to ensure clinical transparency. Clinicians can inspect:
1. **Electrode Contribution Heatmap:** Brain regions driving the seizure probability index.
2. **Frequency Band Decomposition:** Relative dominance of slowing waves ($\delta, \theta$) versus rapid discharge frequencies.

---

## 📂 Repository Structure

```text
epilepsy-detection-ai/
├── backend/                     # FastAPI backend application
│   ├── api/                     # REST API endpoints (inference, history, auth)
│   ├── core/                    # App configuration and rotating logging
│   ├── database/                # Dual-engine database adapter
│   ├── ml/                      # PyTorch GNN-BiLSTM model & weights
│   ├── logs/                    # Rotating log files
│   └── tests/                   # PyTest automated validation suite
├── frontend/                    # React 19 single-page application
│   ├── src/                     # UI components, pages, visualizers
│   ├── vite.config.js           # Bundle code-splitting configuration
│   └── vercel.json              # SPA deep-link rewrite configuration
├── docs/                        # Detailed architectural specifications
├── Dockerfile                   # Multi-stage Python 3.11 runtime container
├── docker-compose.yml           # Backend + PostgreSQL service orchestration
├── railway.json                 # Railway cloud deployment manifest
├── requirements.txt             # Pinned deterministic Python dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Installation & Local Setup

### Prerequisites
* Python 3.11+
* Node.js 20+ & npm
* Git

### 1. Clone Repository
```bash
git clone https://github.com/your-username/epilepsy-detection-ai.git
cd epilepsy-detection-ai
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
cd backend
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## ☁ Deployment Guide

### Docker & Docker Compose
```bash
docker-compose up --build
```
This spins up the FastAPI backend on `http://localhost:8000` connected to a dedicated PostgreSQL 16 container.

### Railway (Backend & PostgreSQL)
1. Link your GitHub repository in Railway.
2. Railway detects `railway.json` and builds via [`Dockerfile`](file:///c:/Users/reena/EpilepsyDetectionAI/epilepsy-detection-ai/Dockerfile).
3. Add a **PostgreSQL** service in Railway and set `DATABASE_URL="${{Postgres.DATABASE_URL}}"`.

### Vercel (Frontend SPA)
1. Import the `frontend` folder into Vercel.
2. Set Framework Preset to **Vite**.
3. Configure environment variable `VITE_API_URL="https://your-backend.up.railway.app"`.

---

## 🔐 Environment Variables

| Variable | Target | Description | Example |
| :--- | :---: | :--- | :--- |
| `PROJECT_NAME` | Backend | Service name | `"Epilepsy Detection API"` |
| `ENVIRONMENT` | Backend | Run mode | `"production"` / `"development"` |
| `PORT` | Backend | Port binding | `8000` |
| `JWT_SECRET` | Backend | Token signing key | `[32-char hex string]` |
| `DATABASE_URL` | Backend | PostgreSQL URI | `postgresql://user:pass@host:5432/db` |
| `BACKEND_CORS_ORIGINS` | Backend | Allowed CORS domains | `https://your-app.vercel.app` |
| `VITE_API_URL` | Frontend | Backend API endpoint | `https://your-api.railway.app` |

---

## 📡 REST API Overview

* `GET /health` — Health check, database status, model readiness, uptime.
* `POST /api/v1/inference/epieeg` — Upload EDF file for automated seizure detection.
* `GET /api/v1/dashboard/stats` — Retrieve aggregated clinical diagnostic telemetry.
* `GET /api/v1/history/` — Query historical analysis sessions.
* `GET /api/v1/search/?q={query}` — Search records by analysis ID, patient name, or file.
* `DELETE /api/v1/history/{id}` — Delete historical analysis record.

---

## 🧪 Testing & Quality Assurance

Run the automated backend test suite:
```bash
# Run unit & API integration tests
pytest backend/tests/ -v

# Run full clinical workflow simulation
python backend/test_complete_audit.py

# Run repeated inference stress test
python backend/test_repeated_and_resilience.py
```

---

## 🗺 Future Roadmap

- [ ] Real-time streaming EEG telemetry via WebSockets.
- [ ] Multi-center federated learning support.
- [ ] HL7 / FHIR clinical EHR interoperability.
- [ ] Mobile edge-deployment support (ONNX Runtime / TensorRT).

---

## 📄 License & Authors

Distributed under the **MIT License**. See [`LICENSE`](file:///c:/Users/reena/EpilepsyDetectionAI/epilepsy-detection-ai/LICENSE) for more details.

**Lead Author & Maintainer:**  
* **EpiDetect AI Research & Engineering Team**

---

## 📚 Citation

If you use EpiDetect AI in your research or clinical engineering projects, please cite:

```bibtex
@article{epidetect2026,
  title={EpiDetect AI: Automated Epilepsy Detection from Multi-Channel Scalp EEG Using Spatial-Temporal Graph Neural Networks and Explainable AI},
  author={EpiDetect AI Team},
  journal={IEEE Transactions on Neural Systems and Rehabilitation Engineering},
  year={2026}
}
```
