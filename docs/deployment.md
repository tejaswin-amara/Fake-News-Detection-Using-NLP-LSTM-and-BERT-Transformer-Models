# Deployment and Operations

## End-to-end prediction trace

The production boundary is deliberately explicit:

> **HTTP payload → Pydantic validation → packaged text transformation/tokenization → native or parity-verified ONNX inference → calibrated probability/uncertainty output → response metadata and latency → probability/text/feature drift logging → non-mutating retraining signal.**

Training creates an immutable artifact containing the fitted text pipeline, estimator, label mapping, feature schema, model/config/source metadata, artifact version, calibration status, and optional confidence-interval manifest. Serving loads that artifact rather than reconstructing preprocessing from configuration. This is the primary defense against notebook-to-production training-serving skew.

## Local API and probes

Start native serving after producing a model artifact:

```bash
MODEL_ARTIFACT=artifacts/models/logistic_l2.joblib \
  SERVING_MODE=native \
  uvicorn src.serving.app:app --host 0.0.0.0 --port 8000
```

The production-compatible container supports the same command and can use Gunicorn workers:

```bash
docker build -t fake-news-api:phase4 .
docker run --rm -p 8000:8000 \
  -e MODEL_ARTIFACT=/mounted/models/logistic_l2.joblib \
  -v "$PWD/artifacts:/mounted/artifacts:ro" \
  fake-news-api:phase4
```

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Process and artifact-load diagnostics; degraded status is allowed when the artifact is absent |
| `/ready` | GET | Strict readiness probe; returns 200 only when a prediction-capable artifact is loaded |
| `/predict` | POST | One validated title/body request |
| `/predict/batch` | POST | Bounded ordered batch of requests |
| `/monitoring/drift` | POST | Numeric, prediction-probability, and text-domain drift reports plus retraining signal |

Every prediction response contains label, label name, real/fake probabilities, raw and calibrated probability fields, nullable confidence-interval bounds, model name, artifact version, calibration status, and serving mode. Every HTTP response exposes `X-Process-Time-Ms`. Confidence intervals remain `null` unless a validated uncertainty manifest is included; the service never fabricates uncertainty.

### Curl examples

```bash
curl -s http://localhost:8000/health
curl -i http://localhost:8000/ready

curl -s -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"title":"Example headline","text":"Example article body."}'

curl -s -X POST http://localhost:8000/predict/batch \
  -H 'Content-Type: application/json' \
  -d '{"requests":[{"text":"First article."},{"text":"Second article."}]}'

curl -s -X POST http://localhost:8000/monitoring/drift \
  -H 'Content-Type: application/json' \
  -d '{"reference_probabilities":[0.1,0.2,0.3,0.4],"current_probabilities":[0.8,0.9,0.9,0.95],"baseline_revision":"training-reference-v1","window_id":"2026-08-20"}'
```

Empty or whitespace-only text, oversized text, empty batches, malformed JSON, and invalid probability/reference arrays are rejected with validation errors. `/ready` returns 503 when the configured model artifact cannot be loaded.

## Native and ONNX packaging

`src/serving/export.py` creates package manifests with model name, artifact version, preprocessing revision, calibration revision, label map, runtime metadata, source IDs, and native/ONNX SHA-256 values. Native joblib packaging is authoritative when a tokenizer, vectorizer, neural layer, or custom operation cannot be represented safely by the selected converter.

Compatible sklearn/tree estimators can be exported with `export_onnx_sklearn`, executed with ONNX Runtime, and checked with `assert_onnx_parity`. Deployment acceptance requires matching output shapes and maximum absolute probability error below `1e-5` on the conformance fixture. Unsupported operations must fail explicitly or use the native fallback; the system must not claim ONNX support merely because an output file can be produced.

TorchScript/ONNX neural export remains optional and resource-dependent. BERT tokenization, dynamic padding, custom layers, and pretrained weights must be included in the model manifest when an adapter supports them. No private model weights, raw datasets, credentials, or DVC/MLflow remotes are committed.

