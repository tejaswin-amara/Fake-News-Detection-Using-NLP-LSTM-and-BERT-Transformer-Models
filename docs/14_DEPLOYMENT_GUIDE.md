# Deployment Guide

## Local development

### API

```bash
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Run:

```bash
uvicorn src.serving.app:app --host 127.0.0.1 --port 8000
```

Use the actual final application import path if the unified repository changes it.

### Frontend

```bash
pnpm install
pnpm dev
```

## Docker

Preferred integrated startup:

```bash
docker compose up --build
```

Expected services:

```text
frontend → ml-api
```

Additional MLflow/Redis services are optional for the MVP and can be enabled for the capstone environment.

## Environment variables

At minimum:

```text
FAKE_NEWS_API_BASE_URL
MODEL_ARTIFACT_PATH
CORS_ALLOWED_ORIGINS
```

Never commit credentials.

## Production-style deployment

Before public deployment:

- use a verified artifact;
- configure explicit CORS;
- configure rate limiting;
- enable artifact integrity controls;
- use secure secret management;
- use TLS;
- configure logging;
- define resource limits;
- verify readiness and health behavior.

## Rollback

Keep the previous known-good artifact and application image.

Rollback should restore:

```text
application version
+
model artifact version
+
configuration version
```

as a coherent unit.
