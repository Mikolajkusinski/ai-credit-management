"""Rysunek 3.3 — Heatmapa korelacji wybranych zmiennych."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import apply_style, save_figure, load_credit_data, engineer_features

apply_style()

SELECTED = [
    "LIMIT_BAL", "AGE",
    "PAY_0", "PAY_2", "PAY_mean", "PAY_max",
    "BILL_mean", "BILL_std", "BILL_trend",
    "PAY_AMT_mean", "payment_ratio",
    "utilization_rate", "late_count", "severe_late", "recent_pay_status",
    "Default",
]


def build():
    df = engineer_features(load_credit_data())
    corr = df[SELECTED].corr(method="pearson")

    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    fig, ax = plt.subplots(figsize=(11, 9))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
                cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                linewidths=0.4, linecolor="white",
                annot_kws={"fontsize": 8},
                cbar_kws={"label": "Współczynnik korelacji Pearsona", "shrink": 0.75},
                ax=ax)
    ax.set_title("Macierz korelacji wybranych 16 zmiennych", pad=12)
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=3, idx="3", name="heatmapa_korelacji",
                comment="Trójkątna heatmapa korelacji Pearsona dla 16 zmiennych (w tym zmiennej docelowej Default) — widoczne silne korelacje wewnątrz grup PAY_*/BILL_* oraz umiarkowane powiązania z Default.")
    plt.close(fig)
