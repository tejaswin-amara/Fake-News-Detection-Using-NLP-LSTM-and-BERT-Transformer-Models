# System Architecture

## Logical architecture

```text
                         VERITAS
                            │
             ┌──────────────┴──────────────┐
             │                             │
        Frontend                        ML Platform
             │                             │
      React + TypeScript             Data / Features
             │                             │
             │ HTTP                       │
             ▼                             ▼
       FastAPI API                  Model Training
             │                             │
             ▼                             ▼
      Model Artifact                Evaluation
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                     Monitoring / Drift
```

## Runtime request flow

```text
POST /predict
    ↓
request validation
    ↓
text normalization
    ↓
packaged TF-IDF transform
    ↓
trained classifier
    ↓
probability / label
    ↓
response metadata
    ↓
dashboard rendering
```

## Training flow

```text
raw data
  ↓
validation
  ↓
canonical schema
  ↓
deduplication
  ↓
train/validation/test split
  ↓
training-only feature fit
  ↓
model fitting
  ↓
validation/model selection
  ↓
calibration
  ↓
final test evaluation
  ↓
artifact packaging
```

## Integration rule

There shall be one authoritative model-serving implementation.

The dashboard must not independently load or train a model in the final architecture.

## Component responsibilities

| Component | Responsibility |
|---|---|
| `frontend/` | UI, API calls, analytics |
| `ml/data/` | ingestion, validation, split manifests |
| `ml/features/` | text and feature transformations |
| `ml/models/` | supervised/unsupervised implementations |
| `ml/evaluation/` | metrics, CV, search, calibration |
| `backend/` / FastAPI | inference boundary and monitoring endpoints |
| `artifacts/` | generated model packages |
| `reports/` | generated evidence |
| `tests/` | regression/integration/security tests |
| `docs/` | requirements, methodology, evidence |

## Architecture principles

1. Training and serving use the same packaged preprocessing contract.
2. Test data remains untouched until final evaluation.
3. Artifacts are generated, not hand-edited.
4. Dashboard is a client of the ML API.
5. Monitoring observes the deployed model; it does not silently retrain it.
