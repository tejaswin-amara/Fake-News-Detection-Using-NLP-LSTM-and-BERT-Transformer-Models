# Unsupervised Learning Plan

## Objective

Use unsupervised methods to discover structure in news representations and investigate whether that structure is informative for fake-news analysis.

## Representation

Recommended:

```text
TF-IDF
→ TruncatedSVD where required for sparse safety
→ bounded dense representation
```

## K-Means

Produce:

- inertia vs K / elbow curve
- silhouette score
- cluster size distribution
- representative examples per cluster

## Hierarchical clustering

Produce:

- linkage comparison
- dendrogram
- cluster interpretation

## DBSCAN

Produce:

- parameter sweep
- number of clusters
- noise count
- silhouette where valid

DBSCAN should remain an offline analytical technique unless a safe serving strategy has been deliberately designed.

## PCA / t-SNE / UMAP

Use for visualization of representation structure.

Do not interpret distances in reduced spaces as universally meaningful.

## Isolation Forest

Use to identify unusual or anomalous representations.

## Research question

Do unsupervised structure and anomaly scores reveal meaningful differences in the distribution of real and fake labels?

## Evidence

Required notebook/report:

```text
notebooks/04_unsupervised_learning.ipynb
reports/unsupervised_summary.json
reports/cluster_visualizations/
```
