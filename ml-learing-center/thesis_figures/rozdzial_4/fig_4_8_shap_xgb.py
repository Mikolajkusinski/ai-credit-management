"""Rysunek 4.8 — Wartości SHAP dla modelu XGBoost (finalny artefakt W3).

TreeExplainer na estymatorze bazowym spod CalibratedClassifierCV (skala margin
modelu bazowego; kalibracja monotoniczna nie zmienia rankingu cech).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # thesis_figures/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # ml-learing-center/

import numpy as np
import matplotlib.pyplot as plt
import shap
from common import (apply_style, save_figure, cached_pickle,
                    load_xgb_w3, load_feature_list_w3, load_static_scaler_w3)

apply_style()
HERE = Path(__file__).resolve().parents[2]


@cached_pickle("shap_xgb_w3")
def compute_shap():
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from features import engineer_features
    from sliding_window import WINDOW_DEFS

    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    y = df["Default"]
    features = load_feature_list_w3()
    X, _ = engineer_features(df, WINDOW_DEFS[3])
    scaler = load_static_scaler_w3()
    _, X_te, _, _ = train_test_split(X[features], y, test_size=0.2,
                                     stratify=y, random_state=42)

    rng = np.random.RandomState(42)
    sample_idx = rng.choice(len(X_te), 1000, replace=False)
    X_sample = scaler.transform(X_te.iloc[sample_idx])

    xgb = load_xgb_w3(base=True)
    shap_values = shap.TreeExplainer(xgb).shap_values(X_sample)
    shap_values = np.asarray(shap_values)
    if shap_values.ndim == 3:
        shap_values = shap_values[..., -1]

    return {
        "shap_values": shap_values,
        "X_sample": X_sample,
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

    plt.suptitle("Wyjaśnialność modelu XGBoost (W3) — wartości SHAP (n=1000 z testu)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    return plt.gcf()


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=4, idx="8", name="shap_xgb",
                comment="Wartości SHAP finalnego XGB W3 (estymator bazowy, n=1000 z testu) — beeswarm pokazuje kierunek i rozkład wpływu cech, bar średnią globalną istotność.")
    plt.close(fig)
