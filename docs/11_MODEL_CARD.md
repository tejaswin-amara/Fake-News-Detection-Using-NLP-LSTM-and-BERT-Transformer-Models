# Model Card

## Model family

The capstone evaluates multiple model families. The deployed MVP begins with:

**TF-IDF + Logistic Regression**

The final champion model may differ after evaluation.

## Intended use

- educational demonstration
- research experimentation
- article triage
- ML lifecycle demonstration

## Out-of-scope use

Do not use the model as the sole basis for:

- legal decisions
- medical decisions
- financial decisions
- public-safety decisions
- censorship or punitive action

## Inputs

- news headline
- article text

## Outputs

- predicted class
- probability estimate
- model and artifact metadata

## Evaluation

The model card shall be updated from executed experiments only.

Required final fields:

```text
dataset/version
train/validation/test split
model configuration
F1
precision
recall
ROC-AUC
PR-AUC
Brier score
latency
artifact version
```

## Fairness and robustness considerations

Evaluate where possible:

- source imbalance
- temporal drift
- topic imbalance
- article-length effects
- duplicate/source leakage

## Limitations

A high probability is not proof of truth or falsehood. Model behavior depends on the training distribution and preprocessing pipeline.
