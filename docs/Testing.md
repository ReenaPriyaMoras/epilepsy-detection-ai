# EpiDetect AI — Testing & Clinical Validation Suite

## 1. Automated Test Framework

EpiDetect AI includes automated unit, integration, resilience, and stress testing suites built on `pytest`.

```bash
# Run backend API validation and logging test suite
pytest backend/tests/ -v

# Run full clinical workflow audit
python backend/test_complete_audit.py

# Run repeated inference stress and malformed input resilience test
python backend/test_repeated_and_resilience.py
```

## 2. Test Coverage Matrix

| Test Module | Description | Assertions | Status |
| :--- | :--- | :--- | :---: |
| `test_valid_edf` | Tests 43-ch EDF analysis pipeline | Prediction, confidence, DB save | PASSED |
| `test_invalid_extension` | Tests non-EDF file rejection | HTTP 400 Bad Request | PASSED |
| `test_corrupted_edf` | Tests corrupt EDF header resilience | HTTP 422 Unprocessable | PASSED |
| `test_empty_edf` | Tests 0-byte file upload rejection | HTTP 400 Bad Request | PASSED |
| `test_missing_file` | Tests empty multipart form post | HTTP 422 Validation Error | PASSED |
| `test_health_check` | Tests `/health` probe metadata | Uptime, database status | PASSED |
| `test_log_files_created` | Verifies rotating log file generation | `inference.log`, `audit.log` | PASSED |
| `test_error_logging_works`| Tests unhandled exception logging | Trace written to `errors.log` | PASSED |
| `test_repeated_inference`| 20-run stress cycle on 56MB EDF | Zero crashes, zero memory leaks | PASSED |
