# Accelerated Execution Plan

## Day 1 — Integration

- freeze both repositories
- create unified repository
- move frontend
- select FastAPI source
- normalize environment configuration
- remove duplicate inference authority

**Gate:** project starts.

## Day 2 — Real model

- canonical data schema
- dataset adapter
- split manifest
- TF-IDF
- Logistic Regression
- artifact creation
- `/predict`

**Gate:** real prediction returned from API.

## Day 3 — Product integration

- dashboard → API
- error/loading states
- `/health`
- `/ready`
- batch prediction
- Docker Compose

**Gate:** browser → model → browser works.

## Day 4 — MVP hardening

- integration tests
- README
- clean setup
- artifact metadata
- input validation
- smoke test

**Gate:** MVP can be reproduced from clean checkout.

## Days 5–6 — M2/M3

- linear experiments
- tree experiments
- model comparison
- explainability

## Day 7 — M4

- clustering
- reduction
- anomaly detection
- visual analysis

## Day 8 — M5

- CV
- search
- metrics
- calibration
- statistical comparison

## Day 9 — M6

- MLflow
- DVC
- packaging
- drift
- dashboard analytics

## Day 10 — Finalization

- report
- capstone matrix
- demo
- README
- cleanup
- final tests

## Hard rule

If a later-day feature is not complete, preserve the working MVP and do not destabilize the core application.
