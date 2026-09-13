# Capstone Compliance Matrix

Course: Machine Learning (25SC2107E)  
System: VERITAS (Verified Explainable Real-time Information Telemetry & Analytics System)

## Traceability & Status Matrix

| CO | Module | Requirement | Implementation | Tests | Generated Evidence | Status |
|---|---|---|---|---|---|---|
| **CO1** | **M1** | ML Lifecycle & Data Governance | `src/data/ingestion.py`<br>`src/features/minhash.py`<br>`src/data/claimreview.py` | `tests/test_ingestion.py`<br>`tests/test_claimreview_dataset.py` | `data/processed/split_manifest.json`<br>`reports/data_summary.json` | **IMPLEMENTED & VERIFIED** |
| **CO2** | **M2** | Linear Models & Regularization | `src/models/classical.py`<br>(Logistic L1/L2/ElasticNet, Ridge, coefficient analysis) | `tests/test_models_evaluation.py` | `reports/linear_models_comparison.json`<br>`reports/linear_models_comparison.csv` | **IMPLEMENTED & VERIFIED** |
| **CO3** | **M3** | Tree Models & Explainability | `src/models/classical.py`<br>(Decision Tree, Random Forest, XGBoost, LightGBM, Gini, Permutation, SHAP) | `tests/test_models_evaluation.py` | `reports/tree_models_comparison.json` | **IMPLEMENTED & VERIFIED** |
| **CO4** | **M4** | Unsupervised Learning & Semantic Discovery | `src/models/unsupervised.py`<br>(K-Means, MiniBatch, Hierarchical, DBSCAN, PCA, t-SNE, Isolation Forest) | `tests/test_features_phase2.py`<br>`tests/test_models_evaluation.py` | `reports/unsupervised_analysis.json` | **IMPLEMENTED & VERIFIED** |
| **CO5** | **M5** | Evaluation, Calibration & Significance | `src/evaluate.py`<br>`src/evaluation/metrics.py`<br>(Stratified CV, Platt & Isotonic calibration, Brier score, McNemar test) | `tests/test_models_evaluation.py` | `reports/evaluation_report.json`<br>`reports/calibration_report.json` | **IMPLEMENTED & VERIFIED** |
| **CO6** | **M6** | ML Engineering, Serving & Monitoring | `src/serving/app.py`<br>`src/monitoring/drift.py`<br>`src/serving/export.py`<br>`docker-compose.dashboard.yml`<br>`frontend/` | `tests/test_serving.py`<br>`tests/test_day5_sre.py`<br>`tests/test_security_hardening.py`<br>`frontend/vitest` | `artifacts/models/logistic_l2.joblib`<br>`artifacts/models/package_manifest.json`<br>`reports/champion_model.json`<br>`reports/drift_report.json`<br>`reports/final_evidence_manifest.json` | **IMPLEMENTED & VERIFIED** |

---

## Detailed Evidence Registry

### CO1 / M1: ML Lifecycle & Data Governance
- **Data Flow**: Raw canonical schema ingestion (`title`, `text`, `content`, `label`, `content_hash`).
- **Leakage Prevention**: Stratified split (70% train, 15% validation, 15% test) executed strictly before feature extraction. Exact SHA-256 deduplication and MinHash LSH near-duplicate clustering.
- **Dataset Qualification**: Governed Curated Benchmark (N=80) explicitly designated as `SMOKE TEST / FIXTURE / CURATED BENCHMARK` for deterministic CI and local reproducibility.

### CO2 / M2: Linear Models & Regularization
- **Regularization Taxonomy**: Evaluated Logistic L1 (Lasso, resulting in 65% coefficient sparsity), Logistic L2 (Ridge penalty, non-zero weight retention), and ElasticNet (convex mixture).
- **Interpretability**: Top positive features driving fake predictions and negative features driving real predictions extracted directly from model coefficients.

### CO3 / M3: Tree Models & Ensembles
- **Tree Architectures**: Cost-complexity pruned Decision Trees, Random Forest bagging with Out-Of-Bag (OOB) generalization scoring, XGBoost gradient boosting, and LightGBM histogram binning.
- **Explainability**: Gini impurity decrease, 5-repeat validation permutation importance, and TreeExplainer SHAP attribution.

### CO4 / M4: Unsupervised Learning & Semantic Discovery
- **Clustering**: K-Means elbow curve ($k=2..6$) and silhouette analysis, MiniBatch K-Means for streaming efficiency, Agglomerative Hierarchical clustering comparing Ward, Average, and Complete linkage, and DBSCAN density analysis.
- **Projections & Anomalies**: PCA and t-SNE 2D manifolds demonstrating semantic topic clustering; Isolation Forest detecting out-of-distribution texts.

### CO5 / M5: Evaluation, Calibration & Hypothesis Testing
- **Multi-Metric Suite**: Accuracy, Precision, Recall, Macro/Weighted F1, ROC-AUC, and PR-AUC.
- **Calibration**: Uncalibrated vs Platt Scaling (sigmoid cross-entropy fit on validation) vs Non-parametric Isotonic Regression evaluated via Brier score loss.
- **Hypothesis Testing**: Paired 2x2 McNemar test computing exact binomial p-values between champion linear classifier and tree ensembles.

### CO6 / M6: ML Engineering, Serving & Monitoring
- **Serving Architecture**: Production rootless FastAPI container exposing bounded `/predict`, `/predict/batch`, `/health`, `/ready`, `/monitoring/drift`, and `/reports/{name}`.
- **Dashboard Bridge**: Next/Express + tRPC bridge connecting React 19 UI to FastAPI inference and live telemetry with zero client-side mock logic.
- **Monitoring**: Kolmogorov-Smirnov distribution test and Population Stability Index (PSI) with automated retraining signals (`continue_monitoring` vs `review_and_retrain`).
- **Artifact Governance**: Cryptographic SHA-256 package verification against `package_manifest.json` with air-gapped loading.
