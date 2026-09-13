"""Leakage-safe tabular preprocessing for text-derived metadata.

Every estimator in this module must be fit on training rows only. Target encoding
uses out-of-fold estimates for training transforms and full-training mappings only
for validation/test transforms. References: SRC-005, SRC-006, and SRC-015.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer, MissingIndicator, SimpleImputer
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, OrdinalEncoder, StandardScaler


def _one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


class SmoothedTargetEncoder(BaseEstimator, TransformerMixin):
    """Out-of-fold smoothed target encoding for categorical columns."""

    def __init__(self, columns: Iterable[str] | None = None, n_splits: int = 5, smoothing: float = 10.0, random_state: int = 42):
        self.columns = None if columns is None else list(columns)
        self.n_splits = n_splits
        self.smoothing = smoothing
        self.random_state = random_state

    @staticmethod
    def _frame(X: Any, columns: list[str] | None = None) -> pd.DataFrame:
        if isinstance(X, pd.DataFrame):
            return X.copy()
        values = np.asarray(X)
        names = columns or [f"feature_{i}" for i in range(values.shape[1])]
        return pd.DataFrame(values, columns=names)

    def _fit_maps(self, X: pd.DataFrame, y: np.ndarray) -> None:
        self.columns_ = self.columns or list(X.columns)
        self.global_mean_ = float(np.mean(y))
        self.maps_: dict[str, dict[Any, float]] = {}
        for column in self.columns_:
            stats = pd.DataFrame({"key": X[column].astype(object), "target": y}).groupby("key")["target"].agg(["mean", "count"])
            weight = stats["count"] / (stats["count"] + self.smoothing)
            values = self.global_mean_ * (1.0 - weight) + stats["mean"] * weight
            self.maps_[column] = values.to_dict()
        self.feature_names_in_ = np.asarray(self.columns_, dtype=object)

    def _transform_with_maps(self, X: pd.DataFrame, maps: dict[str, dict[Any, float]], default: float) -> np.ndarray:
        return np.column_stack(
            [X[column].map(maps.get(column, {})).fillna(default).astype(float).to_numpy() for column in self.columns_]
        )

    def fit(self, X: Any, y: Any) -> SmoothedTargetEncoder:
        frame = self._frame(X, self.columns)
        target = np.asarray(y, dtype=float)
        if len(frame) != len(target):
            raise ValueError("X and y must contain the same number of rows")
        self._fit_maps(frame, target)
        self.fitted_ = True
        return self

    def fit_transform(self, X: Any, y: Any) -> np.ndarray:
        frame = self._frame(X, self.columns)
        target = np.asarray(y, dtype=float)
        if len(frame) != len(target):
            raise ValueError("X and y must contain the same number of rows")
        if len(frame) < 2:
            self.fit(frame, target)
            return self.transform(frame)
        folds = min(self.n_splits, len(frame))
        oof = np.full((len(frame), len(self.columns or frame.columns)), np.mean(target), dtype=float)
        splitter = KFold(n_splits=folds, shuffle=True, random_state=self.random_state)
        for train_idx, valid_idx in splitter.split(frame):
            fold_encoder = SmoothedTargetEncoder(self.columns, n_splits=self.n_splits, smoothing=self.smoothing, random_state=self.random_state)
            fold_encoder.fit(frame.iloc[train_idx], target[train_idx])
            oof[valid_idx] = fold_encoder.transform(frame.iloc[valid_idx])
        self.fit(frame, target)
        return oof

    def transform(self, X: Any) -> np.ndarray:
        if not getattr(self, "fitted_", False):
            raise RuntimeError("SmoothedTargetEncoder must be fit before transform")
        frame = self._frame(X, list(self.columns_))
        return self._transform_with_maps(frame, self.maps_, self.global_mean_)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        return np.asarray([f"{column}__target_mean" for column in self.columns_], dtype=object)


def build_numeric_pipeline(
    imputation: str = "median",
    scaling: str = "standard",
    add_indicator: bool = True,
    n_neighbors: int = 5,
) -> Pipeline:
    """Build a numeric pipeline; fit it only on training metadata."""
    if imputation == "mean" or imputation == "median":
        imputer: Any = SimpleImputer(strategy=imputation, add_indicator=add_indicator)
    elif imputation == "knn":
        imputer = KNNImputer(n_neighbors=n_neighbors, add_indicator=add_indicator)
    elif imputation == "iterative":
        imputer = IterativeImputer(
            estimator=ExtraTreesRegressor(n_estimators=25, random_state=42, n_jobs=1),
            max_iter=10,
            random_state=42,
            add_indicator=add_indicator,
        )
    else:
        raise ValueError("imputation must be mean, median, knn, or iterative")
    scaler: Any = "passthrough"
    if scaling == "standard":
        scaler = StandardScaler()
    elif scaling == "minmax":
        scaler = MinMaxScaler()
    elif scaling != "none":
        raise ValueError("scaling must be standard, minmax, or none")
    return Pipeline([("imputer", imputer), ("scaler", scaler)])


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
    *,
    imputation: str = "median",
    scaling: str = "standard",
    categorical_encoding: str = "onehot",
    add_indicator: bool = True,
) -> ColumnTransformer:
    """Build a fit/transform ColumnTransformer for mixed metadata."""
    numeric = build_numeric_pipeline(imputation, scaling, add_indicator)
    cat_imputer = SimpleImputer(strategy="most_frequent", add_indicator=add_indicator)
    if categorical_encoding == "onehot":
        encoder: Any = _one_hot_encoder()
    elif categorical_encoding == "ordinal":
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    else:
        raise ValueError("categorical_encoding must be onehot or ordinal; use SmoothedTargetEncoder for target encoding")
    categorical = Pipeline([("imputer", cat_imputer), ("encoder", encoder)])
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, numeric_features),
            ("categorical", categorical, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=True,
    )


class MissingIndicatorTransformer(BaseEstimator, TransformerMixin):
    """Standalone MissingIndicator wrapper with stable output names."""

    def __init__(self, features: str = "missing-only"):
        self.features = features

    def fit(self, X: Any, y: Any = None) -> MissingIndicatorTransformer:
        self.indicator_ = MissingIndicator(features=self.features).fit(X)
        self.fitted_ = True
        return self

    def transform(self, X: Any) -> np.ndarray:
        if not getattr(self, "fitted_", False):
            raise RuntimeError("MissingIndicatorTransformer must be fit before transform")
        return self.indicator_.transform(X).astype(np.float32)
