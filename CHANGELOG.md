# Changelog

All notable changes to the **EpiDetect AI** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-07

### Added
- **Core AI Model:** Hybrid Graph Neural Network (GNN) + Bidirectional LSTM/GRU + HistGradientBoosting with calibrated probability outputs.
- **Explainable AI (XAI):** SHAP and LIME multi-channel EEG feature attribution matrices.
- **Signal Processing:** 43-channel EDF parsing, Butterworth bandpass filtering (0.5–70 Hz), notch filtering (50/60 Hz), and wavelet decomposition.
- **Backend Architecture:** Production FastAPI engine with Pydantic v2 settings, dual-engine PostgreSQL 16 / SQLite adapter, and JWT authentication.
- **Frontend Dashboard:** React 19 + Vite web application with interactive Plotly EEG visualizations, multi-parameter search, and PDF reporting.
- **Cloud Infrastructure:** Docker multi-stage containerization, Railway backend orchestration, and Vercel CDN frontend deployment.
- **Observability:** Rotating log handlers (`inference.log`, `errors.log`, `audit.log`) and automated health checks (`/health`).

### Security & Hardening
- Sanitized internal 500/422 exception masking preventing raw stack trace disclosure.
- Non-root container execution (`appuser:10001`).
- Dynamic CORS enforcement via `BACKEND_CORS_ORIGINS`.
- 100MB upload payload ceiling and 30-second asynchronous request timeout protection.
