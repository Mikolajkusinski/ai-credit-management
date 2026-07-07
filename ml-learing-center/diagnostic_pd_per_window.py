"""
B1 (Fable5_Task1 / plan 2026-07-07): PD-per-window diagnostic.

Answers the committee question behind the lead-time histogram: is the dominance
of first alerts at the OLDEST window W0 evidence of risk building up early, or
an artifact of distribution shift (a model trained on W3 applied to W0 data)?

Method: score the 6000-client test split on every window W0..W3 with all five
calibrated W3 models (serving semantics: window values remapped into the W3
column slots, exactly like ml-service/app.py map_to_w3_columns; LSTM channels
transformed with the frozen train-fitted scalers). Report the PD distribution
SEPARATELY for non-defaulters (y=0) and defaulters (y=1), plus the alert rate
at each model's cost threshold.

Reading the output:
  - If PD at W0 is elevated for BOTH classes vs W3 -> distribution shift.
  - If elevated only for y=1 -> genuine early risk signal.

Outputs:
    reports/pd_per_window_diagnostic.csv
    reports/pd_per_window_<model>.png   (5x, boxplots per window split by class)
    reports/pd_per_window_report.md
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from features import engineer_features, prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
W3 = WINDOW_DEFS[3]
WINDOW_NAMES = ["W0", "W1", "W2", "W3"]

MODELS = ["Random Forest", "XGBoost", "LightGBM", "CatBoost", "LSTM"]
_SLUG = {
    "Random Forest": "random_forest", "XGBoost": "xgboost",
    "LightGBM": "lightgbm", "CatBoost": "catboost", "LSTM": "lstm",
}
_THR_KEY = {
    "Random Forest": "randomForest", "XGBoost": "xgboost",
    "LightGBM": "lightgbm", "CatBoost": "catboost", "LSTM": "lstm",
}


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    return df


def _remap_to_w3_slots(df: pd.DataFrame, window) -> pd.DataFrame:
    """Vectorized map_to_w3_columns: W3 column slots receive the window's values."""
    out = df.copy()
    for key in ("pay", "bill", "amt"):
        for i in range(3):
            out[W3[key][i]] = df[window[key][i]]
    return out