## Configuration and runtime mounts

`.env.example` and `configs/default.yaml` define native/ONNX artifact paths, serving mode, calibration and package manifests, readiness behavior, batch/text limits, MLflow URI, drift baselines, drift thresholds, and retraining-hook policy. Baselines and model artifacts should be mounted read-only or retrieved through an approved artifact store at deployment time rather than baked into an image.

## Monitoring and drift policy

`src/monitoring/drift.py` provides:

- **KS tests** for continuous feature and text-statistic distributions, including sample counts, p-values, alpha, and drift decisions.
- **PSI** for numeric features and prediction-probability distributions, with configurable alert thresholds.
- **Text-domain monitoring** for character/token/sentence lengths, lexical diversity, punctuation, uppercase/digit ratios, readability-compatible length features, and OOV rate against the approved reference vocabulary.
- **Structured retraining signals** containing drifted features, baseline revision, window ID, reason, cooldown key, suggested action, approval requirement, and explicit `side_effects: none`.

Reference distributions must be created from an approved training/reference window and never from the final test split. Monitoring is observational: the endpoint does not train, deploy, replace, or mutate a model.

### Retraining trigger policy

A drift signal is a request for review, not an autonomous deployment action. An operator should require a minimum observation window and sample count, apply the configured cooldown/de-duplication key, review data quality and delayed labels, version the new data with DVC, run a new MLflow experiment, reproduce the train/validation/test split, rerun ONNX/native parity and serving tests, perform shadow/canary validation, obtain human approval, and retain a rollback artifact before promotion. Concept drift requires trustworthy delayed labels; feature/probability drift alone does not establish model degradation.

## Container security and operations

The multi-stage Dockerfile builds dependencies separately from the runtime image, excludes compilers from the final stage, runs as a non-root user, exposes only port 8000, and supports Uvicorn or Gunicorn/Uvicorn-worker execution. `.dockerignore` excludes raw data, processed data, DVC cache, MLflow stores, reports, notebooks, tests, secrets, model caches, and local build artifacts. Authentication, TLS, rate limiting, network policy, and secret management remain deployment-boundary responsibilities.

## Notebook-to-production remediation

The repository closes the notebook-to-production gap through train-only fitted transforms, immutable packaged artifacts, explicit validation-only calibration, final-test isolation, runtime Pydantic schemas, bounded payloads, model/version metadata, ONNX parity tests, local/CI verification, baseline-controlled monitoring, and non-mutating retraining hooks. Notebook figures are evidence artifacts; production code imports reusable package functions and never depends on notebook state.

## MLflow and DVC

MLflow remains optional and disabled by default. When enabled, training and held-out evaluation log parameters, metrics, reports, plots, model artifacts, configuration, and provenance to the configured tracking URI. DVC versions raw data and orchestrates the `ingest`, `train`, and `evaluate` stages; credentials and remote endpoints are operator-owned.

```bash
python scripts/init_mlflow.py --tracking-uri mlruns --experiment-name fake-news-detection
python -m src.train --mlflow --train data/processed/train.csv --output artifacts/models/logistic_l2.joblib
python -m src.evaluate --mlflow --test data/processed/test.csv --artifact artifacts/models/logistic_l2.joblib --output reports/evaluation/final_metrics.json
mlflow ui --backend-store-uri mlruns
```

## Phase 5 one-command lifecycle

The master runner is `scripts/run_pipeline.sh`. It resolves the repository root, enables strict shell failure behavior, validates YAML/source/DVC contracts, initializes or reuses local MLflow, runs `dvc repro`, performs a separate MLflow-backed held-out evaluation, exports ONNX when the estimator supports it and native parity is below the configured epsilon, executes the complete pytest suite, and generates the report bundle.

```bash
chmod +x scripts/run_pipeline.sh
./scripts/run_pipeline.sh
```

