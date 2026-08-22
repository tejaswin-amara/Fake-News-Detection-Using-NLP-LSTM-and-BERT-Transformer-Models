"""Regression coverage for deterministic and privacy-safe parser fuzzing."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fuzz.fuzz_text_parsing import DEFAULT_SEED, MAX_CASES, load_seed_corpus, run_fuzz

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "fuzz" / "corpus" / "claimreview_metadata.json"


def test_synthetic_seed_corpus_is_metadata_only_and_parseable() -> None:
    """Keep a compact, synthetic corpus free of imported article content."""
    corpus = load_seed_corpus(CORPUS)
    assert len(corpus) == 3
    assert all(isinstance(item, dict) for item in corpus)
    assert all("http" not in str(item).casefold() for item in corpus)


def test_bounded_fuzz_target_is_deterministic_and_does_not_emit_artifacts(tmp_path: Path) -> None:
    """Same seed and limits must execute the same in-memory campaign safely."""
    first = run_fuzz(corpus_path=CORPUS, seed=DEFAULT_SEED, cases=64, duration_seconds=5, artifact_dir=tmp_path)
    second = run_fuzz(corpus_path=CORPUS, seed=DEFAULT_SEED, cases=64, duration_seconds=5, artifact_dir=tmp_path)
    assert first == second == {"accepted": 0, "executed": 64, "seed": DEFAULT_SEED}
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("cases", (0, MAX_CASES + 1))
def test_fuzz_target_rejects_unbounded_case_counts(cases: int) -> None:
    """Prevent local or CI callers from expanding the deterministic target unboundedly."""
    with pytest.raises(ValueError, match="cases must be"):
        run_fuzz(corpus_path=CORPUS, cases=cases, duration_seconds=5)
