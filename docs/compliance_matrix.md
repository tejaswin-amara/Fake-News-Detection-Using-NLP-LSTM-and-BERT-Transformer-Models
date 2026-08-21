# CO/M Module Compliance Matrix

This matrix is the project’s evidence index for the `25SC2107E` Machine Learning (`25SC2107E`) handout. **All six course outcomes and all six modules are implemented in the repository and covered by executable code, documentation, tests, or generated artifacts.** Completion means the implementation and verification gates exist; it does not permit unexecuted full-dataset benchmark claims.

| Course outcome / module | Required topics from handout | Code, automation, and configuration evidence | Documentation/report evidence | Test/evidence gate | Sources |
|---|---|---|---|---|---|
| CO1 / M1 | Problem framing; raw data lifecycle; supervised versus unsupervised learning; feature/model boundary; deployment and monitoring trace | `src/data/ingestion.py`, `src/features/`, `src/models/`, `src/evaluation/`, `src/serving/`, `src/monitoring/`, `scripts/run_pipeline.sh`, `docker-compose.yml`, `configs/default.yaml` | `README.md` lifecycle trace, `docs/dataset_card.md`, `docs/model_cards.md`, `docs/deployment.md`, `docs/mathematical_formulation.md` | Ingestion/split tests, artifact round trip, API smoke tests, CI quality gate | SRC-003, SRC-004, SRC-008, SRC-009, SRC-010 |
| CO2 / M2 | Linear regression context; ridge/lasso/ElasticNet; logistic sigmoid/softmax; scaling; missing values; categorical handling; coefficient interpretation | `src/models/classical.py`, `src/features/text.py`, `src/features/preprocessing.py`, `configs/models.yaml`, `src/train.py` | Mathematical objectives, preprocessing contracts, model-card architecture/evaluation sections | Linear/logistic, imputation, encoding, scaling, and leakage tests | SRC-004, SRC-005, SRC-006, SRC-021 |
| CO3 / M3 | Decision trees; Gini/entropy; pruning; Random Forest/OOB; boosting; XGBoost; LightGBM; importance and SHAP | `src/models/classical.py`, `configs/models.yaml`, `src/evaluation/plots.py`, `scripts/generate_reports.py` | Model cards, mathematical tree/boosting/SHAP formulations, MLflow report manifest | Tree/ensemble smoke tests and explainability output checks | SRC-005, SRC-006, SRC-022, SRC-023 |
| CO4 / M4 | K-Means++; MiniBatch; elbow/silhouette; hierarchical clustering; DBSCAN density reachability; PCA; t-SNE; UMAP; Isolation Forest; engineered cluster features | `src/models/unsupervised.py`, `src/features/unsupervised_features.py`, `configs/default.yaml` | `notebooks/02_unsupervised_analysis.ipynb`, dataset/model cards, complete mathematical appendix | Shape, determinism, linkage, projection, anomaly, feature-synthesis, and no-test-fit tests | SRC-005, SRC-006, SRC-016–SRC-020 |
| CO5 / M5 | Stratified 3-way split; stratified/nested CV; classification/regression metrics; calibration; learning/validation curves; grid/random/Bayesian search; McNemar; paired bootstrap | `src/evaluation/metrics.py`, `src/evaluation/search.py`, `src/evaluation/plots.py`, `src/train.py`, `src/evaluate.py`, `configs/evaluation.yaml` | `notebooks/03_model_evaluation.ipynb`, model card metric provenance, MLflow report bundle, mathematical appendix | Metric, nested-CV, calibration, statistical, search, plot, CLI, and held-out test controls | SRC-005, SRC-006, SRC-024–SRC-029 |
| CO6 / M6 | Training-serving boundary; native/ONNX packaging and parity; REST serving; online/batch inference; readiness; calibration metadata; drift; retraining governance; rootless containers; MLflow/DVC; CI/CD and orchestration | `src/serving/app.py`, `src/serving/predictor.py`, `src/monitoring/drift.py`, `src/serving/export.py`, `src/tracking.py`, `scripts/init_mlflow.py`, `scripts/export_onnx.py`, `scripts/generate_reports.py`, `scripts/run_pipeline.sh`, `scripts/synthetic_traffic.py`, `.dvc/`, `dvc.yaml`, `Dockerfile`, `.dockerignore`, `.env.example`, `docker-compose.yml`, `.github/workflows/ci.yml` | `docs/deployment.md`, `docs/model_cards.md`, `docs/dataset_card.md`, `README.md`, package/report manifests | API/readiness/error tests, ONNX parity `<1e-5`, KS/PSI/text/OOV tests, retraining signal, MLflow report tests, CI/DVC/YAML checks, container build/scan gates | SRC-008–SRC-010, SRC-030–SRC-036 |

