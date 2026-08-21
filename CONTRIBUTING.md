# Contributing

Thank you for contributing to this repository. Contributions are evaluated for **reproducibility, source traceability, leakage prevention, security, and maintainability** alongside feature completeness. The project is a fake-news classification system; changes must not describe it as an autonomous web-search or fact-verification service.

## Contribution workflow

Fork the repository, create a focused branch from `main`, make an atomic change, and open a pull request against `main`. Use a concise imperative commit subject; the existing `type: summary` convention, such as `fix: align runtime tokenizers with transformers`, is preferred. Pull requests should state the affected subsystem, the verification commands run, the data or model boundary affected, and any operational or security consequence.

| Change category | Pull-request evidence |
|---|---|
| Source code or configuration | Focused tests, Ruff, mypy, and a concise explanation of changed behavior |
| Data pipeline or dataset documentation | Split/leakage rationale, provenance metadata, license boundary, and updates to both source registers |
| Model or evaluation behavior | Training-versus-serving contract, untouched-test-set policy, and explicit statement that no metric is fabricated |
| Serving, container, or Kubernetes assets | API/health behavior, security context implications, and relevant manifest or container validation |
| Documentation | Accurate file references, no unsupported claims, and source-register coverage for each new external URL |

## Local quality gate

Install the pinned development environment, then run the same principal checks enforced by continuous integration.

```bash
python -m pip install -r requirements.txt
ruff check src scripts tests
mypy src scripts tests
python scripts/source_audit.py --root .
git diff --check
python -m pytest -q --cov=src --cov-report=term-missing --cov-fail-under=95
```

Changes to Kubernetes manifests must also remain valid under the repository’s pinned `kubeconform` CI configuration. Changes to the runtime image must preserve the non-root `appuser` contract and pass the critical-vulnerability container gate.

## Data, privacy, and reproducibility boundaries

Do not commit raw datasets, pretrained weights, access credentials, production artifacts, MLflow stores, or `.env` files. Preserve the canonical schema and create a split before fitting text transforms, imputers, encoders, scalers, reducers, clusterers, calibration maps, thresholds, or learned models. The test partition remains unavailable for modelling decisions.

Every external dataset, paper, documentation page, copied algorithmic pattern, or new URL must be registered in both [`docs/sources.md`](docs/sources.md) and [`docs/sources.yaml`](docs/sources.yaml) before it appears elsewhere in tracked text. The repository’s source audit checks this contract.

## Review and acceptance

Maintainers review changes against the governing course handout, the relevant model or deployment contract, test quality, and the project’s security posture. A contribution may be revised, deferred, or declined when it cannot demonstrate a safe and reproducible boundary.

## References

The project’s governing syllabus traceability is recorded in [`docs/compliance_matrix.md`](docs/compliance_matrix.md) [SRC-003]. Operational and source-governance requirements are recorded in [`docs/security_hardening.md`](docs/security_hardening.md) and [`docs/sources.md`](docs/sources.md).
