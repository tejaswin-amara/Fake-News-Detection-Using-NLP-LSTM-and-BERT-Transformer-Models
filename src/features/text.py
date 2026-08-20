"""Split-safe text preprocessing, statistics, and TF-IDF features.

All corpus-dependent vectorizers and learned transforms must be fit on training
text only. References: SRC-004, SRC-005, SRC-006, and SRC-015.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.pipeline import Pipeline

_URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_HTML_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)?")
_SENTENCE_RE = re.compile(r"[.!?]+")


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
    if value is None or (isinstance(value, float) and np.isnan(value)):
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


def tokenize_text(text: str) -> list[str]:
    return _TOKEN_RE.findall(clean_text(text))


def _stem_tokens(tokens: list[str]) -> list[str]:
    try:
        from nltk.stem import PorterStemmer  # type: ignore
    except ImportError:
        return tokens
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]


def _lemmatize_tokens(tokens: list[str]) -> list[str]:
    try:
        from nltk.stem import WordNetLemmatizer  # type: ignore

        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token) for token in tokens]
    except Exception:
        return tokens


def process_tokens(
    text: object,
    *,
    stop_words: str | Iterable[str] | None = "english",
    stemming: bool = False,
    lemmatization: bool = False,
) -> list[str]:
    tokens = tokenize_text(clean_text(text))
    if stop_words == "english":
        stop_set = ENGLISH_STOP_WORDS
    elif stop_words is None:
        stop_set = set()
    else:
        stop_set = set(stop_words)
    tokens = [token for token in tokens if token not in stop_set]
    if lemmatization:
        tokens = _lemmatize_tokens(tokens)
    if stemming:
        tokens = _stem_tokens(tokens)
    return tokens


class TextNormalizer(BaseEstimator, TransformerMixin):
    """A serializable sklearn-compatible text normalization transformer."""

    def __init__(
        self,
        stop_words: str | Iterable[str] | None = "english",
        stemming: bool = False,
        lemmatization: bool = False,
        max_characters: int | None = 50000,
    ) -> None:
        self.stop_words = stop_words
        self.stemming = stemming
        self.lemmatization = lemmatization
        self.max_characters = max_characters

    def fit(self, X: Iterable[object], y: Any = None) -> TextNormalizer:
        self.fitted_ = True
        return self

    def transform(self, X: Iterable[object]) -> np.ndarray:
        if not getattr(self, "fitted_", False):
            raise RuntimeError("TextNormalizer must be fit before transform")
        return np.asarray(
            [
                " ".join(
                    process_tokens(
                        clean_text(value, max_characters=self.max_characters),
                        stop_words=self.stop_words,
                        stemming=self.stemming,
                        lemmatization=self.lemmatization,
                    )
                )
                for value in X
            ],
            dtype=object,
        )


class TextStatisticsTransformer(BaseEstimator, TransformerMixin):
    """Deterministic article-level length, lexical, punctuation, and readability features."""

    feature_names = (
        "char_count",
        "word_count",
        "sentence_count",
        "avg_word_length",
        "lexical_diversity",
        "punctuation_ratio",
        "digit_ratio",
        "uppercase_ratio",
        "flesch_reading_ease",
    )

    def fit(self, X: Iterable[object], y: Any = None) -> TextStatisticsTransformer:
        self.fitted_ = True
        return self

    def transform(self, X: Iterable[object]) -> pd.DataFrame:
        if not getattr(self, "fitted_", False):
            raise RuntimeError("TextStatisticsTransformer must be fit before transform")
        rows = []
        for value in X:
            raw = clean_text(value, lowercase=False)
            words = _TOKEN_RE.findall(raw)
            chars = len(raw)
            word_count = len(words)
            sentence_count = max(1, len(_SENTENCE_RE.findall(raw))) if raw else 0
            syllables = sum(max(1, len(re.findall(r"[aeiouy]+", word.lower()))) for word in words)
            flesch = (
                206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
                if word_count and sentence_count
                else 0.0
            )
            letters = [char for char in raw if char.isalpha()]
            rows.append(
                {
                    "char_count": chars,
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "avg_word_length": float(sum(map(len, words)) / word_count) if word_count else 0.0,
                    "lexical_diversity": float(len(set(word.lower() for word in words)) / word_count)
                    if word_count
                    else 0.0,
                    "punctuation_ratio": float(sum(char in ".,;:!?" for char in raw) / max(1, chars)),
                    "digit_ratio": float(sum(char.isdigit() for char in raw) / max(1, chars)),
                    "uppercase_ratio": float(sum(char.isupper() for char in letters) / max(1, len(letters))),
                    "flesch_reading_ease": float(flesch),
                }
            )
        return pd.DataFrame(rows, columns=self.feature_names, dtype=np.float64)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        return np.asarray(self.feature_names, dtype=object)


class TfidfTextPipeline:
    """Serializable TF-IDF transformer with explicit fit/transform stages."""

    def __init__(
        self,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: int | float = 2,
        max_df: int | float = 0.98,
        max_features: int | None = 200_000,
        sublinear_tf: bool = True,
        stop_words: str | None = "english",
    ) -> None:
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.max_features = max_features
        self.sublinear_tf = sublinear_tf
        self.stop_words = stop_words
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=ngram_range,
            min_df=min_df,
            max_df=max_df,
            max_features=max_features,
            sublinear_tf=sublinear_tf,
            stop_words=stop_words,
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
        return Pipeline([("tfidf", self.vectorizer)])
