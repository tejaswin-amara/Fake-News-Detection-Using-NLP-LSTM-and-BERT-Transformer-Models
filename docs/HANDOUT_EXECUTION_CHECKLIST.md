# 25SC2107E Final Execution Checklist

The handout requires M1–M6 coverage. It does not require turning this project into a generic web application. The following checklist is the release gate.

## M1 / CO1 — ML lifecycle

- [ ] Raw data is identified and provenance is recorded.
- [ ] Data cleaning produces a canonical dataset.
- [ ] Feature engineering is fit only on permitted training data.
- [ ] Train/validation/test split is fixed and recorded.
- [ ] A model is trained and packaged.
- [ ] One request is traced from HTTP input through feature lookup/transform and inference to response.
- [ ] Monitoring records latency/performance/drift.
- [ ] Retraining is a human-reviewed lifecycle transition.

**Evidence:** `docs/deployment.md`, `src/serving/`, `src/monitoring/`, pipeline reports.

## M2 / CO2 — Linear supervised learning

- [ ] Ordinary linear regression exists as an explicit teaching/reference model.
- [ ] Ridge, Lasso, ElasticNet are demonstrated.
- [ ] Binary Logistic Regression is demonstrated.
- [ ] Multinomial Logistic Regression is demonstrated.
- [ ] Sigmoid/softmax and regularization are documented mathematically.
- [ ] StandardScaler and MinMaxScaler are available where appropriate.
- [ ] Mean/median/KNN/iterative imputation is tested.
- [ ] MissingIndicator is tested.
- [ ] One-hot/ordinal/target encoding is tested.
- [ ] Coefficients are interpreted.

**Evidence:** `src/models/classical.py`, `src/models/handout_models.py`, `src/features/preprocessing.py`, model reports.

## M3 / CO3 — Tree-based learning

- [ ] Decision Tree uses Gini and entropy/log-loss options.
- [ ] Pre-pruning controls are tested.
- [ ] Cost-complexity pruning (`ccp_alpha`) is tested.
- [ ] Random Forest uses bagging/feature subsampling and OOB evaluation.
- [ ] AdaBoost is available as the handout's intuition-level boosting method.
- [ ] XGBoost is evaluated.
- [ ] LightGBM is evaluated.
- [ ] Gini/permutation/SHAP importance is generated.

**Evidence:** `src/models/classical.py`, `src/models/handout_models.py`, `src/evaluation/`, reports.

## M4 / CO4 — Unsupervised learning

- [ ] K-Means++ and elbow/silhouette diagnostics.
- [ ] Mini-Batch K-Means.
- [ ] Hierarchical clustering with documented linkage choices.
- [ ] DBSCAN with `eps`/`min_samples` analysis.
- [ ] PCA with standardization rationale.
- [ ] t-SNE visualization.
- [ ] UMAP visualization.
- [ ] Isolation Forest anomaly detection.
- [ ] One-Class SVM anomaly demonstration.
- [ ] Cluster/anomaly features can be added without test leakage.

**Evidence:** `src/models/unsupervised.py`, `src/models/handout_models.py`, `src/features/unsupervised_features.py`.

## M5 / CO5 — Evaluation, selection, calibration

- [ ] Three-way train/validation/test discipline.
- [ ] Stratified k-fold CV.
- [ ] Nested CV when tuning and unbiased evaluation overlap.
- [ ] Accuracy, precision, recall, F1.
- [ ] ROC-AUC and PR-AUC.
- [ ] RMSE, MAE, MAPE, R² generic regression evaluation.
- [ ] Calibration with sigmoid/Platt and isotonic.
- [ ] Reliability diagrams.
- [ ] Grid search.
- [ ] Random search.
- [ ] Bayesian/TPE search.
- [ ] Learning curves.
- [ ] Validation curves.
- [ ] McNemar classifier comparison.
- [ ] Paired bootstrap regression comparison.

**Evidence:** `src/evaluation/metrics.py`, `src/evaluation/search.py`, `src/evaluation/plots.py`.

## M6 / CO6 — ML engineering

- [ ] Training-serving boundary is explicit.
- [ ] Feature transformation is shared by training and serving.
- [ ] Artifact metadata includes dataset/config/git identity.
- [ ] Artifact integrity is verified before deserialization.
- [ ] ONNX parity is measured before portable inference is trusted.
- [ ] FastAPI REST serving works for single and batch inference.
- [ ] Readiness/health are distinct.
- [ ] Latency and throughput are observable.
- [ ] Data/probability/text drift are measured.
- [ ] Retraining signals are non-mutating and human-approved.
- [ ] MLflow tracks experiments/artifacts.
- [ ] DVC versions data/pipeline state.
- [ ] Docker runtime is rootless/read-only where supported.
- [ ] CI performs quality, test, security and container gates.

**Evidence:** `src/serving/`, `src/monitoring/`, `src/tracking.py`, DVC files, Docker, `.github/workflows/`.

## Final academic evidence

For each checked item retain:

```text
Requirement → Source file → Command → Output → Interpretation → Limitation
```

A full-data metric is not allowed in the final report until its corresponding experiment has actually executed against governed data. This is especially important for BERT/BiLSTM and large-dataset cross-domain experiments.
