"""Rysunek 4.7 — Grid search XGBoost (learning_rate × max_depth)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score
from common import apply_style, save_figure, cached_json, get_train_test

apply_style()


@cached_json("xgb_grid")
def xgb_grid():
    X_train, X_test, y_train, y_test, _, _ = get_train_test()
    scale_pw = (len(y_train) - sum(y_train)) / max(sum(y_train), 1)

    lr_vals = [0.01, 0.02, 0.05, 0.1]
    depth_vals = [3, 4, 5, 6, 8]

    grid = []
    for lr in lr_vals:
        for d in depth_vals:
            xgb = XGBClassifier(
                n_estimators=400, learning_rate=lr, max_depth=d,
                subsample=0.7, colsample_bytree=0.7,
                reg_alpha=0.1, reg_lambda=1.0,
                scale_pos_weight=scale_pw,
                random_state=42, eval_metric="auc",
                tree_method="hist", n_jobs=-1,
            )
            xgb.fit(X_train, y_train)
            auc = float(roc_auc_score(y_test, xgb.predict_proba(X_test)[:, 1]))
            grid.append({"lr": lr, "max_depth": d, "auc": auc})
    return {"grid": grid, "lr_vals": lr_vals, "depth_vals": depth_vals}


def build():
    res = xgb_grid()
    lrs = res["lr_vals"]; depths = res["depth_vals"]
    table = np.zeros((len(depths), len(lrs)))
    for row in res["grid"]:
        i = depths.index(row["max_depth"]); j = lrs.index(row["lr"])
        table[i, j] = row["auc"]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    sns.heatmap(table, annot=True, fmt=".3f", cmap="magma",
                xticklabels=lrs, yticklabels=depths,
                cbar_kws={"label": "AUC (test)"},
                linewidths=0.4, linecolor="white", ax=ax)
    ax.set_xlabel("learning_rate")
    ax.set_ylabel("max_depth")
    ax.set_title("XGBoost — grid search learning_rate × max_depth (AUC test)")
    best = np.unravel_index(np.argmax(table), table.shape)
    ax.add_patch(plt.Rectangle((best[1], best[0]), 1, 1, fill=False,
                                edgecolor="#6b8e23", linewidth=2.6))
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="7", name="grid_search_xgb",
                comment="Heatmapa wyników grid search dla XGBoost (learning_rate × max_depth) — zielone obramowanie wskazuje konfigurację z maksymalnym AUC na zbiorze testowym.")
    plt.close(fig)
