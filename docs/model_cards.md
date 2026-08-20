# Model Cards

## Intended use

The models are intended for educational experimentation and editorial triage research on the supported datasets. They estimate whether an article resembles the dataset’s real/fake labels. They do not establish truth, intent, credibility, or legal status.

## Model families

| Model | Input representation | Primary evidence | Resource profile |
|---|---|---|---|
| Logistic L1/L2/ElasticNet | Train-fitted TF-IDF word n-grams | Coefficients, sparsity, calibration, fast baseline | CPU-friendly |
| Decision Tree | TF-IDF or reduced numeric features | Gini/entropy, cost-complexity pruning | CPU-friendly but can overfit |
| Random Forest | Dense/reduced or compatible sparse features | OOB error, permutation/Gini importance | CPU/memory dependent |
| XGBoost / LightGBM | Dense/reduced or compatible numeric features | Boosting, feature importance, SHAP | Optional CPU dependency |
| BiLSTM | Token sequences with optional GloVe matrix | Sequential context and learning curves | CPU smoke; GPU recommended for full run |
| BERT | Dynamic subword tokens from `bert-base-uncased` | Fine-tuning, calibration, held-out comparison | GPU recommended |

## Provenance

Dataset provenance is SRC-001 and SRC-002. GloVe provenance is SRC-011. BERT paper, model card, tokenizer, and framework provenance are SRC-012 and SRC-013. The exact downloaded model revision and checksum must be stored with every deep-learning artifact; pretrained weights are not committed by default.

## Evaluation requirements

Every reported model card must state the dataset source/version, split seed, train/validation/test sizes, preprocessing configuration, cross-validation procedure, calibration method, threshold, hardware, software versions, and whether the final test set remained untouched. Metrics must come from executed artifacts, not from expected or copied benchmark values.

## Limitations

The datasets may contain source, temporal, political, linguistic, and collection biases. Text-only models can learn stylistic and publisher artifacts. Performance on an external news distribution is not implied by in-dataset results. Probabilities may require calibration and still should not be interpreted as objective truth probabilities without a validated deployment population.

## Phase 3 supervised-model additions

The classical model family includes Ridge, Lasso, ElasticNet, binary and multinomial Logistic Regression, pruned Decision Trees, OOB Random Forests, histogram-based XGBoost, and leaf-wise LightGBM. Each model card must identify the exact estimator, hyperparameters or search result, training split, inner/outer CV settings, feature schema, random seed, and whether the reported score is cross-validation, validation, or final test performance.

Permutation importance and Tree SHAP are interpretation aids rather than causal explanations. They must be generated from a declared evaluation partition, retain feature names, record optional-package versions, and report when an explainability dependency or model-specific explainer is unavailable.

The BiLSTM and BERT paths remain resource-dependent. The BiLSTM consumes a declared GloVe/Word2Vec or trainable embedding configuration; BERT uses `bert-base-uncased` with a recorded model revision, tokenizer settings, maximum sequence length, optimizer, warmup, clipping, and hardware/precision configuration. Missing weights, tokenizers, TensorFlow, PyTorch, or Transformers dependencies must produce an explicit unavailable status rather than an unsupported benchmark value.

Calibration maps are fit on training folds or the validation partition and are never fitted using final test labels. Platt and isotonic outputs must record their fit split, method, binning settings, Brier score, and artifact revision. The final test set is evaluated once after model, threshold, search, and calibration decisions are frozen.
