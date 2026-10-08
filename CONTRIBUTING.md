# Contributing to EpiDetect AI

Thank you for your interest in contributing to **EpiDetect AI**!

## Development Guidelines

1. **Fork and Branch:**
   * Create a feature branch: `git checkout -b feature/amazing-feature`
2. **Code Standards:**
   * Backend: Follow PEP 8 style guidelines. Ensure type hints and Pydantic validation are utilized.
   * Frontend: Follow standard React 19 functional component patterns with Tailwind CSS.
3. **Preserve Clinical & ML Integrity:**
   * Do not alter preprocessing mathematics, electrode montage mappings, or model threshold definitions without experimental validation.
4. **Testing:**
   * Run pytest suite: `pytest backend/tests/ -v`
   * Run frontend build: `npm run build` (in `frontend/`)
5. **Pull Requests:**
   * Provide a clear description of changes, rationale, and validation logs.
