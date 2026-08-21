# Dataset Card

## 1. Dataset identity and motivation

This project supports two public fake-news text-classification sources through explicit adapters: the **ISOT Fake News Dataset** and **WELFake**. The purpose is to teach reproducible NLP ingestion, feature engineering, supervised/unsupervised learning, evaluation, packaging, and monitoring. The datasets are not a universal ground-truth corpus and are not a license to label real-world people, publishers, or articles automatically.

The source register in [`docs/sources.md`](sources.md) is authoritative for URLs, citations, access dates, checksums, licenses, and usage terms. Machine-readable provenance is maintained in [`docs/sources.yaml`](sources.yaml). Raw files are not committed by default.

## 2. Supported composition and canonical schema

| Field | Type | Description | Required invariant |
|---|---|---|---|
| `id` | string | Stable source/content-derived identifier | Deterministic within an ingestion run |
| `title` | string | Original title, possibly empty | Preserved for provenance |
| `text` | string | Original article body, possibly empty | Title plus body cannot both be empty |
| `content` | string | Normalized title/body used for modeling | Unicode/whitespace normalized |
| `label` | integer | Project label | `0 = real`, `1 = fake` |
| `dataset` | string | Adapter provenance | `isot` or `welfake` |
| `content_hash` | string | SHA-256 of normalized content | Used for exact duplicate control |

The ingestion output records source provenance, class counts, split sizes, random seed, and label mapping in a split manifest. All downstream consumers use `content` and `label`, not an implicit source-specific column convention.

## 3. ISOT source adapter

The ISOT adapter expects a directory containing `Fake.csv` and `True.csv`. Rows from `Fake.csv` are assigned project label `1`; rows from `True.csv` are assigned project label `0`. Columns are normalized into the canonical schema, missing title/body values are handled deterministically, and exact duplicate normalized content is controlled before splitting. ISOT provenance and the associated publication/source references are registered as SRC-001.

## 4. WELFake source adapter

The WELFake adapter accepts `WELFake_Dataset.csv` and requires `Title`, `Text`, and `Label` columns case-insensitively. The source convention described by the registered dataset record is `0 = fake` and `1 = real`. The adapter explicitly inverts it to the project convention: **source 0 becomes project 1, and source 1 becomes project 0**. The transformation is recorded in code and artifact metadata so a downstream consumer cannot silently reverse the target semantics. WELFake provenance is registered as SRC-002.

## 5. Acquisition, licensing, and governance

Operators must acquire each dataset from a registered source, inspect the applicable license/terms, record the downloaded file checksum, and place the files under `data/raw/` or `data/external/` according to adapter instructions. Credentials and restricted data must not be committed. DVC metadata versions the input path and processed split outputs; a configured remote is operator-owned.

### Current ClaimReview fact-checked claims release

`src/data/claimreview.py` builds the new `claimreview-current-2026-08-21` release from the live Data Commons Fact Check Markup Tool data feed (SRC-045). The feed publishes structured ClaimReview metadata and its compilation is CC BY 4.0; publisher-hosted fact-check article content is not part of the download and is not collected by this project. Each retained claim has a canonical review URL, review publisher, original rating, retrieval timestamp, source-license field where supplied, and a feed checksum in `data/raw/claimreview_current/collection_manifest.json`.

The release is deliberately conservative. It retains English claim text only, accepts only unambiguous source ratings (`accurate`/`correct`/`true`/`verified` as `real`; `fake`/`false`/`incorrect`/`pants on fire`/`wrong` as `fake`), and excludes nuanced ratings such as “mostly false.” The source verdict is metadata and never appears in model input. The detailed release counts, exclusions, temporal boundaries, and limitations are recorded in [`current_dataset_release.md`](current_dataset_release.md).

No source URL, pretrained-model reference, framework reference, statistical-method reference, or deployment reference used by this project may remain undocumented. The source-audit script checks external URLs and SRC identifiers against the repository registers. Local operational endpoint examples are not dataset sources.

## 6. Data quality and preprocessing

The ingestion stage performs the following controls before any learned transform is fit:

1. Validate required columns and source-specific label values.
2. Normalize Unicode and whitespace, strip standard publication datelines such as `CITY (Reuters) -` and leading bylines, and create a deterministic content hash after removing HTML/URLs/email-address noise.
3. Reject rows with empty title and body, invalid labels, or unusable identifiers.
4. Report source and class counts.
5. Remove exact normalized-content duplicates before splitting.
6. When `split.near_duplicate_check` is enabled, create token shingles, generate deterministic MinHash signatures, use LSH bands for candidate generation, confirm candidates with Jaccard similarity, and retain only the first row in each near-duplicate group.
7. Preserve raw title/body fields while constructing normalized `content`.
8. Write a split manifest with seed, proportions, row counts, class counts, source paths, label mapping, and near-duplicate removal notes.

