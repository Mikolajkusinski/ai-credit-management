"""Rysunek 4.5 — Wpływ n_estimators i max_depth w Random Forest."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from common import apply_style, save_figure, cached_json, get_train_test

apply_style()


@cached_json("rf_grid")
def rf_grid_search():
    X_train, X_test, y_train, y_test, _, _ = get_train_test()
    n_estimators_vals = [50, 100, 200, 300, 500]
    max_depth_vals = [4, 6, 8, 10, 14, None]

    result = []
    for n in n_estimators_vals:
        for d in max_depth_vals:
            rf = RandomForestClassifier(
                n_estimators=n, max_depth=d, min_samples_leaf=5,
                class_weight="balanced", n_jobs=-1, random_state=42,
            )
            rf.fit(X_train, y_train)
            auc = float(roc_auc_score(y_test, rf.predict_proba(X_test)[:, 1]))
            result.append({"n_estimators": n, "max_depth": d if d is not None else "None", "auc": auc})
    return {"grid": result,
            "n_estimators_vals": n_estimators_vals,
            "max_depth_vals": [d if d is not None else "None" for d in max_depth_vals]}


def build():
    res = rf_grid_search()
    n_vals = res["n_estimators_vals"]
    d_vals = res["max_depth_vals"]
    table = np.zeros((len(d_vals), len(n_vals)))
    d_index = {str(d): i for i, d in enumerate(d_vals)}
    n_index = {n: j for j, n in enumerate(n_vals)}
    for row in res["grid"]:
        table[d_index[str(row["max_depth"])], n_index[row["n_estimators"]]] = row["auc"]

    fig, ax = plt.subplots(figsize=(9, 5.2))
    sns.heatmap(table, annot=True, fmt=".3f", cmap="viridis",
                xticklabels=n_vals,
                yticklabels=[str(d) for d in d_vals],
                cbar_kws={"label": "AUC (test)"},
                linewidths=0.4, linecolor="white", ax=ax)
    ax.set_xlabel("n_estimators (liczba drzew)")
    ax.set_ylabel("max_depth (głębokość)")
    ax.set_title("Random Forest — wpływ n_estimators × max_depth na AUC testu")
    # Podświetl maksimum
    best = np.unravel_index(np.argmax(table), table.shape)
    ax.add_patch(plt.Rectangle((best[1], best[0]), 1, 1, fill=False,
                                edgecolor="#a63446", linewidth=2.6))
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="5", name="rf_hiperparametry",
                comment="Heatmapa AUC testowego dla Random Forest w siatce n_estimators × max_depth — czerwone obramowanie wskazuje konfigurację z maksymalnym AUC.")
    plt.close(fig)
