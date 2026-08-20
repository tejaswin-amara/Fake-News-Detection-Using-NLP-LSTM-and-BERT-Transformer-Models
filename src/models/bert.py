"""Fine-tuning utilities for ``bert-base-uncased``.

Compliant with CO1/M1 and the project deep-learning requirements. References
SRC-012 and SRC-013 in docs/sources.md. Tokenization uses dynamic padding in the
collator rather than padding every example to the maximum length during storage.
"""

from __future__ import annotations

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
    fp16: bool = True


def load_components(config: BertConfig):
    """Load tokenizer and sequence-classification model lazily."""
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install transformers to use the BERT path") from exc
    tokenizer = AutoTokenizer.from_pretrained(config.model_name, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(config.model_name, num_labels=2)
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


def build_training_arguments(config: BertConfig, output_dir: str | Path, train_size: int) -> Any:
    try:
        from transformers import TrainingArguments  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install transformers to use the BERT training path") from exc
    steps_per_epoch = max(1, train_size // config.batch_size)
    return TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.epochs,
        learning_rate=config.learning_rate,
        warmup_steps=int(steps_per_epoch * config.epochs * config.warmup_ratio),
        per_device_train_batch_size=config.batch_size,
        per_device_eval_batch_size=config.batch_size,
        weight_decay=0.01,
        optim="adamw_torch",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=config.fp16,
        max_grad_norm=config.max_grad_norm,
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
    collator = DataCollatorWithPadding(
        tokenizer=tokenizer, pad_to_multiple_of=8 if config.fp16 else None
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


def predict_proba(trainer: Any, dataset: Any) -> np.ndarray:
    logits = np.asarray(trainer.predict(dataset).predictions)
    logits = logits - logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    return probabilities
