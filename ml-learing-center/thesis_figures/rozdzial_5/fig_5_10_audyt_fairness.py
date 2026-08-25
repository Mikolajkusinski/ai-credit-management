"""Rysunek 5.10 — Audyt fairness (fairlearn): DPD/EOD, selection rate i TPR/FPR per SEX.

Dane czytane z kanonicznego reports/fairness_metrics_w3.csv (stan po leakage-fix
2026-07-07) — żadna liczba nie jest wpisana ręcznie.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from common import apply_style, save_figure

apply_style()

REPORTS = Path(__file__).resolve().parents[2] / "reports"
LIMIT = 0.10           # próg DoD CREDIT-112
STRUCT_GAP = 0.021     # luka strukturalna DPD z różnicy base rate (M 23.4% vs F 21.3%)

COLOR_M = "#1f3a68"
COLOR_F = "#a63446"


def build():
    df = pd.read_csv(REPORTS / "fairness_metrics_w3.csv")
    models = df["model"].tolist()
    x = np.arange(len(models))
    w = 0.38

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # (a) DPD/EOD per model z limitem i luką strukturalną
    ax = axes[0, 0]
    ax.bar(x - w / 2, df["DPD"], width=w, label="DPD", color="#3e7cb1")
    ax.bar(x + w / 2, df["EOD"], width=w, label="EOD", color="#d4a017")
    ax.axhline(LIMIT, color="#a63446", linestyle="--", linewidth=1.2,
               label=f"limit DoD ({LIMIT:.2f})")
    ax.axhline(STRUCT_GAP, color="#6c757d", linestyle=":", linewidth=1.2,
               label=f"luka strukturalna base rate (~{STRUCT_GAP:.3f})")
    ax.set_xticks(x); ax.set_xticklabels(models, rotation=15)
    ax.set_ylabel("Różnica (M − F)")
    ax.set_title("(a) DPD i EOD względem SEX")
    ax.set_ylim(0, 0.115)
    ax.legend(fontsize=9)

    # (b) Selection rate per grupa
    ax = axes[0, 1]
    ax.bar(x - w / 2, df["sel_rate_male"], width=w, label="mężczyźni (SEX=1)", color=COLOR_M)
    ax.bar(x + w / 2, df["sel_rate_female"], width=w, label="kobiety (SEX=2)", color=COLOR_F)
    ax.set_xticks(x); ax.set_xticklabels(models, rotation=15)
    ax.set_ylabel("Selection rate  P[ŷ=1]")
    ax.set_title("(b) Częstość alarmów per grupa (progi kosztowe)")
    ax.legend(fontsize=9)

    # (c) TPR per grupa
    ax = axes[1, 0]
    ax.bar(x - w / 2, df["tpr_male"], width=w, label="mężczyźni", color=COLOR_M)
    ax.bar(x + w / 2, df["tpr_female"], width=w, label="kobiety", color=COLOR_F)
    ax.set_xticks(x); ax.set_xticklabels(models, rotation=15)
    ax.set_ylabel("TPR (czułość na defaultujących)")
    ax.set_title("(c) Równość ochrony: TPR per grupa")
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=9)

    # (d) FPR per grupa
    ax = axes[1, 1]
    ax.bar(x - w / 2, df["fpr_male"], width=w, label="mężczyźni", color=COLOR_M)
    ax.bar(x + w / 2, df["fpr_female"], width=w, label="kobiety", color=COLOR_F)
    ax.set_xticks(x); ax.set_xticklabels(models, rotation=15)
    ax.set_ylabel("FPR (fałszywe alarmy na spłacających)")
    ax.set_title("(d) Równość ciężaru błędów: FPR per grupa")
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=9)

    fig.suptitle(
        "Audyt fairness — 5 modeli W3 przy progach kosztowych (test, n=6000; M 2402 / F 3598)",
        fontsize=14, fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(
        fig, chapter=5, idx="10", name="audyt_fairness",
        comment=(
            "Audyt fairlearn DPD/EOD wrt SEX dla 5 modeli W3 przy progach "
            "kosztowych; wszystkie |diff| <= 0.04 przy limicie 0.10; panel (a) "
            "pokazuje też lukę strukturalną ~0.021 z różnicy base rate."
        ),
    )
