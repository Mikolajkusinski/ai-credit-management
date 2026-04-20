"""Rysunek 4.4 — Wpływ hiperparametrów LSTM na AUC walidacji."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, cached_json, get_lstm_sequences

apply_style()


def _train_once(epochs: int, batch_size: int, units: int):
    import tensorflow as tf
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential
    from sklearn.model_selection import train_test_split

    X_train_all, _, y_train_all, _, _ = get_lstm_sequences()
    # osobny split train/val (z zachowaniem seedu)
    X_tr, X_val, y_tr, y_val = train_test_split(
        X_train_all, y_train_all, test_size=0.2, random_state=42, stratify=y_train_all
    )

    model = Sequential([
        Input(shape=(6, 3)),
        LSTM(units),
        Dropout(0.3),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=[tf.keras.metrics.AUC(name="auc")])
    model.fit(X_tr, y_tr, validation_data=(X_val, y_val),
              epochs=epochs, batch_size=batch_size, verbose=0)
    val_auc = float(model.evaluate(X_val, y_val, verbose=0)[1])
    return val_auc


@cached_json("lstm_hparam")
def hparam_sweep():
    BASE = dict(epochs=15, batch_size=256, units=32)

    epoch_vals = [5, 10, 15, 20, 30]
    batch_vals = [64, 128, 256, 512]
    unit_vals = [8, 16, 32, 64, 128]

    res = {"epochs": {}, "batch_size": {}, "units": {}}
    for e in epoch_vals:
        cfg = {**BASE, "epochs": e}
        res["epochs"][str(e)] = _train_once(**cfg)
    for b in batch_vals:
        cfg = {**BASE, "batch_size": b}
        res["batch_size"][str(b)] = _train_once(**cfg)
    for u in unit_vals:
        cfg = {**BASE, "units": u}
        res["units"][str(u)] = _train_once(**cfg)
    return res


def build():
    res = hparam_sweep()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    panels = [
        ("epochs", "Liczba epok",   "Liczba epok"),
        ("batch_size", "Batch size", "Batch size"),
        ("units", "Liczba jednostek LSTM", "Liczba neuronów LSTM"),
    ]
    for ax, (key, title, xlabel) in zip(axes, panels):
        xs = sorted([int(k) for k in res[key]])
        ys = [res[key][str(x)] for x in xs]
        ax.plot(xs, ys, marker="o", markersize=8, linewidth=2.2,
                color=MODEL_COLORS["LSTM"])
        best_i = int(np.argmax(ys))
        ax.scatter([xs[best_i]], [ys[best_i]], s=220, facecolor="none",
                   edgecolor="#a63446", linewidth=2.2, zorder=5)
        ax.annotate(f"max AUC = {ys[best_i]:.3f}",
                    xy=(xs[best_i], ys[best_i]),
                    xytext=(10, 10), textcoords="offset points",
                    fontsize=9, color="#a63446", fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("AUC walidacji")
        ax.set_title(title)
        ax.grid(linestyle="--", alpha=0.5)

    fig.suptitle("Wpływ hiperparametrów LSTM na AUC walidacji",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="4", name="hiperparametry_lstm",
                comment="Trzy panele wpływu hiperparametrów LSTM (liczba epok, batch size, liczba jednostek) na AUC walidacji — czerwone okręgi zaznaczają konfigurację optymalną.")
    plt.close(fig)
