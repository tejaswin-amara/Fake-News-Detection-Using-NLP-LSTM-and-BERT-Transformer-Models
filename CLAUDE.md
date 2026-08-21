# AI Agent Operating Guide

## Repository mission and scope

This repository implements a reproducible fake-news **text-classification** system. It models patterns associated with governed labels; it does not browse the web, independently verify claims, or make editorial, legal, medical, financial, or public-safety decisions. Preserve that distinction in code, issues, commits, documentation, examples, and user-facing language.

## Required discovery before editing

Read the affected implementation, its tests, related configuration, and relevant documentation before modifying behavior. Inspect `README.md`, `ARCHITECTURE.md`, `docs/compliance_matrix.md`, `docs/security_hardening.md`, and the corresponding source-register entries when the change affects public contracts. Make focused changes; do not reformat or redesign unrelated files.

## Python, quality, and dependency policy

Target Python 3.11 and retain the existing pinned dependency model. Do not add an unpinned library, a broad static-analysis suppression, an untyped escape hatch, or a weaker test/coverage threshold to make a change pass. Prefer the implemented FastAPI, scikit-learn, PyTorch, Transformers, DVC, MLflow, ONNX, Prometheus, and Kubernetes boundaries over introducing duplicate frameworks.

Run the applicable verification commands before delivery:

```bash
ruff check src scripts tests
mypy src scripts tests
python scripts/source_audit.py --root .
dvc stage list
python -m pytest -q --cov=src --cov-fail-under=95
git diff --check
```

When deployment files change, preserve kubeconform validation, the rootless image contract, and the critical-CVE gate. Report environmental limitations honestly; never claim that a check passed when it did not.

## Data, model, privacy, and security rules

Preserve split-before-fit discipline. Fit vocabulary, imputation, encoding, scaling, reduction, clustering, anomaly detection, calibration, thresholds, and models only on their permitted training data. The validation and test partitions are never input to fitting or model-selection decisions. Do not fabricate datasets, records, metrics, benchmarks, model artifacts, test outcomes, or user feedback.

Never commit or log credentials, API keys, tokens, DVC remote details, raw article text, private dataset content, model weights, generated artifacts, MLflow stores, signing keys, or production URLs containing credentials. Keep runtime artifacts in governed external storage and ensure sanitized errors remain sanitized. Security vulnerabilities use the private GitHub reporting process in `SECURITY.md`, not public issues.

## Documentation and source governance

Every new external URL, dataset, paper, documentation page, dependency, action, copied algorithmic pattern, or discoverability destination must be registered in **both** `docs/sources.md` and `docs/sources.yaml` before it appears elsewhere in tracked text. Keep the README reference section intact and never invent an author, contact channel, capability, score, deployment, or compliance result.

## Automation and external side effects

Do not modify repository settings, branch protection, DVC remotes, release tokens, GitHub secrets, public topics, social-preview media, releases, tags, deployment environments, or third-party pages without explicit user authorization. Workflows that can create tags, releases, labels, or external requests must be safe by default and explain their activation preconditions.

## Change handoff

Update `todo.md` before implementation, mark completed work immediately when its implementation is complete, and read the full checklist before commit. Use focused, conventional commit messages. Deliver a concise summary of changed files, validations, known constraints, and any owner action that remains necessary.
