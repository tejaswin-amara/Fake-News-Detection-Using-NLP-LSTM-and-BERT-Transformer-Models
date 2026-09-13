# Mathematical Formulation

This appendix defines the mathematical objects implemented in the repository. It distinguishes general mathematical definitions from implementation choices such as train-only fitting, finite precision, solver settings, and artifact contracts. The source register maps the underlying algorithms and frameworks to SRC-004–SRC-029, SRC-031, SRC-033, and SRC-034.

## 1. Data, labels, and split discipline — CO1/M1 and CO5/M5

Let the canonical dataset be

\[
\mathcal D = \{(x_i, y_i)\}_{i=1}^{n}, \qquad y_i \in \{0,1\},
\]

where `0` means real and `1` means fake. The ingestion protocol creates disjoint stratified sets

\[
\mathcal D = \mathcal D_{train} \dot\cup \mathcal D_{val} \dot\cup \mathcal D_{test},
\qquad (|D_{train}|,|D_{val}|,|D_{test}|) \approx (0.70n,0.15n,0.15n).
\]

For every learned transform \(T\),

\[
T \leftarrow \operatorname{fit}(\mathcal D_{train}) \quad\text{or}\quad
T \leftarrow \operatorname{fit}(\mathcal D_{train}\cup\mathcal D_{val})
\]

only when the declared evaluation stage permits it. The final test rows are not used for model selection, threshold selection, calibration fitting, vocabulary fitting, clustering, anomaly fitting, or preprocessing parameter estimation.

## 2. Text normalization and TF-IDF — CO1/M1 and CO2/M2

After Unicode and whitespace normalization, let \(t_{i,j}\) denote token \(j\) in document \(i\). The term frequency is

