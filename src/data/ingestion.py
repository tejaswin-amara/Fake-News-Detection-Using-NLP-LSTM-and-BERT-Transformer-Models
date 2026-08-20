"""Dataset ingestion and leakage-safe splitting.

This module is compliant with M1/CO1: it makes the raw-data-to-training-data
boundary explicit and records provenance before learned feature transforms are fit.
Dataset references: SRC-001, SRC-002, and SRC-003 in docs/sources.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

INTERNAL_LABELS = {"real": 0, "fake": 1}
_REQUIRED_COLUMNS = {"id", "title", "text", "label", "dataset"}


@dataclass(frozen=True)
class SplitManifest:
    seed: int
    train_size: float
    validation_size: float
    test_size: float
    train_count: int
    validation_count: int
    test_count: int
    train_label_counts: dict[str, int]
    validation_label_counts: dict[str, int]
    test_label_counts: dict[str, int]
    source_files: list[str]
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _stable_id(dataset: str, title: str, text: str, row_number: int) -> str:
    payload = f"{dataset}\x1f{title}\x1f{text}\x1f{row_number}".encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()[:24]


def normalize_text(value: object) -> str:
    """Normalize a raw cell without learning from any split."""
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _canonical_frame(rows: Iterable[dict[str, object]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=sorted(_REQUIRED_COLUMNS))
    if frame.empty:
        return pd.DataFrame(columns=sorted(_REQUIRED_COLUMNS))
    frame["title"] = frame["title"].map(normalize_text)
    frame["text"] = frame["text"].map(normalize_text)
    frame["label"] = pd.to_numeric(frame["label"], errors="coerce").astype("Int64")
    frame["id"] = frame["id"].astype(str)
    frame["dataset"] = frame["dataset"].astype(str)
    frame["content"] = (frame["title"].str.strip() + "\n" + frame["text"].str.strip()).str.strip()
    frame["content_hash"] = frame["content"].map(
        lambda value: hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()
    )
    frame = frame[frame["content"].str.len().gt(0)].copy()
    frame = frame[frame["label"].isin([0, 1])].copy()
    return frame.reset_index(drop=True)


def load_isot(path: str | Path) -> pd.DataFrame:
    """Load ISOT's Fake.csv and True.csv and normalize to 0=real, 1=fake."""
    root = Path(path)
    fake_path = root / "Fake.csv" if root.is_dir() else root
    true_path = root / "True.csv" if root.is_dir() else root.with_name("True.csv")
    if not fake_path.exists() or not true_path.exists():
        raise FileNotFoundError("ISOT expects both Fake.csv and True.csv in the supplied directory")
    fake = pd.read_csv(fake_path, encoding="utf-8", on_bad_lines="skip")
    real = pd.read_csv(true_path, encoding="utf-8", on_bad_lines="skip")
    rows: list[dict[str, object]] = []
    for index, row in fake.iterrows():
        rows.append(
            {
                "id": _stable_id("isot", row.get("title", ""), row.get("text", ""), index),
                "title": row.get("title", ""),
                "text": row.get("text", ""),
                "label": INTERNAL_LABELS["fake"],
                "dataset": "isot",
            }
        )
    offset = len(fake)
    for index, row in real.iterrows():
        rows.append(
            {
                "id": _stable_id("isot", row.get("title", ""), row.get("text", ""), offset + index),
                "title": row.get("title", ""),
                "text": row.get("text", ""),
                "label": INTERNAL_LABELS["real"],
                "dataset": "isot",
            }
        )
    return _canonical_frame(rows)


def load_welfake(path: str | Path) -> pd.DataFrame:
    """Load WELFake CSV and normalize source labels to 0=real, 1=fake.

    The Zenodo record documents its published convention as 0=fake and 1=real;
    this adapter intentionally inverts that convention for the project contract.
    """
    csv_path = Path(path)
    if csv_path.is_dir():
        candidates = list(csv_path.glob("WELFake*.csv")) + list(csv_path.glob("*.csv"))
        if not candidates:
            raise FileNotFoundError("No WELFake CSV found in the supplied directory")
        csv_path = candidates[0]
    frame = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
    columns = {str(column).strip().lower(): column for column in frame.columns}
    title_column = columns.get("title")
    text_column = columns.get("text")
    label_column = columns.get("label")
    if title_column is None or text_column is None or label_column is None:
        raise ValueError("WELFake input must contain Title, Text, and Label columns")
    rows: list[dict[str, object]] = []
    for index, row in frame.iterrows():
        source_label = pd.to_numeric(row[label_column], errors="coerce")
        if pd.isna(source_label) or int(source_label) not in (0, 1):
            continue
        rows.append(
            {
                "id": _stable_id("welfake", row[title_column], row[text_column], index),
                "title": row[title_column],
                "text": row[text_column],
                "label": 1 - int(source_label),
                "dataset": "welfake",
            }
        )
    return _canonical_frame(rows)


