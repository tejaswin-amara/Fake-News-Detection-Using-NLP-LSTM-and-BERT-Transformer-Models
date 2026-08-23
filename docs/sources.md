# Source Register

This file is the authoritative human-readable register for every external source used or referred to by the project. The machine-readable companion is [`sources.yaml`](sources.yaml). Every entry records provenance, access information, usage terms, and the repository files or claims it supports. The register must be updated before adding a new external citation, dependency, dataset, pretrained model, algorithm, benchmark claim, or copied implementation pattern.

## Source-governance policy

The project distinguishes **sources used for implementation or claims**, **background sources listed because the handout requires them**, **project links**, and **locally archived sources**. Restricted materials are not redistributed. When a source cannot lawfully be copied into `docs/references/`, this register preserves its complete bibliographic metadata, URL or DOI, access date, license/terms, and source-to-file mapping.

The attached handout is copied into `docs/references/MachineLearninghandout.pdf` when permitted by the user-provided attachment context. Dataset files and pretrained weights are not committed by default; their source URLs, versions, checksums, and licensing terms are recorded here and in generated artifact metadata.

## Datasets and project requirements

### SRC-001 — ISOT Fake News Dataset and primary publication

**Citation:** Ahmed H, Traore I, Saad S. “Detecting opinion spams and fake news using text classification.” *Security and Privacy*, 2018, 1:e9. The brief specifies the January/February 2018 issue wording; the publisher record reports first publication on 29 December 2017 and issue placement in January/February 2018. DOI: [10.1002/spy2.9](https://doi.org/10.1002/spy2.9).

**Use:** ISOT dataset provenance and the motivation for text-classification baselines. **Files/claims supported:** `README.md`, `src/data/ingestion.py`, dataset card, EDA notebook, benchmark report. **Accessed:** 2026-08-20. **Terms:** publisher and dataset redistribution terms must be checked before redistribution; raw data is not committed by default.

### SRC-002 — WELFake dataset record

**Citation:** Verma PK, Agrawal P, Prodan R. *WELFake dataset for fake news detection in text data*. Zenodo, version 0.1, published 2021-02-25. DOI: [10.5281/zenodo.4561253](https://doi.org/10.5281/zenodo.4561253). The associated research article is Verma PK, Agrawal P, Amorim I, Prodan R. “WELFake: Word Embedding Over Linguistic Features for Fake News Detection.” *IEEE Transactions on Computational Social Systems*, 2021. DOI: [10.1109/TCSS.2021.3068519](https://doi.org/10.1109/TCSS.2021.3068519).

**Use:** WELFake ingestion adapter and dataset provenance. **Files/claims supported:** `README.md`, `src/data/ingestion.py`, dataset card, EDA notebook, benchmark report. **Accessed:** 2026-08-20. **License:** Zenodo record states CC BY 4.0 for the dataset record; downstream component terms must be reviewed before redistribution. **Checksum recorded at source:** `WELFake_Dataset.csv` MD5 `73c9675a4b3d09f86a6933d0b8d7d908`.

### SRC-045 — Data Commons current ClaimReview fact-check feed

**Citation:** Data Commons, *Fact Check Markup Tool Data Feed*, live structured ClaimReview feed. [Download documentation](https://datacommons.org/factcheck/download), [FAQ](https://datacommons.org/factcheck/faq), and [latest feed](https://storage.googleapis.com/datacommons-feeds/factcheck/latest/data.json). **Use:** new current fact-checked claims dataset collection, provenance manifest, label-gated normalization, and time-held-out release. **Files/claims supported:** `src/data/claimreview.py`, `configs/dataset.yaml`, `dvc.yaml`, `README.md`, `docs/dataset_card.md`, `docs/current_dataset_release.md`. **Accessed:** 2026-08-21. **License:** Data Commons states the feed compilation is CC BY 4.0; individual ClaimReview structured-data licensing is represented by `sdLicense` where provided, and publisher terms continue to apply to material on publisher sites. The project does not collect full fact-check article text. **Release provenance:** feed SHA-256 `9266a7bbc99ee16416f05afdad2524557b242a98ba9e823e3cb0734631cdc2b0`, with full release metadata written to `collection_manifest.json` and `release_manifest.json` in DVC-managed data paths.

### SRC-003 — Course handout

**Citation:** *Machine Learning*, course code `25SC2107E`, `MachineLearninghandout.pdf`, supplied by the project owner, dated 2026-08-20 in the attachment metadata. A copy is maintained at `docs/references/MachineLearninghandout.pdf`.

**Use:** Authoritative definition of CO1–CO6, Modules M1–M6, syllabus topics, and required reference books. **Files/claims supported:** `README.md`, `docs/compliance_matrix.md`, all source modules, tests, notebooks, and reports. **Accessed:** 2026-08-20. **Terms:** user-provided course material; local project reference only.

## Handout reference books

### SRC-004 — Géron (2022)

Aurélien Géron. *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*, 3rd ed. O’Reilly, 2022. Publisher page: [oreilly.com/library/view/hands-on-machine-learning/9781098125974](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125974/). **Use:** supervised learning, pipelines, neural networks, evaluation, and practical ML engineering background. **Files:** README, notebooks, `src/` modules, reports. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

### SRC-005 — Hastie, Tibshirani, and Friedman (2017)

Trevor Hastie, Robert Tibshirani, and Jerome Friedman. *The Elements of Statistical Learning: Data Mining, Inference, and Prediction*, 2nd ed., corrected 12th printing. Springer, 2017. [Web edition](https://hastie.su.domains/ElemStatLearn/). **Use:** regularization, trees, ensembles, cross-validation, statistical learning, and model comparison. **Files:** README, `docs/compliance_matrix.md`, classical/evaluation documentation. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference and publisher-hosted web edition only.

### SRC-006 — James et al. (2023)

Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani, and Jonathan Taylor. *An Introduction to Statistical Learning: With Applications in Python*. Springer, 2023. [Official site](https://www.statlearning.com/). **Use:** supervised/unsupervised learning, resampling, regularization, and evaluation explanations. **Files:** README, notebooks, reports. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

### SRC-007 — Bishop (2006)

Christopher M. Bishop. *Pattern Recognition and Machine Learning*. Springer, 2006. [Springer page](https://link.springer.com/book/9780387310732). **Use:** probabilistic classification, optimization, graphical/statistical foundations, and model interpretation. **Files:** README, reports, mathematical appendix. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

### SRC-008 — Huyen (2022)

Chip Huyen. *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*. O’Reilly, 2022. [Publisher page](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/). **Use:** lifecycle, training-serving skew, monitoring, deployment, and retraining design. **Files:** README, `src/serving/`, `src/monitoring/`, deployment docs. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

### SRC-009 — Ameisen (2020)

Emmanuel Ameisen. *Building Machine Learning Powered Applications: Going from Idea to Product*. O’Reilly, 2020. [Publisher page](https://www.oreilly.com/library/view/building-machine-learning/9781492045106/). **Use:** practical model-to-product workflow, error analysis, and deployment design. **Files:** README, notebooks, serving and evaluation docs. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

### SRC-010 — Burkov (2020)

Andriy Burkov. *Machine Learning Engineering*. True Positive Inc., 2020. [Publisher page](https://www.mlebook.com/). **Use:** production ML engineering, testing, monitoring, and lifecycle practices. **Files:** README, tests, deployment docs, monitoring docs. **Accessed:** 2026-08-20. **Terms:** copyrighted; bibliographic reference only.

## NLP, embeddings, and transformers

### SRC-011 — GloVe

Jeffrey Pennington, Richard Socher, and Christopher D. Manning. “GloVe: Global Vectors for Word Representation.” EMNLP, 2014. [Stanford project page](https://nlp.stanford.edu/projects/glove/) and [paper PDF](https://nlp.stanford.edu/pubs/glove.pdf). **Use:** optional pretrained 100d/300d embedding initialization in `src/models/lstm.py` and embedding preparation in `src/features/`. **Accessed:** 2026-08-20. **Terms:** code is Apache-2.0; pretrained vector terms vary by release and must be recorded with the selected artifact checksum.

### SRC-012 — BERT

Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.” arXiv:1810.04805, v2 2019. [arXiv record](https://arxiv.org/abs/1810.04805). **Use:** BERT architecture and fine-tuning rationale in `src/models/bert.py`. **Accessed:** 2026-08-20. **Terms:** arXiv distribution terms; model weights have their own model-card terms.

### SRC-013 — Hugging Face Transformers and BERT model card

Hugging Face. [Transformers documentation](https://huggingface.co/docs/transformers/index) and [`google-bert/bert-base-uncased` model card](https://huggingface.co/google-bert/bert-base-uncased). **Use:** tokenizer, dynamic padding, `AutoModelForSequenceClassification`, optimizer/scheduler integration, model artifact provenance, and implementation compatibility. **Files:** `src/models/bert.py`, configs, requirements, README. **Accessed:** 2026-08-20. **Terms:** documentation and model-card/weight terms must be followed; record downloaded revision and checksum.

### SRC-014 — Sentence Transformers

UKPLab. [Sentence Transformers documentation](https://www.sbert.net/) and [sentence-transformers repository](https://github.com/UKPLab/sentence-transformers). **Use:** optional SBERT embeddings for unsupervised analysis. **Files:** `src/features/`, `src/models/unsupervised.py`, notebooks. **Accessed:** 2026-08-20. **Terms:** project and selected model licenses must be checked; record model revision.

### SRC-015 — scikit-learn user guide

The scikit-learn developers. [User Guide](https://scikit-learn.org/stable/user_guide.html). **Use:** preprocessing, TF-IDF, Logistic Regression, trees, ensembles, clustering, PCA, t-SNE, Isolation Forest, calibration, metrics, model selection, and permutation importance. **Files:** nearly all classical/evaluation modules. **Accessed:** 2026-08-20. **Terms:** BSD-3-Clause for scikit-learn; exact dependency version recorded in `requirements.txt`.

## Unsupervised algorithms

### SRC-016 — K-Means and clustering

Lloyd, S. “Least Squares Quantization in PCM.” IEEE Transactions on Information Theory, 1982. DOI: [10.1109/TIT.1982.1056489](https://doi.org/10.1109/TIT.1982.1056489). scikit-learn clustering guide: [K-Means](https://scikit-learn.org/stable/modules/clustering.html#k-means). **Use:** K-Means, K-Means++, elbow and silhouette analyses in `src/models/unsupervised.py`. **Accessed:** 2026-08-20.

### SRC-017 — Hierarchical clustering

Müllner, D. “Modern hierarchical, agglomerative clustering algorithms.” arXiv:1109.2378, 2011. [arXiv record](https://arxiv.org/abs/1109.2378). scikit-learn [hierarchical clustering guide](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering). **Use:** linkage options and dendrogram generation. **Accessed:** 2026-08-20.

### SRC-018 — DBSCAN

Ester, M., Kriegel, H.-P., Sander, J., and Xu, X. “A density-based algorithm for discovering clusters in large spatial databases with noise.” KDD, 1996. [DBSCAN reference](https://www.aaai.org/papers/kdd96-037-a-density-based-algorithm-for-discovering-clusters-in-large-spatial-databases-with-noise/). **Use:** DBSCAN `eps`, `minPts`, noise, and tuning. **Accessed:** 2026-08-20.

### SRC-019 — PCA, t-SNE, and UMAP

Pearson, K. “On Lines and Planes of Closest Fit to Systems of Points in Space.” Philosophical Magazine, 1901. [doi:10.1080/14786440109462720](https://doi.org/10.1080/14786440109462720). van der Maaten, L., and Hinton, G. “Visualizing Data using t-SNE.” JMLR, 2008. [jmlr.org/papers/v9/vandermaaten08a.html](https://www.jmlr.org/papers/v9/vandermaaten08a.html). McInnes, L., Healy, J., and Melville, J. “UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.” arXiv:1802.03426. [arXiv record](https://arxiv.org/abs/1802.03426). **Use:** dimensionality reduction and visualization in `src/models/unsupervised.py`. **Accessed:** 2026-08-20.

### SRC-020 — Isolation Forest

Liu, F. T., Ting, K. M., and Zhou, Z.-H. “Isolation Forest.” 2008 IEEE International Conference on Data Mining. DOI: [10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17). **Use:** anomaly detection and optional anomaly-score feature augmentation. **Accessed:** 2026-08-20.

## Classical models and explainability

### SRC-021 — Logistic regression and regularization

scikit-learn [LogisticRegression documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html), [linear-model user guide](https://scikit-learn.org/stable/modules/linear_model.html), and Hastie et al. source [SRC-005]. **Use:** L1, L2, ElasticNet, scaling rationale, coefficient interpretation, and bias-variance experiments. **Accessed:** 2026-08-20.

### SRC-022 — Tree ensembles and boosting

scikit-learn [decision trees](https://scikit-learn.org/stable/modules/tree.html) and [ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html); [XGBoost documentation](https://xgboost.readthedocs.io/en/stable/); [LightGBM documentation](https://lightgbm.readthedocs.io/en/latest/). **Use:** pruning, Gini/entropy, OOB error, bagging, gradient boosting, histogram splitting, and feature importance. **Accessed:** 2026-08-20. **Terms:** BSD-3-Clause for scikit-learn; Apache-2.0 for XGBoost; LightGBM uses the MIT License; exact installed versions are recorded.

### SRC-023 — SHAP

Lundberg, S. M., and Lee, S.-I. “A Unified Approach to Interpreting Model Predictions.” NeurIPS, 2017. [arXiv:1705.07874](https://arxiv.org/abs/1705.07874) and [SHAP documentation](https://shap.readthedocs.io/). **Use:** TreeExplainer summaries and feature-attribution caveats. **Accessed:** 2026-08-20. **Terms:** SHAP package license and version recorded in dependency metadata.

## Evaluation, calibration, and statistical testing

### SRC-024 — Cross-validation, metrics, and model selection

scikit-learn [model selection guide](https://scikit-learn.org/stable/model_selection.html), [metrics guide](https://scikit-learn.org/stable/modules/model_evaluation.html), and James et al. [SRC-006]. **Use:** stratified 5-fold CV, train/validation/test discipline, accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrices, learning/validation curves, grid search, and random search. **Accessed:** 2026-08-20.

### SRC-025 — Bayesian optimization

Snoek, J., Larochelle, H., and Adams, R. P. “Practical Bayesian Optimization of Machine Learning Algorithms.” NeurIPS, 2012. [arXiv:1206.2944](https://arxiv.org/abs/1206.2944). **Use:** documented optional Bayesian hyperparameter-search path. **Accessed:** 2026-08-20.

### SRC-026 — Probability calibration

Platt, J. “Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods.” In *Advances in Large Margin Classifiers*, 1999. [author-hosted PDF](https://www.cs.cornell.edu/people/tj/publications/joachims_99a.pdf). scikit-learn [calibration guide](https://scikit-learn.org/stable/modules/calibration.html). **Use:** Platt scaling, reliability diagrams, and Brier score. **Accessed:** 2026-08-20.

### SRC-027 — Isotonic regression

Zadrozny, B., and Elkan, C. “Transforming Classifier Scores into Accurate Multiclass Probability Estimates.” KDD, 2002. DOI: [10.1145/775047.775151](https://doi.org/10.1145/775047.775151). **Use:** isotonic calibration comparison. **Accessed:** 2026-08-20.

### SRC-028 — McNemar’s test

McNemar, Q. “Note on the sampling error of the difference between correlated proportions or percentages.” *Psychometrika*, 1947, 12, 153–157. DOI: [10.1007/BF02295996](https://doi.org/10.1007/BF02295996). **Use:** paired classifier comparison on identical held-out predictions. **Accessed:** 2026-08-20.

### SRC-029 — SciPy statistical functions

SciPy Community. [Statistical functions documentation](https://docs.scipy.org/doc/scipy/reference/stats.html). **Use:** KS tests, statistical distributions, and supporting test implementations. **Accessed:** 2026-08-20. **Terms:** BSD-3-Clause.

## ML engineering and serving

### SRC-030 — FastAPI

Sebastián Ramírez and contributors. [FastAPI documentation](https://fastapi.tiangolo.com/). **Use:** REST API, Pydantic validation, health checks, and endpoint behavior in `src/serving/app.py`. **Accessed:** 2026-08-20. **Terms:** MIT.

### SRC-031 — ONNX and ONNX Runtime

ONNX project. [ONNX documentation](https://onnx.ai/onnx/) and [ONNX Runtime documentation](https://onnxruntime.ai/docs/). **Use:** portable model export, runtime inference, and native-versus-export conformance tests. **Accessed:** 2026-08-20. **Terms:** MIT for ONNX project; exact runtime version recorded.

### SRC-032 — Docker

Docker documentation. [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) and [Python guide](https://docs.docker.com/guides/python/). **Use:** container build, healthcheck, and deployment instructions. **Accessed:** 2026-08-20. **Terms:** documentation reference; Docker Engine licensing depends on distribution.

### SRC-033 — MLflow

MLflow project. [Tracking documentation](https://mlflow.org/docs/latest/ml/tracking/) and [model registry documentation](https://mlflow.org/docs/latest/ml/model-registry/). **Use:** parameters, metrics, artifacts, and model-registration hooks. **Accessed:** 2026-08-20. **Terms:** Apache-2.0.

### SRC-034 — Python packaging and dependency metadata

Python Packaging Authority. [Packaging User Guide](https://packaging.python.org/en/latest/), [PEP 621](https://peps.python.org/pep-0621/), and [Python license documentation](https://docs.python.org/3/license.html). **Use:** package metadata, reproducible dependency declarations, and environment documentation. **Accessed:** 2026-08-20.

## Repository-local source mappings

| Source IDs | Repository files/claims supported |
|---|---|
| SRC-001–003 | Dataset provenance, labels, schema adapters, README data policy, dataset cards |
| SRC-004–010 | Handout-required textbook references and theory explanations |
| SRC-011–015 | NLP preprocessing, embeddings, BERT, SBERT, and model implementation |
| SRC-016–020 | `src/models/unsupervised.py`, M4 notebooks, clustering/anomaly reports |
| SRC-021–023 | Classical model implementations, pruning, boosting, and explanations |
| SRC-024–029 | `src/evaluation/metrics.py`, calibration reports, statistical tests, and M5 notebooks |
| SRC-030–034 | `src/serving/app.py`, `src/monitoring/drift.py`, Docker, MLflow, packaging, and CI |
| SRC-045 | Current ClaimReview source collection, provenance, temporal release policy, and dataset documentation |
| SRC-003 | `docs/compliance_matrix.md`, all CO/M claims, and the project acceptance criteria |

## Change log

| Date | Change |
|---|---|
| 2026-08-20 | Initial source register created from the user brief, course handout, and verified public source records. |
| 2026-08-21 | Added SRC-045 and the current ClaimReview dataset release provenance, source license boundary, and DVC collection workflow. |

### SRC-035 — NLP and ONNX conversion libraries

NLTK, spaCy, Gensim, and skl2onnx official documentation: [NLTK](https://www.nltk.org/), [spaCy](https://spacy.io/), [Gensim](https://radimrehurek.com/gensim/), and [skl2onnx](https://onnx.ai/sklearn-onnx/). **Use:** optional token normalization/lemmatization, Word2Vec training/loading, embedding utilities, and scikit-learn-to-ONNX conversion. **Files:** `requirements.txt`, `src/features/`, and `src/serving/export.py`. **Accessed:** 2026-08-20. **Terms:** record each installed package version and follow its license.

## Audit change log

| Date | Audit finding and resolution |
|---|---|
| 2026-08-20 | Dependency dry-run found `gensim==4.3.3` requires SciPy below 1.14; corrected `requirements.txt` to `scipy==1.13.1`. |
| 2026-08-20 | BERT defaults were aligned to the brief’s exact `bert-base-uncased` identifier. |
| 2026-08-20 | Added SRC-035 for optional NLP and ONNX conversion libraries discovered during dependency/source audit. |

### SRC-036 — DVC data versioning

[DVC documentation](https://dvc.org/doc), [DVC repository](https://github.com/iterative/dvc), and [DVC package metadata](https://pypi.org/project/dvc/). **Use:** `.dvc/`, `.dvcignore`, `dvc.yaml`, `params.yaml`, `requirements.txt`, and `pyproject.toml`. **Accessed:** 2026-08-20. **Terms:** DVC is open-source software; retain the package license and record the selected DVC version in reproducibility metadata.

### SRC-037 — Redis atomic Lua scripting

[Redis Lua scripting documentation](https://redis.io/docs/latest/develop/programmability/lua-api/). **Use:** atomic increment, expiry, and fixed-window decision logic in `src/serving/rate_limiter.py`, the Redis service wiring in `docker-compose.yml`, and the Phase 7 zero-trust documentation. **Accessed:** 2026-08-21. **Terms:** Redis open-source documentation and software terms apply; production operators must review the selected Redis image and deployment license. **Files:** `src/serving/rate_limiter.py`, `docker-compose.yml`, `docs/security_hardening.md`, `docs/deployment.md`, `docs/compliance_matrix.md`.

### SRC-038 — Python regex timeout-capable regular expressions

[Python `regex` package documentation and release record](https://pypi.org/project/regex/). **Use:** timeout-bounded regular-expression search, substitution, and token/statistics extraction in `src/features/text.py`. **Accessed:** 2026-08-21. **Terms:** package license and release metadata apply; the exact pinned version is recorded in `requirements.txt`. **Files:** `requirements.txt`, `src/features/text.py`, `tests/test_zero_trust.py`, `docs/security_hardening.md`.

### SRC-039 — Prometheus Python client

[Prometheus Python client documentation](https://prometheus.github.io/client_python/). **Use:** Prometheus exposition, counters, gauges, and histograms in `src/serving/app.py`. **Accessed:** 2026-08-21. **Terms:** retain the package license and pinned version recorded in `requirements.txt`. **Files:** `requirements.txt`, `src/serving/app.py`, `tests/test_day4_observability.py`, `docs/deployment.md`.

### SRC-040 — Kubernetes workload, autoscaling, and network policy APIs

[Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/), and [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/). **Use:** Kubernetes API manifests, resource/probe contracts, HPA CPU scaling, and Redis ingress isolation under `k8s/base/`. **Accessed:** 2026-08-21. **Terms:** Kubernetes documentation and API compatibility are versioned by the declared manifest validation target. **Files:** `k8s/base/`, `.github/workflows/ci.yml`, `tests/test_day4_observability.py`, `docs/deployment.md`.

### SRC-041 — kubeconform Kubernetes schema validator

[kubeconform repository and release documentation](https://github.com/yannh/kubeconform). **Use:** strict Kubernetes manifest schema validation in GitHub Actions. **Accessed:** 2026-08-21. **Version:** `v0.6.7`. **Terms:** use the pinned validator release and follow its license. **Files:** `.github/workflows/ci.yml`, `tests/test_day4_observability.py`, `docs/deployment.md`.

### SRC-042 — structlog structured logging

[structlog documentation](https://www.structlog.org/en/stable/). **Use:** machine-readable JSON logging, context variables, and standard-library logger integration in `src/config.py` and `src/serving/app.py`. **Accessed:** 2026-08-21. **Version:** `24.4.0`. **Terms:** follow the package license and retain the pinned release. **Files:** `requirements.txt`, `src/config.py`, `src/serving/app.py`, `tests/test_day4_observability.py`, `docs/security_hardening.md`.

### SRC-043 — Kubernetes Ingress API

[Kubernetes Ingress documentation](https://kubernetes.io/docs/concepts/services-networking/ingress/). **Use:** the `networking.k8s.io/v1` NGINX TLS ingress in `k8s/base/ingress.yaml`. **Accessed:** 2026-08-21. **Version:** Kubernetes API target 1.30. **Terms:** deployment requires an NGINX ingress controller, DNS, and an operator-provisioned TLS Secret. **Files:** `k8s/base/ingress.yaml`, `k8s/base/kustomization.yaml`, `tests/test_day4_observability.py`, `docs/deployment.md`.

### SRC-044 — Prometheus Operator ServiceMonitor

[Prometheus Operator API reference for ServiceMonitor](https://prometheus-operator.dev/docs/api-reference/api/). **Use:** the `monitoring.coreos.com/v1` ServiceMonitor scraping `/metrics` in `k8s/base/service-monitor.yaml`. **Accessed:** 2026-08-21. **Version:** Prometheus Operator CRD compatible with the declared cluster. **Terms:** the Prometheus Operator CRD and matching `release` selector must be installed by the cluster operator. **Files:** `k8s/base/service-monitor.yaml`, `k8s/base/kustomization.yaml`, `tests/test_day4_observability.py`, `docs/deployment.md`.

### SRC-046 — Repository status badge endpoints

GitHub repository clone endpoint: [repository.git](https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models.git). GitHub Actions workflow badge: [CI status](https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models/actions/workflows/ci.yml/badge.svg?branch=main). Static technology and license badges: [Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB) and [MIT license](https://img.shields.io/badge/License-MIT-1f6f54). **Use:** transparent visual status markers and the documented clone command in `README.md`; the underlying CI policy remains the repository workflow. **Accessed:** 2026-08-21. **Terms:** externally served visual indicators only; implementation claims are supported by repository configuration and tests, not the badges.

### SRC-047 — GitHub repository configuration and collaboration documentation

GitHub documentation for [CODEOWNERS](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [issue-form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-forms), [Dependabot options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference), [development containers](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers), [repository topics](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics), and [social previews](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview). **Use:** Deliverable 4 configuration/ownership/dev-container files, Deliverable 5 Issue Forms, and Deliverable 7 precise GitHub UI instructions. **Accessed:** 2026-08-21. **Terms:** GitHub documentation; repository settings, ownership, topic, and social-preview changes remain owner-controlled.

### SRC-048 — GitHub Actions automation and supply-chain projects

GitHub Actions and upstream projects: [actions/checkout](https://github.com/actions/checkout), [actions/upload-artifact](https://github.com/actions/upload-artifact), [GitHub CodeQL SARIF upload action](https://github.com/github/codeql-action), [actions/labeler](https://github.com/actions/labeler), [Python Semantic Release GitHub Actions documentation](https://python-semantic-release.readthedocs.io/en/latest/configuration/automatic-releases/github-actions.html), and [OpenSSF Scorecard action](https://github.com/ossf/scorecard-action). **Use:** the release, labeling, and scorecard workflows, plus CI workflow hygiene. **Accessed:** 2026-08-21. **Terms:** retain action-specific licenses and follow their current permission, pinning, and activation guidance. Semantic release remains disabled until the repository owner deliberately enables it with appropriate credentials/permissions; the labeler remains disabled until its labels and activation variable are owner-configured.

### SRC-049 — Discoverability directories and topic discovery

Potential manual, curator-controlled discovery destinations: [Awesome Fake News Detection](https://github.com/wangbing1416/Awesome-Fake-News-Detection), [Awesome Machine Learning](https://github.com/josephmisiti/awesome-machine-learning), [Awesome MLOps](https://github.com/kelvins/awesome-mlops), [Best-of ML Python](https://github.com/lukasmasuch/best-of-ml-python), and [GitHub topic discovery](https://github.com/topics/). **Use:** `github-seo-growth-strategy.md` manual review and submission checklist. **Accessed:** 2026-08-21. **Terms:** directory maintainers control eligibility and acceptance; read current contribution rules immediately before any human-authored submission. No endorsement, affiliation, or acceptance is implied.

### SRC-050 — GitHub-native private vulnerability reporting

Private advisory submission route: [Report a vulnerability](https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models/security/advisories/new). **Use:** the explicit private-reporting link in `SECURITY.md`; reports remain subject to the repository’s GitHub private vulnerability-reporting availability and access controls. **Accessed:** 2026-08-21. **Terms:** GitHub platform feature; no external security contact or response-time commitment is implied.

### SRC-051 — ClusterFuzzLite Python integration

[ClusterFuzzLite Python build integration](https://google.github.io/clusterfuzzlite/build-integration/python-lang/), [GitHub Actions execution guide](https://google.github.io/clusterfuzzlite/running-clusterfuzzlite/github-actions/), and [ClusterFuzzLite repository](https://github.com/google/clusterfuzzlite). **Use:** bounded coverage-guided Python/Atheris fuzzing of synthetic ClaimReview metadata through `.clusterfuzzlite/`, `fuzz/atheris_claimreview_fuzzer.py`, and `.github/workflows/clusterfuzzlite.yml`. **Accessed:** 2026-08-22. **Terms:** ClusterFuzzLite and Atheris licensing and usage requirements apply; the workflow fuzzes only synthetic in-memory metadata and has a 60-second fuzzer budget.

### SRC-052 — Final OpenSSF Scorecard evidence and advisory disposition

OpenSSF Scorecard [check documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md), the repository's [final Scorecard workflow run](https://github.com/tejaswin-amara/Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models/actions/runs/32565674353), and OSV advisory [PYSEC-2026-3552](https://osv.dev/PYSEC-2026-3552). **Use:** exact final SARIF evidence, supply-chain control dispositions, and the unresolved cryptography compatibility constraint in `docs/security/code-scanning-remediation.md`. **Accessed:** 2026-08-22. **Terms:** the workflow artifact is repository evidence; Scorecard and OSV results are time-sensitive and must be re-run or re-checked before making a future remediation decision.

### SRC-053 — Complete Python dependency hash locks

Python Packaging Authority [Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) and Astral [uv pip compile locking environments](https://docs.astral.sh/uv/pip/compile/). **Use:** complete Linux/Python 3.11 hash-locked dependency installation and the reviewed regeneration procedure in `requirements/locks/`, `scripts/generate_hash_locks.sh`, `docs/security/hash-lock-maintenance.md`, the container build, CI, and parser-fuzzing workflows. **Accessed:** 2026-08-23. **Terms:** follow pip and uv documentation, verify all lock diffs in protected-main pull requests, and retain complete SHA-256 coverage for every installed dependency.
