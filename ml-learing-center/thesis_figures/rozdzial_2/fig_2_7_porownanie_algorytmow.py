"""Rysunek 2.7 — Porównanie algorytmów ML (radar chart, wartości teoretyczne)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, MODEL_COLORS

apply_style()

CRITERIA = [
    "Dokładność",
    "Interpretowalność",
    "Szybkość\ntrenowania",
    "Szybkość\ninferencji",
    "Odporność na\nzaszumione dane",
    "Niskie wymagania\nobliczeniowe",
]
# ocena teoretyczna 1..5 (wyższa = lepiej)
SCORES = {
    "LSTM":                 [4.5, 2.0, 2.0, 3.0, 3.5, 2.0],
    "Random Forest":        [4.0, 3.5, 3.5, 4.0, 4.5, 4.0],
    "XGBoost":              [4.5, 3.0, 3.5, 4.5, 4.0, 3.5],
    "Scoring tradycyjny":   [3.0, 5.0, 4.5, 5.0, 2.5, 5.0],
}


def build():
    n = len(CRITERIA)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw={"projection": "polar"})
    for label, vals in SCORES.items():
        v = vals + vals[:1]
        color = MODEL_COLORS[label]
        ax.plot(angles, v, color=color, linewidth=2, label=label, marker="o", markersize=6)
        ax.fill(angles, v, color=color, alpha=0.12)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CRITERIA, fontsize=10)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=9)
    ax.yaxis.grid(True, color="#cfcfcf", linestyle="--", linewidth=0.6)
    ax.spines["polar"].set_color("#888")
    ax.set_title("Porównanie algorytmów — ocena teoretyczna wg kryteriów",
                 fontsize=13, pad=26, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.05), frameon=True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=2, idx="7", name="porownanie_algorytmow",
                comment="Teoretyczne porównanie czterech podejść (LSTM, Random Forest, XGBoost, scoring tradycyjny) na wykresie radarowym wg sześciu kryteriów. Porównanie empiryczne znajduje się w rysunku 5.5.")
    plt.close(fig)
