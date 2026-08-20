# Model Cards

## 1. Model overview

This repository contains a family of supervised fake-news text classifiers and the production boundary used to package and serve them. The models estimate whether an input article resembles the **real/fake label construction** present in the governed ISOT or WELFake datasets. They do not determine whether an article is factually true, identify a speaker’s intent, establish publisher credibility, or make a legal or editorial verdict.

The canonical label convention is **`0 = real` and `1 = fake`**. The WELFake adapter explicitly inverts the source convention before any split or model fitting. The model family is versioned through the packaged artifact metadata, package manifest, MLflow run, DVC data revision, configuration, source IDs, and software environment.

## 2. Intended use

The supported use is educational ML engineering, reproducible model comparison, research on text classification, and **human-reviewed editorial triage** on distributions that are demonstrably comparable to the approved reference data. A prediction is a screening signal that may help prioritize material for a qualified reviewer. It must not be treated as a fact-checking verdict or as evidence independent of the article, source, date, and domain context.

### Out-of-scope use

The models must not be used to make or automate decisions about censorship, publication blocking, employment, credit, insurance, housing, education, immigration, policing, legal liability, political persuasion, voter eligibility, benefits, health care, or personal reputation. They must not be used to infer a person’s identity, ideology, protected attribute, intent, criminality, or credibility. They must not be used to auto-publish accusations, suppress speech, or replace professional fact-checking, source verification, or human review.

## 3. Model variants and architectures

| Variant | Representation and estimator | Production status | Interpretation |
|---|---|---|---|
| Logistic L1 | Train-fitted word-level TF-IDF followed by logistic regression with L1 regularization | Supported baseline | Sparse coefficients and ranked token features |
| Logistic L2 | Train-fitted word-level TF-IDF followed by logistic regression with L2 regularization | Default DVC model | Stable CPU baseline and probability output |
| Logistic ElasticNet | Train-fitted TF-IDF followed by elastic-net logistic regression | Supported comparison | Sparse/dense regularized coefficient trade-off |
| Logistic multinomial | TF-IDF with multinomial logistic objective | Supported comparison | Multiclass-capable softmax path, used with the binary label contract here |
| Decision Tree | TF-IDF or reduced numeric feature matrix with impurity-based splits and cost-complexity pruning | Supported comparison | Rule-like splits; overfitting risk is material |
| Random Forest | Bootstrap decision trees with OOB/permutation importance support | Supported comparison | Ensemble variance reduction; resource dependent |
| XGBoost | Additive histogram gradient-boosted trees | Optional comparison | Nonlinear feature interactions and SHAP support |
| LightGBM | Leaf-wise gradient-boosted trees | Optional comparison | Efficient nonlinear modeling; leaf growth can overfit |
| BiLSTM | Token sequences with optional GloVe initialization and bidirectional recurrent states | Resource-dependent | Sequential context; GPU recommended for full training |
| BERT | Fine-tuning of **`bert-base-uncased`** with dynamic subword tokenization | Resource-dependent | Contextual transformer representation; GPU recommended |

All fitted transforms, including TF-IDF, vocabulary, scalers, clusterers, anomaly detectors, and calibration maps, are fitted only on the permitted training/validation partition. The final test partition is held out from model selection.

## 4. Training and evaluation protocol

The default ingestion protocol removes exact normalized-content duplicates before a stratified **70% train / 15% validation / 15% test** split with seed 42. The validation partition is used for model decisions and optional calibration. The final test partition is evaluated once after model, hyperparameter, threshold, and calibration decisions are frozen. Nested cross-validation is available for selection uncertainty and does not reuse the final test partition.

Calibration uses Platt/sigmoid or isotonic maps fit on validation data or training folds only. A serving response reports `calibration_status: not_available` and nullable confidence-interval fields when no validated calibration/uncertainty manifest is packaged. The service never invents confidence intervals.

The reproducible execution path is:

```bash
python scripts/run_pipeline.sh
```

The path runs DVC ingestion/training/evaluation, optional ONNX export with native parity, the complete test suite, MLflow-backed evaluation, and report generation. It requires the governed raw data or a configured DVC remote; it does not generate substitute benchmark data.

## 5. Metrics and evidence provenance

