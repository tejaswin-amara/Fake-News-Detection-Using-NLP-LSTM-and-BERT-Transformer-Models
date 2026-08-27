# Handout Compliance & Complete Resource Utilization Plan

## Objective

Bring the Fake News Detection project into demonstrable compliance with the Machine Learning course handout while using the resources, methods, datasets, algorithms, evaluation techniques, and deployment requirements supplied by the course materials.

This is a **verification-first** plan: an item is considered complete only when there is implementation evidence, a reproducible execution path, a test/result, and documentation.

## Course-outcome alignment

| Outcome | Required evidence | Project implementation | Verification |
|---|---|---|---|
| CO1 | End-to-end ML lifecycle | ingestion → preprocessing → training → evaluation → deployment → monitoring | reproducibility test |
| CO2 | Logistic Regression / supervised baseline | TF-IDF + Logistic Regression and related linear baselines | metrics + CV |
| CO3 | Tree/ensemble models | Decision Tree, Random Forest, XGBoost, LightGBM | metrics + comparison |
| CO4 | PCA, K-Means and exploratory analysis | dimensionality reduction, clustering, visual EDA | cluster/PCA report |
| CO5 | Cross-validation and evaluation | stratified CV, ROC-AUC, F1, PR-AUC, calibration and statistical comparison | evaluation report |
| CO6 | Deployment and engineering | FastAPI, Docker, monitoring and production controls | integration/load/security tests |

## Required execution order

1. Freeze the current baseline and record the commit/environment.
2. Inventory every handout resource and map it to code, data, experiment, or documentation.
3. Verify dataset provenance, schema, checksums, labels, duplicates, and class balance.
4. Establish leakage-safe train/validation/test splits.
5. Validate preprocessing and feature engineering independently.
6. Execute every required classical ML method.
7. Execute PCA/K-Means exploratory work and retain reproducible outputs.
8. Execute BiLSTM and BERT pipelines where their required resources are available.
9. Run stratified cross-validation and the complete evaluation suite.
10. Add calibration and statistically defensible model comparisons.
11. Run cross-dataset and temporal generalization experiments.
12. Validate explainability for classical and neural models.
13. Run adversarial, robustness, and malformed-input tests.
14. Verify FastAPI serving, artifact integrity, ONNX parity, and monitoring.
15. Run Docker/Kubernetes, performance, failure-injection, and security checks.
16. Produce the academic evidence package and final compliance matrix.
17. Only then tag the final release.

## Resource-utilization rule

Every resource supplied by the handout must be classified as one of:

- **Required and executed** — used in the final experiment or deployment path.
- **Required and validated** — implementation exists and is tested, but execution is resource-constrained; the limitation is recorded.
- **Reference/learning resource** — cited in methodology and used to justify implementation.
- **Not applicable** — only permitted when the handout genuinely does not apply; document the reason.

No metric will be fabricated. No resource will be marked as used merely because a file exists.

## Workstreams

### WS-01 — Handout traceability
- Build a complete resource inventory.
- Map each resource to CO, module, file, experiment, and evidence.
- Add `docs/HANDOUT_RESOURCE_MATRIX.md`.

### WS-02 — Data and leakage
- Dataset acquisition/provenance/checksum validation.
- Schema and label validation.
- Exact and near-duplicate detection.
- Source/group-aware and temporal split checks.
- Leakage regression tests.

### WS-03 — Classical ML
- Logistic Regression baseline.
- Ridge/Lasso/ElasticNet where specified by the project.
- Decision Tree.
- Random Forest.
- XGBoost.
- LightGBM.
- Consistent metrics and cross-validation.

### WS-04 — Unsupervised learning and EDA
- PCA.
- K-Means and Mini-Batch K-Means where implemented.
- Hierarchical clustering / DBSCAN where applicable.
- 2-D visualization using PCA/t-SNE/UMAP.
- Cluster-quality and interpretability analysis.

### WS-05 — Deep learning
- BiLSTM.
- GloVe/Word2Vec resource verification.
- BERT fine-tuning.
- Tokenizer/model revision pinning.
- Deterministic/reproducible training configuration.

### WS-06 — Evaluation and research rigor
- Stratified 5-fold CV.
- Accuracy, precision, recall, F1.
- ROC-AUC and PR-AUC.
- MCC where useful.
- Brier score and calibration.
- Bootstrap confidence intervals.
- McNemar comparisons.
- Learning/validation curves.

### WS-07 — Generalization and robustness
- Cross-dataset evaluation.
- Temporal evaluation.
- Distribution-shift analysis.
- Unicode/formatting/long-input/adversarial NLP tests.
- Data poisoning and retraining safeguards.

### WS-08 — Explainability
- Classical feature importance/SHAP.
- Token-level attribution for neural models.
- Human-readable prediction rationale without presenting the classifier as a fact verifier.

### WS-09 — Deployment and MLOps
- Artifact versioning.
- MLflow/DVC verification.
- ONNX export/parity.
- FastAPI integration.
- Health/readiness checks.
- Prometheus metrics.
- Redis resilience where used.

### WS-10 — Security and reliability
- Static analysis.
- Dependency auditing.
- Container scanning.
- Secret scanning.
- API abuse limits.
- Artifact signature/hash verification.
- Failure injection.
- Kubernetes hardening.

### WS-11 — Academic submission
- Final compliance matrix.
- Dataset card.
- Model cards.
- Methodology.
- Results and statistical analysis.
- Architecture/deployment evidence.
- Viva-ready explanation of every CO.

## Definition of done

A requirement is complete only when all applicable boxes are checked:

- [ ] Implementation exists.
- [ ] Configuration is reproducible.
- [ ] Test or experiment executes successfully.
- [ ] Output/result is retained.
- [ ] Result is documented.
- [ ] Handout resource is cited/mapped.
- [ ] CO mapping is recorded.
- [ ] Limitations are disclosed.

## Release gates

### Gate 1 — Data
No training until provenance, schema, checksum, labels, duplicates, and leakage checks pass.

### Gate 2 — Models
No final comparison until every required model has an executed result or a documented resource-constrained validation state.

### Gate 3 — Evaluation
No champion model until cross-validation, held-out testing, calibration, and statistical comparison are complete.

### Gate 4 — Deployment
No production claim until API, artifact integrity, container, performance, failure, and security tests pass.

### Gate 5 — Academic compliance
No final submission until every handout requirement has an evidence link and every supplied resource has a documented disposition.

## Target final evidence tree

```text
academic/
├── handout_compliance_report.md
├── resource_utilization_report.md
├── methodology.md
├── dataset_analysis.md
├── leakage_audit.md
├── model_comparison.md
├── cross_dataset_evaluation.md
├── temporal_evaluation.md
├── calibration_analysis.md
├── explainability.md
├── robustness.md
├── deployment_demo.md
├── security_analysis.md
└── viva_questions.md

reports/
├── baseline/
├── experiments/
├── evaluation/
├── performance/
└── security/
```

## Final principle

The repository should demonstrate the complete ML engineering lifecycle taught by the handout, not simply contain code for each topic. The final submission must make it possible for a reviewer to trace **handout resource → implementation → experiment → result → evidence**.