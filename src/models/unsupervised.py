"""Unsupervised structure discovery for news-text representations.

Compliant with M4: Unsupervised Learning and CO4. References SRC-016 through
SRC-020 in docs/sources.md. Fit methods must receive training representations;
held-out data may only be passed to transform/predict methods.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score


@dataclass
class KMeansDiagnostics:
    k_values: list[int]
    inertias: list[float]
    silhouette_scores: list[float | None]


class UnsupervisedAnalyzer:
    """Fit unsupervised models on a reference/training representation."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.kmeans: KMeans | None = None
        self.hierarchical: AgglomerativeClustering | None = None
        self.dbscan: DBSCAN | None = None
        self.pca: PCA | None = None
        self.isolation_forest: IsolationForest | None = None

    @staticmethod
    def _as_dense(matrix: Any) -> np.ndarray:
        return matrix.toarray() if hasattr(matrix, "toarray") else np.asarray(matrix)

    def kmeans_diagnostics(self, matrix: Any, k_values: list[int]) -> KMeansDiagnostics:
        values = self._as_dense(matrix)
        inertias: list[float] = []
        silhouettes: list[float | None] = []
        for k in k_values:
            if k < 2 or k >= len(values):
                inertias.append(float("nan"))
                silhouettes.append(None)
                continue
            model = KMeans(
                n_clusters=k, init="k-means++", n_init=10, random_state=self.random_state
            )
            labels = model.fit_predict(values)
            inertias.append(float(model.inertia_))
            silhouettes.append(
                float(silhouette_score(values, labels)) if len(set(labels)) > 1 else None
            )
        return KMeansDiagnostics(
            k_values=k_values, inertias=inertias, silhouette_scores=silhouettes
        )

    def fit_kmeans(self, matrix: Any, n_clusters: int = 2) -> UnsupervisedAnalyzer:
        self.kmeans = KMeans(
            n_clusters=n_clusters, init="k-means++", n_init=10, random_state=self.random_state
        ).fit(self._as_dense(matrix))
        return self

    def fit_hierarchical(
        self, matrix: Any, n_clusters: int = 2, linkage: str = "ward"
    ) -> UnsupervisedAnalyzer:
        self.hierarchical = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage).fit(
            self._as_dense(matrix)
        )
        return self

    def fit_dbscan(
        self, matrix: Any, eps: float = 0.5, min_samples: int = 5
    ) -> UnsupervisedAnalyzer:
        self.dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean").fit(
            self._as_dense(matrix)
        )
        return self

    def dbscan_grid(
        self, matrix: Any, eps_values: list[float], min_samples_values: list[int]
    ) -> list[dict[str, float | int]]:
        values = self._as_dense(matrix)
        results: list[dict[str, float | int]] = []
        for eps in eps_values:
            for min_samples in min_samples_values:
                model = DBSCAN(eps=eps, min_samples=min_samples).fit(values)
                labels = model.labels_
                non_noise = labels != -1
                unique = set(labels[non_noise])
                score = None
                if len(unique) >= 2 and non_noise.sum() > len(unique):
                    score = float(silhouette_score(values[non_noise], labels[non_noise]))
                results.append(
                    {
                        "eps": eps,
                        "min_samples": min_samples,
                        "clusters": int(len(unique)),
                        "noise_count": int((labels == -1).sum()),
                        "silhouette": score if score is not None else float("nan"),
                    }
                )
        return results

    def fit_pca(self, matrix: Any, n_components: int = 2) -> np.ndarray:
        values = self._as_dense(matrix)
        components = min(n_components, values.shape[0], values.shape[1])
        self.pca = PCA(n_components=components, random_state=self.random_state).fit(values)
        return self.pca.transform(values)

    def transform_pca(self, matrix: Any) -> np.ndarray:
        if self.pca is None:
            raise RuntimeError("PCA must be fit on training/reference data before transform")
        return self.pca.transform(self._as_dense(matrix))

    def fit_isolation_forest(
        self, matrix: Any, contamination: str | float = "auto"
    ) -> UnsupervisedAnalyzer:
        self.isolation_forest = IsolationForest(
            contamination=contamination, random_state=self.random_state, n_estimators=200
        ).fit(self._as_dense(matrix))
        return self

    def anomaly_scores(self, matrix: Any) -> np.ndarray:
        if self.isolation_forest is None:
            raise RuntimeError("Isolation Forest must be fit before scoring")
        return -self.isolation_forest.score_samples(self._as_dense(matrix))

    def labels(self, matrix: Any) -> dict[str, np.ndarray]:
        values = self._as_dense(matrix)
        output: dict[str, np.ndarray] = {}
        if self.kmeans is not None:
            output["kmeans_label"] = self.kmeans.predict(values)
        if self.hierarchical is not None and len(values) == len(self.hierarchical.labels_):
            output["hierarchical_label"] = self.hierarchical.labels_
        if self.dbscan is not None and len(values) == len(self.dbscan.labels_):
            output["dbscan_label"] = self.dbscan.labels_
        if self.isolation_forest is not None:
            output["anomaly_score"] = self.anomaly_scores(values)
        return output

    def augment_features(self, matrix: Any) -> np.ndarray:
        """Append fit-derived labels/scores for downstream supervised models."""
        values = self._as_dense(matrix)
        extras = self.labels(values)
        if not extras:
            return values
        appended = np.column_stack(
            [values, *[np.asarray(value).reshape(-1, 1) for value in extras.values()]]
        )
        return appended


def save_diagnostics(diagnostics: KMeansDiagnostics, output_path: str | Path) -> None:
    import json

    payload = {
        "k_values": diagnostics.k_values,
        "inertias": diagnostics.inertias,
        "silhouette_scores": diagnostics.silhouette_scores,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def reduce_for_visualization(
    matrix: Any, method: str = "pca", random_state: int = 42, **kwargs: Any
) -> np.ndarray:
    values = UnsupervisedAnalyzer._as_dense(matrix)
    if method == "pca":
        return PCA(
            n_components=kwargs.get("n_components", 2), random_state=random_state
        ).fit_transform(values)
    if method == "tsne":
        perplexity = min(kwargs.get("perplexity", 30), max(2, len(values) - 1))
        return TSNE(
            n_components=kwargs.get("n_components", 2),
            perplexity=perplexity,
            random_state=random_state,
        ).fit_transform(values)
    if method == "umap":
        import umap  # type: ignore

        reducer = umap.UMAP(
            n_components=kwargs.get("n_components", 2),
            n_neighbors=min(kwargs.get("n_neighbors", 15), max(2, len(values) - 1)),
            min_dist=kwargs.get("min_dist", 0.1),
            random_state=random_state,
        )
        return reducer.fit_transform(values)
    raise ValueError("method must be one of: pca, tsne, umap")
