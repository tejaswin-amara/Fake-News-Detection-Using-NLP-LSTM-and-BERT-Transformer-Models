# ADR 0001: Frontend Modernization, Caddy Edge Proxy, and Async FastAPI Architecture

**Status:** Accepted on 2026-09-20.

## Context

The legacy fake news detection system was constrained by a monolithic Python web interface with high page load latency, tight coupling of machine learning inference with HTML generation, lacking interactive token-level explainability, and exhibiting zero client-side caching or state isolation. Furthermore, direct exposure of the Python ASGI application to client traffic introduced security risks, missing Content Security Policies (CSP), lack of modern compression algorithms (zstd/brotli), and vulnerability to slowloris and unbuffered request attacks.

Modern operational requirements require:
1. An accessible, high-performance web client supporting sub-millisecond local state transitions, interactive token saliency heatmaps, radar/ROC-AUC benchmark visualizations, and persistent audit trail capabilities.
2. A hardened, high-throughput edge reverse proxy terminating client connections, enforcing zero-trust HTTP headers, and proxying backend API requests.
3. A decoupled, high-performance async Python backend focused strictly on sequence classification inference (Bi-LSTM and fine-tuned BERT) with strict OpenAPI 3.1 contracts.
4. Fast, deterministic linting and formatting tooling capable of instantaneous developer feedback loops.

## Decision

We have decided to adopt the following architectural stack:

1. **Frontend: React 19 + TypeScript + Vite 7 + Tailwind CSS v4 + Radix UI**
   - **React 19 & Vite 7:** Provides lightning-fast compilation, native React concurrent features, and deterministic bundling.
   - **Tailwind CSS v4 & OLED Glassmorphism:** CSS-variable driven theme system optimized for high contrast, low eye fatigue, and WCAG 2.1 AA accessibility compliance.
   - **Radix UI Primitives:** Headless, keyboard-accessible components (Tabs, Popovers, Dialogs) guaranteeing strict ARIA attribute adherence.
   - **TanStack Query & LocalStorage:** Client-side caching of benchmark metrics and persistent local audit logging of all inference queries without retaining user-submitted text on remote servers.

2. **Code Quality & Linter: Biome & Ruff**
   - Replaced ESLint and Prettier with **Biome** in the frontend, providing sub-100ms linting and formatting passes.
   - Standardized on **Ruff** for Python backend code formatting and linting.

3. **Edge Reverse Proxy: Caddy 2 (Alpine)**
   - Deployed **Caddy 2** as the ingress proxy container (`caddy:2-alpine`).
   - Handles static SPA delivery with client-side history routing (`try_files {path} /index.html`).
   - Proxies `/api/*` and `/healthz` directly to the upstream FastAPI container (`http://backend:8000`).
   - Automatically negotiates `zstd` and `gzip` compression.
   - Enforces strict security headers: Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), X-Content-Type-Options, X-Frame-Options, and Referrer-Policy.

4. **Inference Backend: FastAPI + Astral uv**
   - Decoupled into `backend/` using **FastAPI** with Pydantic V2 data validation schemas.
   - Packaged with Astral `uv` for sub-second virtualenv resolution and deterministic builds.
   - Serves dual-model architecture: 2-layer Stacked Bi-LSTM and 12-head BERT Transformer with attention extraction.
   - Implements zero-crash calibrated heuristic fallbacks when PyTorch weights are unmounted or host OS binary restrictions apply.

## Consequences

### Positive
- **Separation of Concerns:** ML engineers can iterate independently on PyTorch models without touching frontend code; UI designers can build rich client interfaces without spinning up GPU/Python environments.
- **Security Posture:** FastAPI is never directly exposed to the public internet; Caddy filters invalid requests, buffers slow network clients, and strictly controls allowable script and resource origins via CSP.
- **Latency & Performance:** Static assets are served directly from Caddy memory/cache with zstd compression; API queries are stream-buffered with minimal ASGI overhead.
- **Reproducibility:** Polyglot CI workflow validates TypeScript typecheck (`tsc`), Biome, Ruff, unit tests (`Vitest` and `pytest`), Spectral OpenAPI contracts, and Playwright E2E suites deterministically.

### Negative / Trade-offs
- Multi-container architecture requires Docker Compose orchestration in development and production environments.
- Cross-origin and proxy configuration must be maintained in synchrony between Vite's dev server (`vite.config.ts`) and Caddy's production recipe (`Caddyfile`).
