"""Rysunek 1.3 — Porównanie tradycyjnych metod oceny zdolności kredytowej."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import apply_style, save_figure, FIGSIZE_MEDIUM

apply_style()

METHODS = ["Ocena ekspercka", "Scoring punktowy", "Analiza finansowa"]
CRITERIA = ["Szybkość", "Koszt", "Interpretowalność", "Skuteczność"]
# skala 1-5 na podstawie literatury dziedzinowej (wyższa = lepiej)
# dla "Koszt" wyższa wartość oznacza NIŻSZY koszt (tj. im taniej tym lepiej)
SCORES = np.array([
    [2, 2, 5, 3],   # ekspercka: wolna, droga, pełna interpret., zmienna skuteczność
    [5, 5, 4, 3],   # scoring punktowy: szybki, tani, interpret., umiarkowana skuteczność
    [3, 3, 5, 4],   # analiza finansowa: średnia, umiarkowany koszt, pełna interpret., wysoka skuteczność
])


def build():
    fig, ax = plt.subplots(figsize=FIGSIZE_MEDIUM)
    sns.heatmap(SCORES, annot=True, fmt="d", cmap="RdYlGn",
                xticklabels=CRITERIA, yticklabels=METHODS,
                vmin=1, vmax=5, cbar_kws={"label": "Ocena (1 = słaba, 5 = bardzo dobra)"},
                linewidths=0.8, linecolor="white", ax=ax,
                annot_kws={"fontsize": 12, "fontweight": "bold"})
    ax.set_title("Porównanie tradycyjnych metod oceny zdolności kredytowej",
                 pad=14)
    ax.set_xlabel("Kryterium oceny")
    ax.set_ylabel("Metoda")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=1, idx="3", name="porownanie_metod",
                comment="Heatmapa porównawcza trzech tradycyjnych metod oceny zdolności kredytowej wg czterech kryteriów (szybkość, koszt, interpretowalność, skuteczność).")
    plt.close(fig)
