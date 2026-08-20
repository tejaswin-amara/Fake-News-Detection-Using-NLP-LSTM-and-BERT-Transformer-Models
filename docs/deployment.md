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

## Docker

The Docker image installs the pinned base requirements, copies source and configuration files, and starts Uvicorn. Dataset files, model weights, secrets, and generated artifacts should be mounted or supplied through a secure artifact store rather than baked into the image.

## Monitoring

`src/monitoring/drift.py` computes a two-sample Kolmogorov–Smirnov statistic and Population Stability Index for reference/current feature arrays. Reference arrays must be generated from an approved training/reference window. The default PSI alert threshold is 0.20 and the default KS significance threshold is 0.05; these are monitoring defaults, not universal guarantees.

Operational monitoring should also record latency, throughput, request errors, prediction volume, delayed-label performance, and label distribution. Concept drift cannot be directly measured without trustworthy delayed labels. Drift alerts produce a review signal; they do not silently retrain or replace a deployed model.

## MLflow

MLflow integration is optional and disabled by default. When enabled, `src/tracking.py` logs parameters, metrics, plots, and artifacts to the configured tracking URI. Model promotion remains a human-reviewed operation.

## Security and privacy

Do not log submitted article text by default. Apply payload size limits, authenticate the service at the deployment boundary, protect the model artifact, and restrict filesystem/network permissions. The sample local service is a teaching and project artifact, not a complete internet-facing security configuration.
