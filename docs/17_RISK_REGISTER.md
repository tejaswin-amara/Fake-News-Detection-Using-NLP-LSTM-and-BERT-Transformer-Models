# Risk Register

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Repository merge creates conflicting inference implementations | High | One FastAPI source of truth |
| R2 | Dataset unavailable or licensing unclear | High | Use governed sources and record provenance |
| R3 | Data leakage inflates metrics | Critical | Pre-split deduplication and training-only fitting |
| R4 | MVP blocked by BERT/GPU dependency | High | Logistic Regression MVP first |
| R5 | Dashboard works with fake/bootstrap predictions | High | Integration test against real artifact |
| R6 | Invented benchmark numbers | Critical | Metrics generated only by execution |
| R7 | Model is accurate but poorly calibrated | Medium | Explicit calibration experiments |
| R8 | Distribution drift after deployment | High | KS/PSI monitoring and review workflow |
| R9 | Overengineering consumes capstone time | Medium | Treat Kubernetes/security hardening as secondary |
| R10 | Documentation diverges from implementation | High | Update docs as part of each feature completion |
| R11 | Main branch protection blocks integration | Medium | Use PR-based development |
| R12 | Final project is too complex to explain in viva | Medium | Organize around M1–M6 and a single lifecycle |

## Highest-priority risks

R1, R3, R5, R6, and R12 must be controlled before final submission.
