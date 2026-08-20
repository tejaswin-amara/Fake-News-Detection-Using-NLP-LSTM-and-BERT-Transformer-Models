"""Embedding, tokenizer, and provenance utilities.

References: SRC-011 (GloVe), SRC-013 (Transformers), SRC-014 (Sentence
Transformers), and SRC-035 (Gensim). Heavy pretrained assets are downloaded
only when explicitly requested by the caller and are never committed automatically.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

from src.features.text import process_tokens


def load_glove_vectors(
    path: str | Path, expected_dim: int | None = None, limit: int | None = None
) -> dict[str, np.ndarray]:
    """Load a whitespace-delimited GloVe text file into memory."""
    vectors: dict[str, np.ndarray] = {}
    with Path(path).open("r", encoding="utf-8", errors="ignore") as handle:
        for line_number, line in enumerate(handle):
            if limit is not None and line_number >= limit:
                break
            parts = line.rstrip().split(" ")
            if len(parts) < 3:
                continue
            word, values = parts[0], parts[1:]
            try:
                vector = np.asarray(values, dtype=np.float32)
            except ValueError:
                continue
            if expected_dim is not None and vector.shape != (expected_dim,):
                continue
            vectors[word] = vector
    if not vectors:
        raise ValueError(f"No valid GloVe vectors found in {path}")
    return vectors


def build_embedding_matrix(
    vocabulary: dict[str, int], vectors: dict[str, np.ndarray], dimension: int
) -> np.ndarray:
    """Build a zero-initialized matrix, filling only vocabulary matches."""
    matrix = np.zeros((len(vocabulary) + 1, dimension), dtype=np.float32)
    for token, index in vocabulary.items():
        vector = vectors.get(token)
        if vector is not None and vector.shape == (dimension,):
            matrix[index] = vector
    return matrix


def train_word2vec(
    texts: Iterable[str],
    *,
    vector_size: int = 100,
    window: int = 5,
    min_count: int = 1,
    epochs: int = 5,
    workers: int = 1,
    seed: int = 42,
):
    """Train Word2Vec on the supplied training texts only."""
    try:
        from gensim.models import Word2Vec  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install gensim to train Word2Vec embeddings") from exc
    sentences = [process_tokens(text, stop_words=None) for text in texts]
    if not sentences or not any(sentences):
        raise ValueError("Word2Vec requires at least one non-empty tokenized sentence")
    return Word2Vec(
        sentences=sentences,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=workers,
        seed=seed,
        epochs=epochs,
    )


def load_word2vec(path: str | Path, binary: bool = True):
    """Load a Word2Vec/KeyedVectors file without changing its vocabulary."""
    try:
        from gensim.models import KeyedVectors  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install gensim to load Word2Vec embeddings") from exc
    return KeyedVectors.load_word2vec_format(str(path), binary=binary)


def average_word2vec(texts: Iterable[str], model: Any) -> np.ndarray:
    """Create deterministic mean Word2Vec vectors; unknown tokens are ignored."""
    dimension = int(model.vector_size)
    # Materialize once so generators are not consumed twice.
    materialized = list(texts)
    output = np.zeros((len(materialized), dimension), dtype=np.float32)
    for row, text in enumerate(materialized):
        vectors = [model.wv[token] for token in process_tokens(text, stop_words=None) if token in model.wv]
        if vectors:
            output[row] = np.mean(vectors, axis=0)
    return output


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_transformer_tokenizer(model_name: str = "bert-base-uncased"):
    """Load a Hugging Face tokenizer lazily so classical paths remain CPU-light."""
    from transformers import AutoTokenizer  # type: ignore

    return AutoTokenizer.from_pretrained(model_name, use_fast=True)


def tokenize_dynamic(texts: Iterable[str], tokenizer, max_length: int = 512) -> dict[str, object]:
    """Tokenize with truncation and dynamic padding handled by the data collator."""
    return tokenizer(
        list(texts),
        truncation=True,
        max_length=max_length,
        padding=False,
        return_attention_mask=True,
    )


def encode_sbert(
    texts: Iterable[str], model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> np.ndarray:
    """Extract normalized SBERT embeddings lazily for unsupervised analysis."""
    from sentence_transformers import SentenceTransformer  # type: ignore

    model = SentenceTransformer(model_name)
    return np.asarray(model.encode(list(texts), normalize_embeddings=True, show_progress_bar=False))
