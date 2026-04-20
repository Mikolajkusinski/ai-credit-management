"""Rysunek 3.2 — Histogramy i boxploty kluczowych zmiennych."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import apply_style, save_figure, load_credit_data, engineer_features, PALETTE

apply_style()

VARS = [
    ("LIMIT_BAL", "Limit kredytowy [NT$]", 4000),
    ("AGE", "Wiek klienta [lata]", 200),
    ("BILL_mean", "Średni rachunek z 6 miesięcy [NT$]", 4000),
    ("late_count", "Liczba miesięcy z opóźnieniem (6 m.)", 30),
]


def build():
    df = engineer_features(load_credit_data())
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, (col, xlabel, _) in enumerate(VARS):
        ax_h = axes[0, i]
        ax_b = axes[1, i]
        data = df[col].replace([np.inf, -np.inf], np.nan).dropna()

        # Histogram z podziałem na klasy
        sns.histplot(data=df, x=col, hue="Default", bins=40,
                     palette={0: PALETTE[2], 1: PALETTE[1]},
                     alpha=0.65, edgecolor="white", linewidth=0.4,
                     ax=ax_h, legend=(i == 0), stat="count", multiple="stack")
        ax_h.set_xlabel(xlabel)
        ax_h.set_ylabel("Liczność" if i == 0 else "")
        ax_h.set_title(col)
        if i == 0 and ax_h.get_legend() is not None:
            legend = ax_h.get_legend()
            legend.set_title("Default")
            for t, lbl in zip(legend.texts, ["niespłacający (1)", "spłacający (0)"]):
                t.set_text(lbl)

        # Boxplot
        sns.boxplot(data=df, x="Default", y=col,
                    hue="Default", legend=False,
                    palette={0: PALETTE[2], 1: PALETTE[1]},
                    fliersize=2, linewidth=1.0, ax=ax_b)
        ax_b.set_xticks([0, 1])
        ax_b.set_xticklabels(["spłaca", "nie spłaca"])
        ax_b.set_xlabel("")
        ax_b.set_ylabel(xlabel if i == 0 else "")

    fig.suptitle("Rozkład kluczowych zmiennych w zależności od statusu spłaty",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=3, idx="2", name="histogramy_boxploty",
                comment="Histogramy i boxploty czterech kluczowych zmiennych (limit kredytu, wiek, średni rachunek, liczba opóźnień) z podziałem na klasy — pokazują różnice rozkładów między klientami spłacającymi i niespłacającymi.")
    plt.close(fig)
