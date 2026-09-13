# MLOps Plan

## DVC

Use DVC for datasets and reproducible pipeline inputs where appropriate.

Track:

- data version
- source metadata
- checksum
- split manifest
- pipeline stage

Do not commit secrets or unnecessarily large raw data.

## MLflow

Track:

- experiment name
- model family
- hyperparameters
- metrics
- artifacts
- seed
- dataset identifier

## Artifact registry boundary

The deployable unit should contain:

```text
preprocessing
+
model
+
metadata
+
integrity information
```

This prevents training/serving skew.

## Deployment promotion

```text
experiment
  ↓
candidate
  ↓
validated
  ↓
champion
  ↓
deployed
```

A model should not be promoted solely because it has the highest raw accuracy.

## Monitoring

Monitor:

- request rate
- inference latency
- error rate
- class distribution
- probability distribution
- feature distribution where available
- delayed performance when labels arrive
- drift indicators

## Retraining policy

Drift detection is a signal.

```text
drift
→ human review
→ investigate
→ retrain if justified
→ evaluate
→ promote
```

Do not implement autonomous promotion based solely on drift.
