"""Rysunek 5.2 — Krzywe ROC dla wszystkich modeli."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, get_roc_curves

apply_style()


def build():
    curves = get_roc_curves()
    fig, ax = plt.subplots(figsize=(7.5, 7))

    for name, d in curves.items():
        ax.plot(d["fpr"], d["tpr"], color=MODEL_COLORS[name],
                linewidth=2.2, label=f"{name} (AUC = {d['auc']:.3f})")
    ax.plot([0, 1], [0, 1], "--", color="#888", linewidth=1.2, label="Klasyfikator losowy")

    ax.set_xlabel("False Positive Rate (1 − specyficzność)")
    ax.set_ylabel("True Positive Rate (czułość)")
    ax.set_title("Krzywe ROC — porównanie trzech modeli")
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="lower right")
    ax.grid(linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    ax.set_aspect("equal")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="2", name="krzywe_roc",
                comment="Krzywe ROC trzech modeli na jednym wykresie wraz z wartościami AUC w legendzie — im krzywa bliższa lewego górnego rogu, tym lepszy klasyfikator.")
    plt.close(fig)
