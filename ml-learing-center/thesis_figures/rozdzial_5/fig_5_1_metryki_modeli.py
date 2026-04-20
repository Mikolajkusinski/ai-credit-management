"""Rysunek 5.1 — Porównanie metryk modeli (accuracy, precision, recall, F1, ROC-AUC)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS, get_metrics_table

apply_style()

METRIC_ORDER = ["accuracy", "precision", "recall", "f1", "roc_auc"]
METRIC_LABELS = ["Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]


def build():
    metrics = get_metrics_table()
    models = list(metrics.keys())

    fig, (ax_bar, ax_tab) = plt.subplots(
        2, 1, figsize=(11, 8.5),
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # Grouped bar
    x = np.arange(len(METRIC_ORDER))
    width = 0.25
    for i, m in enumerate(models):
        vals = [metrics[m][k] for k in METRIC_ORDER]
        offset = (i - 1) * width
        bars = ax_bar.bar(x + offset, vals, width,
                          label=m, color=MODEL_COLORS[m],
                          edgecolor="white", linewidth=1.2)
        for b, v in zip(bars, vals):
            ax_bar.text(b.get_x() + b.get_width()/2, v + 0.01,
                        f"{v:.3f}", ha="center", va="bottom", fontsize=9)

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(METRIC_LABELS)
    ax_bar.set_ylim(0, 1.05)
    ax_bar.set_ylabel("Wartość metryki")
    ax_bar.set_title("Porównanie metryk klasyfikacji modeli (test, próg = 0.5)")
    ax_bar.legend(loc="upper right")
    ax_bar.grid(axis="y", linestyle="--", alpha=0.5)
    ax_bar.set_axisbelow(True)

    # Tabela
    ax_tab.axis("off")
    cell_text = []
    for m in models:
        cell_text.append([f"{metrics[m][k]:.4f}" for k in METRIC_ORDER])
    table = ax_tab.table(
        cellText=cell_text,
        rowLabels=models, colLabels=METRIC_LABELS,
        loc="center", cellLoc="center"
    )
    table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1, 1.6)
    for i, m in enumerate(models):
        table[(i + 1, -1)].set_facecolor(MODEL_COLORS[m])
        table[(i + 1, -1)].set_text_props(color="white", fontweight="bold")
    for j in range(len(METRIC_ORDER)):
        table[(0, j)].set_facecolor("#1f3a68")
        table[(0, j)].set_text_props(color="white", fontweight="bold")

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="1", name="metryki_modeli",
                comment="Zestawienie pięciu metryk klasyfikacji (accuracy, precision, recall, F1, ROC-AUC) dla LSTM, Random Forest i XGBoost — wykres słupkowy z pełną tabelą liczbową pod spodem.")
    plt.close(fig)