## Script-to-outcome index

| Planned or implemented file | Primary outcome/module | Evidence |
|---|---|---|
| `src/data/ingestion.py` | CO1/M1 | ISOT/WELFake adapters, validation, duplicate control, stratified split manifest, provenance metadata |
| `src/features/text.py` | CO1/M1, CO2/M2 | Normalization, token processing, text statistics, readability-compatible measures, TF-IDF fit/transform |
| `src/features/embeddings.py` | CO1/M1, CO4/M4 | GloVe, Word2Vec, transformer tokenization, SBERT preparation, model provenance |
| `src/features/preprocessing.py` | CO2/M2 | Imputation, MissingIndicator, One-Hot/Ordinal/target encoding, scaling |
| `src/features/unsupervised_features.py` | CO4/M4 | K-Means/MiniBatch/DBSCAN/anomaly augmentation without test leakage |
| `src/models/unsupervised.py` | CO4/M4 | Required clustering, reduction, and anomaly methods |
| `src/models/classical.py` | CO2/M2, CO3/M3 | Regularized linear/logistic, tree/forest, XGBoost, LightGBM, permutation importance, SHAP |
| `src/models/lstm.py` | CO1/M1, CO5/M5 | GloVe-compatible BiLSTM training/inference and smoke configuration |
| `src/models/bert.py` | CO1/M1, CO5/M5 | `bert-base-uncased` fine-tuning, dynamic padding, warmup, clipping, FP16 path |
| `src/evaluation/metrics.py` | CO5/M5 | Classification/regression metrics, nested CV, calibration, McNemar, paired bootstrap |
| `src/evaluation/plots.py` | CO5/M5 | Confusion, ROC/PR, learning, validation, reliability, calibration comparison |
| `src/evaluation/search.py` | CO5/M5 | Grid, random, Bayesian, nested-search result and serialization helpers |
| `src/train.py`, `src/evaluate.py` | CO1/M1, CO5/M5, CO6/M6 | Training/search orchestration, held-out evaluation, calibration, MLflow artifact logging |
| `src/serving/app.py` | CO1/M1, CO6/M6 | `/health`, `/ready`, `/predict`, `/predict/batch`, `/monitoring/drift`, validation and metadata |
| `src/serving/predictor.py` | CO1/M1, CO6/M6 | Bound preprocessing-plus-estimator inference contract |
| `src/serving/export.py`, `scripts/export_onnx.py` | CO6/M6 | Package manifests, checksums, native fallback, ONNX Runtime parity `<1e-5` |
| `src/monitoring/drift.py` | CO6/M6 | KS/PSI feature/probability drift, text/OOV monitoring, non-mutating retraining signals |
| `src/tracking.py`, `scripts/init_mlflow.py` | CO6/M6 | Idempotent local/remote MLflow experiment and artifact tracking |
| `scripts/generate_reports.py` | CO5/M5, CO6/M6 | Finalized-run selection, real artifact downloads, stable plots, checksums, provenance manifest |
| `scripts/synthetic_traffic.py` | CO6/M6 | Configurable prediction/drift traffic, finite test mode, signal-aware shutdown |
| `scripts/run_pipeline.sh` | CO1/M1, CO5/M5, CO6/M6 | One-command validation, DVC repro, MLflow evaluation, ONNX export, tests, reports |
| `docker-compose.yml` | CO6/M6 | API, MLflow, and traffic services with healthchecks, volumes, network, and dependencies |
| `.github/workflows/ci.yml` | CO6/M6 | Pull-request/main CI, pinned install, Ruff, DVC, MLflow server, tests, build, Trivy scan |
| `Dockerfile`, `.dockerignore`, `.env.example` | CO6/M6 | Rootless multi-stage runtime, exclusion policy, deployment configuration |
| `docs/model_cards.md`, `docs/dataset_card.md` | CO1–CO6 | Provenance, metrics policy, bias, ethics, limitations, intended/out-of-scope use |
| `docs/mathematical_formulation.md` | M1–M6 | Mathematical definitions for all implemented model and monitoring families |
| `scripts/source_audit.py` | All outcomes | Source-register and URL/SRC consistency audit |

