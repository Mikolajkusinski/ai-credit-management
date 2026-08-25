"""Rysunek 4.3 — Krzywe uczenia modelu LSTM W3 (accuracy + loss).

Wariant finalny (3, 3): retrening identyczny z main.py (seed 42, skalery
fitowane wyłącznie na treningu) prowadzony WYŁĄCZNIE po historię uczenia —
model nie jest zapisywany, artefakty produkcyjne pozostają nietknięte.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # thesis_figures/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # ml-learing-center/

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, cached_json

apply_style()
HERE = Path(__file__).resolve().parents[2]


@cached_json("lstm_history_w3")
def train_lstm_and_get_history():
    import pandas as pd
    import tensorflow as tf
    from sklearn.model_selection import train_test_split
    from sklearn.utils.class_weight import compute_class_weight
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential
    from features import prepare_lstm_sequences
    from sliding_window import WINDOW_DEFS

    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    y = df["Default"]
    W3 = WINDOW_DEFS[3]

    # Identyczny protokół co main.py: split indeksów, skalery na treningu.
    idx = np.arange(len(df))
    idx_tmp, _ = train_test_split(idx, test_size=0.2, stratify=y, random_state=42)
    idx_tr, _ = train_test_split(idx_tmp, test_size=0.25, stratify=y.iloc[idx_tmp], random_state=42)
    _, scalers = prepare_lstm_sequences(df.iloc[idx_tr], W3)
    X_seq, _ = prepare_lstm_sequences(df, W3, scalers=scalers)
    Xs_tmp, _, ys_tmp, _ = train_test_split(X_seq, y, test_size=0.2, stratify=y, random_state=42)
    Xs_tr, _, ys_tr, _ = train_test_split(Xs_tmp, ys_tmp, test_size=0.25, stratify=ys_tmp, random_state=42)

    tf.keras.utils.set_random_seed(42)
    model = Sequential([
        Input(shape=(3, 3)),
        LSTM(32),
        Dropout(0.3),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=["accuracy", tf.keras.metrics.AUC(name="auc")])

    cw = compute_class_weight(class_weight="balanced", classes=np.array([0, 1]), y=ys_tr.values)
    hist = model.fit(
        Xs_tr, ys_tr, validation_split=0.2,
        epochs=60, batch_size=256,
        class_weight={0: float(cw[0]), 1: float(cw[1])},
        callbacks=[
            EarlyStopping(monitor="val_auc", mode="max", patience=5, restore_best_weights=True),
            ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=3, min_lr=1e-5),
        ],
        verbose=0,
    )
    return {k: [float(v) for v in vals] for k, vals in hist.history.items()}


def build():
    hist = train_lstm_and_get_history()
    epochs = list(range(1, len(hist["loss"]) + 1))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    c_train, c_val = MODEL_COLORS["LSTM"], "#c9772e"

    acc_key = "accuracy" if "accuracy" in hist else "acc"
    ax1.plot(epochs, hist[acc_key], color=c_train, linewidth=2, marker="o",
             markersize=4, label="trening")
    ax1.plot(epochs, hist[f"val_{acc_key}"], color=c_val, linewidth=2, marker="s",
             markersize=4, label="walidacja")
    ax1.set_xlabel("Epoka")
    ax1.set_ylabel("Accuracy")
    ax1.set_title("Krzywa dokładności (accuracy)")
    ax1.legend()

    ax2.plot(epochs, hist["loss"], color=c_train, linewidth=2, marker="o",
             markersize=4, label="trening")
    ax2.plot(epochs, hist["val_loss"], color=c_val, linewidth=2, marker="s",
             markersize=4, label="walidacja")
    ax2.set_xlabel("Epoka")
    ax2.set_ylabel("Binary crossentropy")
    ax2.set_title("Krzywa funkcji straty (loss)")
    ax2.legend()

    fig.suptitle("Krzywe uczenia modelu LSTM — W3 (3×3), seed = 42",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="3", name="krzywe_uczenia_lstm",
                comment="Krzywe uczenia finalnego LSTM W3 (EarlyStopping na val_auc); retrening deterministyczny wyłącznie po history, model niezapisywany.")
    plt.close(fig)
