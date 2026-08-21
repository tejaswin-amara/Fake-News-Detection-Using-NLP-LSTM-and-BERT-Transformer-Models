# Deployment and Operations

## End-to-end prediction trace

The production boundary is deliberately explicit:

> **HTTP payload → Pydantic validation → packaged text transformation/tokenization → native or parity-verified ONNX inference → calibrated probability/uncertainty output → response metadata and latency → probability/text/feature drift logging → non-mutating retraining signal.**

Training creates an immutable artifact containing the fitted text pipeline, estimator, label mapping, feature schema, model/config/source metadata, artifact version, calibration status, and optional confidence-interval manifest. Serving loads that artifact rather than reconstructing preprocessing from configuration. This is the primary defense against notebook-to-production training-serving skew.

## Local API and probes

Start native serving after producing a model artifact:

```bash
MODEL_ARTIFACT=artifacts/models/logistic_l2.joblib \
  SERVING_MODE=native \
  uvicorn src.serving.app:app --host 0.0.0.0 --port 8000
```

The production-compatible container supports the same command and can use Gunicorn workers:

```bash
docker build -t fake-news-api:phase4 .
docker run --rm -p 8000:8000 \
  -e MODEL_ARTIFACT=/mounted/models/logistic_l2.joblib \
  -v "$PWD/artifacts:/mounted/artifacts:ro" \
  fake-news-api:phase4
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Process and artifact-load diagnostics; degraded status is allowed when the artifact is absent |
| `/ready` | GET | Strict readiness probe; returns 200 only when a prediction-capable artifact is loaded |
| `/predict` | POST | One validated title/body request |
| `/predict/batch` | POST | Bounded ordered batch of requests |
| `/monitoring/drift` | POST | Validate and enqueue numeric, prediction-probability, and text-domain drift work; returns `202` and `job_id` |
| `/monitoring/drift/{job_id}` | GET | Poll bounded drift-job state and completed result |

Every prediction response contains label, label name, real/fake probabilities, raw and calibrated probability fields, nullable confidence-interval bounds, model name, artifact version, calibration status, and serving mode. Every HTTP response exposes `X-Process-Time-Ms`. Confidence intervals remain `null` unless a validated uncertainty manifest is included; the service never fabricates uncertainty.

### Curl examples

```bash
curl -s http://localhost:8000/health
curl -i http://localhost:8000/ready

curl -s -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example headline","text":"Example article body."}'

curl -s -X POST http://localhost:8000/predict/batch \
  -H 'Content-Type: application/json' \
  -d '{"requests":[{"text":"First article."},{"text":"Second article."}]}'

curl -s -X POST http://localhost:8000/monitoring/drift \
  -H 'Content-Type: application/json' \
  -d '{"reference_probabilities":[0.1,0.2,0.3,0.4],"current_probabilities":[0.8,0.9,0.9,0.95],"baseline_revision":"training-reference-v1","window_id":"2026-08-20"}'
