# Architecture Decision Record Index

## ADR-001 — One repository

**Decision:** The capstone uses one unified repository.

**Reason:** The frontend and ML pipeline are two layers of one system.

## ADR-002 — FastAPI is the inference boundary

**Decision:** The dashboard communicates with the ML system through HTTP.

**Reason:** Separates UI from model implementation and demonstrates ML engineering.

## ADR-003 — Logistic Regression is the MVP model

**Decision:** TF-IDF + Logistic Regression is the first deployed model.

**Reason:** Fast, reproducible, CPU-friendly, interpretable, and directly aligned with M2.

## ADR-004 — Classical ML is the capstone core

**Decision:** BERT/BiLSTM are comparison models, not the primary architectural narrative.

**Reason:** The course emphasizes linear models, tree models, unsupervised learning, evaluation, and ML engineering.

## ADR-005 — Drift is a signal, not automatic retraining

**Decision:** Drift detection requires human review.

**Reason:** Prevents an operational signal from becoming an uncontrolled model-promotion mechanism.

## ADR-006 — Generated evidence is authoritative

**Decision:** Metrics and plots are generated from executable experiments.

**Reason:** Avoids unsupported or fabricated claims.
