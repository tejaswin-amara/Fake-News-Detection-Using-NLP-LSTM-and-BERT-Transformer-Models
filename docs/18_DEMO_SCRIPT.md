# Final Demo Script

## Demo duration

Target: 10–15 minutes for the application demonstration, with additional time for technical questions.

## 1. Introduce the problem

Explain:

- problem
- limitation of automated fake-news classification
- objective of VERITAS

## 2. Show architecture

Walk through:

```text
Dashboard
→ FastAPI
→ preprocessing
→ model
→ prediction
→ monitoring
```

## 3. Live prediction

Submit an article through the dashboard.

Show:

- predicted class
- probability
- model version
- latency

## 4. Model comparison

Show:

- Logistic Regression
- Random Forest
- XGBoost
- LightGBM
- optional BiLSTM/BERT

Explain why the champion was selected.

## 5. Explainability

Show feature importance / SHAP output.

Explain that explanation indicates model behavior, not factual truth.

## 6. Unsupervised analysis

Show:

- clustering
- PCA/UMAP
- anomaly detection

Explain what structure was discovered.

## 7. Evaluation

Show:

- confusion matrix
- F1
- PR-AUC
- calibration curve

## 8. Drift demo

First show normal distribution.

Then inject a synthetic shift.

Show:

```text
drift detected
→ monitoring result
→ human review required
```

## 9. Close with course mapping

Summarize:

```text
M1 → lifecycle
M2 → linear
M3 → trees
M4 → unsupervised
M5 → evaluation
M6 → engineering
```
