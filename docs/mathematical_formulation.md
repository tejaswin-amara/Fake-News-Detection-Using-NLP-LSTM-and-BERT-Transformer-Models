# Mathematical Formulations

This appendix records the mathematical definitions used by the implementation. The textbook and algorithm references are listed in [`sources.md`](sources.md), especially SRC-004 through SRC-007 and SRC-021 through SRC-029.

## TF-IDF

For term `t` in document `d`, the implementation uses a sublinear term-frequency variant and inverse document frequency:

\[
\mathrm{tfidf}(t,d) = (1 + \log \mathrm{tf}(t,d)) \times \log\left(\frac{1 + N}{1 + \mathrm{df}(t)}\right) + 1,
\]

where `N` is the number of training documents and `df(t)` is the number of training documents containing `t`. The vectorizer is fit only on training text.

## Logistic regression

The binary probability is the sigmoid of a linear score:

\[
P(y=1\mid x)=\sigma(w^Tx+b)=\frac{1}{1+e^{-(w^Tx+b)}}.
\]

The binary cross-entropy objective is:

\[
\mathcal{L}(w,b)=-\frac{1}{n}\sum_{i=1}^n [y_i\log p_i+(1-y_i)\log(1-p_i)].
\]

The regularized objectives add `L1`, `L2`, or a convex ElasticNet combination:

\[
\mathcal{L}_{L1}=\mathcal{L}+\lambda\lVert w\rVert_1,\quad
\mathcal{L}_{L2}=\mathcal{L}+\frac{\lambda}{2}\lVert w\rVert_2^2,
\]

\[
\mathcal{L}_{EN}=\mathcal{L}+\lambda[\alpha\lVert w\rVert_1+(1-\alpha)\lVert w\rVert_2^2/2].
\]

## Tree splitting and Random Forests

For a node with class proportions `p_k`, Gini impurity is:

\[
G=1-\sum_k p_k^2.
\]

A split is selected by maximizing impurity reduction. Random Forests reduce estimator variance by averaging decorrelated bootstrap trees and random feature subsets; out-of-bag rows provide an internal validation estimate.

## K-Means and PCA

K-Means minimizes within-cluster squared distance:

\[
\min_{C_1,\ldots,C_K}\sum_{k=1}^K\sum_{x_i\in C_k}\lVert x_i-\mu_k\rVert_2^2.
\]

PCA selects orthogonal directions maximizing projected variance. The explained-variance ratio for component `j` is its eigenvalue divided by the sum of all retained eigenvalues.

## Classification metrics

For true positives `TP`, true negatives `TN`, false positives `FP`, and false negatives `FN`:

\[
\mathrm{accuracy}=\frac{TP+TN}{TP+TN+FP+FN},\quad
\mathrm{precision}=\frac{TP}{TP+FP},\quad
\mathrm{recall}=\frac{TP}{TP+FN},
\]

\[
F1=2\frac{\mathrm{precision}\cdot\mathrm{recall}}{\mathrm{precision}+\mathrm{recall}}.
\]

ROC-AUC summarizes ranking across false-positive thresholds; PR-AUC emphasizes positive-class precision and recall and can be more informative under imbalance.

## Calibration and Brier score

A reliability diagram groups predicted probabilities and compares mean predicted probability with empirical positive frequency. The Brier score is:

\[
\mathrm{Brier}=\frac{1}{n}\sum_{i=1}^n(p_i-y_i)^2.
\]

Platt scaling fits a logistic map over a model score; isotonic regression fits a monotonic nonparametric map. Both calibration maps are fit on validation data or cross-validation folds, never on the final test set.

## McNemar’s test

For two classifiers evaluated on identical cases, let `b` count cases correct only for model A and `c` cases correct only for model B. The continuity-corrected statistic is:

\[
\chi^2=\frac{(|b-c|-1)^2}{b+c}.
\]

The implementation reports the discordant counts and a chi-square survival-function p-value; the test compares paired predictions, not independent accuracy estimates.

## Drift

The two-sample KS statistic is the maximum absolute difference between empirical cumulative distribution functions:

\[
D_{n,m}=\sup_x|F_n(x)-G_m(x)|.
\]

PSI compares reference and current bin proportions:

\[
\mathrm{PSI}=\sum_i (p_i-q_i)\ln\left(\frac{p_i}{q_i}\right),
\]

where `p_i` and `q_i` are reference and current proportions with a small floor for empty bins.