# Read the returned job_id, then poll it until status is completed, failed, or expired.
curl -s http://localhost:8000/monitoring/drift/<job_id>
```

Empty or whitespace-only text, oversized text, empty batches, malformed JSON, and invalid probability/reference arrays are rejected with validation errors. `/ready` returns 503 when the configured model artifact cannot be loaded.

## Native and ONNX packaging

`src/serving/export.py` creates package manifests with model name, artifact version, preprocessing revision, calibration revision, label map, runtime metadata, source IDs, and native/ONNX SHA-256 values. Native joblib packaging is authoritative when a tokenizer, vectorizer, neural layer, or custom operation cannot be represented safely by the selected converter.

Compatible sklearn/tree estimators can be exported with `export_onnx_sklearn`, executed with ONNX Runtime, and checked with `assert_onnx_parity`. Deployment acceptance requires matching output shapes and maximum absolute probability error below `1e-5` on the conformance fixture. Unsupported operations must fail explicitly or use the native fallback; the system must not claim ONNX support merely because an output file can be produced.

TorchScript/ONNX neural export remains optional and resource-dependent. BERT tokenization, dynamic padding, custom layers, and pretrained weights must be included in the model manifest when an adapter supports them. No private model weights, raw datasets, credentials, or DVC/MLflow remotes are committed.

## Configuration and runtime mounts

`.env.example` and `configs/default.yaml` define native/ONNX artifact paths, serving mode, calibration and package manifests, readiness behavior, batch/text limits, MLflow URI, drift baselines, drift thresholds, and retraining-hook policy. Baselines and model artifacts should be mounted read-only or retrieved through an approved artifact store at deployment time rather than baked into an image.

## Monitoring and drift policy

`src/monitoring/drift.py` provides:

- **KS tests** for continuous feature and text-statistic distributions, including sample counts, p-values, alpha, and drift decisions.
- **PSI** for numeric features and prediction-probability distributions, with configurable alert thresholds.
- **Text-domain monitoring** for character/token/sentence lengths, lexical diversity, punctuation, uppercase/digit ratios, readability-compatible length features, and OOV rate against the approved reference vocabulary.
- **Structured retraining signals** containing drifted features, baseline revision, window ID, reason, cooldown key, suggested action, approval requirement, and explicit `side_effects: none`.

Reference distributions must be created from an approved training/reference window and never from the final test split. Monitoring is observational: the endpoint does not train, deploy, replace, or mutate a model.

### Retraining trigger policy

A drift signal is a request for review, not an autonomous deployment action. An operator should require a minimum observation window and sample count, apply the configured cooldown/de-duplication key, review data quality and delayed labels, version the new data with DVC, run a new MLflow experiment, reproduce the train/validation/test split, rerun ONNX/native parity and serving tests, perform shadow/canary validation, obtain human approval, and retain a rollback artifact before promotion. Concept drift requires trustworthy delayed labels; feature/probability drift alone does not establish model degradation.

## Container security and operations

The multi-stage Dockerfile builds dependencies separately from the runtime image, excludes compilers from the final stage, runs as a non-root user, exposes only port 8000, and supports Uvicorn or Gunicorn/Uvicorn-worker execution. `.dockerignore` excludes raw data, processed data, DVC cache, MLflow stores, reports, notebooks, tests, secrets, model caches, and local build artifacts. Authentication, TLS, rate limiting, network policy, and secret management remain deployment-boundary responsibilities.

## Notebook-to-production remediation

The repository closes the notebook-to-production gap through train-only fitted transforms, immutable packaged artifacts, explicit validation-only calibration, final-test isolation, runtime Pydantic schemas, bounded payloads, model/version metadata, ONNX parity tests, local/CI verification, baseline-controlled monitoring, and non-mutating retraining hooks. Notebook figures are evidence artifacts; production code imports reusable package functions and never depends on notebook state.

## MLflow and DVC

MLflow remains optional and disabled by default. When enabled, training and held-out evaluation log parameters, metrics, reports, plots, model artifacts, configuration, and provenance to the configured tracking URI. DVC versions raw data and orchestrates the `ingest`, `train`, and `evaluate` stages; credentials and remote endpoints are operator-owned.

```bash
python scripts/init_mlflow.py --tracking-uri mlruns --experiment-name fake-news-detection
python -m src.train --mlflow --train data/processed/train.csv --output artifacts/models/logistic_l2.joblib
python -m src.evaluate --mlflow --test data/processed/test.csv --artifact artifacts/models/logistic_l2.joblib --output reports/evaluation/final_metrics.json
mlflow ui --backend-store-uri mlruns
```

## Phase 5 one-command lifecycle

The master runner is `scripts/run_pipeline.sh`. It resolves the repository root, enables strict shell failure behavior, validates YAML/source/DVC contracts, initializes or reuses local MLflow, runs `dvc repro`, performs a separate MLflow-backed held-out evaluation, exports ONNX when the estimator supports it and native parity is below the configured epsilon, executes the complete pytest suite, and generates the report bundle.

```bash
chmod +x scripts/run_pipeline.sh
./scripts/run_pipeline.sh
```

The runner uses `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME`, `MODEL_ARTIFACT`, `TRAINING_DATA`, `ONNX_PATH`, `PACKAGE_MANIFEST`, and `REPORT_DIR` when supplied. It fails clearly if governed raw data or a configured DVC remote is unavailable. It never substitutes synthetic data for ISOT/WELFake training and never silently converts failed ONNX parity into an ONNX-verified status.

## Docker Compose orchestration

`docker-compose.yml` defines four health-aware services on an isolated bridge network:

| Service | Role | Persistent state and boundary |
|---|---|---|
| `api` | Rootless FastAPI serving image | Read-only `artifacts/` and `configs/` mounts; `/ready` healthcheck; port 8000; depends on healthy Redis |
| `redis` | Atomic distributed rate-limit store | Read-only root filesystem with named `fake-news-detection-redis` data volume; healthchecked on the isolated network |
| `mlflow` | Local MLflow tracking server | Named `fake-news-detection-mlflow` volume under the appuser-owned `/app/mlflow`; port 5000 |
| `traffic` | Synthetic prediction/drift generator | No data volume; logs statuses/latency only; depends on API and MLflow health |

Start and stop the complete local stack:

```bash
cp .env.example .env
docker compose up --build
docker compose ps
curl -s http://localhost:8000/ready
curl -s http://localhost:5000/health
docker compose down
```

The traffic service invokes `/predict` at `TRAFFIC_INTERVAL_SECONDS` and submits `/monitoring/drift` every `TRAFFIC_DRIFT_EVERY` requests. Drift submission is asynchronous and returns `202`; the service records the submission status and does not trigger retraining. It can be run as a finite smoke test outside Compose:

```bash
python scripts/synthetic_traffic.py \
  --base-url http://localhost:8000 \
  --interval 0 \
  --drift-every 2 \
  --max-requests 5