## Phase 5 completion matrix

| Phase 5 requirement | Implemented evidence | Completion status |
|---|---|---|
| Pull-request and main-branch CI | `.github/workflows/ci.yml` | Complete |
| Full pinned dependency installation and Ruff | CI `Install pinned dependencies` and `Ruff lint` steps | Complete |
| DVC pipeline validation | CI `dvc stage list`; `scripts/run_pipeline.sh` `dvc repro` | Complete |
| Local MLflow startup and initialization | CI background `mlflow server`; `scripts/init_mlflow.py` | Complete |
| Complete automated tests | CI `python -m pytest -q`; repository tests | Complete |
| Rootless image build and vulnerability scan | CI Docker build and Trivy gate; `Dockerfile` | Complete |
| FastAPI/MLflow/traffic Compose stack | `docker-compose.yml`, `scripts/synthetic_traffic.py` | Complete |
| One-command lifecycle | `scripts/run_pipeline.sh` | Complete |
| ONNX export and native parity | `scripts/export_onnx.py`, `src/serving/export.py` | Complete |
| MLflow best-run report bundle | `scripts/generate_reports.py`, `reports/report_manifest.json` contract | Complete |
| Mitchell-style model and dataset cards | `docs/model_cards.md`, `docs/dataset_card.md` | Complete |
| Full mathematical formulation | `docs/mathematical_formulation.md` | Complete |
| Source governance | `docs/sources.md`, `docs/sources.yaml`, `scripts/source_audit.py` | Complete |
| No fabricated metrics or autonomous retraining | Model/dataset cards, deployment policy, signal-only implementation | Complete |

## Completion and truthfulness rule

A row is complete only when its code path, documentation path, and executable test or generated evidence artifact are present. A source citation alone is not implementation evidence, and implementation without a source-to-file mapping is not source-governed. A dynamic metric is reportable only when it comes from an executed artifact; unavailable full-data results remain explicitly unavailable rather than being represented by an unexecuted stand-in or invented benchmark.

## Deep Audit and Hardening completion

| Hardening requirement | Implementation evidence | Verification evidence | Status |
|---|---|---|---|
| Strict typing and static quality | `pyproject.toml` mypy configuration; typed serving, predictor, drift, tracking, and automation boundaries | Mypy CI gate, Ruff, compilation | Complete |
| Strict API payload validation | `src/serving/app.py` strict Pydantic models, control-character rejection, finite-value and pair validation | `tests/test_security_hardening.py` adversarial payload tests | Complete |
| CORS and rate limiting | `src/serving/app.py` deny-by-default CORS and bounded thread-safe `RateLimiter` | CORS, wildcard-credentials, retry-after, eviction tests | Complete |
| ONNX execution hardening | `src/serving/predictor.py` provider/thread/session configuration and finite matrix checks | ONNX parity and invalid-configuration tests | Complete |
| Drift numerical stability | `src/monitoring/drift.py` finite filtering, constant-distribution handling, safe PSI, bounded text monitoring | Equal/different constants, non-finite rejection, JSON-safe output tests | Complete |
| MLflow/DVC resilience | `src/tracking.py`, `scripts/init_mlflow.py`, `scripts/run_pipeline.sh` retry/fallback/cache validation | Mocked MLflow fallback and shell/DVC contract tests | Complete |
| Rootless/read-only runtime | `Dockerfile`, `docker-compose.yml`, `.dockerignore` | Compose security assertions, CI non-root image assertion, Trivy | Complete |
| SAST and dependency security | `.github/workflows/ci.yml` Bandit and pip-audit gates | CI reports and failure-on-findings policy | Complete |
| Security governance | `docs/security_hardening.md`, source register, deployment/runbook updates | Source audit and documentation tests | Complete |

