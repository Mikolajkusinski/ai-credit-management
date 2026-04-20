"""Rysunek 3.1 — Rozkład zmiennej docelowej (Default)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
from common import apply_style, save_figure, load_credit_data, PALETTE

apply_style()


def build():
    df = load_credit_data()
    counts = df["Default"].value_counts().sort_index()
    total = counts.sum()
    labels = ["Spłaca zobowiązania\n(Default = 0)", "Niespłacający\n(Default = 1)"]
    colors = [PALETTE[2], PALETTE[1]]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, counts.values, color=colors, edgecolor="white",
                  linewidth=1.5, width=0.55)
    for bar, cnt in zip(bars, counts.values):
        pct = 100 * cnt / total
        ax.text(bar.get_x() + bar.get_width() / 2, cnt + total * 0.01,
                f"{cnt:,}\n({pct:.1f}%)".replace(",", " "),
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("Liczba klientów")
    ax.set_title(f"Rozkład zmiennej docelowej — zbiór {total:,} klientów".replace(",", " "))
    ax.set_ylim(0, counts.max() * 1.18)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=3, idx="1", name="rozklad_target",
                comment="Rozkład klas zmiennej docelowej w zbiorze UCI (default of credit card clients) — widoczna nierównowaga klas (~22% niespłacających).")
    plt.close(fig)
