"""Rysunek 4.1 — Podział danych 60/20/20 (train / kalibracja / test).

Zastępuje wcześniejszy wariant 56/14/30 (legacy 70/30 + validation_split LSTM):
finalny protokół W3 to trójdzielny stratyfikowany split z osobną częścią
kalibracyjną (kalibracja izotoniczna CREDIT-105 + progi kosztowe CREDIT-106).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
from common import apply_style, save_figure, PALETTE, load_credit_data

apply_style()

# 60/20/20: najpierw test 20%, potem 25% reszty jako kalibracja (main.py, seed 42).
FRACTIONS = [0.60, 0.20, 0.20]
LABELS = ["Trenowanie", "Kalibracja", "Test"]


def build():
    df = load_credit_data()
    total = len(df)

    counts = [int(round(total * f)) for f in FRACTIONS]
    counts[-1] = total - sum(counts[:-1])
    colors = [PALETTE[0], PALETTE[4], PALETTE[1]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5),
                                   gridspec_kw={"width_ratios": [1, 1.3]})

    wedges, texts, autotexts = ax1.pie(
        counts, labels=LABELS, colors=colors,
        autopct=lambda p: f"{p:.0f}%\n({int(p * total / 100):,})".replace(",", " "),
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=11, fontweight="bold"),
    )
    ax1.set_title("Podział zbioru " + f"({total:,} rekordów)".replace(",", " "))

    left = 0
    for frac, cnt, lbl, col in zip(FRACTIONS, counts, LABELS, colors):
        ax2.barh(0, frac, left=left, color=col, edgecolor="white", linewidth=2, height=0.5)
        ax2.text(left + frac / 2, 0, f"{lbl}\n{cnt:,}\n({frac*100:.0f}%)".replace(",", " "),
                 ha="center", va="center", color="white",
                 fontsize=11, fontweight="bold")
        left += frac

    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.5, 0.5)
    ax2.set_yticks([])
    ax2.set_xticks([0, 0.60, 0.80, 1.0])
    ax2.set_xticklabels(["0%", "60%", "80%", "100%"])
    ax2.set_title("Proporcje podziału na osi liniowej")
    for spine in ["left", "right", "top"]:
        ax2.spines[spine].set_visible(False)

    fig.suptitle("Podział danych: train / kalibracja / test — stratyfikowany, seed = 42",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="1", name="podzial_danych",
                comment="Trójdzielny split 60/20/20 (18 000 / 6 000 / 6 000) z osobną częścią kalibracyjną; zgodny z main.py po leakage-fix 2026-07-07.")
    plt.close(fig)
