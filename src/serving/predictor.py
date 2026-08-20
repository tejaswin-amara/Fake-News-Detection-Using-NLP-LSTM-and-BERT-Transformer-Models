"""Inference wrappers that bind preprocessing and estimator artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np


class PackagedTextModel:
    """A serialized preprocessing-plus-estimator boundary for online inference."""

    def __init__(self, text_pipeline: Any, estimator: Any) -> None:
        self.text_pipeline = text_pipeline
        self.estimator = estimator

    def predict_proba(self, texts: Iterable[str]) -> np.ndarray:
        features = self.text_pipeline.transform(list(texts))
        return np.asarray(self.estimator.predict_proba(features))

    def predict(self, texts: Iterable[str]) -> np.ndarray:
        features = self.text_pipeline.transform(list(texts))
        return np.asarray(self.estimator.predict(features))
