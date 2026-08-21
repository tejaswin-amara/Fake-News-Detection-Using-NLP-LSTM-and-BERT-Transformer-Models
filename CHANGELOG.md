# Changelog

All notable repository changes are documented in this file. The format follows the intent of **Keep a Changelog** and uses Semantic Versioning terminology where a tagged release exists. This project currently declares package version `0.1.0` in [`pyproject.toml`](pyproject.toml); entries below describe implemented repository state and do not imply fabricated benchmark outcomes.

## [Unreleased]

### Added

- Repository metadata and community documentation: MIT license, citation metadata, funding configuration, contribution guidance, Code of Conduct, security policy, support guide, governance model, roadmap, architecture reference, and the first architecture decision record.
- Current ClaimReview dataset collection stage with provenance, language/rating gates, chronological partitions, and regression tests.

### Changed

- Runtime container dependencies are maintained separately from the full development/training environment and the `tokenizers` pin is compatible with the runtime Transformers pin.
- The root README now provides a quick-start path, stack summary, source-governance links, and an architecture entry point while preserving its complete reference bibliography.

### Security

- CI validates source governance, DVC stages, Kubernetes manifests, static quality checks, a 95% source-coverage gate, non-root image identity, and a critical-CVE image gate.

## [0.1.0] - 2026-08-21

### Added

- Leakage-safe ingestion, feature engineering, classical and optional neural model paths, evaluation/calibration utilities, DVC, MLflow integration, report generation, FastAPI serving, monitoring, Docker Compose, Kubernetes manifests, and GitHub Actions validation.
- Structured request logging, Redis circuit-breaking rate limiting, readiness warm-up, Prometheus metrics, bounded drift processing, and artifact integrity verification boundaries.

## References

The implementation evidence for these entries is mapped in [`docs/compliance_matrix.md`](docs/compliance_matrix.md), [`docs/current_dataset_release.md`](docs/current_dataset_release.md), and [`docs/security_hardening.md`](docs/security_hardening.md) [SRC-003].
