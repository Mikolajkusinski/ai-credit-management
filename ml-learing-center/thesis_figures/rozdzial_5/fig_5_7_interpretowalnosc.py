"""Rysunek 5.7 — Diagram interpretowalności modeli."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import apply_style, save_figure

apply_style()

MODELS = ["LSTM", "Random Forest", "XGBoost"]
DIMENSIONS = [
    "Globalna\ninterpretowalność",
    "Lokalna\ninterpretowalność",
    "Istotność cech\n(feature importance)",
    "Narzędzia SHAP/LIME",
    "Wizualizacja\ndecyzji",
]
# Skala 1..5 (wyższa = lepsza interpretowalność)
MATRIX = np.array([
    # LSTM, RF, XGB
    [1, 4, 3],   # globalna
    [2, 4, 4],   # lokalna
    [1, 5, 5],   # feature importance
    [3, 4, 5],   # SHAP/LIME
    [1, 5, 3],   # wizualizacja decyzji
])


def build():
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.heatmap(MATRIX, annot=True, fmt="d", cmap="RdYlGn",
                xticklabels=MODELS, yticklabels=DIMENSIONS,
                vmin=1, vmax=5, cbar_kws={"label": "Ocena (1 = niska, 5 = wysoka)"},
                linewidths=0.8, linecolor="white", ax=ax,
                annot_kws={"fontsize": 13, "fontweight": "bold"})
    ax.set_xlabel("Model")
    ax.set_ylabel("Wymiar interpretowalności")
    ax.set_title("Interpretowalność modeli — porównanie w pięciu wymiarach", pad=14)

    # Ocena sumaryczna pod heatmapą
    totals = MATRIX.sum(axis=0)
    labels_q = []
    for t in totals:
        if t <= 10: q = "niska"
        elif t <= 18: q = "średnia"
        else: q = "wysoka"
        labels_q.append(f"Σ = {t} → {q}")
    for i, q in enumerate(labels_q):
        ax.text(i + 0.5, len(DIMENSIONS) + 0.4, q,
                ha="center", va="top", fontsize=10, fontweight="bold", color="#333")

    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="7", name="interpretowalnosc",
                comment="Heatmapa 5×3 prezentująca interpretowalność trzech modeli w pięciu wymiarach — pod nią oceny sumaryczne (LSTM = niska, RF i XGB = średnio/wysoka).")
    plt.close(fig)
