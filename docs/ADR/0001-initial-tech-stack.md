# ADR 0001: Initial technology stack

- **Status:** Accepted
- **Date:** 2026-08-21
- **Decision owners:** Repository maintainers

## Context

The project requires an end-to-end, reproducible ML workflow that spans governed text data, leakage-safe features, classical and neural NLP paths, evaluation, local serving, monitoring, and deployment validation. The course handout requires evidence across CO1–CO6 and Modules M1–M6 [SRC-003]. The stack must support local development while preserving explicit boundaries for optional resources, raw data, artifacts, and production infrastructure.

## Decision

The repository adopts the following baseline.

| Concern | Decision | Rationale |
|---|---|---|
| Runtime | Python 3.11 with pinned requirements | Matches project metadata and supports the chosen ML and serving libraries |
| Data pipeline | DVC stages with versioned configuration and external raw-data boundary | Makes collection, ingestion, training, and evaluation graph-visible without committing governed raw data |
| Experiment tracking | Optional local MLflow | Enables local tracking and artifact logging without requiring a hosted service |
| Feature and baseline models | scikit-learn with TF-IDF and classical models | Supplies reproducible, inspectable baselines and leakage-safe pipeline primitives |
| Neural NLP paths | PyTorch plus Transformers for optional BiLSTM and BERT workflows | Supports the repository’s declared LSTM and BERT implementations while retaining optional-resource boundaries |
| Serving | FastAPI with Pydantic request validation | Provides typed HTTP interfaces, health/readiness routes, and deployable API composition |
| Portable inference | Native package plus optional ONNX Runtime export | Keeps sparse native inference authoritative while allowing dense-compatible parity-checked export |
| Observability | structlog and Prometheus client | Provides structured request correlation and metrics exposition for operations |
| Local/container deployment | Rootless multi-stage Docker image and Docker Compose | Separates production serving dependencies from training dependencies and supports local service integration |
| Cluster deployment | Kubernetes base manifests | Captures workload probes, HPA, network isolation, ingress, and monitoring declarations |
| Assurance | GitHub Actions with source audit, static checks, tests, coverage, and container scan | Treats reproducibility, quality, and critical-vulnerability checks as merge gates |

## Consequences

This decision creates explicit integration and maintenance responsibilities. Dependencies must remain pinned and compatible in both `requirements.txt` and the smaller `requirements-runtime.txt`. Raw datasets, third-party weights, credentials, and generated artifacts remain outside Git unless a lawful, reviewed change says otherwise. Operators must provide production-specific DVC storage, artifact location, secret management, TLS, ingress controller, Prometheus Operator CRD, and access controls.

The system deliberately retains a native artifact path because sparse TF-IDF inference may not be safe or useful to force into a dense ONNX representation. BERT, external data, and model weights remain optional when dependencies or lawful resources are unavailable. CI verifies implementation contracts but cannot establish real-world factual truth or substitute for an operational security review.

## Alternatives considered

| Alternative | Reason not selected as the baseline |
|---|---|
| Notebook-only workflow | Does not provide a reliable serving, artifact, or CI boundary |
| Hosted-only MLflow and data storage | Would require infrastructure credentials and violate the local-first, reproducible project baseline |
| Single framework for every model | Would obscure classical baseline behavior and make course-aligned comparison less direct |
| ONNX-only serving | Is unsuitable as a universal boundary for sparse high-dimensional feature paths |
| Docker Compose as the production orchestration target | Does not provide the scaling, policy, ingress, or cluster observability declarations captured in `k8s/base/` |

## References

The source register records the technologies and sources underlying this decision: DVC [SRC-036], MLflow [SRC-033], FastAPI [SRC-030], ONNX [SRC-031], Docker [SRC-032], Kubernetes [SRC-040]–[SRC-044], structlog [SRC-042], and the governing course handout [SRC-003].
