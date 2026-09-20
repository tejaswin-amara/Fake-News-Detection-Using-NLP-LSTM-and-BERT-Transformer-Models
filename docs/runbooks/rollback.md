# Operational Runbook: Rollback Procedures

**Document Version:** 1.0.0  
**Target Systems:** `veritas-frontend` (Caddy 2), `veritas-backend` (FastAPI / ML Engine), Container Images, Model Checkpoints

This runbook defines deterministic standard operating procedures for executing clean, rapid rollbacks of container deployments, application code, and machine learning model checkpoints.

---

## 1. Rollback Triggers

Initiate a rollback immediately if any of the following conditions persist for > 5 minutes after a deployment:
- **Error Rate Spike:** HTTP 5xx error rate on `/api/predict/*` exceeds 1% of total request volume.
- **Latency Regression:** P95 inference latency increases by > 100% over the previous release baseline.
- **Model Regression:** Silent inference degradation, invalid attribution structures, or sudden drop in validation F1 score.
- **Container Health Failure:** Ingress reverse proxy reports consecutive upstream connection refusals (`502 Bad Gateway`).
- **Security Alert:** Critical Zero-Day vulnerability (CVE CVSS >= 9.0) discovered in an active container layer.

---

## 2. Pre-Rollback Assessment & Target Identification

Before executing rollback actions, identify the target known-good release:

```bash
# 1. Identify previous stable git commit tag
git log --oneline -n 5

# 2. Inspect active Docker image digests
docker images --digests | grep -E "veritas|fake-news"

# 3. Check current environment variables and config diff
git diff HEAD~1 docker-compose.yml
```

---

## 3. Rollback Procedures by Component

### Procedure A: Docker Compose Full-Stack Rollback

To revert the entire application stack to the previous stable release tag:

```bash
# Step 1: Checkout the prior stable release tag or commit SHA
git checkout <PREVIOUS_STABLE_TAG_OR_COMMIT>

# Step 2: Re-pull or re-build deterministic images
docker compose build --pull

# Step 3: Recreate containers with zero downtime grace period
docker compose up -d --force-recreate --remove-orphans

# Step 4: Verify container health and process status
docker compose ps
curl -fsSL http://localhost:3000/healthz || exit 1
curl -fsSL http://localhost:8000/readyz || exit 1
```

---

### Procedure B: Fast Backend Container Image Rollback

If the regression is isolated strictly to the backend ML inference engine:

```bash
# Step 1: Export previous image digest
export BACKEND_IMAGE="ghcr.io/tejaswin-amara/fake-news-backend:sha-<PREVIOUS_SHA>"

# Step 2: Update image reference in docker-compose.override.yml
cat <<EOF > docker-compose.override.yml
services:
  backend:
    image: ${BACKEND_IMAGE}
EOF

# Step 3: Re-launch backend service
docker compose up -d backend

# Step 4: Validate model responsiveness
curl -s -X POST http://localhost:8000/api/predict/both \
  -H "Content-Type: application/json" \
  -d '{"text": "Breaking news test article to verify rollback response."}' | grep -o '"prediction"'
```

---

### Procedure C: ML Model Artifact & Weight Rollback

If inference behavior or attribution weights degrade following a model checkpoint update:

```bash
# Step 1: Rollback DVC data/model pointer to previous lockfile
git checkout HEAD~1 -- dvc.lock backend/weights/

# Step 2: Pull validated weights from remote storage
dvc pull backend/weights/

# Step 3: Verify sha256 checksum against model registry ledger
sha256sum backend/weights/bilstm.pt
sha256sum backend/weights/bert/pytorch_model.bin

# Step 4: Signal backend to reload model weights without restarting container
# (or trigger a clean rolling restart of the backend service)
docker compose restart backend

# Step 5: Validate benchmark endpoints reflect previous baseline
curl -fsSL http://localhost:8000/api/benchmarks | grep -o '"models"'
```

---

### Procedure D: Frontend Asset Cache Invalidation

If the frontend bundle has a regression or asset loading failure:

```bash
# Step 1: Force recreation of Caddy edge proxy container
docker compose up -d --force-recreate frontend

# Step 2: Clear edge proxy in-memory cache and verify CSP headers
curl -sI http://localhost:3000/ | grep -iE "content-security-policy|etag"
```

---

## 4. Post-Rollback Verification Checklist

Complete the following validation steps before declaring the system restored:

- [ ] `GET /healthz` returns `{"status":"ok"}` with HTTP 200 within < 100ms.
- [ ] `GET /readyz` returns `{"status":"ready"}` indicating models are fully loaded.
- [ ] `POST /api/predict/both` returns valid JSON with `bilstm` and `bert` predictions and token attributions.
- [ ] `docker compose ps` shows both `frontend` and `backend` in healthy running state with 0 recent restarts.
- [ ] Playwright E2E smoke tests pass:
  ```bash
  pnpm --prefix frontend test:e2e
  ```
- [ ] Incident commander posts notification to on-call channel confirming stable restoration.
