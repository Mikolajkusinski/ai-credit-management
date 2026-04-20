"""Rysunek 2.3 — Zastosowania uczenia maszynowego w finansach."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
from common import apply_style, save_figure, PALETTE, FIGSIZE_MEDIUM

apply_style()

# Wartości odzwierciedlają względną częstość zastosowań na podstawie przeglądu literatury
APPLICATIONS = [
    ("Credit scoring", 95),
    ("Wykrywanie fraudów", 88),
    ("Prognozowanie ryzyka", 74),
    ("AML (anti-money laundering)", 68),
    ("Segmentacja klientów", 62),
    ("Robo-doradztwo", 45),
    ("Automatyzacja compliance", 38),
]


def build():
    labels, values = zip(*APPLICATIONS)
    y_pos = np.arange(len(labels))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(labels))]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(y_pos, values, color=colors, edgecolor="white", linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Względna częstość zastosowań [%]")
    ax.set_xlim(0, 100)
    ax.set_title("Zastosowania uczenia maszynowego w sektorze finansowym")

    for bar, val in zip(bars, values):
        ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{val}%", va="center", fontsize=10, fontweight="bold",
                color="#333")

    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=2, idx="3", name="zastosowania_ml",
                comment="Wykres słupkowy poziomy prezentujący względną częstość siedmiu obszarów zastosowania ML w finansach na podstawie przeglądu literatury.")
    plt.close(fig)