def main() -> None:
    df = _load_csv()
    y = df["Default"]

    feats = joblib.load(HERE / "features_w3.pkl")
    scaler = joblib.load(HERE / "scaler_w3.pkl")
    lstm_scalers = joblib.load(HERE.parent / "ml-service" / "lstm_scalers_w3.pkl")
    lstm_calibrator = joblib.load(HERE.parent / "ml-service" / "lstm_calibrator_w3.pkl")
    with open(HERE.parent / "ml-service" / "alert_thresholds.json") as f:
        thresholds = json.load(f)

    models = {
        "Random Forest": joblib.load(HERE / "rf_model_w3.pkl"),
        "XGBoost": joblib.load(HERE / "xgb_model_w3.pkl"),
        "LightGBM": joblib.load(HERE / "lightgbm_model_w3.pkl"),
        "CatBoost": joblib.load(HERE / "catboost_model_w3.pkl"),
    }
    lstm = load_model(HERE / "lstm_model_w3.keras")

    # Same test split as every evaluation script (indices via identical stratified split).
    idx_all = np.arange(len(df))
    _, idx_te = train_test_split(idx_all, test_size=0.2, stratify=y, random_state=42)
    y_te = y.iloc[idx_te].to_numpy()

    # PD per model per window on the test rows.
    pd_per: dict[str, dict[str, np.ndarray]] = {m: {} for m in MODELS}
    for w_name, window in zip(WINDOW_NAMES, WINDOW_DEFS):
        mapped = _remap_to_w3_slots(df, window)
        X, _ = engineer_features(mapped, W3)
        X_te = scaler.transform(X[feats].iloc[idx_te])
        for name, model in models.items():
            pd_per[name][w_name] = model.predict_proba(X_te)[:, 1]

        X_seq, _ = prepare_lstm_sequences(df, window, scalers=lstm_scalers)
        raw = lstm.predict(X_seq[idx_te], verbose=0).ravel()
        pd_per["LSTM"][w_name] = lstm_calibrator.predict(raw)

    # Aggregate.
    rows = []
    for name in MODELS:
        thr = thresholds[_THR_KEY[name]]
        for w_name in WINDOW_NAMES:
            p = pd_per[name][w_name]
            for cls in (0, 1):
                sel = p[y_te == cls]
                rows.append({
                    "model": name, "window": w_name, "class": cls,
                    "mean_pd": sel.mean(), "median_pd": np.median(sel),
                    "p90_pd": np.percentile(sel, 90),
                    "alert_rate": float((sel >= thr).mean()),
                    "threshold": thr,
                })
    diag = pd.DataFrame(rows)
    diag.to_csv(REPORTS / "pd_per_window_diagnostic.csv", index=False)

    # Boxplots per model.
    for name in MODELS:
        fig, ax = plt.subplots(figsize=(9, 5))
        data, labels, colors = [], [], []
        for w_name in WINDOW_NAMES:
            p = pd_per[name][w_name]
            data += [p[y_te == 0], p[y_te == 1]]
            labels += [f"{w_name}\ny=0", f"{w_name}\ny=1"]
            colors += ["C0", "C3"]
        bp = ax.boxplot(data, tick_labels=labels, showfliers=False, patch_artist=True)
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.5)
        thr = thresholds[_THR_KEY[name]]
        ax.axhline(thr, color="k", linestyle=":", linewidth=1, label=f"próg {thr:.3f}")
        ax.set_ylabel("PD (calibrated)")
        ax.set_title(f"{name} — rozkład PD per okno, osobno dla klas (test, n=6000)")
        ax.legend()
        plt.tight_layout()
        plt.savefig(REPORTS / f"pd_per_window_{_SLUG[name]}.png", dpi=120)
        plt.close()

    # Verdict logic: mean PD drift W0 vs W3 per class.
    lines = [
        "# B1: Diagnoza PD per okno — narastanie ryzyka czy przesunięcie rozkładu?",
        "",
        "Pytanie: czy dominacja pierwszych alertów w najstarszym oknie W0 "
        "(`lead_time_report.md`) to realny sygnał wczesnego ryzyka, czy artefakt "
        "aplikowania modelu trenowanego na W3 do danych W0?",
        "",
        "Kryterium: jeśli średnie PD na W0 jest podwyższone względem W3 **także dla "
        "klientów spłacających (y=0)** — mamy przesunięcie rozkładu; jeśli tylko dla "
        "defaultujących (y=1) — sygnał jest merytoryczny.",
        "",
        "| Model | ΔPD W0−W3 (y=0) | ΔPD W0−W3 (y=1) | Alert rate y=0: W0 vs W3 | Werdykt |",
        "|---|---:|---:|---|---|",
    ]
    for name in MODELS:
        d = diag[diag["model"] == name].set_index(["window", "class"])
        d0 = d.loc[("W0", 0), "mean_pd"] - d.loc[("W3", 0), "mean_pd"]
        d1 = d.loc[("W0", 1), "mean_pd"] - d.loc[("W3", 1), "mean_pd"]
        ar0 = f"{d.loc[('W0', 0), 'alert_rate']:.1%} vs {d.loc[('W3', 0), 'alert_rate']:.1%}"
        if d0 > 0.01:
            verdict = "przesunięcie rozkładu (PD zawyżone też dla y=0)"
        elif d1 > 0.01 and d0 <= 0.005:
            verdict = "sygnał merytoryczny (wzrost tylko dla y=1)"
        else:
            verdict = "brak istotnego dryfu / mieszany"
        lines.append(f"| {name} | {d0:+.4f} | {d1:+.4f} | {ar0} | {verdict} |")

    lines += [
        "",
        "Pełne rozkłady: `pd_per_window_diagnostic.csv` + `pd_per_window_<model>.png`.",
        "",
        "**Jak używać na obronie:** jeśli dla części modeli PD na W0 jest zawyżone "
        "również dla klasy y=0, histogram lead time należy interpretować ostrożnie: "
        "część 'wczesnych' alertów to koszt przesunięcia rozkładu, nie narastanie "
        "ryzyka — i dokładnie dlatego porównanie static-vs-dynamic wykonujemy przy "
        "stałym budżecie fałszywych alarmów, który ten efekt neutralizuje.",
        "",
    ]
    (REPORTS / "pd_per_window_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved: pd_per_window_diagnostic.csv, pd_per_window_report.md, 5x PNG")
    print("\n".join(lines[7:12]))


if __name__ == "__main__":
    main()
