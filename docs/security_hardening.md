# Security Hardening and Operational Resilience

## Scope and security posture

This document records the final hardening controls for the fake-news detection service. It is an engineering control record, not a security certification or a claim of immunity from adversarial abuse. The service accepts untrusted article text and monitoring telemetry, loads a governed model artifact, performs CPU-bound inference, and emits predictions and signal-only drift findings.

> **Security objective:** reject malformed or resource-exhausting input at the API boundary, keep model/artifact failures fail-closed, prevent untrusted text from entering logs or error bodies, and make every infrastructure fallback explicit and observable.

## Threat model and trust boundaries

The public HTTP boundary is untrusted. Article titles, article text, JSON keys, numeric drift arrays, origin headers, forwarded client headers, and request identifiers are attacker-controlled until validation completes. The packaged model, calibration metadata, ONNX artifact, reference distributions, configuration, DVC cache, and MLflow tracking store are trusted only after filesystem, schema, provenance, and parity checks.

The request path is therefore: HTTP server → CORS and rate-limit middleware → strict Pydantic validation → bounded preprocessing → reusable native or parity-verified ONNX session → finite probability validation → response serialization. Monitoring follows the same validation boundary and never initiates retraining. The response never echoes submitted article text or exception tracebacks.

## API boundary controls

`src/serving/app.py` uses Pydantic v2 models with `extra="forbid"`, strict field constraints, maximum text/batch sizes, control-character rejection, finite numeric checks, probability bounds, and complete reference/current-pair validation. NUL bytes, disallowed ASCII control characters, malformed drift arrays, NaN/infinite values, unknown fields, empty content, and oversized batches are rejected with sanitized `422` responses.

CORS is deny-by-default. Production must set `CORS_ALLOWED_ORIGINS` to an explicit allowlist. Wildcard origins cannot be combined with credentials. Allowed methods and headers are explicit and configurable. The service does not trust `X-Forwarded-For` unless the connecting peer is in `TRUSTED_PROXY_IPS`.

The in-process `RateLimiter` uses a bounded fixed window, stale-event eviction, maximum client-entry eviction, thread synchronization, and `Retry-After` responses. `/health` and `/ready` are exempt so orchestration can detect recovery. This limiter is a safe single-instance fallback, not a distributed guarantee. Multi-replica production deployments must enforce a shared gateway or Redis-backed limit before traffic reaches the replicas.

## Model and inference controls

`ModelService` loads the serialized artifact once during FastAPI lifespan startup. It does not initialize a model or ONNX session per request. Native packaged preprocessing remains authoritative. ONNX mode requires an existing artifact, explicit provider configuration, positive intra/inter-op thread counts, and an allowed graph optimization level. The default is one-thread CPU execution to avoid uncontrolled oversubscription in containers.

`src/serving/predictor.py` validates ONNX input/output shapes, finite values, class ordering, probability bounds, and row sums. `src/serving/export.py` enforces export-time native/ONNX probability parity with epsilon strictly below `1e-5`. Provider failures leave readiness false or fail to the explicit native mode; they never silently claim ONNX verification.

## Container controls

The final Docker image is multi-stage and executes as the non-root `appuser`. Compose adds `read_only: true`, `cap_drop: ALL`, `no-new-privileges`, `init`, bounded memory/CPU, and a no-execute/no-setuid `/tmp` tmpfs. Artifacts and configuration are read-only mounts. MLflow’s named volume is the only intended persistent writable path. The image excludes raw data, DVC cache, secrets, reports, notebooks, tests, and serialized model weights from the build context.

The runtime uses the practical slim Python base required by the pinned scientific/ML wheels. A distroless claim is intentionally not made because the full ONNX/NLP/MLflow dependency graph and healthcheck behavior must remain executable. GitHub Actions is the authoritative Docker build and Trivy scan environment.

## Tracking and data-versioning resilience

MLflow initialization retries with bounded exponential backoff and can fall back only to an explicitly configured local file store. The fallback is reported through `fallback_used`; tracking failures are never silently treated as successful logging. Artifact and metric logging failures are sanitized and logged without including article content. The lifecycle runner validates that the DVC cache path is a directory and writable, does not delete corrupted caches, and retries idempotent `dvc repro` execution a bounded number of times.

DVC remains the source of truth for governed ISOT/WELFake inputs. The hardening layer does not substitute synthetic data for missing raw inputs and does not invent benchmark metrics when a remote/cache is unavailable.

## Drift and retraining safety

`src/monitoring/drift.py` filters or rejects non-finite arrays according to the monitoring type, enforces minimum sample sizes, clips safe probabilities, handles equal and different constant distributions, includes out-of-range histogram values, uses positive finite bin probabilities, and rejects non-finite output. PSI and KS reports are JSON-safe. Retraining signals are side-effect free, carry a cooldown key, and always require human approval.

## Phase 7 zero-trust and extreme-scale serving controls

Phase 7 closes the remaining trust-boundary and resource-amplification gaps. When `REQUIRE_SIGNED_ARTIFACT=true`, `src/serving/export.py` verifies the native artifact SHA-256 against `PACKAGE_MANIFEST`, then verifies the manifest’s Ed25519 signature using `ARTIFACT_PUBLIC_KEY_B64` before any joblib deserialization. The canonical signed bytes exclude only the signature field and use deterministic JSON ordering. When signatures are intentionally disabled for a controlled development environment, the trusted SHA-256 path remains mandatory; production deployments should keep signed verification enabled.

