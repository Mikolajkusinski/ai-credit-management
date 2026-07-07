"""Rysunek 4.7 — XGBoost: wpływ learning_rate × max_depth na CV-AUC (train, 5-fold).

Zastępuje heatmapę liczoną na AUC testowym (strojenie-na-teście, Fable5-zmiany.md Task1 #7).
Trenuje WYŁĄCZNIE modele pomocnicze figur — niczego nie zapisuje poza PNG/CSV.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # thesis_figures/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # ml-learing-center/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from xgboost import XGBClassifier
from common import apply_style, save_figure
from features import engineer_features
from sliding_window import WINDOW_DEFS

apply_style()
HERE = Path(__file__).resolve().parents[2]
REPORTS = HERE / "reports"

LEARNING_RATE = [0.005, 0.01, 0.02, 0.05, 0.1]
MAX_DEPTH = [3, 4, 5, 6, 8]
CHOSEN = (0.02, 4)  # (learning_rate, max_depth) z main.py


def train_split():
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    y = df["Default"]
    X, _ = engineer_features(df, WINDOW_DEFS[3])
    X_tmp, _, y_tmp, _ = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    X_tr, _, y_tr, _ = train_test_split(X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42)
    return X_tr.to_numpy(dtype=float), y_tr.to_numpy()


def build():
    X_tr, y_tr = train_split()
    spw = (len(y_tr) - y_tr.sum()) / y_tr.sum()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = np.zeros((len(MAX_DEPTH), len(LEARNING_RATE)))
    rows = []
    for i, depth in enumerate(MAX_DEPTH):
        for j, lr in enumerate(LEARNING_RATE):
            model = XGBClassifier(
                n_estimators=800, learning_rate=lr, max_depth=depth,
                subsample=0.7, colsample_bytree=0.7, reg_alpha=0.1, reg_lambda=1.0,
                scale_pos_weight=spw, random_state=42, eval_metric="auc", n_jobs=-1)
            auc = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="roc_auc").mean()
            grid[i, j] = auc
            rows.append({"learning_rate": lr, "max_depth": depth, "cv_auc": auc})
            print(f"XGB depth={depth} lr={lr}: CV-AUC={auc:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(REPORTS / "heatmap_xgb_cv.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(grid, cmap="magma", aspect="auto")
    ax.set_xticks(range(len(LEARNING_RATE)), LEARNING_RATE)
    ax.set_yticks(range(len(MAX_DEPTH)), MAX_DEPTH)
    ax.set_xlabel("learning_rate")
    ax.set_ylabel("max_depth (głębokość)")
    ax.set_title("XGBoost — CV-AUC (5-fold, zbiór treningowy W3)")
    for i in range(len(MAX_DEPTH)):
        for j in range(len(LEARNING_RATE)):
            ax.text(j, i, f"{grid[i, j]:.4f}", ha="center", va="center",
                    color="white", fontsize=9)
    ci, cj = MAX_DEPTH.index(CHOSEN[1]), LEARNING_RATE.index(CHOSEN[0])
    ax.add_patch(plt.Rectangle((cj - .5, ci - .5), 1, 1, fill=False,
                               edgecolor="#00e676", linewidth=2.5))
    fig.colorbar(im, ax=ax, label="CV-AUC")
    return fig


if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="7", name="heatmapa_xgb_cv",
                comment="XGB: CV-AUC 5-fold na treningu W3; zielona ramka = konfiguracja z main.py (lr=0.02, depth=4).")
