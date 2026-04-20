"""Rysunek 3.6 — Diagram przepływu danych w systemie (sequence diagram)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from common import apply_style, save_figure, PALETTE

apply_style()

ACTORS = [
    ("Klient\n(formularz)", PALETTE[2]),
    ("Frontend\nReact", PALETTE[5]),
    ("Backend\n.NET API", PALETTE[0]),
    ("ML-service\nFlask", PALETTE[1]),
    ("Modele AI\n(RF/XGB/LSTM)", PALETTE[4]),
]


def build():
    fig, ax = plt.subplots(figsize=(12, 6.2))
    n = len(ACTORS)
    x_pos = list(range(n))

    # Boksy aktorów u góry
    for i, (name, color) in enumerate(ACTORS):
        ax.add_patch(mpatches.FancyBboxPatch((i - 0.35, 7.2), 0.7, 0.7,
                                             boxstyle="round,pad=0.1",
                                             facecolor=color, edgecolor="white", linewidth=2))
        ax.text(i, 7.55, name, ha="center", va="center", color="white",
                fontsize=10, fontweight="bold")
        # Pionowe linie życia
        ax.plot([i, i], [0.2, 7.2], color="#888", linestyle="--", linewidth=0.8, zorder=0)

    # Kroki sekwencji (od góry do dołu)
    steps = [
        (0, 1, "1. wypełnij formularz", 6.6),
        (1, 2, "2. POST /api/predict\n(JSON z 22 polami)", 5.9),
        (2, 3, "3. POST /predict\n(przekazanie żądania)", 5.1),
        (3, 4, "4. feature engineering\n+ skalowanie", 4.3),
        (4, 3, "5. 3× probability\n(RF, XGB, LSTM)", 3.5),
        (3, 2, "6. PredictResponse\n(3 wyniki + adnotacje)", 2.7),
        (2, 1, "7. odpowiedź HTTP", 1.9),
        (1, 0, "8. prezentacja wyniku", 1.1),
    ]
    for src, dst, label, y in steps:
        arrow = "->"
        style = "solid"
        color = PALETTE[0]
        if dst < src:
            color = PALETTE[1]
            style = "dashed"
        ax.annotate("", xy=(dst, y), xytext=(src, y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4,
                                    linestyle=style, shrinkA=4, shrinkB=4))
        mid_x = (src + dst) / 2
        ax.text(mid_x, y + 0.12, label, ha="center", va="bottom",
                fontsize=9, color="#333",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5))

    ax.set_xlim(-0.7, n - 0.3)
    ax.set_ylim(0, 8.2)
    ax.set_axis_off()
    ax.set_title("Przepływ danych podczas żądania predykcji",
                 fontsize=13, pad=10, fontweight="bold")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=3, idx="6", name="przeplyw_danych",
                comment="Diagram sekwencji opisujący pełny cykl żądania predykcji — od wypełnienia formularza przez klienta aż po prezentację wyniku (8 kroków).")
    plt.close(fig)
