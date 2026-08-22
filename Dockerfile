# syntax=docker/dockerfile:1.7

FROM python:3.11-slim@sha256:9c900dea9e8fb7e16277c179b555cc72d29a352dbc33cff48ad5a0412fd5bfc7 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

RUN python -m venv "$VIRTUAL_ENV" \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements-runtime.txt pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install -r requirements-runtime.txt

FROM python:3.11-slim@sha256:9c900dea9e8fb7e16277c179b555cc72d29a352dbc33cff48ad5a0412fd5bfc7 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    SERVING_MODE=native \
    MODEL_ARTIFACT=/app/artifacts/models/logistic_l2.joblib \
    HOME=/tmp \
    TMPDIR=/tmp \
    LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends libjemalloc2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY src ./src
COPY configs ./configs
COPY scripts ./scripts
COPY README.md pyproject.toml ./

# Runtime artifacts and monitoring baselines should be mounted at deployment time.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /nonexistent --no-create-home appuser \
    && mkdir -p /app/artifacts /app/reports /app/mlflow \
    && chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["sh", "-c", "if [ \"${GUNICORN_ENABLED:-false}\" = \"true\" ]; then exec gunicorn -k uvicorn.workers.UvicornWorker --workers ${WEB_CONCURRENCY:-2} --bind ${API_HOST:-0.0.0.0}:${API_PORT:-8000} src.serving.app:app; else exec uvicorn src.serving.app:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}; fi"]
