# VERITAS — Project Master Plan

## 1. Project identity

**Project:** VERITAS — End-to-End Machine Learning System for Fake News Classification, Explainability, and Drift Monitoring

**Course:** Machine Learning — 25SC2107E

**Project type:** Project-Based Learning / Capstone

**Primary objective:** Unite the existing fake-news ML repository and dashboard repository into one maintainable, runnable ML application, then extend the MVP so that the implementation demonstrates the course outcomes CO1–CO6 and Modules M1–M6.

## 2. Repository consolidation goal

Current repositories:

1. `Fake-News-Detection-Using-NLP-LSTM-and-BERT-Transformer-Models`
2. `fake-news-dashboard`

Target architecture:

```text
VERITAS/
├── frontend/             # React/TypeScript dashboard
├── ml/                   # data, features, training, evaluation
├── backend/              # FastAPI serving boundary
├── artifacts/            # generated model artifacts; normally ignored
├── data/                 # governed data; normally ignored/versioned with DVC
├── notebooks/
├── reports/
├── docs/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

The existing Python ML repository is the implementation source of truth for training, evaluation, serving, and monitoring. The existing dashboard repository is the UI source of truth.

## 3. MVP acceptance goal

The first milestone is a real end-to-end prediction loop:

```text
User
  ↓
React dashboard
  ↓ POST /predict
FastAPI
  ↓
Packaged TF-IDF + Logistic Regression model
  ↓
FAKE / REAL + probability
  ↓
Dashboard
```

MVP must include:

- one canonical dataset schema
- real training data
- leakage-safe train/validation/test split
- TF-IDF preprocessing
- Logistic Regression
- serialized model artifact
- FastAPI `/predict`
- `/health` and `/ready`
- React dashboard integration
- Docker Compose
- automated smoke tests
- reproducible startup instructions

## 4. Full capstone target

After MVP, implement:

- CO1/M1: lifecycle trace
- CO2/M2: linear model comparison
- CO3/M3: tree ensemble comparison
- CO4/M4: unsupervised analysis
- CO5/M5: rigorous evaluation, search, calibration, statistical comparison
- CO6/M6: packaging, serving, monitoring, MLflow/DVC
- optional advanced comparison using BiLSTM and BERT
- complete project documentation
- capstone report
- live demonstration

## 5. Development principle

Do not let advanced functionality block the MVP.

Build in this order:

```text
Integration
→ Working classifier
→ Dashboard integration
→ Docker
→ Linear models
→ Tree models
→ Unsupervised learning
→ Evaluation/calibration
→ Deep-learning comparison
→ MLOps/monitoring
→ Final capstone evidence
```

## 6. Definition of done

The project is considered capstone-ready only when:

- the end-to-end application runs from a clean environment;
- the final model is trained from documented data;
- no benchmark number is invented;
- train/validation/test discipline is enforced;
- the strongest model is selected using documented criteria;
- all required experiments have executable evidence;
- the production serving boundary uses the same preprocessing contract as training;
- drift monitoring can be demonstrated with an actual injected distribution shift;
- documentation maps implementation evidence to CO1–CO6;
- the final repository is understandable without the original two repositories.
