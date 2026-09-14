# Machine Learning Methodology

## Problem formulation

This is a supervised binary text-classification problem.

Input:

```text
news article
```

Output:

```text
real / fake
```

with a probability estimate.

## Data lifecycle

```text
source
→ ingestion
→ validation
→ cleaning
→ deduplication
→ split
→ features
→ training
→ evaluation
→ packaging
→ serving
→ monitoring
```

## Feature pipeline

Primary classical representation:

```text
raw text
→ normalization
→ tokenization / cleaning
→ TF-IDF
```

The preprocessing object must be fitted only on permitted training data.

## Model progression

### M2 — Linear

- Logistic Regression
- Ridge / L1 / L2 / ElasticNet variants as applicable

### M3 — Tree

- Decision Tree
- Random Forest
- XGBoost
- LightGBM

### M4 — Unsupervised

- K-Means / K-Means++
- MiniBatch K-Means
- Hierarchical clustering
- DBSCAN
- PCA
- t-SNE
- UMAP
- Isolation Forest

### Advanced comparison

- BiLSTM
- BERT

These should be positioned as comparison models rather than the sole academic contribution.

## Model-selection philosophy

The final model should not be selected by accuracy alone.

Consider:

- F1
- PR-AUC
- ROC-AUC
- calibration
- latency
- model size
- interpretability
- operational reliability

## Limitations

The model learns patterns present in the training data. Dataset bias, source artifacts, duplicated content, temporal changes, and label quality can affect performance.
