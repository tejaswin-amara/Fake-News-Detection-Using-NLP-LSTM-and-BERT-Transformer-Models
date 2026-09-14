# 📚 VERITAS Documentation Portal

Welcome to the comprehensive documentation repository for **VERITAS** (*Verified Explainable Real-time Information Telemetry & Analytics System*), engineered to meet and exceed academic requirements for Course **25SC2107E (CO1–CO6)** and enterprise MLOps engineering standards.

---

## 🧭 Documentation Map & Quick Navigation

```
docs/
├── ADR/                                 # Architectural Decision Records
│   ├── 0001-initial-tech-stack.md       # ADR 0001: Core Technology Stack Selection
│   ├── 0006-developer-pipeline.md       # ADR 0006: Universal Pipeline Standard Adoption
│   └── 0007-production-boundary.md     # ADR 0007: Air-Gapped Serving & Deployment Boundary
├── deployment/                          # Production Deployment & Rollout Playbooks
│   ├── production-readiness.md          # Provider-Neutral Production Preflight Gates
│   └── production-rollout.md            # Zero-Downtime Blue/Green & Canary Rollout Strategy
├── references/                          # Academic Course Materials & Proofs
│   └── MachineLearninghandout.pdf       # Official KL University 25SC2107E Course Handout
├── security/                            # Enterprise Security Hardening Documentation
│   ├── api-and-observability.md         # API Ingress & Distributed Observability Security
│   ├── code-scanning-remediation.md     # CodeQL & Static Analysis Vulnerability Remediation
│   ├── hash-lock-maintenance.md         # Cryptographic SHA-256 Dependency Pinning
│   └── secret-handling.md               # Zero-Secret Git Telemetry & Redaction Controls
├── 00_PROJECT_MASTER_PLAN.md            # Comprehensive Lifecycle Plan & Timeline
├── 01_PROJECT_CHARTER.md                # System Purpose, Value Proposition & Constraints
├── 02_REQUIREMENTS.md                   # Functional, Non-Functional & SLA Specifications
├── 03_ARCHITECTURE.md                   # Detailed Architecture, Component Boundaries & Dataflow
├── 04_DEVELOPMENT_WORKFLOW.md           # Git Branching, Conventional Commits & Quality Gates
├── 05_MVP_IMPLEMENTATION_PLAN.md        # Minimum Viable Product Scope & Milestones
├── 06_ML_METHODOLOGY.md                 # Preprocessing, Vectorization & Regularization Taxonomy
├── 07_EVALUATION_PROTOCOL.md            # Cross-Validation Protocol, Brier Loss & Significance
├── 08_UNSUPERVISED_PLAN.md              # K-Means, Silhouette, Dendrograms & Anomaly Discovery
├── 09_API_SPEC.md                       # Complete OpenAPI REST Serving Specification
├── 10_DATASET_CARD.md                   # Ingestion Schemas, Partitioning & Ethics
├── 11_MODEL_CARD.md                     # Model Governance, Production Champion & Limitations
├── 12_EXPERIMENT_TRACKER_TEMPLATE.md    # MLflow Tracking Schema & Run Metrics
├── 13_TESTING_STRATEGY.md               # Polyglot Test Pyramid & 95% Coverage Gates
├── 14_DEPLOYMENT_GUIDE.md               # Rootless Docker, Compose & Kubernetes Orchestration
├── 15_MLOPS_PLAN.md                     # Automated SRE Drift Guardrails & Rollback Runbooks
├── 16_CAPSTONE_COMPLIANCE_MATRIX.md     # Line-by-Line Syllabus Traceability Matrix
├── 17_RISK_REGISTER.md                  # Failure Mode Analysis & Engineering Mitigations
├── 18_DEMO_SCRIPT.md                    # Structured Defense Script for Academic Judges
├── 19_CAPSTONE_REPORT_OUTLINE.md        # Formal Academic Publication & Report Structure
├── 20_DEVELOPER_CHECKLIST.md            # Pre-Commit, Pre-PR & Release Verification Checklists
├── 21_GITHUB_REPO_STRUCTURE.md          # Canonical Repository Directory Layout
├── 22_WEEKLY_EXECUTION_PLAN.md          # Multi-Week Sprint Roadmap & Completion Status
├── 23_SOURCE_GOVERNANCE.md              # Strict Bibliographic Provenance & License Auditing
├── 24_DECISION_LOG.md                   # Historical Engineering Decision Register
├── compliance_matrix.md                 # Primary Course Outcome Compliance Matrix (CO1–CO6)
├── current_dataset_release.md           # Ingested Dataset Versioning & Checksums
├── dataset_card.md                      # Comprehensive Dataset Documentation (WELFake, ISOT, ClaimReview)
├── dependency_licenses.md               # Complete Third-Party License Audit
├── deployment.md                        # Containerization & Kubernetes Architecture
├── developer-pipeline-adoption.md       # Universal Engineering Standards Alignment
├── mathematical_formulation.md          # Rigorous Mathematical Proofs & Theoretical Formulations
├── model_cards.md                       # Comprehensive Model Cards (8 Model Families)
├── performance-testing.md               # Latency Benchmarks, p95/p99 Profiles & Stress Testing
├── security_hardening.md                # Threat Modeling, Memory Limits & Attack Surface
├── sources.md                           # Bibliographic External Source Register (SRC-001 to SRC-053)
└── sources.yaml                         # Machine-Readable Source Provenance Database
```

