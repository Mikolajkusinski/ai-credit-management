"""Rysunek 4.6 — Feature importance Random Forest (finalny artefakt W3).

Ważności Gini estymatora bazowego spod CalibratedClassifierCV (kalibracja
izotoniczna jest monotoniczna — nie zmienia rankingu cech).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure, PALETTE, load_rf_w3, load_feature_list_w3

apply_style()


def build():
    rf = load_rf_w3(base=True)
    features = load_feature_list_w3()
    importances = rf.feature_importances_

    idx = np.argsort(importances)[-20:][::-1]
    names = [features[i] for i in idx]
    vals = importances[idx]

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(names)))
    bars = ax.barh(range(len(names)), vals, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Istotność cechy (Gini importance)")
    ax.set_title("Top 20 cech wg istotności w modelu Random Forest (W3)")
    for bar, v in zip(bars, vals):
        ax.text(v + max(vals) * 0.01, bar.get_y() + bar.get_height()/2,
                f"{v:.3f}", va="center", fontsize=9)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="6", name="feature_importance_rf",
                comment="Top-20 cech wg istotności (Gini) finalnego RF W3 (estymator bazowy spod kalibracji) — dominują świeże zachowania płatnicze i inżynierowane wskaźniki opóźnień.")
    plt.close(fig)
