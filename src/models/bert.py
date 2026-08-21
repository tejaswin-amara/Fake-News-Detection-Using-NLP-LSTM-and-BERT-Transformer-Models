"""Fine-tuning utilities for ``bert-base-uncased``.

Compliant with CO1/M1 and the project deep-learning requirements. References
SRC-012 and SRC-013 in docs/sources.md. Tokenization uses dynamic padding in the
collator rather than padding every example to the maximum length during storage.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class BertConfig:
    model_name: str = "bert-base-uncased"
    epochs: int = 3
    learning_rate: float = 2e-5
    warmup_ratio: float = 0.10
    max_grad_norm: float = 1.0
    max_length: int = 512
    batch_size: int = 8
    fp16: bool | None = None
    offline_root: str | None = None
    require_safetensors: bool = True


def validate_offline_bundle(model_path: str | Path, require_safetensors: bool = True) -> Path:
    """Validate the immutable local Hugging Face bundle before loading it."""
    root = Path(model_path)
    if not root.is_dir():
        raise FileNotFoundError(f"Offline BERT bundle does not exist: {root}")
    required = {"config.json", "vocab.txt"}
    if require_safetensors:
        required.add("model.safetensors")
    missing = sorted(name for name in required if not (root / name).is_file())
    if missing:
        raise FileNotFoundError(f"Offline BERT bundle is missing required files: {missing}")
    try:
        config_payload = json.loads((root / "config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Offline BERT config.json is not valid JSON") from exc
    if not isinstance(config_payload, dict) or config_payload.get("model_type") not in {"bert", None}:
        raise ValueError("Offline BERT bundle config.json is not a BERT configuration")
    return root


def load_components(config: BertConfig):
    """Load tokenizer and sequence-classification model strictly from local files."""
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install transformers to use the BERT path") from exc
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    model_root = validate_offline_bundle(config.offline_root or config.model_name, config.require_safetensors)
    tokenizer = AutoTokenizer.from_pretrained(str(model_root), use_fast=True, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(str(model_root), num_labels=2, local_files_only=True, use_safetensors=config.require_safetensors)
    return tokenizer, model


def tokenize_dataset(
    texts: list[str], labels: list[int], tokenizer: Any, max_length: int = 512
) -> Any:
    try:
        from datasets import Dataset  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install datasets to use the BERT data path") from exc
    dataset = Dataset.from_dict({"text": texts, "labels": labels})

    def tokenize(batch: dict[str, list[str]]) -> dict[str, Any]:
        return tokenizer(batch["text"], truncation=True, max_length=max_length, padding=False)

    return dataset.map(tokenize, batched=True, remove_columns=["text"])


def resolve_fp16(config: BertConfig) -> bool:
    """Enable mixed precision only when the runtime has a CUDA accelerator."""
    try:
        import torch
    except ImportError:
        return False
    return bool(torch.cuda.is_available() and config.fp16 is not False)


def build_training_arguments(config: BertConfig, output_dir: str | Path, train_size: int) -> Any:
    try:
        from transformers import TrainingArguments  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install transformers to use the BERT training path") from exc
    steps_per_epoch = max(1, train_size // config.batch_size)
    use_fp16 = resolve_fp16(config)
    return TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.epochs,
        learning_rate=config.learning_rate,
        warmup_steps=int(steps_per_epoch * config.epochs * config.warmup_ratio),
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        weight_decay=0.01,
        optim="adamw_torch",
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=use_fp16,
        max_grad_norm=config.max_grad_norm,
        save_safetensors=True,
        logging_strategy="steps",
        logging_steps=50,
        report_to="none",
        seed=42,
    )


def train_bert(
    train_dataset: Any,
    validation_dataset: Any,
    config: BertConfig,
    output_dir: str | Path,
) -> Any:
    """Fine-tune with AdamW, warmup, clipping, and dynamic padding."""
    try:
        from transformers import DataCollatorWithPadding, Trainer  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install transformers to use the BERT training path") from exc
    tokenizer, model = load_components(config)
    use_fp16 = resolve_fp16(config)
    collator = DataCollatorWithPadding(
        tokenizer=tokenizer, pad_to_multiple_of=8 if use_fp16 else None
    )
    args = build_training_arguments(config, output_dir, len(train_dataset))
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=collator,
        tokenizer=tokenizer,
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    return trainer


class BertArtifactAdapter:
    """Offline BERT serving adapter matching the common n x 2 probability contract."""

    def __init__(self, trainer: Any, tokenizer: Any, max_length: int = 512) -> None:
        self.trainer = trainer
        self.tokenizer = tokenizer
        self.max_length = max_length

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        dataset = tokenize_dataset(texts, [0] * len(texts), self.tokenizer, self.max_length)
        return predict_proba(self.trainer, dataset)


def predict_proba(trainer: Any, dataset: Any) -> np.ndarray:
    logits = np.asarray(trainer.predict(dataset).predictions)
    logits = logits - logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    return probabilities
