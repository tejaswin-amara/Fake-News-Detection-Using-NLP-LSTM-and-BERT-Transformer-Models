"""Bounded in-memory fuzzing for ClaimReview metadata parsing.

The target only constructs synthetic bounded strings and metadata. It never fetches,
logs, prints, or writes input payloads; a failure artifact contains only the seed,
case number, and exception class needed for deterministic reproduction.
"""

from __future__ import annotations

import argparse
import json
import random
import string
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.claimreview import _record_from_review

DEFAULT_SEED = 20_260_822
MAX_CASES = 2_048
MAX_DURATION_SECONDS = 60
MAX_DEPTH = 3
MAX_STRING_LENGTH = 64
_KEYS = (
    "claimReviewed",
    "url",
    "datePublished",
    "inLanguage",
    "reviewRating",
    "author",
    "itemReviewed",
    "sdLicense",
)


def load_seed_corpus(path: Path) -> list[dict[str, Any]]:
    """Load the versioned synthetic metadata corpus without retaining source text."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("Fuzz corpus must be a JSON list of metadata objects")
    return payload


def _synthetic_string(generator: random.Random) -> str:
    alphabet = string.ascii_letters + string.digits + " _-/.<>\u0000"
    return "".join(generator.choice(alphabet) for _ in range(generator.randrange(MAX_STRING_LENGTH + 1)))


def _synthetic_value(generator: random.Random, depth: int = 0) -> Any:
    scalar_values: tuple[Any, ...] = (None, True, False, -1, 0, 1, "", _synthetic_string(generator))
    if depth >= MAX_DEPTH or generator.randrange(4) != 0:
        return generator.choice(scalar_values)
    if generator.choice((True, False)):
        return [_synthetic_value(generator, depth + 1) for _ in range(generator.randrange(4))]
    return {
        generator.choice(_KEYS): _synthetic_value(generator, depth + 1)
        for _ in range(generator.randrange(4))
    }


def _synthetic_review(generator: random.Random) -> dict[str, Any]:
    return {key: _synthetic_value(generator) for key in _KEYS if generator.choice((True, False))}


def _exercise(review: dict[str, Any]) -> bool:
    """Exercise parser acceptance/rejection without persisting the candidate record."""
    record, reason = _record_from_review(
        review,
        cutoff=date(2020, 1, 1),
        maximum_review_date=date(2030, 1, 1),
        fetched_at_utc="2026-08-22T00:00:00+00:00",
    )
    if record is None:
        assert isinstance(reason, str) and reason
        return False
    assert reason is None
    assert set(("id", "content_hash", "label", "review_date")) <= set(record)
    return True


def run_fuzz(
    *,
    corpus_path: Path,
    seed: int = DEFAULT_SEED,
    cases: int = MAX_CASES,
    duration_seconds: int = MAX_DURATION_SECONDS,
    artifact_dir: Path | None = None,
) -> dict[str, int]:
    """Run a reproducible, time- and count-bounded metadata fuzz campaign."""
    if not 1 <= cases <= MAX_CASES:
        raise ValueError(f"cases must be between 1 and {MAX_CASES}")
    if not 1 <= duration_seconds <= MAX_DURATION_SECONDS:
        raise ValueError(f"duration_seconds must be between 1 and {MAX_DURATION_SECONDS}")

    generator = random.Random(seed)
    corpus = load_seed_corpus(corpus_path)
    deadline = time.monotonic() + duration_seconds
    accepted = 0
    executed = 0
    for case_number, review in enumerate([*corpus, *(_synthetic_review(generator) for _ in range(cases))]):
        if case_number >= cases or time.monotonic() >= deadline:
            break
        try:
            accepted += int(_exercise(review))
        except Exception as exc:
            if artifact_dir is not None:
                artifact_dir.mkdir(parents=True, exist_ok=True)
                (artifact_dir / "failure.json").write_text(
                    json.dumps(
                        {"seed": seed, "case_number": case_number, "exception_type": type(exc).__name__},
                        sort_keys=True,
                    ),
                    encoding="utf-8",
                )
            raise
        executed += 1
    return {"accepted": accepted, "executed": executed, "seed": seed}


def main() -> None:
    """Execute the target without printing synthetic payloads."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path("fuzz/corpus/claimreview_metadata.json"))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--cases", type=int, default=MAX_CASES)
    parser.add_argument("--duration-seconds", type=int, default=MAX_DURATION_SECONDS)
    parser.add_argument("--artifact-dir", type=Path, default=Path(".fuzz-artifacts"))
    arguments = parser.parse_args()
    summary = run_fuzz(
        corpus_path=arguments.corpus,
        seed=arguments.seed,
        cases=arguments.cases,
        duration_seconds=arguments.duration_seconds,
        artifact_dir=arguments.artifact_dir,
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
