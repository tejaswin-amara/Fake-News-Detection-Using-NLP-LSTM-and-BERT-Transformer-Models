"""Current ClaimReview dataset collection with provenance and temporal split safeguards.

The collector intentionally creates a fact-checked *claims* dataset. It does not
scrape full publisher articles, infer labels, or treat a model label as a factual
verdict. Labels preserve an originating publisher's unambiguous ClaimReview rating.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import unicodedata
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import ijson
import pandas as pd
import yaml

from src.data.ingestion import normalize_text, remove_near_duplicates

SOURCE_ID = "SRC-045"
DEFAULT_FEED_URL = "https://storage.googleapis.com/datacommons-feeds/factcheck/latest/data.json"
REAL_RATINGS = frozenset({"accurate", "correct", "true", "verified"})
FAKE_RATINGS = frozenset({"fake", "false", "incorrect", "pants on fire", "wrong"})
ENGLISH_CUES = frozenset(
    {
        "a", "an", "and", "are", "at", "for", "from", "has", "in", "is", "of", "on", "the",
        "that", "this", "to", "was", "will", "with",
    }
)


@dataclass(frozen=True)
class CollectionManifest:
    feed_url: str
    feed_sha256: str
    fetched_at_utc: str
    max_age_days: int
    raw_feed_path: str
    response_content_type: str
    response_etag: str | None
    response_last_modified: str | None
    source_id: str


@dataclass(frozen=True)
class DatasetReleaseManifest:
    collection: CollectionManifest
    exclusions: dict[str, int]
    label_counts: dict[str, int]
    near_duplicates_removed: int
    release_id: str
    split_counts: dict[str, int]
    split_label_counts: dict[str, dict[str, int]]
    unbalanced_split_label_counts: dict[str, dict[str, int]]
    temporal_boundaries: dict[str, str]
    total_candidates: int
    retained_records: int


def normalized_rating(value: object) -> str:
    """Canonicalize a publisher rating without deciding its meaning."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).casefold()).strip()


def map_binary_rating(value: object) -> tuple[int, str] | None:
    """Map only unambiguous English publisher ratings to the project labels."""
    rating = normalized_rating(value)
    if rating in REAL_RATINGS:
        return (0, "real")
    if rating in FAKE_RATINGS:
        return (1, "fake")
    return None


def is_english_claim(claim: str, declared_language: object) -> bool:
    """Use declared language when present; otherwise apply a conservative fallback."""
    language = str(declared_language or "").strip().casefold()
    if language:
        return language == "en" or language.startswith("en-")
    letters = re.findall(r"[A-Za-z]", claim)
    if len(letters) < 20:
        return False
    ascii_ratio = len(letters) / max(1, len(re.findall(r"\w", claim, flags=re.UNICODE)))
    words = {word.casefold() for word in re.findall(r"[A-Za-z]{1,}", claim)}
    return ascii_ratio >= 0.85 and bool(words & ENGLISH_CUES)


def _iso_date(value: object) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _organization_name(value: object) -> str:
    if isinstance(value, Mapping):
        return normalize_text(value.get("name", ""))
    if isinstance(value, list):
        return ", ".join(filter(None, (_organization_name(item) for item in value)))
    return normalize_text(value)


def _rating_name(review: Mapping[str, Any]) -> str:
    rating = review.get("reviewRating", {})
    if not isinstance(rating, Mapping):
        return ""
    return normalize_text(rating.get("alternateName") or rating.get("name") or rating.get("ratingValue"))


def _review_language(review: Mapping[str, Any]) -> object:
    item_reviewed = review.get("itemReviewed", {})
    item_language = item_reviewed.get("inLanguage", "") if isinstance(item_reviewed, Mapping) else ""
    return review.get("inLanguage") or item_language


def _record_from_review(
    review: Mapping[str, Any],
    *,
    cutoff: date,
    fetched_at_utc: str,
    maximum_review_date: date | None = None,
) -> tuple[dict[str, object] | None, str | None]:
    claim = normalize_text(review.get("claimReviewed", ""))
    if not claim:
        return None, "missing_claim"
    review_url = str(review.get("url") or "").strip()
    if not review_url.startswith(("http://", "https://")):
        return None, "missing_canonical_review_url"
    review_date = _iso_date(review.get("datePublished"))
    if review_date is None:
        return None, "missing_or_invalid_review_date"
    if review_date < cutoff:
        return None, "outside_recency_window"
    if maximum_review_date is not None and review_date > maximum_review_date:
        return None, "future_review_date"
    if not is_english_claim(claim, _review_language(review)):
        return None, "not_english"
    original_rating = _rating_name(review)
    mapped = map_binary_rating(original_rating)
    if mapped is None:
        return None, "ambiguous_or_unsupported_rating"
    label, normalized_label = mapped
    publisher = _organization_name(review.get("author"))
    if not publisher:
        return None, "missing_publisher"
    normalized_claim = normalize_text(claim).casefold()
    content_hash = hashlib.sha256(normalized_claim.encode("utf-8")).hexdigest()
    record_id = hashlib.sha256(f"{review_url}\x1f{content_hash}".encode()).hexdigest()[:24]
    item_reviewed = review.get("itemReviewed", {})
    claimant = _organization_name(item_reviewed.get("author", "") if isinstance(item_reviewed, Mapping) else "")
    return {
        "id": record_id,
        "dataset": "claimreview_current",
        "title": "",
        "text": claim,
        "content": claim,
        "content_hash": content_hash,
        "label": label,
        "normalized_label": normalized_label,
        "original_rating": original_rating,
        "publisher": publisher,
        "claimant": claimant,
        "review_url": review_url,
        "claim_url": str(item_reviewed.get("url") or "") if isinstance(item_reviewed, Mapping) else "",
        "review_date": review_date.isoformat(),
        "declared_language": str(_review_language(review) or ""),
        "source_id": SOURCE_ID,
        "source_license": str(review.get("sdLicense") or "feed_compilation_cc_by_4.0"),
        "retrieved_at_utc": fetched_at_utc,
    }, None


