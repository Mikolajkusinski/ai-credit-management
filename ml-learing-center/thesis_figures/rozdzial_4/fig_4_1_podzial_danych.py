"""Rysunek 4.1 — Podział danych na train/val/test."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
from common import apply_style, save_figure, PALETTE, load_credit_data

apply_style()

TOTAL = 30000  # wiersze UCI
TEST_FRAC = 0.30        # test_size=0.3 w main.py
LSTM_VAL_FRAC = 0.20    # validation_split=0.2 w model.fit
# train po pierwszym splicie = 70%, dalej 20% tego dla walidacji LSTM
TRAIN_FRAC = (1 - TEST_FRAC) * (1 - LSTM_VAL_FRAC)   # 56%
VAL_FRAC   = (1 - TEST_FRAC) * LSTM_VAL_FRAC         # 14%


def build():
    df = load_credit_data()
    total = len(df)

    fractions = [TRAIN_FRAC, VAL_FRAC, TEST_FRAC]
    labels = ["Trenowanie", "Walidacja", "Test"]
    counts = [int(round(total * f)) for f in fractions]
    # Korekta zaokrągleń: ostatni zbiór dopełnia do całości
    counts[-1] = total - sum(counts[:-1])
    colors = [PALETTE[0], PALETTE[4], PALETTE[1]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5),
                                    gridspec_kw={"width_ratios": [1, 1.3]})

    # Donut chart
    wedges, texts, autotexts = ax1.pie(
        counts, labels=labels, colors=colors,
        autopct=lambda p: f"{p:.0f}%\n({int(p * total / 100):,})".replace(",", " "),
        startangle=90, pctdistance=0.75, wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11, fontweight="bold"),
    )
    ax1.set_title("Podział zbioru " + f"({total:,} rekordów)".replace(",", " "))

    # Stacked bar poziomy
    left = 0
    for frac, cnt, lbl, col in zip(fractions, counts, labels, colors):
        ax2.barh(0, frac, left=left, color=col, edgecolor="white", linewidth=2, height=0.5)
        ax2.text(left + frac / 2, 0, f"{lbl}\n{cnt:,}\n({frac*100:.0f}%)".replace(",", " "),
                 ha="center", va="center", color="white",
                 fontsize=11, fontweight="bold")
        left += frac

    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.5, 0.5)
    ax2.set_yticks([])
    ax2.set_xticks([0, 0.56, 0.7, 1.0])
    ax2.set_xticklabels(["0%", "56%", "70%", "100%"])
    ax2.set_title("Proporcje podziału na osi liniowej")
    for spine in ["left", "right", "top"]:
        ax2.spines[spine].set_visible(False)

    fig.suptitle("Podział danych: train / val / test — stratyfikowany, seed = 42",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="1", name="podzial_danych",
                comment="Podział zbioru UCI na 56% trenowania / 14% walidacji / 30% testu — stratyfikowany, zgodny z konfiguracją w main.py.")
    plt.close(fig)
