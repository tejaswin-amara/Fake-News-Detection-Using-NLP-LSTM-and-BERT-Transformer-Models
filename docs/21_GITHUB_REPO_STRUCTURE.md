# Final GitHub Repository Structure

Recommended final structure:

```text
VERITAS-Fake-News-ML-Capstone/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── ml/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── evaluation/
│
├── backend/
│   ├── app/
│   └── requirements.txt
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_linear_models.ipynb
│   ├── 03_tree_models.ipynb
│   ├── 04_unsupervised_learning.ipynb
│   ├── 05_evaluation.ipynb
│   └── 06_final_comparison.ipynb
│
├── artifacts/
│   └── .gitkeep
│
├── reports/
│   ├── model_comparison.csv
│   ├── evaluation.json
│   ├── calibration.json
│   └── drift_report.json
│
├── docs/
│   ├── 00_PROJECT_MASTER_PLAN.md
│   ├── 01_PROJECT_CHARTER.md
│   ├── 02_REQUIREMENTS.md
│   ├── 03_ARCHITECTURE.md
│   ├── ...
│   └── 21_GITHUB_REPO_STRUCTURE.md
│
├── tests/
├── configs/
├── Dockerfile
├── docker-compose.yml
├── README.md
└── .env.example
```

## README priorities

The README should show, in order:

1. What VERITAS is.
2. Architecture.
3. MVP features.
4. Quick start.
5. API.
6. ML experiments.
7. Results.
8. Capstone CO mapping.
9. References.
10. Limitations.
