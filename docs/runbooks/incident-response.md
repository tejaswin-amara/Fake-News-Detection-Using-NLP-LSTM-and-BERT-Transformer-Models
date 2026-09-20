# Operational Runbook: Incident Response & Triage

**Document Version:** 1.0.0  
**Target Systems:** `veritas-frontend` (Caddy 2), `veritas-backend` (FastAPI / PyTorch ML Engine)

This runbook defines triage procedures, operational protocols, and remediation workflows for runtime incidents in the **VERITAS AI** full-stack fake news detection platform.

---

## 1. Incident Severity Classifications

| Severity | Definition | Target MTTA | Target MTTR | Examples |
| :--- | :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Complete service outage or API failure across all models; customer-facing 502/504 errors on `/api/predict/*`. | < 15 min | < 1 hour | Backend container crash looping; Caddy unable to connect to upstream; persistent host OOM kills. |
| **SEV-2 (High)** | Degraded inference performance; single model failure (e.g. BERT timing out while Bi-LSTM functions); P99 latency > 3000ms. | < 30 min | < 2 hours | Transformer attention extraction CPU saturation; PyTorch memory leak causing pod throttling. |
| **SEV-3 (Medium)** | Minor non-blocking anomalies; benchmark endpoint slow; frontend layout distortion or non-critical telemetry failure. | < 2 hours | < 8 hours | Static asset cache miss; telemetry header missing; local heuristic fallback activated due to weight path issue. |

---

## 2. Emergency Triage Command Center

When an alert fires or an incident is reported, execute immediate diagnostic queries:

```bash
# 1. Inspect container running states and restart counts
docker compose ps

# 2. Tail real-time backend logs filtered for errors or tracebacks
docker compose logs --tail=200 -f backend | grep -iE "error|exception|traceback|oom|timeout"

# 3. Check live resource consumption (CPU and Memory limits)
docker stats --no-stream

# 4. Validate health probe responsiveness
curl -i http://localhost:3000/healthz
curl -i http://localhost:8000/readyz
```

---

## 3. Incident Scenarios & Remediation Procedures

### Scenario A: Model Inference Timeouts & Latency Spikes (SEV-1 / SEV-2)

#### Symptoms:
- Client experiences pending spinners or HTTP 504 Gateway Timeout from Caddy.
- `X-Process-Time` response header exceeds 2000ms.
- High CPU utilization (>95%) on the backend container.

#### Root Causes:
1. Long input sequences submitted without truncation, forcing quadratic self-attention complexity $\mathcal{O}(N^2)$ in BERT.
2. Worker process queue starvation under concurrent request loads.
3. Thread contention within PyTorch intra-op parallelism.

#### Remediation Steps:
1. **Verify payload length:** Confirm input text conforms to max token constraints (default `max_length=512`).
2. **Throttle PyTorch thread pools:** In container environment, set intra-op thread count:
   ```bash
   # Add to backend environment:
   export OMP_NUM_THREADS=4
   export MKL_NUM_THREADS=4
   ```
3. **Switch traffic to lightweight Bi-LSTM:** If BERT is saturated, route frontend clients to `/api/predict/lstm` which completes in ~18ms vs ~140ms for BERT.
4. **Restart backend workers:**
   ```bash
   docker compose restart backend
   ```

---

### Scenario B: Container Memory Exhaustion (OOMKilled) (SEV-1)

#### Symptoms:
- Backend container exits unexpectedly with code `137` (`SIGKILL` by kernel OOM killer).
- `docker compose ps` shows backend container status `Restarting (...)`.
- Syslog shows: `Out of memory: Killed process ... (python)`.

#### Root Causes:
1. Accumulated intermediate transformer attention tensors in PyTorch memory without `torch.no_grad()` context.
2. Container memory limit configured too tight (< 1.5 GiB for BERT transformer weights).
3. Memory fragmentation under sustained batch inference.

#### Remediation Steps:
1. **Check OOM status:**
   ```bash
   docker inspect veritas-backend --format='{{.State.OOMKilled}}'
   ```
2. **Ensure inference runs under evaluation mode:** Verify `model.eval()` and `with torch.no_grad():` are wrapping all prediction loops in `backend/app/models/bert.py`.
3. **Clear PyTorch caching:** Trigger garbage collection or restart the worker pool.
4. **Increase container memory headroom:** In `docker-compose.yml`, update deploy resources:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2.5G
           reservations:
             memory: 1.5G
   ```
5. **Redeploy updated compose configuration:**
   ```bash
   docker compose up -d backend
   ```

---

### Scenario C: Corrupted or Missing Model Checkpoints (SEV-2)

#### Symptoms:
- Backend starts with warnings: `PyTorch model weights not found or failed to load. Initializing fallback engine.`
- `/readyz` returns 200 OK but inference uses calibrated heuristic attribution instead of trained weights.

#### Remediation Steps:
1. **Check weight volume mounts:**
   ```bash
   docker compose exec backend ls -la /app/weights
   ```
2. **Verify sha256 checksums of model artifacts:**
   ```bash
   sha256sum backend/weights/bilstm.pt backend/weights/bert/pytorch_model.bin
   ```
3. **Re-sync weights from secure artifact storage:**
   ```bash
   # Pull versioned artifacts from release registry / S3
   dvc pull
   docker compose restart backend
   ```

---

## 4. Post-Incident Review Protocol

Following resolution of any SEV-1 or SEV-2 incident:
1. Preserve container logs and telemetry metrics for the affected window.
2. File an Incident Post-Mortem within 24 hours documenting:
   - Root cause analysis (5 Whys methodology).
   - Exact timeline of detection, diagnosis, mitigation, and recovery.
   - Preventive action items (e.g. tightening rate limits, optimizing tensor caching, refining alert thresholds).
