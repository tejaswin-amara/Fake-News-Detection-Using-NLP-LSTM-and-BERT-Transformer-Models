# Contributing

Thank you for contributing to this repository. Contributions are evaluated for **reproducibility, source traceability, leakage prevention, security, and maintainability** alongside feature completeness. The project is a fake-news classification system; changes must not describe it as an autonomous web-search or fact-verification service.

## Contribution workflow

Fork the repository, create a focused branch from `main`, make an atomic change, and open a pull request against `main`. Use a conventional `type: summary` commit subject, such as `fix: align runtime tokenizers with transformers`; do not combine unrelated feature, refactor, dependency, or documentation changes in one commit. Pull requests must state the affected subsystem, the verification commands run, the data or model boundary affected, the operational or security consequence, and the rollback path.

| Change category | Pull-request evidence |
|---|---|
| Source code or configuration | Focused tests, Ruff, mypy, and a concise explanation of changed behavior |
| Data pipeline or dataset documentation | Split/leakage rationale, provenance metadata, license boundary, and updates to both source registers |
| Model or evaluation behavior | Training-versus-serving contract, untouched-test-set policy, and explicit statement that no metric is fabricated |
| Serving, container, or Kubernetes assets | API/health behavior, security context implications, and relevant manifest or container validation |
| Documentation | Accurate file references, no unsupported claims, and source-register coverage for each new external URL |
| Security, secrets, or dependency locks | No new suppression/allowlist/baseline, secret-rotation impact, immutable reference review, and hash-lock/resolver evidence |
| New platform or operational service | An ADR, a row in `docs/developer-pipeline-adoption.md`, privacy/license/owner analysis, and a demonstrated adoption trigger |

## Local quality gate

On Linux/Python 3.11, install the reviewed complete lock used by continuous integration, then run the same principal checks enforced by continuous integration. Other platforms must regenerate and review an appropriate complete lock rather than bypassing hash checks.

```bash
python -m pip install --require-hashes -r requirements/locks/development-py311-manylinux_2_28.txt
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

Maintainers review changes against the governing course handout, the relevant model or deployment contract, test quality, and the project’s security posture. Reviewers must check that the change is focused, that validation evidence supports the stated behavior, that security/privacy effects and rollback are credible, and that a deferred platform has not been introduced speculatively. A contribution may be revised, deferred, or declined when it cannot demonstrate a safe and reproducible boundary.

Repository automation cannot stand in for an independent reviewer. When branch protection requires an approval, a trusted person other than the author must supply it; do not fabricate review evidence, self-approve to improve a metric, or treat a bot comment as an independent human approval.

## Security reporting and secret handling

Never commit a real credential to demonstrate a test or workflow. Do not add `gitleaks:allow`, a broad `.gitleaksignore`, a secret-scanning baseline, or a workflow exception to make a finding disappear. If a credential is suspected to be exposed, stop further disclosure, revoke/rotate it through the owning provider, preserve only redacted evidence, and use the private route in [`SECURITY.md`](SECURITY.md). See [`docs/security/secret-handling.md`](docs/security/secret-handling.md) when that runbook is introduced.

## Platform adoption boundary

The repository deliberately uses the smallest appropriate operational surface. Before proposing a queue, scheduler, gateway, object store, telemetry service, cloud resource, CMS, search system, or product platform, read [`docs/developer-pipeline-adoption.md`](docs/developer-pipeline-adoption.md) and add the required ADR/evidence. A catalogue recommendation alone is not an adoption trigger.

## References

The project’s governing syllabus traceability is recorded in [`docs/compliance_matrix.md`](docs/compliance_matrix.md) [SRC-003]. Operational and source-governance requirements are recorded in [`docs/security_hardening.md`](docs/security_hardening.md) and [`docs/sources.md`](docs/sources.md).
