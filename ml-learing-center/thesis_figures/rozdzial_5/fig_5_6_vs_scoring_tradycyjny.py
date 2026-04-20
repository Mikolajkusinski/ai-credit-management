"""Rysunek 5.6 — Porównanie modeli ML z klasycznym scoringiem (logistic regression)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
from common import apply_style, save_figure, MODEL_COLORS, cached_json, get_metrics_table, get_train_test

apply_style()


@cached_json("baseline_lr")
def train_logistic_baseline():
    X_train, X_test, y_train, y_test, _, _ = get_train_test()
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
    lr.fit(X_train, y_train)
    y_prob = lr.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
    }


def build():
    baseline = train_logistic_baseline()
    metrics = get_metrics_table()

    models = ["Scoring tradycyjny", "Random Forest", "XGBoost", "LSTM"]
    data = {
        "Scoring tradycyjny": [baseline["accuracy"], baseline["f1"], baseline["roc_auc"]],
        "Random Forest":       [metrics["Random Forest"]["accuracy"],
                                metrics["Random Forest"]["f1"],
                                metrics["Random Forest"]["roc_auc"]],
        "XGBoost":             [metrics["XGBoost"]["accuracy"],
                                metrics["XGBoost"]["f1"],
                                metrics["XGBoost"]["roc_auc"]],
        "LSTM":                [metrics["LSTM"]["accuracy"],
                                metrics["LSTM"]["f1"],
                                metrics["LSTM"]["roc_auc"]],
    }
    LABELS = ["Accuracy", "F1-score", "ROC-AUC"]
    x = np.arange(len(LABELS))
    width = 0.2

    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    for i, m in enumerate(models):
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, data[m], width, label=m,
                      color=MODEL_COLORS[m], edgecolor="white", linewidth=1.2)
        for b, v in zip(bars, data[m]):
            ax.text(b.get_x() + b.get_width()/2, v + 0.012,
                    f"{v:.3f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x); ax.set_xticklabels(LABELS)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Wartość metryki")
    ax.set_title("Modele ML vs klasyczny scoring (regresja logistyczna) — porównanie metryk")
    ax.legend(loc="lower left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="6", name="vs_scoring_tradycyjny",
                comment="Porównanie modeli ML z baseline'em klasycznego scoringu (regresja logistyczna) wg trzech metryk (accuracy, F1, ROC-AUC) — kwantyfikacja przewagi uczenia maszynowego.")
    plt.close(fig)