BERT loading is air-gapped by contract. `validate_offline_bundle()` requires a local `config.json`, `vocab.txt`, and `model.safetensors` bundle, while `load_components()` sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` and passes `local_files_only=True`. The model identifier remains `bert-base-uncased`; no runtime path may resolve missing weights from the public Hub. A missing, malformed, or non-BERT bundle fails readiness rather than silently downloading or substituting weights.

Sparse TF-IDF is safe in native serving and is deliberately rejected by ONNX export and runtime adapters. This prevents accidental `.toarray()` conversion of high-dimensional sparse matrices. The unsupervised sparse path reduces through bounded TruncatedSVD, while DBSCAN is prohibited in `online=true` feature augmentation because its prediction semantics and memory profile are offline-oriented. Near-duplicate detection uses fixed-size streaming MinHash/LSH signatures, bounded bucket occupancy, and exact Jaccard confirmation only for LSH candidates; it does not materialize an all-pairs similarity matrix.

Multi-worker and multi-replica deployments use the Redis-backed atomic Lua fixed-window limiter through `DISTRIBUTED_RATE_LIMITER=redis` and `REDIS_URL`. The in-process limiter remains a single-instance fallback only. The API also enforces `MAX_INFLIGHT_INFERENCE` with an asynchronous semaphore and executes CPU-bound prediction in a threadpool; requests arriving after the budget is exhausted receive `429` rather than accumulating unbounded work.

Drift monitoring is a bounded asynchronous job queue. `POST /monitoring/drift` validates and enqueues a job, returns `202` with a `job_id`, and never performs potentially expensive statistics on the request thread. Operators poll `GET /monitoring/drift/{job_id}` for `queued`, `running`, `completed`, `failed`, or `expired` states. `DRIFT_QUEUE_MAXSIZE`, `DRIFT_WORKERS`, and `DRIFT_JOB_TTL_SECONDS` bound memory and lifecycle; the resulting retraining signal remains observational and requires human approval.

## CI/CD security gates

Every pull request and `main` push runs Ruff, strict mypy, compilation, configuration/source/DVC validation, Bandit SAST, pip-audit dependency scanning, the full pytest suite, local MLflow smoke operation, a rootless image-user assertion, and Trivy scanning for high/critical OS and library vulnerabilities. Bandit, the explicit High/Critical pip-audit severity gate, and Trivy are blocking gates. pip-audit JSON versions that omit severity are reported as unrated for manual triage rather than assigned an invented severity; the machine-readable report and gate output are uploaded on every run. Scan reports are uploaded as CI artifacts. The workflow has read-only repository permissions and does not require application secrets.

## Verification evidence

The hardening tests cover CORS allowlists, wildcard/credential rejection, rate-limit exhaustion and eviction, control-character and unknown-field rejection, massive batch rejection, finite drift behavior, invalid probability handling, ONNX configuration validation, MLflow fallback, Compose security fields, CI scan gates, async drift job polling, inference-budget exhaustion, signed manifest verification, sparse ONNX rejection, air-gapped BERT validation, Redis limiter behavior, streaming TF-IDF fitting, MinHash/LSH duplicate detection, and the existing prediction/ONNX/monitoring contracts.
 Local verification distinguishes tests that run in the sandbox from Docker and vulnerability scans that require the GitHub Actions runner.

## Incident and rollback response

A readiness failure is a deployment failure, not a reason to serve an unverified artifact. Operators should remove the unhealthy revision from traffic, preserve the sanitized diagnostics and CI scan reports, inspect model/package manifests and MLflow/DVC provenance, and roll back to the last parity-verified artifact. Drift signals recommend review and retraining but never retrain or replace a model automatically. Secrets must be rotated through the deployment platform rather than committed to `.env`, Compose, MLflow artifacts, or reports.

## Day 3 vulnerability closure

The asynchronous drift queue now treats saturation as a normal overload condition rather than a service failure. `DriftJobManager.submit()` checks the bounded queue without awaiting, reserves a job record only for an admitted slot, rolls back defensively on `asyncio.QueueFull`, and raises `OverflowError` when capacity is exhausted. The API maps that condition to HTTP 429 with `Retry-After: 5`; manager shutdown remains HTTP 503. This distinction gives callers a retryable back-pressure signal without masking process or lifecycle failure.

The runtime image installs `libjemalloc2` and sets `LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2` in the runtime stage. This is an allocator mitigation for high-frequency sparse-matrix workloads, not a substitute for bounded request sizes, sparse-safe model paths, process limits, or load testing. The image remains digest-pinned, multi-stage, rootless, read-only at runtime, and subject to CI container verification.

Redis is now authenticated and isolated. Compose requires `REDIS_PASSWORD`, starts Redis with `--requirepass`, passes an authenticated `REDIS_URL` to the API, and places Redis and the API on an `internal: true` `redis-internal` network. MLflow and synthetic traffic remain only on `fake-news-net`, while the API is the sole bridge between the application network and the Redis network. Deployment secrets must be injected through the runtime environment or secret manager; no real password belongs in Git.

Untrusted text processing in `src/features/text.py` uses the pinned `regex` package rather than direct stdlib `re` execution. Search, substitution, and find-all operations are capped at 50,000 characters and receive a 50-millisecond timeout. Timeout fallbacks are safe (`None`, an empty result, or the bounded input for substitution), and tokenization, HTML/URL/email removal, sentence counting, and syllable counting all use the bounded helpers. This reduces ReDoS exposure while preserving the existing normalization and feature-schema contracts.

The Day 3 controls are covered by queue saturation and HTTP 429 tests, bounded-regex fallback and input-bound tests, jemalloc/Dockerfile contract tests, Redis authentication/network topology tests, source-audit registration, and the complete repository quality gate.
