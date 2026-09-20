# ADR 0008: Frontend Modernization, Caddy Edge Proxy, and Async FastAPI Architecture

**Status:** Accepted on 2026-09-20.

*Note: Canonical architecture record is maintained in [docs/architecture/adr/0001-frontend-modernization-and-edge-proxy.md](../architecture/adr/0001-frontend-modernization-and-edge-proxy.md).*

## Context
The legacy fake news detection system coupled ML inference with monolithic page rendering, lacked client-side explainability heatmaps, and lacked an edge reverse proxy with modern Content Security Policies (CSP) and compression.

## Decision
1. **Frontend:** Modernized with React 19, TypeScript, Vite 7, Tailwind CSS v4 OLED theme, Radix UI accessible primitives, and Biome linting.
2. **Edge Proxy:** Containerized Caddy 2 Alpine serving SPA assets, compressing with zstd/gzip, enforcing zero-trust headers, and reverse proxying `/api/*` to FastAPI.
3. **Backend:** Async Python 3.11 FastAPI service managed via Astral `uv` and Ruff, exposing dual-model inference (Bi-LSTM and BERT transformer) with token attention attribution and OpenAPI 3.1 schemas.
4. **DevSecOps:** Playwright cross-browser + axe-core WCAG 2.1 AA E2E testing, Lefthook pre-commit hooks, and GitHub Actions 5-job pipeline.

## Consequences
Achieves sub-millisecond client state management, decoupled ML deployments, strict zero-trust edge security, and comprehensive automated quality gates.
