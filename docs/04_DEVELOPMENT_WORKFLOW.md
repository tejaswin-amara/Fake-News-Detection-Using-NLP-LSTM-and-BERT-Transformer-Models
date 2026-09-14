# Development Workflow

## Branch strategy

Recommended:

```text
main
├── integration/*
├── feature/*
├── experiment/*
├── docs/*
└── fix/*
```

The final deliverable should converge to a single working `main` branch.

## Repository merge sequence

1. Freeze current repositories.
2. Create an integration branch.
3. Copy the dashboard application into `frontend/`.
4. Move/retain ML code under `ml/` or `src/` using one naming convention.
5. Select one FastAPI implementation.
6. Remove the dashboard's duplicate inference path from the production flow.
7. Normalize configuration and environment variables.
8. Make model artifact loading deterministic.
9. Add integration tests.
10. Build and verify Docker Compose.
11. Merge only after the unified application runs.

## Definition of ready

A feature is ready for implementation when:

- requirement is identified;
- acceptance criterion is written;
- affected components are known;
- test strategy is known.

## Definition of done

A feature is done when:

- code is implemented;
- tests pass;
- lint/type checks pass where applicable;
- documentation is updated;
- configuration is documented;
- no placeholder behavior remains;
- generated outputs are reproducible.

## Commit convention

Use focused commits:

```text
feat: add canonical dataset adapter
feat: connect dashboard to fastapi inference
feat: add tree model comparison
fix: prevent preprocessing leakage
docs: add capstone evaluation protocol
test: add prediction integration coverage
```

## Experiment convention

Each experiment should record:

```text
experiment_id
dataset/version
features
model
hyperparameters
seed
split
metrics
artifact
notes
```