def validate_frame(frame: pd.DataFrame) -> dict[str, object]:
    missing = sorted(_REQUIRED_COLUMNS.difference(frame.columns))
    if missing:
        raise ValueError(f"Canonical frame is missing columns: {missing}")
    if frame.empty:
        raise ValueError("Canonical frame is empty after validation")
    labels = set(frame["label"].dropna().astype(int).unique())
    if not labels.issubset({0, 1}) or len(labels) < 2:
        raise ValueError(f"Expected both binary labels 0 and 1, received {sorted(labels)}")
    duplicate_count = int(frame["content_hash"].duplicated(keep="first").sum())
    empty_count = int(frame["content"].str.len().eq(0).sum())
    return {
        "rows": int(len(frame)),
        "label_counts": {
            str(k): int(v) for k, v in frame["label"].value_counts().sort_index().items()
        },
        "duplicate_content_rows": duplicate_count,
        "empty_content_rows": empty_count,
        "datasets": {str(k): int(v) for k, v in frame["dataset"].value_counts().items()},
    }


def deduplicate(frame: pd.DataFrame) -> pd.DataFrame:
    """Remove exact normalized-content duplicates before splitting."""
    return frame.drop_duplicates(subset=["content_hash"], keep="first").reset_index(drop=True)


def split_frame(
    frame: pd.DataFrame,
    seed: int = 42,
    train_size: float = 0.70,
    validation_size: float = 0.15,
    test_size: float = 0.15,
) -> tuple[dict[str, pd.DataFrame], SplitManifest]:
    """Create a deterministic stratified three-way split.

    No feature transformer is fit here. This keeps splitting upstream of TF-IDF,
    vocabulary, embedding reduction, clustering, anomaly detection, and calibration.
    """
    total = train_size + validation_size + test_size
    if abs(total - 1.0) > 1e-9:
        raise ValueError("train_size + validation_size + test_size must equal 1.0")
    validate_frame(frame)
    clean = deduplicate(frame)
    train, remainder = train_test_split(
        clean, test_size=(validation_size + test_size), random_state=seed, stratify=clean["label"]
    )
    relative_test = test_size / (validation_size + test_size)
    validation, test = train_test_split(
        remainder, test_size=relative_test, random_state=seed, stratify=remainder["label"]
    )
    splits = {
        "train": train.reset_index(drop=True),
        "validation": validation.reset_index(drop=True),
        "test": test.reset_index(drop=True),
    }
    manifest = SplitManifest(
        seed=seed,
        train_size=train_size,
        validation_size=validation_size,
        test_size=test_size,
        train_count=len(splits["train"]),
        validation_count=len(splits["validation"]),
        test_count=len(splits["test"]),
        train_label_counts={
            str(k): int(v) for k, v in splits["train"]["label"].value_counts().sort_index().items()
        },
        validation_label_counts={
            str(k): int(v)
            for k, v in splits["validation"]["label"].value_counts().sort_index().items()
        },
        test_label_counts={
            str(k): int(v) for k, v in splits["test"]["label"].value_counts().sort_index().items()
        },
        source_files=[],
        notes=[
            "Exact normalized-content duplicates removed before splitting.",
            "No learned feature transform fitted in this function.",
        ],
    )
    return splits, manifest


def save_splits(
    splits: dict[str, pd.DataFrame], manifest: SplitManifest, output_dir: str | Path
) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, split in splits.items():
        split.to_csv(output / f"{name}.csv", index=False)
    (output / "split_manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2), encoding="utf-8"
    )


def load_dataset(dataset: str, path: str | Path) -> pd.DataFrame:
    dataset_key = dataset.lower()
    if dataset_key == "isot":
        return load_isot(path)
    if dataset_key == "welfake":
        return load_welfake(path)
    raise ValueError("dataset must be either 'isot' or 'welfake'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest and split ISOT or WELFake data")
    parser.add_argument("--dataset", choices=["isot", "welfake"], required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--output", default="data/processed")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    frame = load_dataset(args.dataset, args.path)
    quality = validate_frame(frame)
    splits, manifest = split_frame(frame, seed=args.seed)
    manifest = SplitManifest(**{**manifest.to_dict(), "source_files": [str(args.path)]})
    save_splits(splits, manifest, args.output)
    print(json.dumps({"quality": quality, "manifest": manifest.to_dict()}, indent=2))


if __name__ == "__main__":
    main()
