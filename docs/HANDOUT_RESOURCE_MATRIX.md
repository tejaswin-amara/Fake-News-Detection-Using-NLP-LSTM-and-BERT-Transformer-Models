# Handout Resource Traceability Matrix

> Working compliance register. Each row must be updated with the exact source/resource name from the course handout and a concrete evidence path before final release.

| Handout resource / requirement | CO | Project use | Evidence | Status |
|---|---|---|---|---|
| End-to-end ML lifecycle | CO1 | Data ingestion, preprocessing, training, evaluation, deployment, monitoring | `docs/architecture.md`, pipeline scripts, integration tests | 🔄 Verify |
| Logistic Regression | CO2 | TF-IDF supervised baseline | model implementation + experiment report | 🔄 Verify |
| Random Forest | CO3 | Ensemble classifier | model implementation + experiment report | 🔄 Verify |
| XGBoost | CO3 | Gradient-boosted classifier | model implementation + experiment report | 🔄 Verify |
| PCA | CO4 | Dimensionality reduction and EDA | PCA experiment/report | 🔄 Verify |
| K-Means | CO4 | Unsupervised clustering/EDA | clustering experiment/report | 🔄 Verify |
| Cross-validation | CO5 | Stratified 5-fold validation | evaluation report | 🔄 Verify |
| ROC-AUC | CO5 | Threshold-independent evaluation | evaluation report | 🔄 Verify |
| F1-score | CO5 | Primary classification metric | evaluation report | 🔄 Verify |
| Calibration | CO5 | Probability reliability | calibration report | 🔄 Verify |
| FastAPI | CO6 | Model inference service | serving tests + API docs | 🔄 Verify |
| Docker | CO6 | Reproducible application packaging | Docker build/security evidence | 🔄 Verify |
| Monitoring | CO6 | Production telemetry and model monitoring | Prometheus/monitoring evidence | 🔄 Verify |
| DVC | Engineering support | Dataset/version lifecycle | DVC pipeline and verification logs | 🔄 Verify |
| MLflow | Engineering support | Experiment/artifact tracking | MLflow evidence | 🔄 Verify |
| ONNX | Engineering support | Portable inference + parity validation | ONNX parity test | 🔄 Verify |
| BERT / Transformer | Deep learning resource | Transformer-based fake-news classifier | training/evaluation evidence | 🔄 Verify |
| BiLSTM | Deep learning resource | Recurrent neural classifier | training/evaluation evidence | 🔄 Verify |
| GloVe / Word2Vec | NLP resource | Embedding-based representation | resource checksum + experiment | 🔄 Verify |

## Status definitions

- ✅ **Complete:** implemented, executed, tested, documented, and linked to evidence.
- 🔄 **Verify:** implementation appears present but execution/evidence still needs verification.
- ⚠️ **Constrained:** required resource is unavailable in the execution environment; validation and limitation must be documented.
- ❌ **Missing:** requirement/resource has no adequate implementation.

## Completion rule

Do not convert `🔄 Verify` to `✅ Complete` because a source file exists. The final matrix requires a reproducible command, retained output, and a documented result.

## Final audit additions

Before release, add rows for **every exact dataset, algorithm, evaluation method, software/tool, reading/resource, and submission artifact named by the handout**. Preserve the handout's original terminology so a faculty reviewer can trace it directly.
