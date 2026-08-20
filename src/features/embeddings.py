"""Embedding and tokenizer utilities.

References: SRC-011 (GloVe), SRC-013 (Transformers), and SRC-014 (Sentence
Transformers). Heavy pretrained assets are downloaded only when explicitly
requested by the caller and are never committed automatically.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

import numpy as np


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


def file_sha256(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_transformer_tokenizer(model_name: str = "google-bert/bert-base-uncased"):
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
