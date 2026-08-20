# Dependency and License Inventory

This inventory complements `requirements.txt` and `docs/sources.md`. Exact installed versions are controlled by the pinned requirements file; package license metadata should be rechecked when dependencies are upgraded.

| Dependency group | Packages | Primary license/source note |
|---|---|---|
| Numerical/data | NumPy, pandas, SciPy, joblib, PyYAML | BSD-family or MIT-style licenses; see each package metadata and SRC-015, SRC-029, SRC-034 |
| Classical ML | scikit-learn | BSD-3-Clause; SRC-015 |
| Boosting | XGBoost, LightGBM | Apache-2.0 and MIT respectively; SRC-022 |
| Explainability | SHAP | Package license and SRC-023 |
| NLP | NLTK, spaCy, Gensim, sentence-transformers | Package-specific licenses; SRC-014 and SRC-035 |
| Deep learning | PyTorch, TensorFlow CPU, Transformers, Datasets, Accelerate | Framework/model licenses and model-card terms; SRC-012, SRC-013 |
| Visualization | Matplotlib, seaborn, Plotly, UMAP, scikit-image, NetworkX | Package-specific permissive licenses; SRC-015 and SRC-019 |
| Serving | FastAPI, Uvicorn, Pydantic, HTTPX | MIT or package-specific permissive licenses; SRC-030 |
| Export | ONNX, ONNX Runtime, ONNX Script, skl2onnx | Package-specific permissive licenses; SRC-031 and SRC-035 |
| Tracking/search | MLflow, Optuna, statsmodels, psutil | Package-specific licenses; SRC-025, SRC-029, SRC-033 |
| Data versioning | DVC | Open-source package; record selected version and license; SRC-036 |
| Quality/operations | pytest, pytest-cov, Ruff, mypy, pre-commit | Package-specific permissive licenses; SRC-034 |

## Redistribution rules

The repository does not redistribute raw datasets or pretrained model weights by default. Dataset/model URLs, checksums, revisions, and license/usage terms are recorded in `docs/sources.md` and generated artifact metadata. Any future release that bundles weights or raw data must perform a separate license review and update this inventory.
