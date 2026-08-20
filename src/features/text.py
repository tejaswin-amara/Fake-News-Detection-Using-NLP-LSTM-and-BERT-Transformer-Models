"""Text normalization and TF-IDF features.

All vectorizers are fit only on the training partition by the caller. References:
SRC-004, SRC-005, SRC-006, and SRC-015 in docs/sources.md.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

_URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_HTML_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def clean_text(
    value: object,
    *,
    lowercase: bool = True,
    remove_urls: bool = True,
    remove_email_addresses: bool = True,
    remove_html: bool = True,
    max_characters: int | None = 50000,
) -> str:
    """Normalize text without fitting any corpus-dependent operation."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    if remove_html:
        text = _HTML_RE.sub(" ", text)
    if remove_urls:
        text = _URL_RE.sub(" ", text)
    if remove_email_addresses:
        text = _EMAIL_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    if lowercase:
        text = text.lower()
    return text[:max_characters] if max_characters else text


def combine_title_and_body(
    titles: Iterable[object], bodies: Iterable[object], title_weight: float = 1.0
) -> list[str]:
    """Create model text while preserving a configurable title emphasis."""
    multiplier = max(1, int(round(title_weight)))
    return [
        (clean_text(title) + "\n") * multiplier + clean_text(body)
        for title, body in zip(titles, bodies, strict=False)
    ]


@dataclass
class TfidfTextPipeline:
    """Serializable TF-IDF transformer with explicit fit/transform stages."""

    ngram_range: tuple[int, int] = (1, 2)
    min_df: int | float = 2
    max_df: int | float = 0.98
    max_features: int | None = 200_000
    sublinear_tf: bool = True
    stop_words: str | None = "english"

    def __post_init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            max_features=self.max_features,
            sublinear_tf=self.sublinear_tf,
            stop_words=self.stop_words,
            dtype=np.float32,
        )
        self.fitted = False

    def fit(self, texts: Iterable[str]) -> TfidfTextPipeline:
        self.vectorizer.fit([clean_text(text) for text in texts])
        self.fitted = True
        return self

    def transform(self, texts: Iterable[str]):
        if not self.fitted:
            raise RuntimeError("TfidfTextPipeline must be fit on training text before transform")
        return self.vectorizer.transform([clean_text(text) for text in texts])

    def fit_transform(self, texts: Iterable[str]):
        self.fit(texts)
        return self.transform(texts)

    def get_feature_names(self) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("TfidfTextPipeline is not fitted")
        return self.vectorizer.get_feature_names_out()

    def as_sklearn_pipeline(self) -> Pipeline:
        """Return a native sklearn pipeline for artifact packaging."""
        return Pipeline([("tfidf", self.vectorizer)])
