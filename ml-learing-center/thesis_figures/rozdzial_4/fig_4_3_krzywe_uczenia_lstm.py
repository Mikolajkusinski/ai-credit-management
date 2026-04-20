"""Rysunek 4.3 — Krzywe uczenia modelu LSTM (accuracy + loss)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, cached_json, get_lstm_sequences

apply_style()


@cached_json("lstm_history")
def train_lstm_and_get_history():
    import tensorflow as tf
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from sklearn.utils.class_weight import compute_class_weight

    X_train, _, y_train, _, _ = get_lstm_sequences()

    model = Sequential([
        Input(shape=(6, 3)),
        LSTM(32),
        Dropout(0.3),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=["accuracy", tf.keras.metrics.AUC(name="auc")])

    cw = compute_class_weight(class_weight="balanced", classes=np.array([0, 1]), y=y_train)
    cw_dict = {0: float(cw[0]), 1: float(cw[1])}

    callbacks = [
        EarlyStopping(monitor="val_auc", mode="max", patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=3, min_lr=1e-5),
    ]
    hist = model.fit(
        X_train, y_train, validation_split=0.2,
        epochs=40, batch_size=256, class_weight=cw_dict,
        callbacks=callbacks, verbose=0,
    )
    return {k: [float(v) for v in vals] for k, vals in hist.history.items()}


def build():
    hist = train_lstm_and_get_history()
    epochs = list(range(1, len(hist["loss"]) + 1))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    c_train, c_val = MODEL_COLORS["LSTM"], "#c9772e"
    # Accuracy
    acc_key = "accuracy" if "accuracy" in hist else "acc"
    val_acc_key = f"val_{acc_key}"
    ax1.plot(epochs, hist[acc_key], color=c_train, linewidth=2, marker="o", markersize=4, label="train")
    ax1.plot(epochs, hist[val_acc_key], color=c_val, linewidth=2, marker="s", markersize=4, label="walidacja")
    ax1.set_xlabel("Epoka")
    ax1.set_ylabel("Accuracy")
    ax1.set_title("Krzywa dokładności (accuracy)")
    ax1.legend(loc="lower right")
    ax1.grid(linestyle="--", alpha=0.5)

    # Loss
    ax2.plot(epochs, hist["loss"], color=c_train, linewidth=2, marker="o", markersize=4, label="train")
    ax2.plot(epochs, hist["val_loss"], color=c_val, linewidth=2, marker="s", markersize=4, label="walidacja")
    ax2.set_xlabel("Epoka")
    ax2.set_ylabel("Binary Crossentropy")
    ax2.set_title("Krzywa funkcji straty (loss)")
    ax2.legend(loc="upper right")
    ax2.grid(linestyle="--", alpha=0.5)

    fig.suptitle("Krzywe uczenia modelu LSTM", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="3", name="krzywe_uczenia_lstm",
                comment="Krzywe accuracy i loss dla LSTM (train vs walidacja) w kolejnych epokach — pozwala ocenić przeuczenie/niedouczenie i moment aktywacji EarlyStopping.")
    plt.close(fig)
