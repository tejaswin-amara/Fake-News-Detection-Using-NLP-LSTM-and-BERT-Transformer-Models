# Dataset Card

## Dataset sources

The current project references:

- ISOT Fake News Dataset
- WELFake
- Data Commons ClaimReview structured fact-check feed

The exact retrieved versions, checksums, dates, licenses, and mappings are maintained in the source register.

## Intended use

Dataset use is limited to research and educational fake-news classification within this project.

## Canonical schema

```text
id
title
content
label
source
```

## Labels

Internal convention:

```text
0 = real
1 = fake
```

Source-specific label mappings must be recorded during ingestion.

## Data quality risks

Potential issues:

- duplicates
- near-duplicates
- source-specific artifacts
- label noise
- historical vocabulary bias
- temporal distribution shift
- publisher/source imbalance

## Leakage controls

The pipeline must:

1. identify and remove/handle duplicates before splitting when permitted;
2. fit learned transforms only on training data;
3. keep the final test set isolated;
4. record split manifests;
5. avoid using test information in model selection.

## Licensing

Do not redistribute datasets unless their terms allow it. Preserve provenance metadata and source-register entries.

## Known limitation

The dataset label is not equivalent to an objective ground-truth statement about reality.
