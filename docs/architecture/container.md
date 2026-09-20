# Container Architecture (C4 Level 2)

This diagram details the containerized runtime components, processes, networks, and communication protocols within the **VERITAS AI** deployment.

```mermaid
graph TD
    subgraph ClientBrowser["User Desktop / Mobile Browser"]
        SPA["React 19 OLED SPA<br/>(Tailwind v4, TanStack Query, Radix UI)"]
        LocalStorage["Browser LocalStorage<br/>(Persistent Verification Audit Trail)"]
        SPA -->|Persist Audits| LocalStorage
    end

    subgraph DockerHost["Docker Container Network (veritas-net)"]
        subgraph FrontendContainer["Frontend Container (caddy:2-alpine) - Port 3000:80"]
            CaddyProxy["Caddy 2 Edge Proxy<br/>gzip/zstd, Security Headers, CSP"]
            StaticFiles["Static SPA Assets<br/>(/usr/share/caddy)"]
            CaddyProxy -->|Serve Static /| StaticFiles
        end

        subgraph BackendContainer["Backend Container (python:3.11-slim) - Port 8000"]
            FastAPIEngine["FastAPI Async App<br/>(Telemetry Middleware, CORS, Pydantic V2)"]
            HealthEndpoint["Health Check Router<br/>(/healthz, /readyz)"]
            InferenceRouter["Inference Router<br/>(/api/predict/lstm, bert, both)"]
            BenchmarksRouter["Benchmarks Router<br/>(/api/benchmarks)"]

            subgraph MLWorkers["Neural ML Predictors"]
                LSTMEngine["GloVe + Stacked Bi-LSTM<br/>(~4.2M params, 18.5ms latency)"]
                BERTEngine["Fine-Tuned BERT Transformer<br/>(~109.5M params, 12 attention heads)"]
                HeuristicEngine["Calibrated Local Heuristic Fallback<br/>(Zero-Crash Offline Engine)"]
            end

            FastAPIEngine --> HealthEndpoint
            FastAPIEngine --> InferenceRouter
            FastAPIEngine --> BenchmarksRouter
            InferenceRouter --> LSTMEngine
            InferenceRouter --> BERTEngine
            InferenceRouter -.->|Fallback if weights missing| HeuristicEngine
        end
    end

    SPA -->|HTTPS / HTTP Requests| CaddyProxy
    CaddyProxy -->|Reverse Proxy /api/* & /healthz| FastAPIEngine
```

## Component Breakdown

| Component | Technology | Role & Security Hardening |
| :--- | :--- | :--- |
| **Edge Reverse Proxy** | `Caddy 2` (Alpine OCI) | Terminates client traffic, enforces strict Content Security Policy (CSP), compresses with zstd/gzip, routes `/api/*` to backend. |
| **Client Frontend** | `React 19` + `Vite 7` | OLED glassmorphic UI, TanStack Query cache, client-side token heatmap rendering, and instant export to JSON/Markdown/CSV. |
| **Backend API Engine** | `FastAPI` (Python 3.11) | Async ASGI server run by non-root `appuser` (UID 10001), validates input payloads, tracks execution latency telemetry in `X-Process-Time`. |
| **Bi-LSTM Predictor** | `PyTorch` | 2-layer stacked bidirectional LSTM mapping sequential word embeddings, generating gradient saliency attribution. |
| **BERT Predictor** | `Hugging Face Transformers` | 12-layer multi-head self-attention transformer extracting head-level token attributions for interpretable verification. |
| **Resilience Engine** | Calibrated Heuristics | Guaranteed zero unhandled runtime 500 exceptions if neural weight checkpoints are absent from disk. |