The hardening controls are engineering safeguards rather than a security certification. The local in-process limiter is explicitly not a distributed rate-limit guarantee, and Docker/vulnerability-scan evidence is authoritative only when the GitHub Actions container job executes.

## Attached audit remediation closure matrix

| Audit ID | Remediation evidence | Verification | Status |
|---|---|---|---|
| C-1 | `src/train.py` dispatches classical, unsupervised, BiLSTM, and BERT paths; `dvc.yaml` routes the configured model name and includes all path dependencies | Compile/import checks and model-path contract tests; full deep training requires governed data and pretrained assets | Complete |
| C-2 | `src/train.py` loads `configs/models.yaml` and `configs/evaluation.yaml`; configured search type, folds, scoring, iterations, and model grids are applied | Phase 5 pipeline contract and search tests | Complete |
| C-3 | `src/data/ingestion.py` strips publication datelines/bylines and applies deterministic MinHash/LSH plus Jaccard near-duplicate filtering before splitting | Ingestion regression tests; dataset-card artifact-leakage policy | Complete |
| C-4 | `.github/workflows/ci.yml` runs `pip-audit` through `scripts/gate_on_severity.py` with a blocking explicit High/Critical gate | Workflow YAML contract and gate-unit behavior | Complete |
| C-5 | `src/serving/export.py` requires a trusted SHA-256 before `joblib.load`; `src/serving/app.py` reads the digest from environment or package manifest | Artifact integrity tests | Complete |
| H-1 | `src/models/lstm.py` sets Adam `clipnorm=1.0` | Source and compile checks | Complete |
| H-2 | `src/monitoring/drift.py` applies Benjamini–Hochberg correction to numeric and text KS families | API drift response and correction metadata tests | Complete |
| H-3 | `src/serving/app.py` rejects `WEB_CONCURRENCY>1` without `DISTRIBUTED_RATE_LIMITER` | Startup assertion test and deployment scaling matrix | Complete |
| H-4 | CI uses `docker/build-push-action@v6` with `type=gha` cache | Workflow contract; runner executes the authoritative image build | Complete |
| H-5 | `src/models/bert.py` resolves fp16 from CUDA availability | CPU-safe configuration implementation | Complete |
| H-6 | `src/models/bert.py` uses `eval_strategy="epoch"` | Source check and BERT configuration path | Complete |
| M-1 | `TfidfTextPipeline.fit` reports fold size, token count, and pruning settings on empty vocabulary | Diagnostic exception test | Complete |
| M-2 | `PredictionResponse.low_signal` is set after transform/request signal checks | Punctuation-only API test | Complete |
| M-3 | `tests/test_serving_stress.py` exercises a 200,000-feature sparse matrix at batch size 64 and writes RSS evidence | `reports/serving_stress_memory.json`; local observed delta approximately 1.1 MB | Complete |
| M-4 | `compute_scale_pos_weight` uses training labels; XGBoost receives the ratio and LightGBM receives `is_unbalance=True` | Factory and training-path checks | Complete |
| M-5 | `split.near_duplicate_check` and threshold are read by ingestion and recorded in the split manifest | YAML and ingestion tests | Complete |
| L-1 | Grid, random, and Bayesian search accept and propagate `n_jobs` | Search signature and configured training path | Complete |
| L-2 | Dataset, model, mathematical, deployment, and security documents state intended use, limitations, integrity risks, and evidence boundaries | Documentation/source audit | Complete |
| L-3 | `docs/deployment.md` specifies Uvicorn/Gunicorn worker, replica, CPU, ONNX-thread, and distributed-limiter relationships | Deployment scaling table | Complete |

The matrix distinguishes implementation closure from benchmark availability. No full-data metric is claimed unless the governed ISOT/WELFake lifecycle has actually executed with the required raw data and pretrained assets.

## Phase 7 EX-01–EX-15 zero-trust closure matrix

