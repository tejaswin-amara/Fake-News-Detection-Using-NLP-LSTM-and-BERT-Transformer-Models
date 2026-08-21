from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.claimreview import (
    _record_from_review,
    is_english_claim,
    map_binary_rating,
    parse_feed,
    temporal_split,
)


def _review(claim: str, rating: str, published: str, url: str) -> dict[str, object]:
    return {
        "author": {"name": "Example Fact Checker"},
        "claimReviewed": claim,
        "datePublished": published,
        "inLanguage": "en",
        "reviewRating": {"alternateName": rating},
        "sdLicense": "https://creativecommons.org/licenses/by/4.0/",
        "url": url,
    }


def test_binary_rating_mapping_excludes_ambiguous_ratings() -> None:
    assert map_binary_rating("True") == (0, "real")
    assert map_binary_rating("FALSE") == (1, "fake")
    assert map_binary_rating("Mostly False") is None
    assert map_binary_rating("Misleading") is None


def test_english_filter_uses_declared_language_or_conservative_fallback() -> None:
    assert is_english_claim("The government announced a policy for the public", "en")
    assert not is_english_claim("The government announced a policy for the public", "fa")
    assert is_english_claim("This is a statement that was shared on the internet", "")
    assert not is_english_claim("این یک ادعای فارسی است", "")


def test_record_requires_current_attributable_unambiguous_claim() -> None:
    accepted, reason = _record_from_review(
        _review("The city opened a new school", "False", "2026-08-20", "https://example.test/review"),
        cutoff=pd.Timestamp("2024-08-21").date(),
        fetched_at_utc="2026-08-21T00:00:00+00:00",
    )
    assert reason is None
    assert accepted is not None
    assert accepted["label"] == 1
    assert "The city opened" in str(accepted["text"])
    assert "False" not in str(accepted["text"])
    future, future_reason = _record_from_review(
        _review("The city opened a new school", "False", "9999-01-01", "https://example.test/future"),
        cutoff=pd.Timestamp("2024-08-21").date(),
        maximum_review_date=pd.Timestamp("2026-08-21").date(),
        fetched_at_utc="2026-08-21T00:00:00+00:00",
    )
    assert future is None
    assert future_reason == "future_review_date"


def test_parse_feed_streams_claimreview_objects_and_excludes_ambiguous_rows(tmp_path: Path) -> None:
    payload = {
        "dataFeedElement": [
            {"item": [_review("This claim is false", "False", "2026-08-20", "https://example.test/1")]},
            {"item": [_review("This claim is nuanced", "Mostly False", "2026-08-20", "https://example.test/2")]},
        ]
    }
    path = tmp_path / "feed.json"
    path.write_text(__import__("json").dumps(payload), encoding="utf-8")
    frame, exclusions, total = parse_feed(path, cutoff=pd.Timestamp("2024-08-21").date(), fetched_at_utc="2026-08-21T00:00:00+00:00")
    assert total == 2
    assert len(frame) == 1
    assert exclusions["ambiguous_or_unsupported_rating"] == 1


def test_temporal_split_prevents_content_hash_overlap_and_preserves_time_order() -> None:
    rows = []
    for index in range(60):
        label = index % 2
        if index < 30:
            review_date = f"2022-01-{(index % 28) + 1:02d}"
        elif index < 46:
            review_date = f"2024-01-{(index % 16) + 1:02d}"
        else:
            review_date = f"2025-01-{(index % 14) + 1:02d}"
        rows.append(
            {
                "id": f"id-{index}",
                "content_hash": f"hash-{index}",
                "label": label,
                "review_date": review_date,
            }
        )
    splits, boundaries, unbalanced = temporal_split(
        pd.DataFrame(rows),
        validation_start=pd.Timestamp("2023-08-21").date(),
        test_start=pd.Timestamp("2024-08-21").date(),
        minimum_per_label=2,
        seed=42,
    )
    assert not (set(splits["train"]["content_hash"]) & set(splits["test"]["content_hash"]))
    assert boundaries["train_end"] <= boundaries["validation_start"] <= boundaries["test_start"]
    assert all(counts["0"] == counts["1"] for counts in ({str(label): count for label, count in split["label"].value_counts().items()} for split in splits.values()))
    assert unbalanced["test"]["0"] >= 2
