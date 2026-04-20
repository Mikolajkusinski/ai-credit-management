"""Rysunek 5.5 — Radar chart porównujący modele (wartości empiryczne)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, get_metrics_table

apply_style()

CRITERIA = ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]


def build():
    metrics = get_metrics_table()
    models = list(metrics.keys())

    angles = np.linspace(0, 2 * np.pi, len(CRITERIA), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8.5, 8), subplot_kw={"projection": "polar"})
    for m in models:
        vals = [metrics[m][k] for k in ["accuracy", "precision", "recall", "f1", "roc_auc"]]
        v = vals + vals[:1]
        ax.plot(angles, v, linewidth=2.2, marker="o", markersize=6,
                color=MODEL_COLORS[m], label=m)
        ax.fill(angles, v, color=MODEL_COLORS[m], alpha=0.14)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CRITERIA, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=9)
    ax.yaxis.grid(True, color="#cfcfcf", linestyle="--", linewidth=0.6)
    ax.spines["polar"].set_color("#888")

    ax.set_title("Radar — porównanie modeli wg pięciu metryk (wartości empiryczne)",
                 fontsize=13, pad=26, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05), frameon=True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="5", name="radar_modeli",
                comment="Radar chart prezentujący empiryczne wartości pięciu metryk dla każdego z trzech modeli — szybkie wizualne porównanie mocnych i słabych stron każdego podejścia.")
    plt.close(fig)
