"""Rysunek 5.4 — Porównanie modeli: dokładność / interpretowalność / czas / stabilność."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
from common import apply_style, save_figure, MODEL_COLORS, cached_json, get_predictions, get_metrics_table

apply_style()


@cached_json("stability")
def bootstrap_stability(n_boot: int = 40):
    """Stabilność = odchylenie standardowe AUC na bootstrapach test set."""
    p = get_predictions()
    rng = np.random.RandomState(42)
    datasets = {
        "Random Forest": (p["y_test"], p["y_rf"]),
        "XGBoost": (p["y_test"], p["y_xgb"]),
        "LSTM": (p["y_test_lstm"], p["y_lstm"]),
    }
    stab = {}
    for name, (y_true, y_prob) in datasets.items():
        y_true = np.asarray(y_true)
        y_prob = np.asarray(y_prob)
        aucs = []
        n = len(y_true)
        for _ in range(n_boot):
            idx = rng.randint(0, n, size=n)
            try:
                aucs.append(roc_auc_score(y_true[idx], y_prob[idx]))
            except ValueError:
                continue
        stab[name] = float(np.std(aucs))
    return stab


def build():
    metrics = get_metrics_table()
    p = get_predictions()
    stab = bootstrap_stability()
    times = p["inference_time"]

    models = ["Random Forest", "XGBoost", "LSTM"]

    # Oceny 1..5 (wyższa = lepiej). Stabilność: im mniejsze std, tym wyższa ocena.
    # Interpretowalność: wartości stałe (bazując na literaturze/własności modeli).
    interpret_score = {"Random Forest": 3.5, "XGBoost": 3.2, "LSTM": 1.5}

    # Normalizacja AUC → 1..5: map [0.5, 1.0] → [1, 5]
    def map_auc(a): return 1 + (min(max(a, 0.5), 1.0) - 0.5) * 8  # 0.5→1, 1.0→5
    # Normalizacja czasu: inwersja (szybszy = lepiej), skala względna
    max_t = max(times.values()); min_t = min(times.values())
    def map_time(t): return 5 - 4 * ((t - min_t) / max(max_t - min_t, 1e-9))
    # Normalizacja stabilności: inwersja
    max_s = max(stab.values()); min_s = min(stab.values())
    def map_stab(s): return 5 - 4 * ((s - min_s) / max(max_s - min_s, 1e-9))

    data = {}
    for m in models:
        data[m] = [
            map_auc(metrics[m]["roc_auc"]),
            interpret_score[m],
            map_time(times[m]),
            map_stab(stab[m]),
        ]

    CRITERIA = ["Dokładność\n(AUC)", "Interpretowalność", "Szybkość\ninferencji", "Stabilność\n(1/std AUC)"]
    x = np.arange(len(CRITERIA))
    width = 0.25

    fig, ax = plt.subplots(figsize=(11, 5.5))
    for i, m in enumerate(models):
        offset = (i - 1) * width
        bars = ax.bar(x + offset, data[m], width, label=m,
                      color=MODEL_COLORS[m], edgecolor="white", linewidth=1.2)
        for b, v in zip(bars, data[m]):
            ax.text(b.get_x() + b.get_width()/2, v + 0.08,
                    f"{v:.2f}", ha="center", va="bottom", fontsize=9)

    ax.set_xticks(x); ax.set_xticklabels(CRITERIA)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Ocena (skala 1 = słabo, 5 = bardzo dobrze)")
    ax.set_title("Porównanie modeli: dokładność, interpretowalność, szybkość, stabilność")
    ax.legend(loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    # Dodatkowe info pod wykresem
    info = ("Źródło: AUC — zbiór testowy; czas — czas inferencji na całym teście; "
            f"stabilność — std AUC z 40 bootstrapów (RF={stab['Random Forest']:.4f}, "
            f"XGB={stab['XGBoost']:.4f}, LSTM={stab['LSTM']:.4f}).")
    ax.text(0.5, -0.18, info, transform=ax.transAxes,
            ha="center", va="top", fontsize=8, style="italic", color="#555", wrap=True)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="4", name="porownanie_modeli",
                comment="Porównanie trzech modeli wg czterech kryteriów (dokładność mierzona AUC, interpretowalność ekspercka, szybkość inferencji, stabilność z bootstrapu) w ujednoliconej skali 1–5.")
    plt.close(fig)
