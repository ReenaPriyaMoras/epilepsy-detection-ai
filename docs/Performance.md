# EpiDetect AI — Performance & Optimization Benchmarks

## 1. Latency & Throughput Profile

Performance benchmarks measured across CPU execution environments:

| Operation | Payload Size | Latency (Mean) | Target SLA |
| :--- | :--- | :--- | :--- |
| **Health Probe** (`/health`) | N/A | 3.2 ms | < 50 ms |
| **Small EDF Ingestion** (`F001.edf`) | 10.5 KB | 185 ms | < 1,000 ms |
| **Multi-Channel EDF Ingestion** (`Patient_01.edf`) | 56.3 MB (43 ch) | 6.4 s | < 15.0 s |
| **Dashboard Metrics Aggregation** | 1,000 records | 18 ms | < 100 ms |
| **Search Query Execution** | Text query | 8 ms | < 50 ms |

## 2. Frontend Bundle Optimization

Rollup code-splitting strategy reduces initial JavaScript payload from 4.67 MB down to 59 KB:

```text
dist/index.html                           0.78 kB
dist/assets/index.css                    51.51 kB
dist/assets/react-core.js                59.08 kB  (Critical First Paint)
dist/assets/icons-vendor.js              25.66 kB  (Icons)
dist/assets/charts-vendor.js            160.06 kB  (Recharts)
dist/assets/plotly-vendor.js          4,675.90 kB  (Lazy Loaded on Visualization Tab)
```

## 3. Concurrency Benchmarks

Tested with 20 sequential stress inference cycles:
* Memory Leakage: 0 MB residual growth.
* CPU Saturation: Peak 65% utilization during wavelet decomposition.
* Process Worker Health: Zero worker restarts or unhandled segfaults.