Missing-value handling, encoders, scalers, TF-IDF, clusterers, anomaly detectors, tokenizers, and calibration maps are train-fitted only. The near-duplicate threshold is configurable and must be recorded with the ingestion run.

## 7. Split and leakage policy

The default protocol is a stratified three-way split:

| Partition | Default share | Role |
|---|---:|---|
| Train | 70% | Fit model parameters and train-only feature transforms |
| Validation | 15% | Hyperparameter, threshold, and optional calibration decisions |
| Test | 15% | One final held-out evaluation after all decisions are frozen |

The random seed is 42 by default and is recorded in the manifest. No vocabulary, scaler, imputer, target encoder, dimensionality reducer, clusterer, anomaly detector, calibrator, threshold, or feature-selection decision may use validation/test rows before its permitted stage. Final test results are never used for model selection.

The ClaimReview release uses an additional fixed chronological protocol because it is a current source: records before `2023-08-21` train the model, records from `2023-08-21` through `2024-08-20` validate it, and records on/after `2024-08-21` form the final time-held-out test set. Exact and MinHash/LSH near duplicates are removed before splitting. To prevent the extreme source-rating imbalance from making a trivial classifier, the majority class is downsampled deterministically **inside** each already fixed temporal split. No record crosses a temporal boundary to achieve balance.

## 8. Representational limitations and bias

The sources may overrepresent particular publishers, time periods, topics, political contexts, English-language conventions, collection procedures, and label-generation rules. In particular, ISOT real articles contain systematic Reuters wire-service formatting and datelines that can be absent from the fake subset. A classifier can therefore learn publication/source artifacts rather than factual status. Dateline/byline normalization and near-duplicate filtering reduce, but do not prove elimination of, this shortcut. Performance must be benchmarked with normalization enabled and disabled, and with a source-conditional or cross-dataset holdout such as training on ISOT and evaluating an appropriate WELFake slice. The source distributions may not represent local news, international news, multilingual content, satire, social-media fragments, transcripts, scientific reporting, or future events. Performance can change under temporal, topic, publisher, language, and platform shift.

Labels should be interpreted as dataset annotations/source construction, not objective truth. Dataset artifacts can encode social and political bias. Users must not infer that a high model score proves deception or that a low score proves reliability.

## 9. Privacy, ethics, and security

The data may contain names, locations, organizations, quotations, contact details, or other potentially identifying text. Operators should minimize copies, restrict access, avoid logging raw article content, protect DVC/MLflow stores, and follow the applicable source terms. The serving API validates payload size and the deployment boundary must provide authentication, TLS, rate limiting, network controls, and retention policy.

Use is limited to education, reproducible research, model-development evaluation, and human-reviewed triage. Out-of-scope uses include automated censorship, publication blocking, political targeting, legal or reputational judgments, employment/credit/insurance/housing decisions, law-enforcement decisions, and any fully automated accusation or sanction.

## 10. Monitoring and retraining implications

Approved reference distributions must be generated from an appropriate training/reference window, never from the final test partition. The monitoring layer measures numeric KS/PSI drift, prediction-probability drift, text lengths/lexical statistics, and OOV rate. A drift report is a non-mutating review signal. It does not prove degradation, retrain a model, or promote a replacement.

Retraining requires human review of data quality, delayed labels, source/temporal shift, cooldown and sample-count policy, DVC versioning, a new MLflow run, leakage checks, calibration, ONNX/native parity, serving tests, shadow/canary evidence, and rollback readiness.

## 11. Reproducibility record

The complete lifecycle is defined by `dvc.yaml`, `params.yaml`, `configs/default.yaml`, `scripts/run_pipeline.sh`, the MLflow experiment, the split manifest, package manifest, report manifest, source registers, and pinned dependencies. The lifecycle runner fails clearly if governed raw inputs or a DVC remote are unavailable; it does not substitute synthetic data for official training or benchmark claims.

## 12. Course alignment

This card covers CO1/M1 data provenance and problem framing; CO2/M2 preprocessing, missing values, encoding, and scaling; CO3/M3 supervised target integrity; CO4/M4 clustering/anomaly feature boundaries; CO5/M5 stratified splits and held-out evaluation; and CO6/M6 DVC, MLflow, packaging, API monitoring, CI/CD, security, and retraining governance.
