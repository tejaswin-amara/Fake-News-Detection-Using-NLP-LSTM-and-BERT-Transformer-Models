"""Leakage-safe cluster and anomaly feature synthesis.

Compliant with M4/CO4. Every clusterer/anomaly detector is fit on training
representations only; validation/test rows are transformed or assigned without
refitting. References SRC-016 through SRC-020.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from src.models.unsupervised import UnsupervisedAnalyzer


@dataclass
class UnsupervisedFeatureAugmenter:
    n_clusters: int = 2
    dbscan_eps: float = 0.5
    dbscan_min_samples: int = 5
    random_state: int = 42
    include_kmeans: bool = True
    include_minibatch_kmeans: bool = False
    include_dbscan: bool = True
    include_anomaly: bool = True
    online: bool = False
    minibatch_size: int = 256

    def __post_init__(self) -> None:
        self.analyzer = UnsupervisedAnalyzer(random_state=self.random_state)
        self._fitted = False
        self.feature_names_: list[str] = []
        self.n_input_features_: int | None = None

    def fit(self, X: Any, y: Any = None) -> UnsupervisedFeatureAugmenter:
        if self.online and self.include_dbscan:
            raise ValueError("DBSCAN is offline-only and cannot be used in online feature generation")
        values = self.analyzer._as_dense(X)
        self.n_input_features_ = int(values.shape[1])
        if self.include_kmeans:
            self.analyzer.fit_kmeans(values, n_clusters=self.n_clusters)
            self.feature_names_.append("kmeans_cluster_id")
        if self.include_minibatch_kmeans:
            self.analyzer.fit_minibatch_kmeans(
                values, n_clusters=self.n_clusters, batch_size=self.minibatch_size
            )
            self.feature_names_.append("minibatch_kmeans_cluster_id")
        if self.include_dbscan:
            self.analyzer.fit_dbscan(
                values, eps=self.dbscan_eps, min_samples=self.dbscan_min_samples
            )
            self.feature_names_.append("dbscan_cluster_id")
        if self.include_anomaly:
            self.analyzer.fit_isolation_forest(values)
            self.feature_names_.append("isolation_forest_anomaly_score")
        self._fitted = True
        return self

    def transform(self, X: Any) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("UnsupervisedFeatureAugmenter must be fit on training data first")
        values = self.analyzer._as_dense(X)
        if values.shape[1] != self.n_input_features_:
            raise ValueError("Input feature dimension differs from the fitted training schema")
        extras: list[np.ndarray] = []
        if self.analyzer.kmeans is not None:
            extras.append(self.analyzer.kmeans.predict(values).reshape(-1, 1))
        if self.analyzer.minibatch_kmeans is not None:
            extras.append(self.analyzer.minibatch_kmeans.predict(values).reshape(-1, 1))
        if self.analyzer.dbscan is not None:
            extras.append(self.analyzer.dbscan_predict(values).reshape(-1, 1))
        if self.analyzer.isolation_forest is not None:
            extras.append(self.analyzer.anomaly_scores(values).reshape(-1, 1))
        return np.column_stack([values, *extras]) if extras else values

    def fit_transform(self, X: Any, y: Any = None) -> np.ndarray:
        self.fit(X, y=y)
        return self.transform(X)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        if self.n_input_features_ is None:
            raise RuntimeError("UnsupervisedFeatureAugmenter must be fit first")
        base = list(input_features) if input_features is not None else [
            f"feature_{index}" for index in range(self.n_input_features_)
        ]
        return np.asarray(base + self.feature_names_, dtype=object)
