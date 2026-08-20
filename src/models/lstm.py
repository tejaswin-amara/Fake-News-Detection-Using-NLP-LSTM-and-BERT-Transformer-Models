"""GloVe-initialized Bidirectional LSTM classifier.

Compliant with the deep-learning extension requested alongside CO1/CO5. The
syllabus scope remains grounded in the handout; see SRC-004, SRC-011, and SRC-003.
TensorFlow is imported lazily so classical CPU workflows remain usable without a
GPU or downloaded embeddings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass
class LSTMConfig:
    vocab_size: int = 30_000
    embedding_dim: int = 100
    max_length: int = 400
    lstm_units: tuple[int, int] = (128, 64)
    dropout: float = 0.30
    learning_rate: float = 1e-3


def build_bilstm_model(config: LSTMConfig, embedding_matrix: np.ndarray | None = None) -> Any:
    """Build the requested embedding + SpatialDropout1D + stacked BiLSTM model."""
    try:
        import tensorflow as tf  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install tensorflow-cpu to use the BiLSTM path") from exc

    inputs = tf.keras.Input(shape=(config.max_length,), dtype="int32", name="token_ids")
    if embedding_matrix is not None:
        embedding = tf.keras.layers.Embedding(
            input_dim=embedding_matrix.shape[0],
            output_dim=embedding_matrix.shape[1],
            weights=[embedding_matrix],
            trainable=False,
            mask_zero=True,
            name="glove_embedding",
        )(inputs)
    else:
        embedding = tf.keras.layers.Embedding(
            input_dim=config.vocab_size,
            output_dim=config.embedding_dim,
            trainable=True,
            mask_zero=True,
            name="trainable_embedding",
        )(inputs)
    x = tf.keras.layers.SpatialDropout1D(config.dropout, name="spatial_dropout")(embedding)
    x = tf.keras.layers.Bidirectional(
        tf.keras.layers.LSTM(config.lstm_units[0], return_sequences=True), name="bilstm_1"
    )(x)
    x = tf.keras.layers.BatchNormalization(name="batch_norm_1")(x)
    x = tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(config.lstm_units[1]), name="bilstm_2")(
        x
    )
    x = tf.keras.layers.BatchNormalization(name="batch_norm_2")(x)
    x = tf.keras.layers.Dropout(config.dropout, name="dense_dropout")(x)
    x = tf.keras.layers.Dense(64, activation="relu", name="dense_features")(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="fake_probability")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="glove_bilstm_fake_news")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=config.learning_rate),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.AUC(name="roc_auc"),
        ],
    )
    return model


def train_bilstm(
    model: Any,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_validation: np.ndarray,
    y_validation: np.ndarray,
    output_dir: str | Path,
    epochs: int = 10,
    batch_size: int = 64,
) -> Any:
    """Train with best-checkpoint restoration and early stopping."""
    try:
        import tensorflow as tf  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install tensorflow-cpu to use the BiLSTM path") from exc
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(
            output / "bilstm_best.keras",
            monitor="val_loss",
            save_best_only=True,
            save_weights_only=False,
        ),
        tf.keras.callbacks.CSVLogger(output / "bilstm_training.csv"),
    ]
    return model.fit(
        X_train,
        y_train,
        validation_data=(X_validation, y_validation),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=2,
    )


def predict_proba(model: Any, token_ids: np.ndarray) -> np.ndarray:
    probabilities = np.asarray(model.predict(token_ids, verbose=0)).reshape(-1)
    return np.column_stack([1.0 - probabilities, probabilities])
