"""Leakage-safe wrapper for optional cluster and anomaly features.

Compliant with M4/CO4. The wrapper separates ``fit`` from ``transform`` so
cluster labels and anomaly scores are not learned from validation or test data.
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
    include_anomaly: bool = True

    def __post_init__(self) -> None:
        self.analyzer = UnsupervisedAnalyzer(random_state=self.random_state)
        self._fitted = False

    def fit(self, X: Any) -> UnsupervisedFeatureAugmenter:
        if self.include_kmeans:
            self.analyzer.fit_kmeans(X, n_clusters=self.n_clusters)
        if self.include_anomaly:
            self.analyzer.fit_isolation_forest(X)
        self._fitted = True
        return self

    def transform(self, X: Any) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("UnsupervisedFeatureAugmenter must be fit on training data first")
        values = X.toarray() if hasattr(X, "toarray") else np.asarray(X)
        extras = []
        if self.analyzer.kmeans is not None:
            extras.append(self.analyzer.kmeans.predict(values).reshape(-1, 1))
        if self.analyzer.isolation_forest is not None:
            extras.append(self.analyzer.anomaly_scores(values).reshape(-1, 1))
        return np.column_stack([values, *extras]) if extras else values

    def fit_transform(self, X: Any) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
