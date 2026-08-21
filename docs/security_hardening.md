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

## CI/CD security gates

Every pull request and `main` push runs Ruff, strict mypy, compilation, configuration/source/DVC validation, Bandit SAST, pip-audit dependency scanning, the full pytest suite, local MLflow smoke operation, a rootless image-user assertion, and Trivy scanning for high/critical OS and library vulnerabilities. Bandit and Trivy are blocking gates. The pinned legacy ML/NLP matrix currently resolves upstream advisories reported by pip-audit, so pip-audit is an evidence-producing non-blocking gate until the compatibility-preserving dependency refresh is completed; its machine-readable report is uploaded on every run. Scan reports are uploaded as CI artifacts. The workflow has read-only repository permissions and does not require application secrets.

## Verification evidence

The hardening tests cover CORS allowlists, wildcard/credential rejection, rate-limit exhaustion and eviction, control-character and unknown-field rejection, massive batch rejection, finite drift behavior, invalid probability handling, ONNX configuration validation, MLflow fallback, Compose security fields, CI scan gates, and the existing prediction/ONNX/monitoring contracts. Local verification distinguishes tests that run in the sandbox from Docker and vulnerability scans that require the GitHub Actions runner.

## Incident and rollback response

A readiness failure is a deployment failure, not a reason to serve an unverified artifact. Operators should remove the unhealthy revision from traffic, preserve the sanitized diagnostics and CI scan reports, inspect model/package manifests and MLflow/DVC provenance, and roll back to the last parity-verified artifact. Drift signals recommend review and retraining but never retrain or replace a model automatically. Secrets must be rotated through the deployment platform rather than committed to `.env`, Compose, MLflow artifacts, or reports.
