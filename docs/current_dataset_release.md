# Current ClaimReview Dataset Release

## Release identity

The `claimreview-current-2026-08-21` release is a new English fact-checked **claims** dataset generated from the Data Commons Fact Check Markup Tool data feed (SRC-045). It is suitable for research and educational model development only. It does not establish objective truth, does not replace verification against sources, and must not be used for automated accusations or enforcement.

| Property | Recorded value |
| --- | --- |
| Feed retrieved | `2026-08-21T11:42:06+00:00` |
| Feed SHA-256 | `9266a7bbc99ee16416f05afdad2524557b242a98ba9e823e3cb0734631cdc2b0` |
| Source window | 2016-08-22 through 2026-08-21 (3,652 days) |
| Live candidates streamed | 105,888 |
| Governed English records before near-duplicate removal | 16,963 |
| Records retained in master registry | 16,948 |
| Exact/model-input unit | Normalized `claimReviewed` text only; no fact-check article body or verdict text |

## Label policy and exclusions

The binary model pool preserves the source’s original rating and admits only unambiguous ratings. The master registry retains 412 `real` and 16,536 `fake` claims after near-duplicate filtering. This severe class imbalance originates in the retrieved structured source and is documented rather than obscured.

| Exclusion reason | Count |
| --- | ---: |
| Non-English or failed conservative English filter | 48,049 |
| Ambiguous or unsupported publisher rating | 22,451 |
| Missing claim text | 7,145 |
| Missing or invalid review date | 10,634 |
| Missing publisher | 448 |
| Outside the release window | 70 |
| Future-dated review | 1 |

## Temporal partitions

The release fixes time boundaries before balancing. The model-development split ends on `2023-08-11`; validation begins `2023-09-08`; the final untouched test partition begins `2024-08-21`. Within each partition only, the majority label is deterministically downsampled to the minority count. This produces a balanced model-development package without moving later claims into earlier partitions.

| Partition | Raw `real` | Raw `fake` | Released `real` | Released `fake` |
| --- | ---: | ---: | ---: | ---: |
| Train | 376 | 9,863 | 376 | 376 |
| Validation | 17 | 3,038 | 17 | 17 |
| Test | 19 | 3,635 | 19 | 19 |

## Provenance and reproducibility

Run `python -m src.data.claimreview --config configs/dataset.yaml --refresh` or `dvc repro claimreview_current` to create a new dated release. The raw feed and generated data files stay out of Git and are intended for DVC-backed storage. The release writes `collection_manifest.json` and `release_manifest.json`, retaining feed HTTP metadata when fetched and a checksum in all cases.

Data Commons states that the feed compilation is licensed under CC BY 4.0, while each ClaimReview record may include its own `sdLicense` and publishers retain terms governing material on their own sites.[1] This release stores structured claim metadata and canonical links; it does not collect full publisher article text.

## Limitations

The dataset is English-only, source-selective, historically and politically skewed, and highly imbalanced before bounded downsampling. The small validation and test partitions mean model results have high uncertainty; they are appropriate for integrity testing and methodology demonstration, not sweeping performance claims. Model input does not include evidence retrieval, browser search, or live source verification, so a prediction must be treated as a review signal rather than a factual conclusion.

## References

[1] [Data Commons Fact Check Data Download and FAQ](https://datacommons.org/factcheck/download)
