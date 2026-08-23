# Developer-Pipeline Adoption Matrix

This matrix operationalizes the owner-approved **full relevant adoption** decision in [ADR 0006](ADR/0006-full-relevant-developer-pipeline-adoption.md). “Deferred” is an explicit architecture choice with a measurable trigger, not a missing task. The matrix complements the 25SC2107E compliance matrix and does not change the project's privacy, source-governance, or protected-main requirements.

## Universal and repository-governance defaults

| Catalogue capability | Status | Repository implementation or objective trigger |
|---|---|---|
| Git workflow and conventional commits | Adopted | Focused protected-main branches, conventional `type: summary` commits, atomic reviews, and release automation constraints are documented in `CONTRIBUTING.md`, `CLAUDE.md`, `.cursorrules`, and Copilot instructions. |
| Contributor governance and independent review | Adopted with human gate | Contribution evidence, `CODEOWNERS`, issue/PR forms, and a review checklist are in-repository. An independent approval remains an owner/team action and is never synthesized by automation. |
| Security review and secret detection | Adopted | OWASP-aligned API/privacy controls, CodeQL, Bandit, pip-audit, Scorecard, and the immutable secret-scan workflow together provide layered controls. A secret finding requires private rotation and investigation; it is not an item to suppress.[SRC-054] [SRC-055] |
| Source governance | Adopted | Every implementation or claim URL must be synchronized in `docs/sources.md` and `docs/sources.yaml`, then verified by `scripts/source_audit.py --root .`. |
| AI-agent governance | Adopted | Repository-local agent instructions require source registration, privacy preservation, test-first changes, safe dependency handling, and no unreviewed external-tool installation. |
| Project-management platform | Deferred | Adopt Plane or a comparable tool only when more than one active contributor needs issue/sprint/roadmap management beyond GitHub Issues and Projects. |
| Integration automation platform | Deferred | Adopt n8n only for a declared external workflow that cannot be safely expressed in the existing deterministic code/CI architecture; first assess persistence, credentials, licensing, webhooks, privacy, and ownership. |

## Python ML, FastAPI, and MLOps defaults

| Catalogue capability | Status | Repository implementation or objective trigger |
|---|---|---|
| Reproducible ML lifecycle | Adopted | DVC controls data-stage reproducibility; MLflow records runs/artifacts via SQLite metadata and file artifacts; split-before-fit and held-out test constraints remain mandatory. |
| FastAPI contract and documentation | Adopted | FastAPI's OpenAPI schema is treated as an executable API contract. Documentation, examples, tests, and errors remain metadata-only and never expose credentials or retained article text. |
| API security and privacy | Adopted | Bounded request validation, strict Pydantic models, allowed CORS origins, rate limiting, circuit-breaker behavior, warm-up/readiness, safe errors, structured logs, and Prometheus metrics are reviewed against OWASP API, REST, and logging guidance.[SRC-055] |
| End-to-end and contract testing | Adopted | API contract and privacy-negative tests join the existing unit, ONNX, DVC, MLflow, fuzzing, and container validation suites. |
| Performance/load testing | Adopted with safety boundary | A small k6 smoke profile uses a controlled target, synthetic metadata-only requests, fixed iteration budgets, and pass/fail thresholds. Longer or production load profiles require explicit target, rate, consent, and capacity review.[SRC-056] |
| Metrics and operational observability | Adopted | Prometheus latency, inference, drift-queue, rejection, and error metrics are retained. Labels and logs must never carry article text, credentials, raw request payloads, or high-cardinality personal identifiers. |
| Airflow or another DAG scheduler | Deferred | Adopt only when recurring multi-stage data workflows need scheduling, retries, observability, and ownership beyond the reproducible DVC graph and GitHub's existing scheduled maintenance/fuzz jobs. |
| dbt | Deferred | Adopt only when a governed SQL warehouse transformation layer exists; it is not a substitute for DVC-managed ML data preparation. |
| Redis queue/cache expansion | Conditional | Redis remains limited to the rate-limit/circuit-breaker contract unless a bounded, monitored workload demonstrates that an additional cache or durable queue is needed. |
| Object-store platform | Deferred | Adopt MinIO or another S3-compatible store only when approved artifact or user-file retention requires it; do not store raw article text, raw datasets, secrets, or unbounded logs. |

## Deployment, scale, and product-platform defaults

| Catalogue capability | Status | Repository implementation or objective trigger |
|---|---|---|
| Container and Kubernetes controls | Adopted | Rootless image builds, critical-vulnerability enforcement, kubeconform, resource limits, probes, HPA, network policy, Ingress, and ServiceMonitor manifests are version-controlled and validated. |
| API gateway | Deferred | Adopt Kong only when multiple independently deployed services need centralized policy, authentication, routing, or externally managed rate limits beyond the application and ingress controls. |
| Event streaming | Deferred | Adopt NATS only when independently produced/consumed events require durable, asynchronous messaging beyond the bounded in-process drift queue. |
| Search, real-time transport, CMS, payments | Deferred | Adopt only after a user-facing product requirement exists and a privacy, license, threat-model, and operational owner is approved. |
| Infrastructure as code | Deferred | Prefer OpenTofu if an owner approves a supported cloud target, state backend, account boundary, and reviewed deployment plan. Do not create unverified cloud resources or placeholder stacks. |
| Privacy analytics | Deferred | Consider an aggregate, consent-aware analytics system only for an approved deployed UI. Payloads must exclude raw article text, API keys, and direct identifiers. |
| TypeScript dashboard defaults | Boundary recorded | React UI libraries, TypeScript auth/ORM, i18n, Storybook, and motion tooling apply only when a dashboard change calls for them. They are not added to this Python ML repository by default. |

## Change-control rule

When a deferred trigger is met, the contributor must document the objective **adoption trigger**, add a source-governed ADR, update this matrix, document privacy/licensing/operational ownership, and submit a focused protected-main pull request with tests. No status may move from “deferred” to “adopted” based on a proposal alone.

## References

The governing external sources are registered as [SRC-054], [SRC-055], and [SRC-056] in [`docs/sources.md`](sources.md) and [`docs/sources.yaml`](sources.yaml).
