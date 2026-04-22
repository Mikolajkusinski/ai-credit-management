"""Rysunek 4.9 — Schemat k-fold cross-validation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from common import apply_style, save_figure, PALETTE

apply_style()

K = 5


def build():
    fig, ax = plt.subplots(figsize=(12, 5.5))

    fold_w = 1.0
    gap = 0.02
    row_h = 0.7

    for i in range(K):
        y = (K - 1 - i) * (row_h + 0.15)
        # Etykieta foldu
        ax.text(-0.5, y + row_h / 2, f"Iteracja {i + 1}", ha="right", va="center",
                fontsize=11, fontweight="bold")
        for j in range(K):
            x = j * (fold_w + gap)
            is_val = (j == i)
            color = PALETTE[1] if is_val else PALETTE[0]
            label = "walidacja" if is_val else "trenowanie"
            ax.add_patch(mpatches.FancyBboxPatch((x, y), fold_w, row_h,
                                                 boxstyle="round,pad=0.03",
                                                 facecolor=color,
                                                 edgecolor="white", linewidth=2))
            ax.text(x + fold_w / 2, y + row_h / 2, label,
                    ha="center", va="center", color="white",
                    fontsize=10, fontweight="bold")

    # Podpisy kolumn
    for j in range(K):
        x = j * (fold_w + gap) + fold_w / 2
        ax.text(x, (K - 1) * (row_h + 0.15) + row_h + 0.15, f"Fold {j + 1}",
                ha="center", va="bottom", fontsize=11, fontweight="bold",
                color="#333")

    # Legenda
    legend_handles = [
        mpatches.Patch(color=PALETTE[0], label="Zbiór treningowy"),
        mpatches.Patch(color=PALETTE[1], label="Zbiór walidacyjny"),
    ]
    ax.legend(handles=legend_handles, loc="lower center",
              bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=True)

    ax.set_xlim(-2.5, K * (fold_w + gap) + 0.2)
    ax.set_ylim(-0.6, (K - 1) * (row_h + 0.15) + row_h + 0.6)
    ax.set_axis_off()
    ax.set_title(f"Walidacja krzyżowa {K}-fold (stratified) — rotacja zbioru walidacyjnego",
                 fontsize=13, pad=14, fontweight="bold")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="9", name="cross_validation",
                comment="Schemat 5-fold walidacji krzyżowej — w każdej z 5 iteracji inny fold pełni rolę zbioru walidacyjnego (kolor czerwony), pozostałe cztery trenują model.")
    plt.close(fig)