---

## 🔬 Core Academic & Scientific Documentation

| Document | Description | Key Topics |
| :--- | :--- | :--- |
| **[`compliance_matrix.md`](compliance_matrix.md)** | **Primary Course Traceability Matrix** | Exhaustive mapping of Course 25SC2107E (CO1–CO6) to source code, tests, and evidence reports. |
| **[`mathematical_formulation.md`](mathematical_formulation.md)** | **Mathematical Foundations & Proofs** | Sublinear TF-IDF, L1/L2 penalties, Gini impurity, Platt scaling, KS drift statistic, and PSI. |
| **[`dataset_card.md`](dataset_card.md)** | **Dataset Governance & Ethics** | WELFake, ISOT, and ClaimReview provenance, MinHash deduplication, zero-leakage splits. |
| **[`model_cards.md`](model_cards.md)** | **Multi-Model Governance Cards** | Comprehensive governance cards across 8 model architectures including Champion specs. |
| **[`sources.md`](sources.md)** | **Formal Source Register** | Bibliographic citation, terms of use, and access dates for all 53 external resources. |
| **[`sources.yaml`](sources.yaml)** | **Machine-Readable Provenance** | Audited database checked by automated CI gates (`scripts/source_audit.py`). |

---

## ⚙️ Systems Engineering & SRE Documentation

| Document | Description | Key Topics |
| :--- | :--- | :--- |
| **[`deployment.md`](deployment.md)** | **Production Serving Architecture** | Rootless container specification, Kubernetes manifests, resource limits, and ingress. |
| **[`security_hardening.md`](security_hardening.md)** | **Zero-Trust Security Controls** | Rate limiting, memory bounds, ReDoS protection, secret scrubbing, non-root execution. |
| **[`performance-testing.md`](performance-testing.md)** | **Benchmark & Stress Profiles** | Sub-millisecond latency measurements, p95/p99 histograms, and memory stress budgets. |
| **[`developer-pipeline-adoption.md`](developer-pipeline-adoption.md)** | **Engineering Pipeline Standard** | Alignment with Awesome Dev Pipeline universal engineering standards. |
| **[`dependency_licenses.md`](dependency_licenses.md)** | **Open-Source License Audit** | License verification across all Python and Node.js dependencies. |

---

## 🏛️ Architectural Decision Records (ADRs)

Located in [`docs/ADR/`](ADR/):

- **[`ADR-0001: Initial Technology Stack Selection`](ADR/0001-initial-tech-stack.md)**: Rationale for choosing FastAPI, React 19, scikit-learn, and PyTorch for high-throughput serving.
- **[`ADR-0006: Full Developer Pipeline Adoption`](ADR/0006-full-relevant-developer-pipeline-adoption.md)**: Standardizing CI/CD, linting, typing, SAST, and automated verification.
- **[`ADR-0007: Production Deployment Boundary`](ADR/0007-production-deployment-boundary.md)**: Air-gapped model loading, signed artifact manifests, and container boundaries.

---

## 🛡️ Security & Observability Playbooks

Located in [`docs/security/`](security/):

- **[`api-and-observability.md`](security/api-and-observability.md)**: API admission control, distributed Prometheus metrics, and rate limiting.
- **[`code-scanning-remediation.md`](security/code-scanning-remediation.md)**: CodeQL alerts resolution, SAST scanning, and CVE remediations.
- **[`hash-lock-maintenance.md`](security/hash-lock-maintenance.md)**: Pinned hash-locked dependency generation and supply-chain hardening.
- **[`secret-handling.md`](security/secret-handling.md)**: Gitleaks integration, zero-secret logging, and credential management.

---

## 📋 Comprehensive Capstone Playbooks (00–24)

