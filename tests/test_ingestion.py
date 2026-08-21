from __future__ import annotations

import pandas as pd
import pytest

from src.data.ingestion import _canonical_frame, load_welfake, split_frame, validate_frame
from src.features.text import TfidfTextPipeline, clean_text


def make_frame() -> pd.DataFrame:
    rows = []
    for index in range(20):
        rows.append(
            {
                "id": str(index),
                "title": f"Title {index}",
                "text": f"Article text {index} with distinct token {index}",
                "label": index % 2,
                "dataset": "fixture",
            }
        )
    return _canonical_frame(rows)


def test_welfake_labels_are_normalized(tmp_path):
    source = tmp_path / "WELFake_Dataset.csv"
    pd.DataFrame(
        {
            "Serial no.": [0, 1, 2, 3],
            "Title": ["fake", "real", "fake2", "real2"],
            "Text": ["fabricated", "verified", "invented", "documented"],
            "Label": [0, 1, 0, 1],
        }
    ).to_csv(source, index=False)
    frame = load_welfake(source)
    assert frame["label"].tolist() == [1, 0, 1, 0]


def test_clean_text_removes_urls_and_normalizes_whitespace():
    assert clean_text("  Hello https://example.com  <b>world</b> ") == "hello world"


def test_split_is_stratified_and_disjoint():
    frame = make_frame()
    splits, manifest = split_frame(frame, seed=42)
    assert sum(len(value) for value in splits.values()) == len(frame)
    assert len(set(splits["train"]["id"]).intersection(splits["test"]["id"])) == 0
    assert manifest.train_count == 14
    assert manifest.validation_count == 3
    assert manifest.test_count == 3
    assert set(splits["train"]["label"]) == {0, 1}


def test_validation_rejects_single_class():
    frame = make_frame()
    frame["label"] = 0
    with pytest.raises(ValueError):
        validate_frame(frame)


def test_tfidf_requires_fit_before_transform():
    pipeline = TfidfTextPipeline(min_df=1, max_features=100)
    with pytest.raises(RuntimeError):
        pipeline.transform(["unfitted"])
    matrix = pipeline.fit_transform(["real article", "fake article"])
    assert matrix.shape[0] == 2
    assert pipeline.transform(["new article"]).shape[1] == matrix.shape[1]


def test_normalize_text_strips_publication_dateline_and_byline() -> None:
    from src.data.ingestion import normalize_text

    assert normalize_text("WASHINGTON (Reuters) - The report was released.") == "The report was released."
    assert normalize_text("By Jane Doe - The report was released.") == "The report was released."


def test_near_duplicate_minhash_groups_are_removed_before_split() -> None:
    from src.data.ingestion import remove_near_duplicates

    frame = make_frame()
    frame.loc[1, "content"] = frame.loc[0, "content"] + " additional syndicated sentence"
    filtered, removed = remove_near_duplicates(frame, threshold=0.5)
    assert removed >= 1
    assert len(filtered) < len(frame)


def test_tfidf_empty_vocabulary_contains_diagnostics() -> None:
    pipeline = TfidfTextPipeline(min_df=2)
    with pytest.raises(ValueError, match=r"fold_size=2.*unique_token_count=0"):
        pipeline.fit(["!!!", "???"])