```

Synthetic traffic contains no user article text and does not trigger retraining, model replacement, or deployment. SIGINT/SIGTERM stops the loop cleanly.

## CI/CD gates

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`. The quality job installs the pinned requirements, validates configuration and DVC stages, runs the source audit, Ruff, compilation, starts a local MLflow server, initializes the CI experiment, and runs `python -m pytest -q`. The container job builds the rootless multi-stage image and scans it with Trivy for high and critical vulnerabilities, failing on actionable findings. Logs, reports, and image metadata are uploaded as CI artifacts without including raw data or secrets.

The workflow does not claim a full-dataset benchmark when CI lacks governed raw inputs. DVC graph validation and the deterministic fixture/integration tests remain separate from a data-dependent `dvc repro` invocation.

## MLflow report bundle

`scripts/generate_reports.py` queries only `FINISHED` MLflow runs in the selected experiment and selects the best run by the declared metric and direction. It downloads all logged artifacts recursively and writes:

- `reports/best_model_summary.json` with run ID, model name, metrics, parameters, tags, selection direction, provenance, and test-selection policy.
- Stable plot names for reliability, calibration comparison, ROC/PR, confusion, and SHAP images when the selected run logged them.
- `reports/mlflow_runs/<run_id>/` containing the downloaded source artifacts.
- `reports/report_manifest.json` containing SHA-256 checksums, run IDs, plot availability, and summary path.

A missing plot is recorded as `unavailable` with a reason; no stand-in image or fabricated metric is generated. The command fails when no finalized run contains the configured primary metric or when MLflow provenance cannot be resolved.

```bash
python scripts/generate_reports.py \
  --tracking-uri mlruns \
  --experiment-name fake-news-detection \
  --output-dir reports \
  --primary-metric pr_auc \
  --direction maximize
```

## Phase 5 acceptance evidence

The repository acceptance gate includes YAML parsing for workflow/Compose/configuration, DVC stage parsing, source-register audit, shell syntax, Ruff, compilation, the complete test suite, dependency resolution, MLflow report selection/download checks, ONNX parity checks, API/drift checks, and CI Docker build/scan. A local Docker build is environment-dependent; the authoritative image build and vulnerability scan run in GitHub Actions.

## Deep Audit hardening controls