The runner uses `MLFLOW_TRACKING_URI`, `MLFLOW_EXPERIMENT_NAME`, `MODEL_ARTIFACT`, `TRAINING_DATA`, `ONNX_PATH`, `PACKAGE_MANIFEST`, and `REPORT_DIR` when supplied. It fails clearly if governed raw data or a configured DVC remote is unavailable. It never substitutes synthetic data for ISOT/WELFake training and never silently converts failed ONNX parity into an ONNX-verified status.

## Docker Compose orchestration

`docker-compose.yml` defines three health-aware services on an isolated bridge network:

| Service | Role | Persistent state and boundary |
|---|---|---|
| `api` | Rootless FastAPI serving image | Read-only `artifacts/` and `configs/` mounts; `/ready` healthcheck; port 8000 |
| `mlflow` | Local MLflow tracking server | Named `fake-news-detection-mlflow` volume under the appuser-owned `/app/mlflow`; port 5000 |
| `traffic` | Synthetic prediction/drift generator | No data volume; logs statuses/latency only; depends on API and MLflow health |

Start and stop the complete local stack:

```bash
cp .env.example .env
docker compose up --build
docker compose ps
curl -s http://localhost:8000/ready
curl -s http://localhost:5000/health
docker compose down
```

The traffic service invokes `/predict` at `TRAFFIC_INTERVAL_SECONDS` and `/monitoring/drift` every `TRAFFIC_DRIFT_EVERY` requests. It can be run as a finite smoke test outside Compose:

```bash
python scripts/synthetic_traffic.py \
  --base-url http://localhost:8000 \
  --interval 0 \
  --drift-every 2 \
  --max-requests 5
```

Synthetic traffic contains no user article text and does not trigger retraining, model replacement, or deployment. SIGINT/SIGTERM stops the loop cleanly.

## CI/CD gates

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`. The quality job installs the pinned requirements, validates configuration and DVC stages, runs the source audit, Ruff, compilation, starts a local MLflow server, initializes the CI experiment, and runs `python -m pytest -q`. The container job builds the rootless multi-stage image and scans it with Trivy for high and critical vulnerabilities, failing on actionable findings. Logs, reports, and image metadata are uploaded as CI artifacts without including raw data or secrets.

The workflow does not claim a full-dataset benchmark when CI lacks governed raw inputs. DVC graph validation and the deterministic fixture/integration tests remain separate from a data-dependent `dvc repro` invocation.

## MLflow report bundle

`scripts/generate_reports.py` queries only `FINISHED` MLflow runs in the selected experiment and selects the best run by the declared metric and direction. It downloads all logged artifacts recursively and writes:

- `reports/best_model_summary.json` with run ID, model name, metrics, parameters, tags, selection direction, provenance, and test-selection policy.
- Stable plot names for reliability, calibration comparison, ROC/PR, confusion, and SHAP images when the selected run logged them.
- `reports/mlflow_runs/<run_id>/` containing the downloaded source artifacts.
- `reports/report_manifest.json` containing SHA-256 checksums, run IDs, plot availability, and summary path.

A missing plot is recorded as `unavailable` with a reason; no stand-in image or fabricated metric is generated. The command fails when no finalized run contains the configured primary metric or when MLflow provenance cannot be resolved.

```bash
python scripts/generate_reports.py \
  --tracking-uri mlruns \
  --experiment-name fake-news-detection \
  --output-dir reports \
  --primary-metric pr_auc \
  --direction maximize
```

## Phase 5 acceptance evidence

The repository acceptance gate includes YAML parsing for workflow/Compose/configuration, DVC stage parsing, source-register audit, shell syntax, Ruff, compilation, the complete test suite, dependency resolution, MLflow report selection/download checks, ONNX parity checks, API/drift checks, and CI Docker build/scan. A local Docker build is environment-dependent; the authoritative image build and vulnerability scan run in GitHub Actions.