The following controls close the Phase 7 extreme-scale, air-gapped, and zero-trust serving requirements. They are implementation claims backed by repository tests and configuration contracts; production load, image, and vulnerability evidence remains authoritative when the corresponding CI or deployment runner executes.

| EX ID | Requirement | Implementation evidence | Verification evidence | Status |
|---|---|---|---|---|
| EX-01 | Bounded streaming MinHash/LSH near-duplicate detection with no all-pairs matrix | `src/features/minhash.py`; `src/data/ingestion.py` | `tests/test_ingestion.py`; `tests/test_zero_trust.py` near-duplicate test | Complete |
| EX-02 | Sparse TF-IDF must not be densified at the ONNX boundary | `src/serving/export.py`; `src/serving/predictor.py` | Sparse export/runtime rejection tests; 200,000-feature stress test | Complete |
| EX-03 | Sparse unsupervised representations use bounded TruncatedSVD | `src/models/unsupervised.py`; `src/features/unsupervised_features.py` | Phase 2 dimensionality and schema tests | Complete |
| EX-04 | DBSCAN is blocked for online feature augmentation | `UnsupervisedFeatureAugmenter(online=True)` guard | `tests/test_zero_trust.py` online DBSCAN guard | Complete |
| EX-05 | Air-gapped BERT loading uses local files only | `src/models/bert.py`, `validate_offline_bundle`, offline environment flags | `tests/test_zero_trust.py` valid/missing bundle tests | Complete |
| EX-06 | BERT bundle requires model configuration, vocabulary, and safetensors | `config.json`, `vocab.txt`, `model.safetensors` validation | Offline bundle validation regression test | Complete |
| EX-07 | Signed native artifacts use Ed25519 manifest verification | `src/serving/export.py`; canonical manifest bytes; `REQUIRE_SIGNED_ARTIFACT` | Valid signature and digest-mismatch tests | Complete |
| EX-08 | Artifact integrity fails closed before native deserialization | `load_verified_native_artifact()` and SHA-256 manifest checks | Existing artifact-integrity tests and signed-manifest tests | Complete |
| EX-09 | Distributed multi-worker limiting uses atomic Redis Lua fixed windows | `src/serving/rate_limiter.py`; Compose Redis service | Mocked Redis `eval` contract; startup multi-worker assertion | Complete |
| EX-10 | Inference concurrency is explicitly budgeted | `asyncio.Semaphore(MAX_INFLIGHT_INFERENCE)` and threadpool inference | Exhausted-budget `429` test | Complete |
| EX-11 | Drift monitoring is asynchronous and bounded | `src/monitoring/jobs.py`; `DRIFT_QUEUE_MAXSIZE`; worker and TTL controls | `202` enqueue plus status polling tests | Complete |
| EX-12 | Drift results have bounded lifecycle states and no autonomous retraining | Job TTL/status states; signal-only retraining hook | Drift completion and human-approval assertions | Complete |
| EX-13 | Container base image is immutable and runtime is rootless | Digest-pinned multi-stage `Dockerfile`; non-root `appuser`; Compose read-only controls | Dockerfile/Compose contract tests and CI image assertion | Complete |
| EX-14 | Runtime configuration exposes all zero-trust controls without secrets | `.env.example`; `configs/default.yaml`; read-only mounts | YAML/Compose parsing and source/config validation gates | Complete |
| EX-15 | Phase 7 evidence is traceable to the handout and repository sources | This matrix; `docs/security_hardening.md`; `docs/deployment.md`; README; source register | `scripts/source_audit.py`, full test/lint/type/compile gates | Complete |

These EX controls extend, rather than replace, the CO1–CO6 and M1–M6 matrix above. No row authorizes fabricated full-data metrics, test-set leakage, unreviewed retraining, or a claim that a local fixture is a production benchmark.

## Completion and truthfulness rule

A row is complete only when its code path, documentation path, and executable test or generated evidence artifact are present. A source citation alone is not implementation evidence, and implementation without a source-to-file mapping is not source-governed. A dynamic metric is reportable only when it comes from an executed artifact; unavailable full-data results remain explicitly unavailable rather than being represented by an unexecuted stand-in or invented benchmark.

