"""Bounded streaming MinHash/LSH near-duplicate detection.

The implementation uses fixed-size signatures, bounded bucket occupancy, and
streaming insertion. It never constructs an all-pairs similarity matrix.
Compliant with M1/CO1 data integrity and M5/CO5 leakage prevention.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_MAX_HASH = (1 << 64) - 1


def shingles(text: str, shingle_size: int = 5) -> set[str]:
    if shingle_size < 1:
        raise ValueError("shingle_size must be positive")
    tokens = _TOKEN_RE.findall(text.lower())
    if not tokens:
        return set()
    if len(tokens) <= shingle_size:
        return {" ".join(tokens)}
    return {" ".join(tokens[index : index + shingle_size]) for index in range(len(tokens) - shingle_size + 1)}


def minhash_signature(tokens: Iterable[str], permutations: int = 64) -> tuple[int, ...]:
    if permutations < 4:
        raise ValueError("permutations must be at least four")
    values = tuple(tokens)
    if not values:
        return (_MAX_HASH,) * permutations
    return tuple(
        min(
            int.from_bytes(hashlib.blake2b(f"{seed}:{token}".encode(), digest_size=8).digest(), "big")
            for token in values
        )
        for seed in range(permutations)
    )


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    union = left | right
    return 1.0 if not union else len(left & right) / len(union)


@dataclass
class StreamingMinHashLSH:
    threshold: float = 0.85
    permutations: int = 64
    bands: int = 16
    max_bucket_size: int = 64
    shingle_size: int = 5
    _buckets: dict[tuple[int, tuple[int, ...]], list[int]] = field(default_factory=lambda: defaultdict(list), init=False)
    _signatures: list[tuple[int, ...]] = field(default_factory=list, init=False)
    _shingle_sets: list[set[str]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not 0.0 < self.threshold <= 1.0:
            raise ValueError("threshold must lie in (0, 1]")
        if self.permutations < 4 or self.bands < 1 or self.permutations % self.bands != 0:
            raise ValueError("bands must evenly divide permutations >= 4")
        if self.max_bucket_size < 2:
            raise ValueError("max_bucket_size must be at least two")

    @property
    def rows_per_band(self) -> int:
        return self.permutations // self.bands

    def _candidate_indices(self, signature: tuple[int, ...]) -> set[int]:
        candidates: set[int] = set()
        for band in range(self.bands):
            start = band * self.rows_per_band
            key = (band, signature[start : start + self.rows_per_band])
            candidates.update(self._buckets.get(key, ()))
        return candidates

    def insert(self, text: str) -> list[int]:
        index = len(self._signatures)
        token_set = shingles(text, self.shingle_size)
        signature = minhash_signature(token_set, self.permutations)
        candidates = self._candidate_indices(signature)
        matches = [candidate for candidate in candidates if jaccard_similarity(token_set, self._shingle_sets[candidate]) >= self.threshold]
        self._signatures.append(signature)
        self._shingle_sets.append(token_set)
        for band in range(self.bands):
            start = band * self.rows_per_band
            key = (band, signature[start : start + self.rows_per_band])
            bucket = self._buckets[key]
            if len(bucket) < self.max_bucket_size:
                bucket.append(index)
        return sorted(matches)

    def find_groups(self, texts: Sequence[str]) -> list[list[int]]:
        parent = list(range(len(texts)))

        def find(index: int) -> int:
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index

        for index, text in enumerate(texts):
            for candidate in self.insert(text):
                left, right = find(index), find(candidate)
                if left != right:
                    parent[right] = left
        groups: dict[int, list[int]] = defaultdict(list)
        for index in range(len(texts)):
            groups[find(index)].append(index)
        return [sorted(group) for group in groups.values() if len(group) > 1]


def find_near_duplicate_groups(
    texts: Sequence[str],
    *,
    threshold: float = 0.85,
    permutations: int = 64,
    bands: int = 16,
    max_bucket_size: int = 64,
    shingle_size: int = 5,
) -> list[list[int]]:
    detector = StreamingMinHashLSH(
        threshold=threshold,
        permutations=permutations,
        bands=bands,
        max_bucket_size=max_bucket_size,
        shingle_size=shingle_size,
    )
    return detector.find_groups(texts)