Metrics are accepted only from executed artifacts. The authoritative dynamic report is `reports/best_model_summary.json`, and its checksums and downloaded plots are recorded in `reports/report_manifest.json`. The selected run must contain the configured primary metric, normally PR-AUC, and must be a successful finalized MLflow run. No full-dataset benchmark is claimed in this documentation unless those files exist.

The repository includes one **executed four-row fixture evaluation** for smoke-test verification. It is not a deployment benchmark and must not be generalized beyond that fixture:

| Evidence | Rows | Accuracy | Precision | Recall | F1 macro | ROC-AUC | PR-AUC | Brier score | Confusion matrix |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `reports/fixture_evaluation.json` | 4 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00234475374205099 | `[[2, 0], [0, 2]]` |
| ISOT/WELFake full-data run | Not available in the committed snapshot | Not reported | Not reported | Not reported | Not reported | Not reported | Not reported | Not reported | Not reported |

The absence of a full-data row is an explicit provenance status, not a zero score. A report generated from an executed MLflow run must also record model name, run ID, data revision, split manifest, feature configuration, calibration fit partition, software versions, hardware, and whether the final test was used for selection.

## 6. Explainability and auditability

Linear models expose coefficient-based feature evidence. Tree models expose impurity/permutation importance and optional Tree SHAP values. SHAP and permutation importance describe model behavior on a declared evaluation partition; they are not causal explanations, evidence that a token is false, or proof that a publisher is unreliable. Every generated explanation must retain feature names, model/artifact revision, split, and optional-dependency status.

Native artifacts and optional ONNX artifacts are accompanied by package manifests and SHA-256 checksums. ONNX is deployable only when ONNX Runtime probabilities match native probabilities with maximum absolute error strictly below `1e-5` on the conformance fixture. Unsupported operations remain explicitly `native_only`.

## 7. Ethical considerations and known biases

ISOT and WELFake labels reflect source construction, collection choices, temporal context, publisher composition, language, political context, and annotation assumptions. A text-only model may learn headline style, punctuation, named entities, publisher artifacts, or repeated dataset phrasing rather than factuality. Distribution shift can occur across countries, languages, topics, time periods, platforms, and emerging events. Class imbalance, duplicate handling, and source overlap can alter apparent performance.

The system must not log submitted article text by default. Operators should restrict access to artifacts, use payload limits, apply authentication/TLS/rate controls at the deployment boundary, and provide a human appeal/review path. Monitoring alerts are review signals. Retraining and promotion require human approval, delayed-label review, reproducible data/version checks, parity tests, shadow or canary evidence, and rollback readiness.

## 8. Limitations and failure modes

The models can be confidently wrong on satire, quotations, breaking news, multilingual text, short text, copied text, adversarial wording, unseen topics, and articles whose factual status cannot be inferred from prose. Probabilities are model scores, not universal truth probabilities. Concept drift cannot be established without trustworthy delayed labels. A detected feature or probability drift does not itself establish model degradation.

The production service validates payload size, non-empty content, batch bounds, artifact readiness, and model metadata. It does not independently verify claims, retrieve evidence, resolve entities, or determine publisher intent. `/monitoring/drift` emits structured signals only; it never retrains, replaces, or promotes a model.

## 9. Versioning and provenance checklist

A releasable model card must be accompanied by the native artifact, optional ONNX artifact, package manifest, split manifest, configuration, DVC revision, MLflow run ID, report manifest, dependency versions, source IDs, calibration status, and test evidence. The source register in [`docs/sources.md`](sources.md) and machine-readable register in [`docs/sources.yaml`](sources.yaml) are authoritative for citations and usage terms. Pretrained GloVe/BERT revisions and checksums must be recorded with deep-learning artifacts; weights are not committed by default.

## 10. Course alignment

This card provides CO1/M1 problem and data context; CO2/M2 regularized linear modeling and preprocessing; CO3/M3 tree/ensemble comparison and explainability; CO4/M4 unsupervised feature and anomaly context; CO5/M5 validation, calibration, metrics, and statistical comparison; and CO6/M6 packaging, serving, monitoring, CI/CD, DVC, MLflow, security, and human-approved retraining.