[1]: https://scikit-learn.org/stable/modules/clustering.html "scikit-learn clustering documentation"
[2]: https://onnxruntime.ai/docs/ "ONNX Runtime documentation"
[3]: https://huggingface.co/docs/transformers/index "Hugging Face Transformers documentation"
[4]: https://redis.io/docs/latest/develop/programmability/lua-api/ "Redis Lua scripting documentation"
[5]: https://docs.docker.com/reference/dockerfile/ "Dockerfile reference"

## Day 3 vulnerability closure matrix

| Day 3 ID | Vulnerability/control | Implementation evidence | Verification evidence | Status |
|---|---|---|---|---|
| EX-16 | Drift queue exhaustion is an overload condition with retryable admission control | `src/monitoring/jobs.py` raises `OverflowError` on bounded admission failure; `src/serving/app.py` returns HTTP 429 and `Retry-After: 5` | `tests/test_zero_trust.py` queue saturation and endpoint 429 tests | Complete |
| EX-17 | Python allocator fragmentation is mitigated in the runtime image | `Dockerfile` runtime stage installs `libjemalloc2` and sets the immutable preload path | `tests/test_zero_trust.py` Dockerfile contract; CI container build remains authoritative | Complete |
| EX-18 | Redis SSRF/network exposure and unauthenticated access are reduced | `docker-compose.yml` requires `REDIS_PASSWORD`, uses `--requirepass`, authenticated `REDIS_URL`, and isolated `redis-internal` network | Compose topology/authentication contract tests and source/config audits | Complete |
| EX-19 | Regex denial of service is bounded and fail-safe | `requirements.txt` pins `regex==2024.11.6`; `src/features/text.py` caps input at 50,000 characters and regex execution at 0.050 seconds | Bounded-input, timeout-fallback, cleaning, tokenization, and statistics tests | Complete |

The Day 3 controls extend the Phase 7 matrix and retain the project’s core truthfulness rules: no test-set leakage, no fabricated metrics, no autonomous retraining, no committed runtime secrets, and no claim that static container contracts replace CI image execution.

## Day 4 cloud-native closure matrix

| Day 4 ID | Operational requirement | Implementation evidence | Verification evidence | Status |
|---|---|---|---|---|
| EX-20 | Time-series visibility for HTTP latency, inference latency, queue depth, rejections, and drift failures | `src/serving/app.py` Prometheus metrics and `/metrics` endpoint; `requirements.txt` | `tests/test_day4_observability.py` metrics exposition/rejection assertions | Complete |
| EX-21 | Metrics have bounded cardinality and remain available during overload | Normalized route labels; `/metrics` exempt from request limiter; no user/job/request labels | Metrics endpoint test under rate-limit exhaustion | Complete |
| EX-22 | ONNX/native cold-start warm-up before readiness | `src/serving/predictor.py:warmup_text_model`; serving lifespan warm-up gate; health/readiness diagnostics | Successful and failed warm-up tests | Complete |
| EX-23 | Kubernetes API deployment with cloud resource/security/probe parity | `k8s/base/api-deployment.yaml` | Manifest contract tests; kubeconform CI gate | Complete |
| EX-24 | CPU-based HPA at 75% with bounded replicas | `k8s/base/api-hpa.yaml` | HPA target and bounds assertions; kubeconform CI gate | Complete |
| EX-25 | Authenticated Redis orchestration with persistent data | `k8s/base/redis-deployment.yaml` references external Secret and requires password | Redis manifest contract; kubeconform CI gate | Complete |
| EX-26 | Redis ingress restricted to API pods | `k8s/base/networkpolicy.yaml` with API-only TCP 6379 ingress and DNS-only Redis egress | NetworkPolicy selector/port assertions; cluster CNI remains an operational prerequisite | Complete |
| EX-27 | Kubernetes manifest schema validation is blocking in CI | `.github/workflows/ci.yml` pinned `ghcr.io/yannh/kubeconform:v0.6.7`, strict Kubernetes 1.30 validation | Workflow contract test and CI execution | Complete |

Day 4 extends the Phase 7 zero-trust matrix. It does not claim that a static manifest replaces cluster-specific admission, CNI enforcement, metrics-server availability, secret provisioning, artifact PVC population, or production load testing.
