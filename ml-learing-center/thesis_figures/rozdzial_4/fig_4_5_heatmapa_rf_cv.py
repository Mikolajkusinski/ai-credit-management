"""Rysunek 4.5 — Random Forest: wpływ n_estimators × max_depth na CV-AUC (train, 5-fold).

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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from common import apply_style, save_figure
from features import engineer_features
from sliding_window import WINDOW_DEFS

apply_style()
HERE = Path(__file__).resolve().parents[2]
REPORTS = HERE / "reports"

N_ESTIMATORS = [50, 100, 200, 300, 500]
MAX_DEPTH = [4, 6, 8, 10, 14]
CHOSEN = (500, 10)  # konfiguracja z main.py


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
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = np.zeros((len(MAX_DEPTH), len(N_ESTIMATORS)))
    rows = []
    for i, depth in enumerate(MAX_DEPTH):
        for j, n_est in enumerate(N_ESTIMATORS):
            model = RandomForestClassifier(
                n_estimators=n_est, max_depth=depth, min_samples_leaf=5,
                class_weight="balanced", random_state=42, n_jobs=-1)
            auc = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="roc_auc").mean()
            grid[i, j] = auc
            rows.append({"n_estimators": n_est, "max_depth": depth, "cv_auc": auc})
            print(f"RF depth={depth} n={n_est}: CV-AUC={auc:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(REPORTS / "heatmap_rf_cv.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(grid, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(N_ESTIMATORS)), N_ESTIMATORS)
    ax.set_yticks(range(len(MAX_DEPTH)), MAX_DEPTH)
    ax.set_xlabel("n_estimators (liczba drzew)")
    ax.set_ylabel("max_depth (głębokość)")
    ax.set_title("Random Forest — CV-AUC (5-fold, zbiór treningowy W3)")
    for i in range(len(MAX_DEPTH)):
        for j in range(len(N_ESTIMATORS)):
            ax.text(j, i, f"{grid[i, j]:.4f}", ha="center", va="center",
                    color="white", fontsize=9)
    ci, cj = MAX_DEPTH.index(CHOSEN[1]), N_ESTIMATORS.index(CHOSEN[0])
    ax.add_patch(plt.Rectangle((cj - .5, ci - .5), 1, 1, fill=False,
                               edgecolor="red", linewidth=2.5))
    fig.colorbar(im, ax=ax, label="CV-AUC")
    return fig


if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="5", name="heatmapa_rf_cv",
                comment="RF: CV-AUC 5-fold na treningu W3; czerwona ramka = konfiguracja z main.py (500, 10).")