def fetch_feed(feed_url: str, raw_path: Path, *, timeout_seconds: int = 120) -> CollectionManifest:
    """Fetch the live public feed to a file while recording response provenance."""
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(feed_url, headers={"User-Agent": "fake-news-detection-research/1.0"})
    fetched_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    digest = hashlib.sha256()
    with urlopen(request, timeout=timeout_seconds) as response, tempfile.NamedTemporaryFile(
        mode="wb", delete=False, dir=raw_path.parent, prefix=".claimreview-"
    ) as temporary:
        content_type = str(response.headers.get("Content-Type", ""))
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")
        for chunk in iter(lambda: response.read(1024 * 1024), b""):
            digest.update(chunk)
            temporary.write(chunk)
        temporary_path = Path(temporary.name)
    shutil.move(str(temporary_path), raw_path)
    return CollectionManifest(
        feed_url=feed_url,
        feed_sha256=digest.hexdigest(),
        fetched_at_utc=fetched_at,
        max_age_days=0,
        raw_feed_path=str(raw_path),
        response_content_type=content_type,
        response_etag=etag,
        response_last_modified=last_modified,
        source_id=SOURCE_ID,
    )


def parse_feed(
    raw_path: Path,
    *,
    cutoff: date,
    fetched_at_utc: str,
    maximum_review_date: date | None = None,
) -> tuple[pd.DataFrame, Counter[str], int]:
    """Stream ClaimReview objects and retain only governed binary candidates."""
    exclusions: Counter[str] = Counter()
    rows: list[dict[str, object]] = []
    total_candidates = 0
    with raw_path.open("rb") as source:
        for review in ijson.items(source, "dataFeedElement.item.item.item"):
            if not isinstance(review, Mapping):
                exclusions["invalid_claimreview_object"] += 1
                continue
            total_candidates += 1
            record, reason = _record_from_review(
                review,
                cutoff=cutoff,
                fetched_at_utc=fetched_at_utc,
                maximum_review_date=maximum_review_date,
            )
            if record is None:
                exclusions[reason or "unknown_rejection"] += 1
                continue
            rows.append(record)
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("No governed ClaimReview records passed source, language, rating, and recency gates")
    frame = frame.drop_duplicates(subset=["content_hash"], keep="first").reset_index(drop=True)
    return frame, exclusions, total_candidates


def _downsample_to_minority(split: pd.DataFrame, *, seed: int) -> pd.DataFrame:
    """Downsample only the majority class inside an already fixed temporal split."""
    counts = split["label"].value_counts()
    target = int(counts.min())
    if target < 1:
        raise ValueError("Cannot balance a split without both labels")
    sampled = [
        group.sample(n=target, random_state=seed + int(label), replace=False)
        for label, group in split.groupby("label", sort=True)
    ]
    return pd.concat(sampled, ignore_index=True).sort_values(["review_date", "id"], kind="stable").reset_index(drop=True)


