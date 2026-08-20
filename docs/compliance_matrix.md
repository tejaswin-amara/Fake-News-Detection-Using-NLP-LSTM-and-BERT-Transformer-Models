# CO/M Module Compliance Matrix

This matrix is the project’s evidence index for the `25SC2107E` Machine Learning handout. It will be updated whenever a script, notebook, test, report, or deployment artifact is added or renamed.

| Course outcome / module | Required topics from handout | Code and configuration evidence | Notebook/report evidence | Test/evidence artifact | Sources |
|---|---|---|---|---|---|
| CO1 / M1 | Lifecycle from raw data through features, training, evaluation, deployment, monitoring, and retraining; trace one prediction request; supervised versus unsupervised boundary; training-serving boundary | `src/data/ingestion.py`, `src/features/`, `src/models/`, `src/evaluation/`, `src/serving/app.py`, `src/monitoring/`, `configs/default.yaml` | `notebooks/01_eda.ipynb`, lifecycle diagram, request-trace section in README | Data-to-API smoke test; artifact round trip; `/health`, `/predict`, `/predict/batch` tests | SRC-003, SRC-004, SRC-008, SRC-009, SRC-010 |
| CO2 / M2 | Linear regression context, ridge/lasso/ElasticNet regularization, logistic regression, binary/multinomial sigmoid/softmax, feature scaling, categorical/missing-value handling, coefficient interpretation | `src/models/classical.py`, `src/features/text.py`, `src/features/preprocessing.py`, `configs/models.yaml` | Regularization, text-statistics, imputation, encoding, scaling, and coefficient reports | Linear/logistic fitting, imputation, encoding, scaling, and leakage tests | SRC-004, SRC-005, SRC-006, SRC-021 |
| CO3 / M3 | Decision trees, Gini/entropy, stopping/pruning, Random Forest, OOB error, boosting, XGBoost, LightGBM, feature importance and SHAP | `src/models/classical.py`, `configs/models.yaml` | Classical model comparison and explainability report | Tree/ensemble smoke tests; importance output checks | SRC-005, SRC-006, SRC-022, SRC-023 |
| CO4 / M4 | K-Means/K-Means++, Mini-Batch K-Means, elbow/silhouette, hierarchical clustering/dendrogram, DBSCAN, PCA, t-SNE, UMAP, Isolation Forest, cluster labels as downstream features | `src/models/unsupervised.py`, `src/features/unsupervised_features.py`, `configs/default.yaml` | `notebooks/02_unsupervised_analysis.ipynb` with elbow, silhouette, dendrogram, scree, t-SNE, UMAP, and feature-synthesis figures | Shape, determinism, linkage, tuning, projection dimensions, and no-test-fit tests | SRC-005, SRC-006, SRC-016–SRC-020 |
| CO5 / M5 | 3-way split, stratified k-fold, nested CV, classification/regression metrics, calibration, learning/validation curves, grid/random/Bayesian search, McNemar, paired bootstrap | `src/evaluation/metrics.py`, `src/evaluation/search.py`, `src/evaluation/plots.py`, `src/train.py`, `src/evaluate.py`, `configs/evaluation.yaml` | `notebooks/03_model_evaluation.ipynb`, benchmark, search, calibration, and statistical reports | Metric correctness, nested-CV separation, calibration, McNemar, paired bootstrap, search, plot, and CLI tests | SRC-005, SRC-006, SRC-024–SRC-029 |
| CO6 / M6 | Feature-store concept, skew avoidance, artifact packaging, ONNX, REST serving, batch/online inference, drift/performance monitoring, MLflow/DVC concepts | `src/serving/app.py`, `src/monitoring/drift.py`, `src/serving/export.py`, `src/tracking.py`, `scripts/init_mlflow.py`, `.dvc/`, `dvc.yaml`, `Dockerfile`, `.github/workflows/ci.yml` | Deployment, DVC, MLflow, and monitoring documentation; architecture diagram | API, export conformance, KS/PSI, drift endpoint, DVC pipeline, MLflow initialization, Docker, and CI smoke tests | SRC-008–SRC-010, SRC-030–SRC-036 |

## Script-to-outcome index

| Planned script | Primary outcome/module | Required evidence |
|---|---|---|
| `src/data/ingestion.py` | CO1/M1 | Dataset adapters, validation, split manifest, provenance metadata |
| `src/features/text.py` | CO1/M1, CO2/M2 | Cleaning, token processing, text statistics, readability, and TF-IDF fit/transform contracts |
| `src/features/embeddings.py` | CO1/M1, CO4/M4 | GloVe, Word2Vec, transformer tokenization, SBERT preparation, and model provenance |
| `src/features/preprocessing.py` | CO2/M2 | Imputation, MissingIndicator, One-Hot/Ordinal/target encoding, and scaling contracts |
| `src/features/unsupervised_features.py` | CO4/M4 | K-Means/Mini-Batch/DBSCAN/anomaly augmentation without test leakage |
| `src/models/unsupervised.py` | CO4/M4 | All required clustering, reduction, and anomaly methods |
| `src/models/classical.py` | CO2/M2, CO3/M3 | Ridge/Lasso/ElasticNet, binary/multinomial Logistic, tree, forest, XGBoost, LightGBM, permutation and SHAP reports |
| `src/models/lstm.py` | CO1/M1, CO5/M5 | GloVe BiLSTM training/inference and smoke configuration |
| `src/models/bert.py` | CO1/M1, CO5/M5 | BERT fine-tuning, dynamic padding, warmup, clipping, FP16 |
| `src/evaluation/metrics.py` | CO5/M5 | Classification/regression metrics, nested CV, calibration, McNemar, paired bootstrap, and report schemas |
| `src/evaluation/plots.py` | CO5/M5 | Confusion, ROC/PR, learning, validation, reliability, and calibration comparison curves |
| `src/evaluation/search.py` | CO5/M5 | Grid, random, Bayesian, nested-search result, and serialization helpers |
| `src/train.py`, `src/evaluate.py` | CO1/M1, CO5/M5, CO6/M6 | Search/training orchestration, held-out evaluation, calibration, report generation, and MLflow artifact logging |
| `src/serving/app.py` | CO1/M1, CO6/M6 | FastAPI health and prediction endpoints |
| `src/serving/predictor.py` | CO1/M1, CO6/M6 | Bound preprocessing-plus-model inference contract |
| `src/serving/export.py` | CO6/M6 | Native, ONNX, and TorchScript export helpers |
| `src/monitoring/drift.py` | CO6/M6 | KS, PSI, performance and latency monitoring hooks |
| `src/tracking.py` | CO6/M6 | Optional MLflow tracking and artifact logging |
| `scripts/init_mlflow.py` | CO1/M1, CO6/M6 | Idempotent local MLflow experiment initialization |
| `.dvc/config`, `.dvcignore`, `dvc.yaml` | CO1/M1, CO6/M6 | DVC initialization, cache policy, and ingest/train/evaluate pipeline |
| `scripts/source_audit.py` | All outcomes | Source register and URL/citation consistency checks |

## Acceptance rule

A row is complete only when its code path, documentation path, and executable test or generated evidence artifact are present. A source citation alone is not treated as implementation evidence, and an implementation without a source-to-file mapping is not treated as source-governed.