The final serving boundary is deny-by-default. Set `CORS_ALLOWED_ORIGINS` to an explicit comma-separated allowlist in production; do not combine `*` with credentials. `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `RATE_LIMIT_MAX_CLIENTS`, and `TRUSTED_PROXY_IPS` control the bounded in-process limiter. `/health` and `/ready` remain available to orchestration even when prediction traffic is rate-limited.

```bash
export CORS_ALLOWED_ORIGINS=https://example.com
export CORS_ALLOW_CREDENTIALS=false
export RATE_LIMIT_REQUESTS=120
export RATE_LIMIT_WINDOW_SECONDS=60
export TRUSTED_PROXY_IPS=10.0.0.10
```

The local limiter is intentionally not described as a distributed protection mechanism. Multi-replica deployments must enforce a shared gateway or Redis-backed limiter before the API replicas. Forwarded client addresses are accepted only from configured trusted proxy peers.

`SERVING_MODE=onnx` requires `ONNX_MODEL_PATH`, an existing packaged artifact, and an allowed provider list. `ONNX_EXECUTION_PROVIDERS`, `ONNX_INTRA_OP_THREADS`, `ONNX_INTER_OP_THREADS`, `ONNX_GRAPH_OPTIMIZATION`, and `ONNX_CPU_MEM_ARENA` are validated at startup. Native mode remains the safe fallback when ONNX is unavailable; a parity failure is fatal to ONNX packaging and never becomes an unverified ONNX deployment.

The Compose stack runs each service with a read-only root filesystem, `cap_drop: ALL`, `no-new-privileges`, a dedicated init process, bounded memory/CPU, and a restricted `/tmp` tmpfs. Only the MLflow named volume is writable. The API’s artifacts and configuration are mounted read-only. The runtime image executes as `appuser`.

The lifecycle runner validates the DVC cache path before running and retries idempotent `dvc repro` a bounded number of times. MLflow initialization retries transient failures and can use the explicitly configured local fallback. Neither path deletes caches, fabricates data, suppresses provenance failures, nor performs autonomous retraining.

See [`docs/security_hardening.md`](security_hardening.md) for the threat model, request-boundary policy, signed-artifact and air-gapped BERT controls, sparse/dense serving boundary, Redis/semaphore/queue safeguards, logging/secrets policy, drift safeguards, CI security gates, and rollback response.

## Phase 7 zero-trust operating profile

Production artifact promotion should set `REQUIRE_SIGNED_ARTIFACT=true`, provide `PACKAGE_MANIFEST` and `ARTIFACT_PUBLIC_KEY_B64`, and mount the artifact directory read-only. `MODEL_ARTIFACT_SHA256` remains a valid single-artifact integrity fallback only when signed manifests are explicitly disabled for development. BERT deployments must point `HF_MODEL_DIR` at a pre-staged local `bert-base-uncased` bundle containing `config.json`, `vocab.txt`, and `model.safetensors`; outbound Hub access is disabled by the loader.

ONNX is a dense-only serving format in this project. Native TF-IDF models retain sparse matrices, while ONNX export and runtime reject sparse feature objects rather than densifying them. For online unsupervised augmentation, keep DBSCAN disabled and use the bounded SVD-backed path. Near-duplicate filtering is streaming MinHash/LSH with bounded buckets and no all-pairs matrix.

For more than one worker or replica, set `DISTRIBUTED_RATE_LIMITER=redis` and `REDIS_URL` and ensure the Redis service or an equivalent shared gateway is healthy before admitting traffic. Set `MAX_INFLIGHT_INFERENCE`, `DRIFT_QUEUE_MAXSIZE`, `DRIFT_WORKERS`, and `DRIFT_JOB_TTL_SECONDS` from observed capacity. A full drift queue returns `503`, inference-budget exhaustion returns `429`, and expired job IDs return a non-success status; none of these conditions silently execute unbounded work.

## Scaling, workers, and rate limiting

The default Compose deployment uses one Uvicorn worker and one CPU because the rate limiter is intentionally in-process and the ONNX/native thread budget is one intra-op and one inter-op thread. This is the safe single-instance baseline.

For a larger deployment, choose one scaling dimension deliberately:

| Deployment shape | Guidance | Rate-limit requirement |
|---|---|---|
| One container, one Uvicorn worker | Lowest operational complexity and deterministic local limiter behavior | In-process limiter is sufficient for the single instance |
| One container, multiple Gunicorn/Uvicorn workers | Set `GUNICORN_ENABLED=true` and `WEB_CONCURRENCY` only after configuring `DISTRIBUTED_RATE_LIMITER` | A shared gateway or Redis-backed limiter is required; startup rejects workers greater than one without the declaration |
| Multiple replicas | Prefer one worker per CPU-bounded replica and scale replicas through the orchestrator | Enforce a shared limiter and trusted proxy policy before the replicas |

Gunicorn workers multiply model memory, preprocessing state, and request concurrency. Replicas multiply that cost again. Do not increase workers while leaving `cpus: 1.0` and ONNX intra/inter-op threads at one without load evidence. Re-run `tests/test_serving_stress.py` or an equivalent production load test after changing vocabulary size, batch size, worker count, or replica count. The stress evidence is written to `reports/serving_stress_memory.json` when the test runs.

## Day 3 zero-trust deployment controls

Drift admission is bounded and non-blocking. `POST /monitoring/drift` returns `202` with a `job_id` when work is accepted, `429` with `Retry-After: 5` when the queue is full, and `503` only when the queue manager is stopping or unavailable. Clients should retry 429 responses with backoff and poll `GET /monitoring/drift/{job_id}` only for accepted jobs. Queue capacity, worker count, and job TTL are controlled by `DRIFT_QUEUE_MAXSIZE`, `DRIFT_WORKERS`, and `DRIFT_JOB_TTL_SECONDS`.

The Compose deployment requires a URL-safe `REDIS_PASSWORD`. The API uses an authenticated URL such as `redis://:${REDIS_PASSWORD}@redis:6379/0`, while Redis starts with `--requirepass`. Redis is attached only to the internal `redis-internal` network, and the API is attached to both `fake-news-net` and `redis-internal`. MLflow and synthetic traffic remain on `fake-news-net` only. Do not commit the password; inject it through an untracked `.env`, an orchestrator secret, or an equivalent secret manager. If a password contains URL-reserved characters, percent-encode it before constructing `REDIS_URL`.

