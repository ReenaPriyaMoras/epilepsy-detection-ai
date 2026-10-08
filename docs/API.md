# EpiDetect AI — REST API Reference

Base URL: `https://your-backend.up.railway.app` (or `http://localhost:8000` locally)

## 1. System & Health Endpoints

### `GET /health`
Returns system status, active database engine, model readiness, and server uptime.
```json
{
  "status": "healthy",
  "database": "connected (sqlite)",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 124.5
}
```

## 2. Inference Endpoints

### `POST /api/v1/inference/epieeg`
Accepts a binary EDF file upload (multipart/form-data) and returns classification metrics.

* **Headers:** `Content-Type: multipart/form-data`
* **Form Field:** `file: <binary-edf-data>`
* **Response (200 OK):**
```json
{
  "status": "Success",
  "analysis_id": "ANL-A1B2C3D4",
  "filename": "Patient_01.edf",
  "prediction": "Non-Epileptic",
  "confidence_score": 0.824,
  "seizure_probability": 0.176,
  "risk_level": "Low",
  "channels_analyzed": 43,
  "sampling_rate": 256.0,
  "duration_seconds": 10.0,
  "execution_time_ms": 1420.5,
  "explainability": {
    "top_contributing_channels": ["Fp1-F7", "T3-T5", "C3-P3"],
    "frequency_band_dominance": {
      "delta": 0.42,
      "theta": 0.28,
      "alpha": 0.18,
      "beta": 0.09,
      "gamma": 0.03
    }
  }
}
```

## 3. History & Search Endpoints

### `GET /api/v1/history/`
Returns all recorded analyses sorted chronologically.

### `GET /api/v1/search/?q={query}`
Searches records matching analysis ID, filename, or patient identifier.

### `DELETE /api/v1/history/{id}`
Removes an analysis record by unique ID.
