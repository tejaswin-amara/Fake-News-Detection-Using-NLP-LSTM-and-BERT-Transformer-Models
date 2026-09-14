# Project Charter

## Project title

**VERITAS: An End-to-End Machine Learning System for Fake News Classification, Explainability, and Drift Monitoring**

## Problem statement

Online news content is produced at high volume, creating a need for automated classification systems that can help analysts prioritize potentially unreliable content. The project develops a machine-learning system that classifies news text according to learned dataset labels and exposes the result through a web application.

The system is a classifier, not an autonomous fact-checking engine. A prediction represents a learned association with the training labels and must not be treated as definitive evidence of truth.

## Objectives

1. Build a reproducible data-to-model pipeline.
2. Compare classical supervised ML models.
3. Apply unsupervised learning to discover structure in news representations.
4. Evaluate models using leakage-safe methodology.
5. Calibrate prediction probabilities.
6. Package and serve a selected model through FastAPI.
7. Expose operational information through a dashboard.
8. Detect distribution drift.
9. Produce evidence aligned with CO1–CO6.

## Success criteria

### MVP

A user can submit article text in the dashboard and receive a real prediction from a trained model.

### Capstone

The system demonstrates the full ML lifecycle and contains traceable implementation, experiment, evaluation, and deployment evidence.

## Out of scope

- Autonomous fact verification
- Legal, medical, financial, or public-safety decision making
- Automatic retraining without human review
- Claims of production accuracy beyond executed experiments
- Uncontrolled web scraping as the core truth source

## Primary research question

How do classical machine-learning models compare with deep-learning approaches for fake-news classification under leakage-safe evaluation, probability calibration, and production-oriented deployment constraints?

## Secondary questions

- How does regularization affect TF-IDF Logistic Regression?
- Do tree ensembles outperform the best linear model?
- Can unsupervised structure provide useful analytical or feature-engineering signals?
- Does BERT materially outperform the best classical model?
- Which model offers the best performance/latency/interpretability trade-off?
- How does the serving system behave under distribution drift?
