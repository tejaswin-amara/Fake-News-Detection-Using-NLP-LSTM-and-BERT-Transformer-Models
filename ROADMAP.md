# Roadmap

## Planning principles

This roadmap distinguishes **implemented repository evidence** from future proposals. It is not a promise of release dates, benchmark improvements, data availability, hosted service operation, or automated truth verification. Each future item requires source governance, reproducibility review, security review, and tests before acceptance.

## Implemented foundation

| Milestone | Status | Evidence |
|---|---|---|
| Reproducible project scaffold and configurations | Completed | `configs/`, `src/`, `tests/`, `pyproject.toml`, `requirements.txt` |
| Leakage-safe ingestion and split contract | Completed | `src/data/ingestion.py`, `src/data/claimreview.py`, DVC pipeline, ingestion tests |
| Text features, classical models, neural model paths, and unsupervised utilities | Completed | `src/features/`, `src/models/`, notebooks, and unit tests |
| Evaluation, calibration, artifacts, and report lifecycle | Completed | `src/evaluation/`, `src/evaluate.py`, `scripts/generate_reports.py` |
| Serving, drift monitoring, observability, and resilience controls | Completed | `src/serving/`, `src/monitoring/`, serving/SRE tests |
| Container, Kubernetes, and CI quality gates | Completed | `Dockerfile`, `docker-compose.yml`, `k8s/base/`, `.github/workflows/ci.yml` |
| Repository documentation and governance tranche one | Completed | Root metadata, community policies, architecture document, and ADR 0001 |

## Proposed next milestones

| Milestone | Definition of ready | Status |
|---|---|---|
| Governed full-dataset benchmark | Licenses, immutable dataset manifests, executable DVC remote, reviewed resource budget, and non-fabricated held-out reports | Proposed |
| Model and data release provenance | Versioned release procedure, artifact checksums/signatures, retention policy, and documented release review | Proposed |
| Deployment runbooks | Environment-specific TLS, ingress, remote storage, alerting, backup, and rollback procedures tested by an operator | Proposed |
| Fairness and error-analysis expansion | A lawful, documented evaluation design with appropriate data and explicit limitations; no demographic claims without evidence | Proposed |
| Documentation tranches four through seven | Explicit user approval, scope review, source registration, and validation plan | Awaiting approval |

## References

The completed scope is traceable to [`docs/compliance_matrix.md`](docs/compliance_matrix.md) [SRC-003]. Data and operational constraints are documented in [`docs/dataset_card.md`](docs/dataset_card.md), [`docs/current_dataset_release.md`](docs/current_dataset_release.md), and [`docs/security_hardening.md`](docs/security_hardening.md).
