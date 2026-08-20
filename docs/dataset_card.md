# Dataset Card

## Scope

This project supports two text-classification sources through adapters: the ISOT Fake News Dataset and WELFake. The source register in [`sources.md`](sources.md) is authoritative for citations, URLs, access dates, checksums, and usage terms.

## Canonical schema

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Stable content/source-derived identifier |
| `title` | string | News title; may be empty |
| `text` | string | Article body; may be empty in the raw source but is rejected if title and body are both empty |
| `content` | string | Normalized title/body text used by features |
| `label` | integer | Internal convention: `0 = real`, `1 = fake` |
| `dataset` | string | Adapter provenance, e.g. `isot` or `welfake` |
| `content_hash` | string | SHA-256 hash of normalized content for duplicate control |

## ISOT adapter

The ISOT adapter expects a directory containing `Fake.csv` and `True.csv`. It assigns label `1` to `Fake.csv` rows and `0` to `True.csv` rows, then normalizes columns into the canonical schema. The primary publication and dataset provenance are recorded as SRC-001.

## WELFake adapter

The WELFake adapter accepts `WELFake_Dataset.csv` and requires `Title`, `Text`, and `Label` columns, case-insensitively. The Zenodo record describes the source convention as `0 = fake` and `1 = real`; the adapter explicitly inverts it to the project’s canonical `0 = real`, `1 = fake` convention and records that transformation in the code and metadata.

## Quality controls

The ingestion stage normalizes Unicode, removes HTML/URLs/email addresses for the canonical content hash, collapses whitespace, rejects empty content and invalid labels, reports class counts, and removes exact normalized-content duplicates before splitting. The split manifest records the seed, sizes, class counts, and source path. Near-duplicate detection beyond exact normalized hashes is a planned extension and must not be claimed as executed unless its report exists.

## Split and leakage policy

The default split is stratified 70% train, 15% validation, and 15% test. No TF-IDF vocabulary, tokenizer vocabulary, scaler, dimensionality reducer, clusterer, anomaly detector, calibration map, or threshold may be fit on validation or test rows. Final test results are reported only after all model and calibration decisions are fixed.

## Limitations and ethics

Dataset labels encode the source construction and may reflect source, temporal, political, linguistic, and annotation bias. Text-based classifiers can learn stylistic or publisher artifacts instead of factuality. The output is a probabilistic screening signal and is not a fact-checking verdict.

## Acquisition

Raw files are intentionally not committed by default. Use the source URLs in [`sources.md`](sources.md), verify the applicable license/terms, record the downloaded file checksum, and place files under `data/raw/` or `data/external/` according to the adapter instructions. Do not include restricted raw data in commits.
