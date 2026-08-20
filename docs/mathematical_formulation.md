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

## Phase 2 feature-engineering contracts

For a feature value `x`, mean and median imputation replace missing values with statistics computed from the training partition only. KNN and iterative imputation likewise fit their neighbor/model parameters on training rows only. A MissingIndicator adds a binary coordinate `m_j = 1[x_j is missing]` so missingness remains observable without using held-out distributions.

Standard scaling uses `z_j = (x_j - μ_j) / σ_j`, where `μ_j` and `σ_j` are training-only statistics. Min-max scaling uses `x'_j = (x_j - min_j) / (max_j - min_j)` with training-only bounds. One-hot and ordinal encoders learn category vocabularies on training data; unknown validation/test categories follow the configured unknown-category policy.

Smoothed target encoding for category `c` uses `TE(c) = (n_c μ_c + α μ) / (n_c + α)`, where `μ_c` and `n_c` are category-specific training statistics, `μ` is the training global target mean, and `α` is the smoothing strength. Training rows receive out-of-fold estimates so their own labels do not directly determine their encoded values; validation/test rows use the full-training mapping and never their own labels.

## Phase 2 unsupervised contracts

K-Means minimizes `Σ_i ||x_i - μ_{z_i}||²`; K-Means++ initializes centroids with distance-aware sampling, while Mini-Batch K-Means approximates the same objective using batches. The elbow diagnostic records inertia as a function of `K`, and the silhouette score compares within-cluster cohesion with nearest-cluster separation.

PCA on standardized training features decomposes the covariance structure into orthogonal components. The explained-variance ratio for component `k` is `λ_k / Σ_j λ_j`; validation/test rows are projected through the fitted training scaler and PCA basis without refitting. t-SNE and UMAP coordinates are visualization-only manifold projections and are not interpreted as factual or causal representations.

DBSCAN identifies dense regions using `ε` neighborhoods and `min_samples`; points not assigned to a dense region receive the noise label `-1`. For held-out feature synthesis, the implementation assigns a row to the nearest fitted core point only when it lies within the fitted `ε`; otherwise it remains noise. Isolation Forest anomaly severity is reported as the negated `score_samples` value, so larger values indicate stronger anomaly evidence relative to the fitted training reference.

## Phase 3 supervised evaluation

For regression smoke fixtures, RMSE is `sqrt((1/n) Σ_i (y_i - ŷ_i)^2)`, MAE is `(1/n) Σ_i |y_i - ŷ_i|`, MAPE is `(100/n) Σ_i |(y_i - ŷ_i) / max(|y_i|, ε)|`, and `R² = 1 - Σ_i (y_i - ŷ_i)^2 / Σ_i (y_i - ȳ)^2`. MAPE uses a small denominator floor and is not used as a fake-news classification benchmark.

Nested stratified cross-validation partitions the available training data into outer folds. For each outer fold, an inner search fits preprocessing and model parameters only on the outer-training portion; the selected estimator is then scored once on the outer holdout. The final test split is not passed to either inner search or outer model selection.

Platt calibration fits a logistic mapping from a model score to a probability on the validation partition. Isotonic calibration fits a monotone mapping on the same permitted calibration partition. The final test set is scored only after the calibration map and threshold are frozen. Reliability diagrams compare empirical positive frequency with mean predicted probability in probability bins, and the Brier score remains `n⁻¹ Σ_i(p_i-y_i)^2`.

For paired bootstrap regression comparison, each resample draws row indices with replacement from the same paired observations for both predictors. The reported confidence interval is formed from the empirical quantiles of `metric_A - metric_B`; the random seed, metric, number of draws, and confidence level are stored with the report.

Permutation importance measures the decrease in a declared scoring function after a feature column is randomly permuted. Tree SHAP reports mean absolute local attribution values for a declared sample and is an interpretive diagnostic, not a causal explanation.
