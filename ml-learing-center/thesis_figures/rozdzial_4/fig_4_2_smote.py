"""Rysunek 4.2 — Porównanie rozkładu klas przed i po SMOTE."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
from common import apply_style, save_figure, PALETTE, cached_pickle, get_train_test

apply_style()


@cached_pickle("smote_pca")
def compute_smote_and_pca():
    X_train, _, y_train, _, _, _ = get_train_test()
    y_train = np.asarray(y_train)

    smote = SMOTE(random_state=42, k_neighbors=5)
    X_res, y_res = smote.fit_resample(X_train, y_train)

    pca = PCA(n_components=2, random_state=42)
    # fitujemy PCA na danych po SMOTE, projekcja również dla before
    pca.fit(X_res)
    X_before_2d = pca.transform(X_train)
    X_after_2d = pca.transform(X_res)

    return {
        "before_counts": np.bincount(y_train).tolist(),
        "after_counts": np.bincount(y_res).tolist(),
        "before_2d": X_before_2d,
        "after_2d": X_after_2d,
        "y_before": y_train,
        "y_after": y_res,
    }


def build():
    d = compute_smote_and_pca()
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # Row 1: bar charts
    for ax, counts, title in [
        (axes[0, 0], d["before_counts"], "Przed SMOTE"),
        (axes[0, 1], d["after_counts"], "Po SMOTE"),
    ]:
        total = sum(counts)
        bars = ax.bar(["Default = 0", "Default = 1"], counts,
                      color=[PALETTE[2], PALETTE[1]], edgecolor="white", linewidth=1.5, width=0.55)
        for bar, cnt in zip(bars, counts):
            pct = 100 * cnt / total
            ax.text(bar.get_x() + bar.get_width()/2, cnt + total*0.01,
                    f"{cnt:,}\n({pct:.1f}%)".replace(",", " "),
                    ha="center", va="bottom", fontweight="bold")
        ax.set_ylabel("Liczność")
        ax.set_title(title)
        ax.set_ylim(0, max(counts) * 1.2)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)

    # Row 2: scatter PCA
    for ax, X_2d, y, title in [
        (axes[1, 0], d["before_2d"], np.asarray(d["y_before"]), "Przed SMOTE — projekcja PCA (2D)"),
        (axes[1, 1], d["after_2d"], np.asarray(d["y_after"]), "Po SMOTE — projekcja PCA (2D)"),
    ]:
        # subsample dla czytelności
        for cls, color, label in [(0, PALETTE[2], "Default = 0"),
                                  (1, PALETTE[1], "Default = 1")]:
            mask = y == cls
            idx = np.where(mask)[0]
            if len(idx) > 2500:
                idx = np.random.RandomState(42).choice(idx, 2500, replace=False)
            ax.scatter(X_2d[idx, 0], X_2d[idx, 1], s=6, color=color, alpha=0.35, label=label)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.set_title(title)
        ax.legend(loc="upper right", markerscale=2)

    fig.suptitle("Wpływ techniki SMOTE na balans klas w zbiorze treningowym",
                 fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="2", name="smote",
                comment="Porównanie przed/po zastosowaniu SMOTE: górny wiersz — rozkład klas, dolny — rzut 2D-PCA 5000 próbek z widocznym zagęszczeniem klasy mniejszościowej po oversamplingu.")
    plt.close(fig)