\[
\operatorname{tf}(t,d) = \frac{\#(t\text{ in }d)}{\sum_{u}\#(u\text{ in }d)}.
\]

With document frequency \(df(t)\), number of documents \(N\), and optional sublinear scaling,

\[
\operatorname{tf}_{sub}(t,d) = 1 + \log(\#(t\text{ in }d)) \quad\text{if the count is positive},
\]

and the inverse document frequency is

\[
\operatorname{idf}(t) = \log\left(\frac{1+N}{1+df(t)}\right)+1.
\]

The TF-IDF coordinate is

\[
v_{d,t} = \operatorname{tf}(t,d)\operatorname{idf}(t),
\]

followed by optional \(\ell_2\) normalization \(\hat v_d=v_d/\|v_d\|_2\). The vocabulary is pruned using train-fitted `min_df`, `max_df`, and `max_features` rules. Validation/test text is transformed with the frozen vocabulary and IDF values.

Text-statistic features include token count, character count, sentence count, lexical diversity, punctuation ratio, uppercase ratio, digit ratio, and length-derived readability-compatible measures. These descriptive features do not themselves establish factuality.

## 3. Missing values, encoders, and scaling — CO2/M2

For a numeric feature \(x_j\), mean and median imputation are

\[
\tilde x_{ij}=\begin{cases}
 x_{ij},&x_{ij}\text{ observed},\\
 \mu_j=\frac{1}{|I_j|}\sum_{i\in I_j}x_{ij},&\text{mean},\\
 \operatorname{median}(\{x_{ij}:i\in I_j\}),&\text{median}.
\end{cases}
\]

A missingness indicator is \(m_{ij}=1\) when the original value is missing and 0 otherwise. KNN/model-based imputers estimate the missing value from a train-fitted neighborhood or predictive model.

For a categorical value \(c\), one-hot encoding is \(\mathbf 1[c=k]\); ordinal encoding maps categories to an ordered integer; target encoding uses a smoothed training estimate

\[
TE(c)=\frac{n_c\bar y_c+\lambda\bar y}{n_c+\lambda},
\]

where \(n_c\) and \(\bar y_c\) are category count and target mean, \(\bar y\) is the global training mean, and \(\lambda>0\) controls shrinkage. Out-of-fold target estimates prevent a row from using its own target directly.

Standard scaling is

\[
z_{ij}=\frac{x_{ij}-\mu_j}{\sigma_j},
\]

and min-max scaling is

\[
x'_{ij}=\frac{x_{ij}-\min_j}{\max_j-\min_j}.
\]

All statistics are estimated on the permitted fit split only.

## 4. Linear and logistic models — CO2/M2

For a linear prediction \(\hat y=X\beta+b\), ridge, lasso, and elastic-net objectives are respectively

\[
\min_{\beta,b}\frac{1}{2n}\|y-X\beta-b\mathbf1\|_2^2+\lambda\|\beta\|_2^2,
\]

\[
\min_{\beta,b}\frac{1}{2n}\|y-X\beta-b\mathbf1\|_2^2+\lambda\|\beta\|_1,
\]

and

\[
\min_{\beta,b}\frac{1}{2n}\|y-X\beta-b\mathbf1\|_2^2+\lambda\left[\rho\|\beta\|_1+(1-\rho)\|\beta\|_2^2\right].
\]

For binary logistic regression,

\[
z_i=x_i^T\beta+b, \qquad p_i=P(y_i=1\mid x_i)=\sigma(z_i)=\frac{1}{1+e^{-z_i}},
\]

with negative log-likelihood

\[
\mathcal L(\beta,b)=-\frac1n\sum_i \left[y_i\log p_i+(1-y_i)\log(1-p_i)\right].
\]

The regularized objective is \(\mathcal L+\lambda\|\beta\|_1\), \(\mathcal L+\lambda\|\beta\|_2^2\), or the elastic-net combination above. Multinomial logistic regression uses softmax

\[
P(y_i=k\mid x_i)=\frac{e^{x_i^T\beta_k+b_k}}{\sum_{r=1}^{K}e^{x_i^T\beta_r+b_r}}.
\]

## 5. Trees, Random Forest, boosting, permutation importance, and SHAP — CO3/M3

For a node with class proportions \(p_k\), Gini impurity and entropy are

\[
G=1-\sum_k p_k^2, \qquad H=-\sum_k p_k\log p_k.
\]

A split is selected by impurity reduction, and cost-complexity pruning minimizes

\[
R_\alpha(T)=R(T)+\alpha|\widetilde T|,
\]

where \(R(T)\) is empirical tree error and \(|\widetilde T|\) is the number of leaves. A Random Forest averages bootstrapped tree predictors:

\[
\hat f_{RF}(x)=\frac1B\sum_{b=1}^{B}\hat f_b(x),
\]

while OOB observations estimate error using trees whose bootstrap samples omitted the observation.

Gradient boosting builds

\[
F_M(x)=F_0(x)+\sum_{m=1}^{M}\eta h_m(x),
\]

where \(h_m\) approximates the negative gradient of the loss at iteration \(m\). XGBoost adds regularization over tree leaves and split complexity; LightGBM grows leaves according to gain under its configured leaf-wise constraints. Exact implementation parameters are recorded in `configs/models.yaml` and artifacts.

Permutation importance for feature \(j\) is the score decrease

\[
I_j=S(X,y)-S(\pi_j(X),y),
\]

where \(\pi_j\) randomly permutes feature \(j\) on a declared evaluation partition. SHAP values \(\phi_j\) satisfy the additive explanation

\[
f(x)=\phi_0+\sum_{j=1}^{p}\phi_j,
\]

with Shapley values computed from marginal contributions across feature coalitions. They describe model behavior, not causal effects.

## 6. BiLSTM — CO3/M3 and CO5/M5

For input embedding \(x_t\), previous hidden state \(h_{t-1}\), and previous cell state \(c_{t-1}\), an LSTM computes

\[
f_t=\sigma(W_f x_t+U_f h_{t-1}+b_f),
\]
\[
i_t=\sigma(W_i x_t+U_i h_{t-1}+b_i),
\]
\[
\tilde c_t=\tanh(W_c x_t+U_c h_{t-1}+b_c),
\]
\[
c_t=f_t\odot c_{t-1}+i_t\odot\tilde c_t,
\]
\[
o_t=\sigma(W_o x_t+U_o h_{t-1}+b_o),
\]
\[
h_t=o_t\odot\tanh(c_t).
\]

A bidirectional LSTM computes forward and reverse states and concatenates them:

\[
h_t^{bi}=[h_t^{\rightarrow};h_t^{\leftarrow}].
\]

A binary classification head may use \(p=\sigma(w^Th+b)\). GloVe initialization supplies a trainable or frozen embedding matrix according to configuration; the pretrained revision and checksum belong in the artifact provenance.

## 7. BERT self-attention — CO3/M3 and CO5/M5

The supported transformer identifier is **`bert-base-uncased`**. For token position \(i\), the input representation is the sum of token, position, and segment embeddings:

\[
h_i^0=e_i^{token}+e_i^{position}+e_i^{segment}.
\]

For one attention head,

\[
Q=HW_Q,\qquad K=HW_K,\qquad V=HW_V,
\]

and scaled dot-product attention is

\[
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V,
\]

where mask \(M\) suppresses padding or disallowed positions. Multi-head attention is

\[
\operatorname{MultiHead}(H)=\operatorname{Concat}(head_1,\ldots,head_h)W_O.
\]

A transformer block applies residual connections and layer normalization around attention and the position-wise feed-forward network:

\[
U=\operatorname{LayerNorm}(H+\operatorname{MultiHead}(H)),
\]
\[
\operatorname{FFN}(U)=\phi(UW_1+b_1)W_2+b_2,
\]
\[
H'=\operatorname{LayerNorm}(U+\operatorname{FFN}(U)).
\]

A classification head uses the pooled `[CLS]` representation \(h_{CLS}\), for example \(p=\sigma(w^Th_{CLS}+b)\). Tokenizer revision, maximum sequence length, optimizer, warmup, clipping, precision, hardware, and checkpoint are required provenance fields.

## 8. K-Means, hierarchical clustering, DBSCAN, PCA, t-SNE, UMAP, and Isolation Forest — CO4/M4

K-Means minimizes within-cluster squared distance:

\[
\min_{\{C_k,\mu_k\}_{k=1}^{K}}\sum_{k=1}^{K}\sum_{x_i\in C_k}\|x_i-\mu_k\|_2^2,
\qquad \mu_k=\frac1{|C_k|}\sum_{x_i\in C_k}x_i.
\]

K-Means++ selects initial centers with probability proportional to squared distance from the nearest existing center. MiniBatch K-Means approximates the same objective using small batches. Elbow analysis compares inertia and silhouette analysis compares within/between-cluster separation.

Agglomerative clustering starts from singleton clusters and repeatedly merges the closest pair under single, complete, average, or Ward linkage. Ward merging minimizes the increase in within-cluster sum of squares.

For DBSCAN with radius \(\varepsilon\) and minimum count `min_samples`, define

\[
N_\varepsilon(p)=\{q:d(p,q)\le\varepsilon\}.
\]

A point is core when \(|N_\varepsilon(p)|\ge\text{min\_samples}\). Point \(q\) is directly density-reachable from core point \(p\) when \(q\in N_\varepsilon(p)\). Density reachability is the transitive closure of direct reachability through core points. A cluster is a maximal density-connected set; points not assigned to a cluster are noise/outliers.

PCA centers \(X\), computes covariance \(S=X^TX/(n-1)\), and solves

\[
Sv_j=\lambda_jv_j,
\qquad \lambda_1\ge\cdots\ge\lambda_p.
\]

The projection onto the first \(r\) components is \(Z=XV_r\), and explained-variance ratio is \(\lambda_j/\sum_k\lambda_k\). t-SNE constructs a low-dimensional embedding by minimizing a KL divergence between high-dimensional and low-dimensional neighborhood probabilities; it is a visualization method with stochastic and perplexity-sensitive behavior. UMAP builds a fuzzy neighborhood graph and optimizes a low-dimensional graph cross-entropy; its random state and neighborhood parameters must be recorded.

Isolation Forest recursively partitions data with random splits. If a point has average path length \(E[h(x)]\) over \(t\) trees and \(c(n)\) is the expected unsuccessful-search path length in a binary search tree,

\[
c(n)=2H(n-1)-\frac{2(n-1)}{n},
\]

where \(H(m)\) is the harmonic number. The anomaly score is commonly

\[
s(x,n)=2^{-E[h(x)]/c(n)}.
\]

Short paths imply isolation and higher anomaly score. The repository’s severity convention is derived from the fitted estimator score and is recorded in the unsupervised feature contract. Cluster labels and anomaly scores can be appended as train-fitted downstream features; no test rows may fit the unsupervised components.

## 9. Metrics, calibration, and statistical comparisons — CO5/M5

Given positive-class probability \(p_i\), threshold \(\tau\), and prediction \(\hat y_i=\mathbf1[p_i\ge\tau]\), accuracy, precision, recall, and F1 are

\[
\operatorname{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN},
\]
\[
\operatorname{Precision}=\frac{TP}{TP+FP},\qquad
\operatorname{Recall}=\frac{TP}{TP+FN},
\]
\[
F1=\frac{2\operatorname{Precision}\operatorname{Recall}}{\operatorname{Precision}+\operatorname{Recall}}.
\]

ROC-AUC ranks positive scores against negative scores; PR-AUC summarizes precision-recall behavior and is often more informative under imbalance. The Brier score is

\[
\operatorname{BS}=\frac1n\sum_{i=1}^{n}(p_i-y_i)^2.
\]

Platt calibration fits

\[
\tilde p=\sigma(ap+b)
\]

on permitted validation/training-fold predictions. Isotonic calibration fits a nondecreasing piecewise-constant function \(g\) and returns \(\tilde p=g(p)\). Reliability diagrams compare empirical event frequency with mean predicted probability within bins.

McNemar compares paired predictions through the discordant counts \(b\) and \(c\), often using

\[
\chi^2=\frac{(|b-c|-1)^2}{b+c}.
\]

A paired bootstrap samples paired rows with replacement, recomputes a metric difference \(\Delta^{(b)}\), and reports empirical quantiles for a declared confidence level. Nested cross-validation fits selection only inside inner folds and evaluates outer folds without using the final test partition. Regression smoke metrics are \(RMSE=\sqrt{n^{-1}\sum_i(y_i-\hat y_i)^2}\), \(MAE=n^{-1}\sum_i|y_i-\hat y_i|\), and \(R^2=1-\sum_i(y_i-\hat y_i)^2/\sum_i(y_i-\bar y)^2\); they are not fake-news classification benchmarks.

## 10. Drift and production signals — CO6/M6

The two-sample Kolmogorov–Smirnov statistic is

\[
D_{n,m}=\sup_x|F_n(x)-G_m(x)|,
\]

with a drift decision based on a declared significance level \(\alpha\). Population Stability Index over bins \(b\) is

\[
PSI=\sum_b(q_b-p_b)\ln\left(\frac{q_b}{p_b}\right),
\]

where \(p_b\) and \(q_b\) are reference/current bin proportions with a numerical floor for empty bins. Text monitoring applies analogous distribution comparisons to length, lexical, punctuation, digit, uppercase, and OOV statistics.

A retraining signal is a structured record

\[
S=(\text{triggered},\text{drifted features},\text{baseline revision},\text{window ID},\text{reason},\text{cooldown key},\text{approval required},\text{side effects}),
\]

with `side_effects = none` and human approval required. It is a review event, not an optimization step, retraining command, model replacement, or deployment decision.

## 11. Production parity and artifact semantics — CO6/M6

For native probability matrix \(P\) and ONNX probability matrix \(\widehat P\), parity requires equal shape and

\[
\max_{i,k}|P_{ik}-\widehat P_{ik}|<\varepsilon,
\qquad \varepsilon<10^{-5}.
\]

The package manifest records model, preprocessing revision, calibration revision, label mapping, source IDs, runtime metadata, and SHA-256 checksums. Native serving is authoritative when an operation cannot be exported without changing the mathematical prediction function.