| File | Title | Strategic Focus |
| :--- | :--- | :--- |
| **[`00_PROJECT_MASTER_PLAN.md`](00_PROJECT_MASTER_PLAN.md)** | Master Plan | Overall vision, lifecycle phases, timeline, and delivery milestones. |
| **[`01_PROJECT_CHARTER.md`](01_PROJECT_CHARTER.md)** | Project Charter | Problem statement, stakeholder expectations, and project constraints. |
| **[`02_REQUIREMENTS.md`](02_REQUIREMENTS.md)** | Requirements | Functional requirements, performance SLAs, and quality standards. |
| **[`03_ARCHITECTURE.md`](03_ARCHITECTURE.md)** | Architecture | System boundaries, component interfaces, and serving topology. |
| **[`04_DEVELOPMENT_WORKFLOW.md`](04_DEVELOPMENT_WORKFLOW.md)** | Development Workflow | Branching strategy, commit conventions, and CI quality gates. |
| **[`05_MVP_IMPLEMENTATION_PLAN.md`](05_MVP_IMPLEMENTATION_PLAN.md)** | MVP Plan | Core MVP deliverables, minimum acceptance criteria, and demo readiness. |
| **[`06_ML_METHODOLOGY.md`](06_ML_METHODOLOGY.md)** | ML Methodology | Text cleaning, MinHash LSH, sublinear TF-IDF, model taxonomy. |
| **[`07_EVALUATION_PROTOCOL.md`](07_EVALUATION_PROTOCOL.md)** | Evaluation Protocol | 5-fold stratified CV, Platt sigmoid calibration, McNemar tests. |
| **[`08_UNSUPERVISED_PLAN.md`](08_UNSUPERVISED_PLAN.md)** | Unsupervised Plan | K-Means elbow analysis, silhouette scoring, PCA/t-SNE projections. |
| **[`09_API_SPEC.md`](09_API_SPEC.md)** | API Specification | OpenAPI 3.0 request/response schemas, error codes, and headers. |
| **[`10_DATASET_CARD.md`](10_DATASET_CARD.md)** | Dataset Card | Data collection methods, schema validation, and ethical considerations. |
| **[`11_MODEL_CARD.md`](11_MODEL_CARD.md)** | Model Card | Performance benchmarks, calibration results, and operational bounds. |
| **[`12_EXPERIMENT_TRACKER_TEMPLATE.md`](12_EXPERIMENT_TRACKER_TEMPLATE.md)** | Experiment Tracker | MLflow tracking protocol, hyperparameter logging, and metrics. |
| **[`13_TESTING_STRATEGY.md`](13_TESTING_STRATEGY.md)** | Testing Strategy | Unit tests, integration tests, contract verification, and 95% coverage. |
| **[`14_DEPLOYMENT_GUIDE.md`](14_DEPLOYMENT_GUIDE.md)** | Deployment Guide | Container builds, Docker Compose execution, and environment config. |
| **[`15_MLOPS_PLAN.md`](15_MLOPS_PLAN.md)** | MLOps Plan | Continuous drift detection, retraining signals, and rollback procedures. |
| **[`16_CAPSTONE_COMPLIANCE_MATRIX.md`](16_CAPSTONE_COMPLIANCE_MATRIX.md)** | Compliance Matrix | Course outcomes traceability with exact evidence file links. |
| **[`17_RISK_REGISTER.md`](17_RISK_REGISTER.md)** | Risk Register | Technical, operational, and ethical risk matrix with mitigations. |
| **[`18_DEMO_SCRIPT.md`](18_DEMO_SCRIPT.md)** | Demo Script | Step-by-step presentation flow for academic evaluators and judges. |
| **[`19_CAPSTONE_REPORT_OUTLINE.md`](19_CAPSTONE_REPORT_OUTLINE.md)** | Report Outline | Publication structure, methodology chapters, and results formatting. |
| **[`20_DEVELOPER_CHECKLIST.md`](20_DEVELOPER_CHECKLIST.md)** | Developer Checklist | Pre-flight validation steps before committing or opening pull requests. |
| **[`21_GITHUB_REPO_STRUCTURE.md`](21_GITHUB_REPO_STRUCTURE.md)** | Repo Structure | Canonical repository directory tree and file organization rules. |
| **[`22_WEEKLY_EXECUTION_PLAN.md`](22_WEEKLY_EXECUTION_PLAN.md)** | Weekly Plan | Execution breakdown by sprint and deliverable milestones. |
| **[`23_SOURCE_GOVERNANCE.md`](23_SOURCE_GOVERNANCE.md)** | Source Governance | Policy for external code, papers, datasets, and license attribution. |
| **[`24_DECISION_LOG.md`](24_DECISION_LOG.md)** | Decision Log | Chronological register of architectural decisions and their trade-offs. |
