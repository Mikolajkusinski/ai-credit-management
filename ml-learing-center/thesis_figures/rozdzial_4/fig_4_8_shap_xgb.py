"""Rysunek 4.8 — Wartości SHAP dla modelu XGBoost."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import shap
from common import apply_style, save_figure, cached_pickle, get_train_test, load_xgb, load_feature_list

apply_style()


@cached_pickle("shap_xgb")
def compute_shap():
    X_train, X_test, _, _, _, _ = get_train_test()
    features = load_feature_list()
    xgb = load_xgb()

    # Background z 200 próbek trenujących, eksplanacja dla 1000 z testu
    rng = np.random.RandomState(42)
    bg_idx = rng.choice(len(X_train), 200, replace=False)
    sample_idx = rng.choice(len(X_test), 1000, replace=False)

    explainer = shap.TreeExplainer(xgb, X_train[bg_idx])
    shap_values = explainer.shap_values(X_test[sample_idx])

    return {
        "shap_values": shap_values,
        "X_sample": X_test[sample_idx],
        "features": features,
    }


def build():
    d = compute_shap()
    features = d["features"]
    sv = d["shap_values"]
    X_sample = d["X_sample"]

    fig = plt.figure(figsize=(14, 6.5))

    # Lewy panel: beeswarm summary plot
    plt.subplot(1, 2, 1)
    shap.summary_plot(sv, X_sample, feature_names=features,
                      max_display=15, show=False, plot_size=None)
    plt.title("SHAP beeswarm — rozkład wartości SHAP dla top 15 cech",
              fontsize=11, fontweight="bold")

    # Prawy panel: bar mean |SHAP|
    plt.subplot(1, 2, 2)
    shap.summary_plot(sv, X_sample, feature_names=features,
                      plot_type="bar", max_display=15, show=False,
                      color="#6b8e23")
    plt.title("Średnia |SHAP| — globalna istotność cech",
              fontsize=11, fontweight="bold")

    plt.suptitle("Wyjaśnialność modelu XGBoost — wartości SHAP (n=1000)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    return plt.gcf()


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="8", name="shap_xgb",
                comment="Wartości SHAP dla 1000 próbek testowych z wytrenowanego XGBoost — beeswarm (lewo) pokazuje kierunek i rozkład wpływu cech, bar (prawo) średnią globalną istotność.")
    plt.close(fig)
