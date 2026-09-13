# ADR 0006: Full Relevant Developer-Pipeline Adoption

**Status:** Accepted on 2026-08-23.

## Context

The project owner supplied a broad engineering-pipeline catalogue and selected **full relevant adoption**. The catalogue spans universal development practice, full-stack web platforms, ML/data operations, agent tooling, and deployment infrastructure. This repository is a Python ML system with a FastAPI serving boundary, DVC, MLflow, ONNX, Kubernetes manifests, and a separate TypeScript dashboard. Treating every catalogue entry as a required runtime dependency would create speculative services, unnecessary attack surface, licensing risk, operational cost, and conflicts with the course and privacy controls.

## Decision

The repository will adopt every item that is applicable to its current capabilities, risks, or governance needs. Each other item receives an objective adoption trigger, so the decision is transparent and reversible rather than a silent omission. This ADR is implemented by the detailed matrix in [`docs/developer-pipeline-adoption.md`](../developer-pipeline-adoption.md).

The decision requires conventional commits, protected-main pull requests, source governance, immutable workflow/image references, complete dependency hash locks, least-privilege automation, synthetic-only fuzzing, privacy-preserving observability, and evidence-based security reporting. The repository will add secret detection, OWASP-aligned API/security documentation, safe API-contract coverage, bounded performance validation, and maintainable operational architecture documentation. Secret scanning detects potential credentials; it never substitutes for revocation, rotation, or a private incident response process.[SRC-054]

No unrelated service is added merely for catalogue completeness. In particular, Airflow, dbt, n8n, NATS, Kong, MinIO, search engines, a CMS, payment systems, desktop/mobile frameworks, and OpenTofu are deferred until the matrix's explicit operational trigger is met. The existing DVC/MLflow pipeline remains the appropriate deterministic ML lifecycle control. The existing dashboard remains isolated; the Python repository does not adopt its TypeScript-specific ORM, authentication, or component-stack defaults.

## Consequences

The project gains a measurable adoption standard without inventing infrastructure or presenting future possibilities as completed capability. Contributors must update the matrix whenever a new platform is adopted, a trigger is met, or a source changes. Every external URL that supports an adoption claim appears in both source registers. The existing no-suppression policy applies equally to secret scanning, CodeQL, pip-audit, fuzzing, and Scorecard.

## References

[SRC-054], [SRC-055], and [SRC-056] are registered in [`docs/sources.md`](../sources.md) and [`docs/sources.yaml`](../sources.yaml).
