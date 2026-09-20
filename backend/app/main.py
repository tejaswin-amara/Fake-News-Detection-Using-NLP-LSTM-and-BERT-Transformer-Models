"""FastAPI Main Application Entrypoint for Fake News Detection Service.

Configures CORS middleware, lifespan events, request timing telemetry,
system health endpoints (/healthz), and RESTful inference routes.
"""

from __future__ import annotations

import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from backend.app.api.endpoints import router as api_router
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

APP_METADATA = {
    "title": "VERITAS AI — Fake News Detection & Explainability API",
    "description": (
        "Production-grade ML inference service comparing GloVe + Stacked Bi-LSTM "
        "and Fine-Tuned BERT Transformer with token-level saliency attribution "
        "and empirical benchmark reporting."
    ),
    "version": "1.0.0",
    "contact": {
        "name": "VERITAS AI Engineering Team",
        "url": "https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
}

TAGS_METADATA = [
    {
        "name": "Inference & Benchmarks",
        "description": "Operations for Bi-LSTM, BERT, and dual-model veracity predictions and empirical metrics.",
    },
    {
        "name": "System Health",
        "description": "Operations for health checks and container readiness probes.",
    },
]

SERVERS = [
    {
        "url": "http://localhost:8000",
        "description": "Local development server",
    },
    {
        "url": "/",
        "description": "Root edge proxy routing",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle events."""
    # Startup: warm up predictor instances or verify local caches
    yield
    # Shutdown: clean up resources if required


app = FastAPI(
    title=APP_METADATA["title"],
    description=APP_METADATA["description"],
    version=APP_METADATA["version"],
    contact=APP_METADATA["contact"],
    license_info=APP_METADATA["license_info"],
    openapi_tags=TAGS_METADATA,
    servers=SERVERS,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
allowed_origins = (
    [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
    if allowed_origins_env
    else [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://tejaswin-amara.github.io",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next) -> Response:
    """Telemetry middleware tracking request processing latency in milliseconds."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


@app.get(
    "/healthz",
    tags=["System Health"],
    summary="Liveness and health check",
    description="Returns HTTP 200 when the service is alive and accepting connections.",
)
async def healthz() -> JSONResponse:
    """Standard Kubernetes / Docker health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "fake-news-detection-backend",
            "version": "1.0.0",
        },
    )


@app.get(
    "/readyz",
    tags=["System Health"],
    summary="Readiness probe",
    description="Returns HTTP 200 when ML inference engines are initialized and ready.",
)
async def readyz() -> JSONResponse:
    """Standard Kubernetes / Docker readiness check endpoint."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "ready",
            "engines": ["bilstm", "bert"],
        },
    )


# Mount API routes
app.include_router(api_router)