def temporal_split(
    frame: pd.DataFrame,
    *,
    validation_start: date,
    test_start: date,
    minimum_per_label: int,
    seed: int,
) -> tuple[dict[str, pd.DataFrame], dict[str, str], dict[str, dict[str, int]]]:
    """Create fixed chronological splits, then balance each split without moving time boundaries."""
    if validation_start >= test_start:
        raise ValueError("validation_start must be earlier than test_start")
    ordered = frame.copy()
    ordered["_date"] = pd.to_datetime(ordered["review_date"], utc=True, errors="coerce")
    if ordered["_date"].isna().any():
        raise ValueError("Temporal split requires valid review dates")
    ordered = ordered.sort_values(["_date", "id"], kind="stable").reset_index(drop=True)
    validation_boundary = pd.Timestamp(validation_start, tz="UTC")
    test_boundary = pd.Timestamp(test_start, tz="UTC")
    raw_splits = {
        "train": ordered.loc[ordered["_date"] < validation_boundary].drop(columns="_date").reset_index(drop=True),
        "validation": ordered.loc[(ordered["_date"] >= validation_boundary) & (ordered["_date"] < test_boundary)].drop(columns="_date").reset_index(drop=True),
        "test": ordered.loc[ordered["_date"] >= test_boundary].drop(columns="_date").reset_index(drop=True),
    }
    unbalanced_counts: dict[str, dict[str, int]] = {}
    for split_name, split in raw_splits.items():
        counts = split["label"].value_counts().to_dict()
        unbalanced_counts[split_name] = {str(label): int(count) for label, count in counts.items()}
        if min(counts.get(0, 0), counts.get(1, 0)) < minimum_per_label:
            raise ValueError(f"Temporal {split_name} split does not meet the per-label minimum of {minimum_per_label}")
    splits = {
        name: _downsample_to_minority(split, seed=seed)
        for name, split in raw_splits.items()
    }
    split_hashes = [set(split["content_hash"]) for split in splits.values()]
    if any(left & right for index, left in enumerate(split_hashes) for right in split_hashes[index + 1 :]):
        raise ValueError("Content-hash overlap detected across temporal splits")
    boundaries = {
        "train_end": str(splits["train"]["review_date"].max()),
        "validation_start": str(splits["validation"]["review_date"].min()),
        "validation_end": str(splits["validation"]["review_date"].max()),
        "test_start": str(splits["test"]["review_date"].min()),
    }
    return splits, boundaries, unbalanced_counts


def create_release(config_path: Path, *, refresh: bool = False) -> DatasetReleaseManifest:
    """Fetch, normalize, deduplicate, split, and document the configured current release."""
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    dataset = config.get("claimreview_current", {})
    release_id = str(dataset["release_id"])
    max_age_days = int(dataset["max_age_days"])
    reference_date = _iso_date(dataset.get("reference_date")) or datetime.now(UTC).date()
    cutoff = reference_date - timedelta(days=max_age_days)
    raw_path = Path(str(dataset["raw_feed_path"]))
    output_dir = Path(str(dataset["output_dir"]))
    feed_url = str(dataset.get("feed_url", DEFAULT_FEED_URL))
    if refresh or not raw_path.exists():
        collection = fetch_feed(feed_url, raw_path, timeout_seconds=int(dataset.get("timeout_seconds", 120)))
    else:
        digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        collection = CollectionManifest(
            feed_url=feed_url,
            feed_sha256=digest,
            fetched_at_utc=datetime.fromtimestamp(raw_path.stat().st_mtime, tz=UTC).replace(microsecond=0).isoformat(),
            max_age_days=max_age_days,
            raw_feed_path=str(raw_path),
            response_content_type="application/json (cached)",
            response_etag=None,
            response_last_modified=None,
            source_id=SOURCE_ID,
        )
    collection = CollectionManifest(**{**asdict(collection), "max_age_days": max_age_days})
    frame, exclusions, total_candidates = parse_feed(
        raw_path,
        cutoff=cutoff,
        fetched_at_utc=collection.fetched_at_utc,
        maximum_review_date=reference_date,
    )
    frame, removed_near_duplicates = remove_near_duplicates(
        frame,
        threshold=float(dataset.get("near_duplicate_threshold", 0.92)),
        permutations=int(dataset.get("minhash_permutations", 64)),
        bands=int(dataset.get("minhash_bands", 8)),
    )
    label_counts = {str(label): int(count) for label, count in frame["label"].value_counts().sort_index().items()}
    if set(label_counts) != {"0", "1"}:
        raise ValueError("The governed release requires both real and fake records after deduplication")
    splits, boundaries, unbalanced_counts = temporal_split(
        frame,
        validation_start=date.fromisoformat(str(dataset["validation_start"])),
        test_start=date.fromisoformat(str(dataset["test_start"])),
        minimum_per_label=int(dataset.get("minimum_per_label", 10)),
        seed=int(dataset.get("random_seed", 42)),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_dir / "master.csv", index=False)
    for name, split in splits.items():
        split.to_csv(output_dir / f"{name}.csv", index=False)
    manifest = DatasetReleaseManifest(
        collection=collection,
        exclusions=dict(sorted(exclusions.items())),
        label_counts=label_counts,
        near_duplicates_removed=removed_near_duplicates,
        release_id=release_id,
        split_counts={name: int(len(split)) for name, split in splits.items()},
        split_label_counts={
            name: {str(label): int(count) for label, count in split["label"].value_counts().sort_index().items()}
            for name, split in splits.items()
        },
        unbalanced_split_label_counts=unbalanced_counts,
        temporal_boundaries=boundaries,
        total_candidates=total_candidates,
        retained_records=int(len(frame)),
    )
    (output_dir / "release_manifest.json").write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
    raw_path.with_name("collection_manifest.json").write_text(json.dumps(asdict(collection), indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a governed current ClaimReview claims dataset")
    parser.add_argument("--config", default="configs/dataset.yaml")
    parser.add_argument("--refresh", action="store_true", help="Fetch the live feed before building the release")
    arguments = parser.parse_args()
    manifest = create_release(Path(arguments.config), refresh=arguments.refresh)
    print(json.dumps(asdict(manifest), indent=2))


if __name__ == "__main__":
    main()