The runtime Docker stage installs `libjemalloc2` and preloads `/usr/lib/x86_64-linux-gnu/libjemalloc.so.2`. This reduces allocator fragmentation risk for repeated sparse operations, but operators must still size memory, batch limits, workers, and ONNX threads from load evidence. The setting is validated statically and by the authoritative container build in CI.

All regex execution in `src/features/text.py` uses the pinned `regex` package with a 50,000-character bound and a 0.050-second timeout. Timeout-safe fallbacks prevent an adversarial article from monopolizing a request worker. The bound complements, rather than replaces, API-level `MAX_TEXT_CHARACTERS` and request-body limits.

## Day 4 cloud-native observability and orchestration

The service exposes Prometheus metrics at `/metrics`. A cluster scraper should use the API Service annotations in `k8s/base/api-deployment.yaml` or an organization-managed ServiceMonitor. The primary series are `fake_news_http_request_latency_seconds`, `fake_news_inference_latency_seconds`, `fake_news_drift_queue_depth`, `fake_news_rate_limiter_rejections_total`, and `fake_news_drift_monitoring_errors_total`. Labels are intentionally bounded and exclude article text, request IDs, job IDs, client addresses, and arbitrary paths.

Startup now performs a deterministic warm-up inference after the model artifact and any ONNX session are loaded. `/health` reports `warmup_complete`; `/ready` returns 503 until warm-up succeeds. Kubernetes therefore uses a startup probe on `/health`, a liveness probe on `/health`, and a readiness probe on `/ready`. The initial startup budget is intentionally generous enough for model loading and the first inference; reducing it can cause restart loops during cold cluster nodes.

The Kubernetes base can be inspected and built with:

```bash
kubectl kustomize k8s/base
kubectl apply -k k8s/base
kubectl -n fake-news get deploy,svc,hpa,networkpolicy,pods
kubectl -n fake-news port-forward svc/fake-news-api 8000:80
curl -s http://127.0.0.1:8000/metrics
```

Before applying the base, an operator must create the external Redis and artifact-verification Secrets and provision the artifact PVC content. The committed manifests intentionally contain no passwords or private keys:

```bash
kubectl -n fake-news create secret generic fake-news-redis \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --from-literal=redis-url="redis://:${REDIS_PASSWORD}@redis:6379/0"
kubectl -n fake-news create secret generic fake-news-artifact-verification \
  --from-literal=public-key-b64="$ARTIFACT_PUBLIC_KEY_B64"
```

The `fake-news-api` Deployment requests two replicas and limits each pod to 1 CPU and 1Gi memory. `api-hpa.yaml` scales between two and ten replicas at a 75% average CPU target, with a conservative scale-down window. HPA operation requires metrics-server or an equivalent resource metrics API, and the artifact volume must be available to every scheduled API pod.

Redis is exposed only as the in-cluster `redis` Service. `networkpolicy.yaml` allows TCP 6379 ingress only from API pods and restricts Redis egress to cluster DNS. The cluster must use a NetworkPolicy-enforcing CNI; otherwise the policy is only declarative metadata and cannot be treated as an isolation control. MLflow and synthetic traffic are not permitted by the Redis ingress policy.

CI validates every Kubernetes resource with strict kubeconform v0.6.7 against Kubernetes API version 1.30.0. Local static YAML parsing is useful but is not a substitute for the CI schema gate or a cluster-level dry run.
