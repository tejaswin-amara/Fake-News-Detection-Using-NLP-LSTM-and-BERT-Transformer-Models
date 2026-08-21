## Summary

Describe the focused change and its user, reproducibility, or operational value.

## Linked issues

Closes #

## Contracts and provenance

- [ ] This change preserves split-before-fit discipline and does not use validation or test data for model decisions.
- [ ] This change does not commit raw datasets, article text, credentials, model weights, private artifacts, or MLflow/DVC stores.
- [ ] I updated `docs/sources.md` and `docs/sources.yaml` for every added external source or URL, or no new source was introduced.
- [ ] I did not add fabricated metrics, benchmark results, reviews, support contacts, or truth-verification claims.

## Validation

List the exact commands and outcomes.

- [ ] `ruff check src scripts tests`
- [ ] `mypy src scripts tests`
- [ ] `python scripts/source_audit.py --root .`
- [ ] `python -m pytest -q --cov=src --cov-fail-under=95`
- [ ] DVC, Kubernetes, Docker, API, or artifact validation where relevant

## Risk, rollback, and documentation

Describe compatibility impact, failure modes, rollback approach, and documentation updates.

## Accessibility and usability

- [ ] I reviewed keyboard, readable-language, and error-state impact for any user-facing API/dashboard/documentation change.
- [ ] Not applicable: this change has no user-facing interface or interaction impact.

## Checklist

- [ ] My change is focused, tested, and ready for review.
- [ ] I have read and followed `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md`.
