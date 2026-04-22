"""Rysunek 1.4 — Diagram ograniczeń klasycznych metod scoringowych."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, PALETTE

apply_style()

LIMITATIONS = [
    "Niska adaptacyjność\ndo zmian rynku",
    "Ograniczona liczba\nzmiennych wejściowych",
    "Słaba skuteczność dla\ndanych nieliniowych",
    "Brak uczenia się\nz nowych danych",
    "Wysoka wrażliwość\nna outliery",
    "Ograniczone wsparcie\ndanych niestrukt.",
]
# intensywność ograniczenia w skali 0..1 (im większa wartość, tym większe ograniczenie)
SEVERITY = [0.82, 0.70, 0.90, 0.85, 0.65, 0.78]


def build():
    n = len(LIMITATIONS)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values = SEVERITY + SEVERITY[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(9, 8), subplot_kw={"projection": "polar"})
    ax.fill(angles, values, color=PALETTE[1], alpha=0.25)
    ax.plot(angles, values, color=PALETTE[1], linewidth=2, marker="o",
            markersize=8, markerfacecolor=PALETTE[1], markeredgecolor="white")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(LIMITATIONS, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["niska", "umiark.", "wysoka", "b. wysoka"], fontsize=9)
    ax.yaxis.grid(True, color="#cfcfcf", linestyle="--", linewidth=0.6)
    ax.xaxis.grid(True, color="#cfcfcf", linewidth=0.6)
    ax.spines["polar"].set_color("#888")

    ax.set_title("Ograniczenia klasycznych metod scoringowych\n(im bliżej krawędzi, tym istotniejsze ograniczenie)",
                 fontsize=13, pad=30, fontweight="bold")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=1, idx="4", name="ograniczenia_klasyczne",
                comment="Wykres radarowy prezentujący istotność sześciu głównych ograniczeń tradycyjnych modeli scoringowych — punkt wyjścia dla uzasadnienia użycia uczenia maszynowego.")
    plt.close(fig)
