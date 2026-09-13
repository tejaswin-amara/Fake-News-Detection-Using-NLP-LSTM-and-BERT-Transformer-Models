"""Coverage-guided, in-memory fuzzing of bounded synthetic ClaimReview metadata.

The harness never fetches, logs, prints, or persists fuzz inputs. Each candidate
is synthesized from opaque fuzzer bytes and is discarded after parser execution.
"""

from __future__ import annotations

import atheris

with atheris.instrument_imports():
    from datetime import date
    from typing import Any

    from src.data.claimreview import _record_from_review


MAX_STRING_LENGTH = 64
MAX_COLLECTION_ITEMS = 3


def _scalar(data: atheris.FuzzedDataProvider) -> object:
    """Create only bounded synthetic scalar values from a fuzzer input."""
    choice = data.ConsumeIntInRange(0, 5)
    if choice == 0:
        return None
    if choice == 1:
        return data.ConsumeBool()
    if choice == 2:
        return data.ConsumeIntInRange(-1_000_000, 1_000_000)
    if choice == 3:
        return data.ConsumeUnicodeNoSurrogates(MAX_STRING_LENGTH)
    if choice == 4:
        return "https:" + "//synthetic.invalid/" + data.ConsumeUnicodeNoSurrogates(16)
    return "2026-08-22"


def _value(data: atheris.FuzzedDataProvider, depth: int = 0) -> Any:
    """Create bounded nested metadata while preventing recursive growth."""
    if depth >= 2 or data.ConsumeBool():
        return _scalar(data)
    if data.ConsumeBool():
        return [_value(data, depth + 1) for _ in range(data.ConsumeIntInRange(0, MAX_COLLECTION_ITEMS))]
    return {
        data.ConsumeUnicodeNoSurrogates(16): _value(data, depth + 1)
        for _ in range(data.ConsumeIntInRange(0, MAX_COLLECTION_ITEMS))
    }


def TestOneInput(input_bytes: bytes) -> None:
    """Exercise the parser with malformed metadata and discard all candidate output."""
    data = atheris.FuzzedDataProvider(input_bytes)
    review = {
        "claimReviewed": "synthetic fuzz input " + data.ConsumeUnicodeNoSurrogates(MAX_STRING_LENGTH),
        "url": "https:" + "//synthetic.invalid/review",
        "datePublished": "2026-08-22",
        "inLanguage": "en",
        "reviewRating": {"alternateName": "false"},
        "author": {"name": "Synthetic publisher"},
        "itemReviewed": _value(data),
        "sdLicense": _value(data),
    }
    _record_from_review(
        review,
        cutoff=date(2020, 1, 1),
        maximum_review_date=date(2030, 1, 1),
        fetched_at_utc="2026-08-22T00:00:00+00:00",
    )


def main() -> None:
    """Launch the Atheris engine without emitting fuzz input or candidate metadata."""
    atheris.Setup([], TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
