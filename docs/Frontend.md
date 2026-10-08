# EpiDetect AI — Frontend Architecture & UI/UX

## 1. Overview

The frontend is a single-page application built with **React 19**, **Vite 8**, and **Tailwind CSS**. It provides a real-time clinical dashboard for EEG file ingestion, waveform tracing, seizure probability visualization, and PDF reporting.

## 2. Directory Structure

```text
frontend/src/
├── components/
│   ├── Navbar.jsx              # Global navigation bar & system status
│   ├── Footer.jsx              # Footer & copyright metadata
│   ├── EEGVisualization.jsx   # Multi-channel Plotly waveform visualizer
│   ├── XAIDashboard.jsx        # SHAP/LIME feature importance charts
│   └── ErrorBoundary.jsx       # Fallback wrapper for resilient rendering
├── pages/
│   ├── Home.jsx                # Landing page & quick analysis portal
│   ├── Dashboard.jsx           # Clinical metrics & aggregate stats
│   ├── History.jsx             # Searchable historical records
│   ├── Settings.jsx            # System telemetry & API configuration
│   └── Documentation.jsx       # Interactive user guide & API docs
├── services/
│   └── api.js                  # Axios client with JWT interceptor & base URL
├── App.jsx                     # Route definitions & global layout
└── main.jsx                    # React 19 root entrypoint
```

## 3. Performance & Code-Splitting

To optimize client-side load times, Rollup manual chunking is configured in `vite.config.js`:
* `plotly-vendor`: Isolates heavy WebGL/SVG plotting engines.
* `charts-vendor`: Isolates Recharts and D3 dependencies.
* `icons-vendor`: Isolates Lucide React icon packs.
* `react-core`: Isolates React, React-DOM, and React-Router runtime.

This reduces the primary entry JavaScript payload to ~59 KB, achieving sub-second first contentful paint (FCP).

## 4. Vercel SPA Routing

Configured in `vercel.json`:
* `/(.*)` rewrites to `/index.html` to support deep links and browser refreshes on routes like `/dashboard`, `/history`, and `/settings`.
* Static assets in `/assets/` are served with 1-year immutable cache headers (`public, max-age=31536000, immutable`).
