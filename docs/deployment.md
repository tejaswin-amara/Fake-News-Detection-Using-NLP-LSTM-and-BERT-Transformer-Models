# Deployment and Operations

## Training-serving boundary

Training produces a versioned artifact containing the fitted text feature transform, estimator weights, feature schema, label mapping, seed, software metadata, and dataset provenance. Serving loads that artifact rather than reconstructing preprocessing from configuration. This is the primary defense against training-serving skew.

## Local API

Start the service after producing a native artifact:

```bash
MODEL_ARTIFACT=artifacts/models/logistic_l2.joblib \
  uvicorn src.serving.app:app --host 0.0.0.0 --port 8000
```

The endpoints are:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Readiness and artifact-load status |
| `/predict` | POST | One title/body request |
| `/predict/batch` | POST | Bounded batch of requests |

Every response exposes model name and artifact version. Responses also include `X-Process-Time-Ms` for a basic latency signal. The API validates text length and batch size through Pydantic models.

## Portable exports

The native artifact is the fallback because not every estimator or preprocessing operation is exportable to ONNX or TorchScript. `src/serving/export.py` provides ONNX export for compatible scikit-learn estimators and TorchScript tracing for compatible PyTorch modules. Every export must be compared against native predictions on a conformance fixture before deployment.

## Docker (SRC-032)

The Docker image installs the pinned base requirements, copies source and configuration files, and starts Uvicorn. Dataset files, model weights, secrets, and generated artifacts should be mounted or supplied through a secure artifact store rather than baked into the image.

## Monitoring

`src/monitoring/drift.py` computes a two-sample Kolmogorov–Smirnov statistic and Population Stability Index for reference/current feature arrays. Reference arrays must be generated from an approved training/reference window. The default PSI alert threshold is 0.20 and the default KS significance threshold is 0.05; these are monitoring defaults, not universal guarantees.

Operational monitoring should also record latency, throughput, request errors, prediction volume, delayed-label performance, and label distribution. Concept drift cannot be directly measured without trustworthy delayed labels. Drift alerts produce a review signal; they do not silently retrain or replace a deployed model.

## MLflow

MLflow integration is optional and disabled by default. When enabled, `src/tracking.py` logs parameters, metrics, plots, and artifacts to the configured tracking URI. Model promotion remains a human-reviewed operation.

## Security and privacy

Do not log submitted article text by default. Apply payload size limits, authenticate the service at the deployment boundary, protect the model artifact, and restrict filesystem/network permissions. The sample local service is a teaching and project artifact, not a complete internet-facing security configuration.

## DVC data versioning (SRC-036)

DVC metadata is initialized under `.dvc/`, while the reproducible `ingest`, `train`, and `evaluate` stages are defined in `dvc.yaml`. The default pipeline enforces the repository’s stratified 70/15/15 split through `src.data.ingestion` before any learned feature transform is fit.

```bash
python -m pip install -r requirements.txt
# Configure a user-owned remote; do not commit credentials.
dvc remote add -d storage <your-dvc-remote-url>
dvc add data/raw/isot
dvc repro
dvc status
```

Raw data and large generated artifacts remain outside ordinary Git commits. The remote URL, credentials, and dataset acquisition terms are environment-specific and must be configured by the operator.

## Local MLflow tracking

Initialize a local experiment without a hosted server, then enable tracking for training or evaluation:

```bash
python scripts/init_mlflow.py --tracking-uri mlruns --experiment-name fake-news-detection
python -m src.train --mlflow --train data/processed/train.csv --output artifacts/models/logistic_l2.joblib
python -m src.evaluate --mlflow --test data/processed/test.csv --artifact artifacts/models/logistic_l2.joblib --output reports/evaluation.json
mlflow ui --backend-store-uri mlruns
```

The default configuration keeps tracking disabled for lightweight smoke tests. When enabled, parameters, metrics, configuration, model artifacts, and evaluation reports are logged to the selected local or hosted tracking URI.

## ONNX verification and drift hook

`src.serving.export.export_onnx_sklearn` exports compatible scikit-learn models, while `tests/test_serving.py` verifies ONNX Runtime inference when `skl2onnx` and `onnxruntime` are installed. Unsupported models retain the native joblib artifact as the authoritative fallback. The FastAPI endpoint `POST /monitoring/drift` delegates to the KS/PSI monitor and accepts reference/current feature arrays for an operational drift report.
