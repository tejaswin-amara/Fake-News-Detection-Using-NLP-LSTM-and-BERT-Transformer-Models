# MVP Implementation Plan

## Goal

Produce a working application before adding advanced capstone requirements.

## Phase 1 — Repository integration

Deliverables:

- unified directory structure
- one frontend
- one ML API
- one configuration strategy
- no duplicate inference source of truth

Acceptance:

```bash
docker compose up --build
```

starts the dashboard and API.

## Phase 2 — Canonical data pipeline

Implement:

```text
raw dataset
→ validate
→ normalize
→ deduplicate
→ split
```

Canonical supervised columns:

```text
id
title
content
label
source
```

Default label convention:

```text
0 = real
1 = fake
```

Record any source-specific inversion in ingestion metadata.

## Phase 3 — MVP model

Implement:

```text
TF-IDF + Logistic Regression
```

Training artifact:

```text
artifacts/models/logistic_l2.joblib
```

## Phase 4 — API

Required:

```text
GET  /health
GET  /ready
POST /predict
POST /predict/batch
```

Example response:

```json
{
  "prediction": "fake",
  "probability_fake": 0.82,
  "probability_real": 0.18,
  "model_name": "logistic_l2",
  "artifact_version": "..."
}
```

Numbers must come from the actual artifact.

## Phase 5 — Dashboard integration

Dashboard requirements:

- text input
- prediction result
- probability
- model/version information
- loading state
- validation errors
- API failure state

## Phase 6 — MVP verification

Must pass:

```bash
pytest
pnpm check
pnpm test
pnpm build
docker compose up --build
```

## MVP release criterion

A fresh developer can clone the unified repository, follow the README, start the system, submit text, and receive a real prediction without manually modifying source code.
