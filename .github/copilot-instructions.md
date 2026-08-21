# GitHub Copilot Instructions

Treat this project as a **Python 3.11, DVC, MLflow, FastAPI, ONNX, Docker, and Kubernetes** ML system with strict reproducibility and privacy boundaries. Read adjacent code, tests, configuration, and the source register before suggesting edits. Follow existing naming, typing, logging, validation, and error-handling patterns.

The system is a pattern classifier trained on governed labels. Do not describe it as a search engine, a fact-checking authority, or a basis for high-impact decisions. Do not invent data, metrics, model outcomes, user feedback, operational status, contacts, or external references.

Maintain strict **split-before-fit** behavior: keep all learned transforms train-only. The final test set must not influence vocabulary, preprocessing, calibration, thresholds, hyperparameter selection, model fitting, or drift references. Preserve Pydantic validation, bounded request/queue behavior, artifact verification, structured request-ID logs, and safe error handling.

Never emit, log, or commit raw article text, secrets, credentials, private URLs, model weights, artifacts, MLflow/DVC state, or signing material. Use `SECURITY.md` for private vulnerability-reporting guidance.

Maintain pinned dependencies and existing CI gates. Validate relevant changes with Ruff, mypy, the source audit, DVC, Kubernetes, coverage-gated pytest, and `git diff --check`. Every external URL, dependency, GitHub Action, source, or implementation pattern must be recorded in both source registers before it appears in repository text.

Do not modify repository settings, secrets, topics, social-preview images, tags, releases, remote storage, deployments, or external sites unless the repository owner explicitly asks for that action.
