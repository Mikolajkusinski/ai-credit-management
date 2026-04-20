"""Rysunek 5.3 — Macierze pomyłek dla LSTM, Random Forest, XGBoost."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import apply_style, save_figure, get_confusion_matrices

apply_style()


def build():
    cms = get_confusion_matrices()
    models = list(cms.keys())
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    labels = ["Spłaca (0)", "Nie spłaca (1)"]
    for ax, name in zip(axes, models):
        cm = cms[name]
        cm_norm = cm / cm.sum(axis=1, keepdims=True)

        # Adnotacje: liczba + procent
        annot = np.empty_like(cm, dtype=object)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                annot[i, j] = f"{cm[i, j]:,}\n({cm_norm[i, j]*100:.1f}%)".replace(",", " ")

        sns.heatmap(cm_norm, annot=annot, fmt="", cmap="Blues",
                    xticklabels=labels, yticklabels=labels,
                    cbar=False, linewidths=0.8, linecolor="white",
                    annot_kws={"fontsize": 11, "fontweight": "bold"}, ax=ax,
                    vmin=0, vmax=1)
        ax.set_xlabel("Predykcja"); ax.set_ylabel("Rzeczywistość")
        ax.set_title(name)

    fig.suptitle("Macierze pomyłek (znormalizowane wierszami) — test set",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="3", name="macierze_pomylek",
                comment="Macierze pomyłek dla trzech modeli na zbiorze testowym — każda komórka podaje liczbę przypadków oraz udział procentowy w danym wierszu (rzeczywistej klasie).")
    plt.close(fig)
