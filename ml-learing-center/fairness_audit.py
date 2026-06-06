"""
CREDIT-112: Fairness audit (fairlearn) -- DPD / EOD wrt SEX for the 5 W3 models.

Loads the calibrated W3 artifacts produced by CREDIT-102 / CREDIT-105 /
CREDIT-109, replicates the 80/20 test split (random_state=42, stratify=y),
and computes per-model fairness metrics across the SEX attribute:

    - Demographic Parity Difference (DPD)  -- gap in selection rate male vs female
    - Equalized Odds Difference (EOD)      -- max(|TPR_m - TPR_f|, |FPR_m - FPR_f|)
    - Per-group selection rate, TPR, FPR   -- diagnostic breakdown

Binarization uses the cost-optimized per-model thresholds saved by CREDIT-106 in
`../ml-service/alert_thresholds.json`. Falls back to 0.5 if the file is missing.

SEX coding (UCI): 1 = male, 2 = female. The audit emits a WARN flag whenever
|DPD| > 0.1 or |EOD| > 0.1 (CREDIT-112 DoD).

Outputs:
    - reports/fairness_metrics_w3.csv     -- one row per model, all metrics + warns
    - reports/fairness_selection_rate_w3.png  -- grouped bar chart, sel-rate by SEX
    - reports/fairness_tpr_fpr_w3.png     -- grouped bar chart, TPR/FPR by SEX
    - reports/fairness_report.md          -- markdown summary

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python fairness_audit.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    equalized_odds_difference,
    false_positive_rate,
    selection_rate,
    true_positive_rate,
)
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from features import engineer_features, prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
REPORTS.mkdir(exist_ok=True)
THRESHOLDS_PATH = HERE.parent / "ml-service" / "alert_thresholds.json"

MODELS: List[str] = ["Random Forest", "XGBoost", "LightGBM", "CatBoost", "LSTM"]
_THR_KEY: Dict[str, str] = {
    "Random Forest": "randomForest",
    "XGBoost":       "xgboost",
    "LightGBM":      "lightgbm",
    "CatBoost":      "catboost",
    "LSTM":          "lstm",
}
SEX_LABELS = {1: "male", 2: "female"}
WARN_THRESHOLD = 0.1


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def _load_thresholds() -> Dict[str, float]:
    if not THRESHOLDS_PATH.exists():
        print(f"WARN: {THRESHOLDS_PATH} not found, falling back to 0.5 for all models.")
        return {k: 0.5 for k in _THR_KEY.values()}
    with open(THRESHOLDS_PATH) as f:
        payload = json.load(f)
    return {k: float(payload[k]) for k in _THR_KEY.values()}


def load_test_split() -> Tuple[Dict[str, Dict[str, np.ndarray]], np.ndarray]:
    """Return ({model: {y_true, y_prob}}, sex_te) on the W3 20% test split.

    Mirrors evaluation.py.load_data_and_predict() but additionally returns the
    aligned SEX column for fairness slicing.
    """
    df = _load_csv()
    y = df["Default"]
    sex_all = df["SEX"].to_numpy()
    W3 = WINDOW_DEFS[3]

    # Static path -- shared scaler + split for RF / XGBoost / LightGBM / CatBoost
    X_w3, _ = engineer_features(df, W3)
    scaler_w3 = joblib.load(HERE / "scaler_w3.pkl")
    X_scaled = scaler_w3.transform(X_w3)
    _, X_te, _, y_te, _, sex_te = train_test_split(
        X_scaled, y, sex_all, test_size=0.2, stratify=y, random_state=42
    )

    rf = joblib.load(HERE / "rf_model_w3.pkl")
    xgb = joblib.load(HERE / "xgb_model_w3.pkl")
    lgbm = joblib.load(HERE / "lightgbm_model_w3.pkl")
    cat = joblib.load(HERE / "catboost_model_w3.pkl")

    # Sequence path -- LSTM with external isotonic calibrator
    X_seq, _ = prepare_lstm_sequences(df, W3)
    _, Xs_te, _, ys_te = train_test_split(
        X_seq, y, test_size=0.2, stratify=y, random_state=42
    )
    lstm = load_model(HERE / "lstm_model_w3.keras")
    lstm_calibrator = joblib.load(HERE.parent / "ml-service" / "lstm_calibrator_w3.pkl")
    lstm_raw = lstm.predict(Xs_te, verbose=0).ravel()

    y_te_arr = y_te.to_numpy()
    ys_te_arr = ys_te.to_numpy()
    assert np.array_equal(y_te_arr, ys_te_arr), "Static and sequence splits diverged"

    preds = {
        "Random Forest": {"y_true": y_te_arr, "y_prob": rf.predict_proba(X_te)[:, 1]},
        "XGBoost":       {"y_true": y_te_arr, "y_prob": xgb.predict_proba(X_te)[:, 1]},
        "LightGBM":      {"y_true": y_te_arr, "y_prob": lgbm.predict_proba(X_te)[:, 1]},
        "CatBoost":      {"y_true": y_te_arr, "y_prob": cat.predict_proba(X_te)[:, 1]},
        "LSTM":          {"y_true": y_te_arr, "y_prob": lstm_calibrator.predict(lstm_raw)},
    }
    return preds, sex_te


def compute_fairness_metrics(
    preds: Dict[str, Dict[str, np.ndarray]],
    sex_te: np.ndarray,
    thresholds: Dict[str, float],
) -> pd.DataFrame:
    """One row per model with DPD/EOD, per-group rates, warn flags."""
    rows = []
    for name in MODELS:
        y_true = preds[name]["y_true"]
        y_prob = preds[name]["y_prob"]
        thr = thresholds[_THR_KEY[name]]
        y_pred = (y_prob >= thr).astype(int)

        dpd = demographic_parity_difference(y_true, y_pred, sensitive_features=sex_te)
        eod = equalized_odds_difference(y_true, y_pred, sensitive_features=sex_te)

        # Per-group breakdown (selection rate, TPR, FPR, accuracy)
        mf = MetricFrame(
            metrics={
                "selection_rate": selection_rate,
                "tpr": true_positive_rate,
                "fpr": false_positive_rate,
                "accuracy": accuracy_score,
            },
            y_true=y_true,
            y_pred=y_pred,
            sensitive_features=sex_te,
        )
        by_group = mf.by_group  # DataFrame indexed by SEX value

        rows.append({
            "model": name,
            "threshold": round(thr, 4),
            "DPD": dpd,
            "EOD": eod,
            "sel_rate_male":   by_group.loc[1, "selection_rate"],
            "sel_rate_female": by_group.loc[2, "selection_rate"],
            "tpr_male":   by_group.loc[1, "tpr"],
            "tpr_female": by_group.loc[2, "tpr"],
            "fpr_male":   by_group.loc[1, "fpr"],
            "fpr_female": by_group.loc[2, "fpr"],
            "acc_male":   by_group.loc[1, "accuracy"],
            "acc_female": by_group.loc[2, "accuracy"],
            "n_male":   int((sex_te == 1).sum()),
            "n_female": int((sex_te == 2).sum()),
            "dpd_warn": abs(dpd) > WARN_THRESHOLD,
            "eod_warn": abs(eod) > WARN_THRESHOLD,
        })
    return pd.DataFrame(rows)


def plot_selection_rate(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(df))
    w = 0.38
    ax.bar(x - w / 2, df["sel_rate_male"],   width=w, label="male (SEX=1)",   color="C0")
    ax.bar(x + w / 2, df["sel_rate_female"], width=w, label="female (SEX=2)", color="C3")
    ax.set_xticks(x)
    ax.set_xticklabels(df["model"], rotation=15)
    ax.set_ylabel("Selection rate (P[ŷ=1])")
    ax.set_title("Demographic Parity: selection rate by SEX -- W3 (cost-opt threshold)")
    ax.legend()
    ax.grid(axis="y", linestyle=":", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_tpr_fpr(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    x = np.arange(len(df))
    w = 0.38

    axes[0].bar(x - w / 2, df["tpr_male"],   width=w, label="male",   color="C0")
    axes[0].bar(x + w / 2, df["tpr_female"], width=w, label="female", color="C3")
    axes[0].set_xticks(x); axes[0].set_xticklabels(df["model"], rotation=15)
    axes[0].set_title("TPR by SEX (recall on defaulters)")
    axes[0].set_ylabel("Rate")
    axes[0].grid(axis="y", linestyle=":", linewidth=0.5)
    axes[0].legend()

    axes[1].bar(x - w / 2, df["fpr_male"],   width=w, label="male",   color="C0")
    axes[1].bar(x + w / 2, df["fpr_female"], width=w, label="female", color="C3")
    axes[1].set_xticks(x); axes[1].set_xticklabels(df["model"], rotation=15)
    axes[1].set_title("FPR by SEX (false alerts on non-defaulters)")
    axes[1].grid(axis="y", linestyle=":", linewidth=0.5)
    axes[1].legend()

    fig.suptitle("Equalized Odds breakdown -- W3 (cost-opt threshold)")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def write_markdown_report(df: pd.DataFrame, sex_te: np.ndarray, path: Path) -> None:
    n_total = len(sex_te)
    n_male = int((sex_te == 1).sum())
    n_female = int((sex_te == 2).sum())

    lines: List[str] = []
    lines.append("# CREDIT-112: Fairness audit (DPD / EOD wrt SEX)")
    lines.append("")
    lines.append("Audit dataset: **W3 test split** (random_state=42, test_size=0.2, stratify=y).")
    lines.append(
        f"Test size: **{n_total}** clients "
        f"(male={n_male}, female={n_female}); SEX coding: 1=male, 2=female (UCI)."
    )
    lines.append(
        "Binarization: per-model cost-optimized thresholds from "
        "`ml-service/alert_thresholds.json` (CREDIT-106, FN=5x FP)."
    )
    lines.append(f"Warning rule: **|DPD| > {WARN_THRESHOLD}** or **|EOD| > {WARN_THRESHOLD}**.")
    lines.append("")
    lines.append("## Summary table")
    lines.append("")
    lines.append("| Model | Threshold | DPD | EOD | DPD warn | EOD warn |")
    lines.append("|---|---:|---:|---:|:---:|:---:|")
    for _, r in df.iterrows():
        dpd_flag = "[WARN]" if r["dpd_warn"] else "ok"
        eod_flag = "[WARN]" if r["eod_warn"] else "ok"
        lines.append(
            f"| {r['model']} | {r['threshold']:.3f} | {r['DPD']:+.4f} | {r['EOD']:+.4f} | {dpd_flag} | {eod_flag} |"
        )
    lines.append("")

    lines.append("## Per-group breakdown")
    lines.append("")
    lines.append("| Model | sel_rate male | sel_rate female | TPR male | TPR female | FPR male | FPR female |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, r in df.iterrows():
        lines.append(
            f"| {r['model']} | {r['sel_rate_male']:.4f} | {r['sel_rate_female']:.4f} | "
            f"{r['tpr_male']:.4f} | {r['tpr_female']:.4f} | {r['fpr_male']:.4f} | {r['fpr_female']:.4f} |"
        )
    lines.append("")

    n_warn = int(df["dpd_warn"].sum() + df["eod_warn"].sum())
    lines.append("## Verdict")
    lines.append("")
    if n_warn == 0:
        lines.append(
            "All 5 models pass the |diff| <= 0.1 threshold on both DPD and EOD. "
            "No fairness warnings raised."
        )
    else:
        warned = df[df["dpd_warn"] | df["eod_warn"]]["model"].tolist()
        lines.append(
            f"{n_warn} warning(s) raised across {len(warned)} model(s): {', '.join(warned)}. "
            "Review per-group selection / TPR / FPR rates above."
        )
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append("- `reports/fairness_metrics_w3.csv` -- full numeric table")
    lines.append("- `reports/fairness_selection_rate_w3.png` -- selection rate by SEX")
    lines.append("- `reports/fairness_tpr_fpr_w3.png` -- TPR / FPR by SEX")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("Loading W3 artifacts and reproducing predictions...")
    preds, sex_te = load_test_split()
    thresholds = _load_thresholds()

    print("Computing fairness metrics (DPD, EOD, per-group rates)...")
    df = compute_fairness_metrics(preds, sex_te, thresholds)

    csv_path = REPORTS / "fairness_metrics_w3.csv"
    df.to_csv(csv_path, index=False)

    print("\n===== CREDIT-112 fairness audit (W3, |diff| > 0.1 triggers WARN) =====")
    print(
        df[["model", "threshold", "DPD", "EOD", "dpd_warn", "eod_warn"]]
        .to_string(index=False, float_format=lambda v: f"{v:+.4f}")
    )

    warn_models = df[df["dpd_warn"] | df["eod_warn"]]["model"].tolist()
    if warn_models:
        print(f"\nWARN: fairness threshold breached for: {', '.join(warn_models)}")
    else:
        print("\nOK: all models within |diff| <= 0.1 on both DPD and EOD.")

    print("\nGenerating plots...")
    plot_selection_rate(df, REPORTS / "fairness_selection_rate_w3.png")
    plot_tpr_fpr(df, REPORTS / "fairness_tpr_fpr_w3.png")

    print("Writing markdown report...")
    write_markdown_report(df, sex_te, REPORTS / "fairness_report.md")

    print(f"\nSaved: {csv_path}")
    print(f"Saved: {REPORTS / 'fairness_selection_rate_w3.png'}")
    print(f"Saved: {REPORTS / 'fairness_tpr_fpr_w3.png'}")
    print(f"Saved: {REPORTS / 'fairness_report.md'}")


if __name__ == "__main__":
    main()
