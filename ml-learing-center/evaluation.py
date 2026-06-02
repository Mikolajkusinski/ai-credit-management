"""
CREDIT-103: extended metrics + 12 plots for the W3 (3-month) model family.

Loads the _w3 artifacts written by CREDIT-102, replicates the deterministic
train/test split (random_state=42), and produces:
    - reports/metrics_w3.csv          (3 rows x 5 cols: model, AUC, Gini, KS, Brier)
    - reports/roc_comparison_w3.png   (3 models on one plot)
    - reports/pr_comparison_w3.png
    - reports/calibration_comparison_w3.png
    - reports/roc_<model>_w3.png      (3 files)
    - reports/confusion_<model>_w3.png (3 files, threshold 0.5)
    - reports/ks_<model>_w3.png        (3 files)

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python evaluation.py
"""
from pathlib import Path
from typing import Dict, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import ks_2samp
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from features import engineer_features, prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
REPORTS.mkdir(exist_ok=True)

MODELS = ["Random Forest", "XGBoost", "LSTM"]
_SLUG = {"Random Forest": "random_forest", "XGBoost": "xgboost", "LSTM": "lstm"}


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def load_data_and_predict() -> Dict[str, Dict[str, np.ndarray]]:
    """Return {model_name: {"y_true": ..., "y_prob": ...}} on the W3 test split."""
    df = _load_csv()
    y = df["Default"]
    W3 = WINDOW_DEFS[3]

    # Static path -- RF / XGBoost
    X_w3, _ = engineer_features(df, W3)
    scaler_w3 = joblib.load(HERE / "scaler_w3.pkl")
    X_scaled = scaler_w3.transform(X_w3)
    _, X_te, _, y_te = train_test_split(
        X_scaled, y, test_size=0.3, stratify=y, random_state=42
    )

    rf = joblib.load(HERE / "rf_model_w3.pkl")
    xgb = joblib.load(HERE / "xgb_model_w3.pkl")
    rf_prob = rf.predict_proba(X_te)[:, 1]
    xgb_prob = xgb.predict_proba(X_te)[:, 1]

    # Sequence path -- LSTM
    X_seq, _ = prepare_lstm_sequences(df, W3)  # refits scalers, deterministic
    _, Xs_te, _, ys_te = train_test_split(
        X_seq, y, test_size=0.3, stratify=y, random_state=42
    )
    lstm = load_model(HERE / "lstm_model_w3.keras")
    lstm_prob = lstm.predict(Xs_te, verbose=0).ravel()

    y_te_arr = y_te.to_numpy()
    ys_te_arr = ys_te.to_numpy()
    assert np.array_equal(y_te_arr, ys_te_arr), "Static and sequence splits diverged"

    return {
        "Random Forest": {"y_true": y_te_arr, "y_prob": rf_prob},
        "XGBoost":       {"y_true": y_te_arr, "y_prob": xgb_prob},
        "LSTM":          {"y_true": ys_te_arr, "y_prob": lstm_prob},
    }


def compute_metrics_table(preds: Dict[str, Dict[str, np.ndarray]]) -> pd.DataFrame:
    rows = []
    for name in MODELS:
        y_true = preds[name]["y_true"]
        y_prob = preds[name]["y_prob"]
        auc = roc_auc_score(y_true, y_prob)
        gini = 2 * auc - 1
        ks = ks_2samp(y_prob[y_true == 1], y_prob[y_true == 0]).statistic
        brier = brier_score_loss(y_true, y_prob)
        rows.append({"model": name, "AUC": auc, "Gini": gini, "KS": ks, "Brier": brier})
    return pd.DataFrame(rows)


def plot_roc_comparison(preds: Dict, path: Path) -> None:
    plt.figure(figsize=(7, 6))
    for name in MODELS:
        y_true, y_prob = preds[name]["y_true"], preds[name]["y_prob"]
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.4f})")
    plt.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Random")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC -- W3 (3-month window)")
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_pr_comparison(preds: Dict, path: Path) -> None:
    plt.figure(figsize=(7, 6))
    for name in MODELS:
        y_true, y_prob = preds[name]["y_true"], preds[name]["y_prob"]
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        ap = average_precision_score(y_true, y_prob)
        plt.plot(recall, precision, label=f"{name} (AP = {ap:.4f})")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall -- W3 (3-month window)")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_calibration_comparison(preds: Dict, path: Path) -> None:
    plt.figure(figsize=(7, 6))
    for name in MODELS:
        y_true, y_prob = preds[name]["y_true"], preds[name]["y_prob"]
        frac_pos, mean_pred = calibration_curve(y_true, y_prob, n_bins=10, strategy="quantile")
        plt.plot(mean_pred, frac_pos, marker="o", label=name)
    plt.plot([0, 1], [0, 1], "k--", linewidth=0.8, label="Perfectly calibrated")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Fraction of positives")
    plt.title("Calibration (reliability diagram) -- W3")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_roc_single(y_true: np.ndarray, y_prob: np.ndarray, name: str, path: Path) -> None:
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color="C0", linewidth=2)
    plt.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    plt.fill_between(fpr, tpr, alpha=0.15, color="C0")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC -- {name} W3 (AUC = {auc:.4f})")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_confusion(y_true: np.ndarray, y_prob: np.ndarray, name: str, path: Path, threshold: float = 0.5) -> None:
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["NO DEFAULT", "DEFAULT"],
                yticklabels=["NO DEFAULT", "DEFAULT"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion matrix -- {name} W3 (threshold {threshold})")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_ks(y_true: np.ndarray, y_prob: np.ndarray, name: str, path: Path) -> None:
    prob_pos = y_prob[y_true == 1]
    prob_neg = y_prob[y_true == 0]
    ks_stat = ks_2samp(prob_pos, prob_neg).statistic
    plt.figure(figsize=(7, 5))
    sns.kdeplot(prob_neg, label="NO DEFAULT (y=0)", fill=True, color="C0")
    sns.kdeplot(prob_pos, label="DEFAULT (y=1)", fill=True, color="C3")
    plt.xlabel("Predicted probability")
    plt.ylabel("Density")
    plt.title(f"PD distribution -- {name} W3 (KS = {ks_stat:.4f})")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def main() -> None:
    print("Loading W3 artifacts and replicating predictions...")
    preds = load_data_and_predict()

    metrics = compute_metrics_table(preds)
    print("\n===== METRYKI W3 (3-mies.) =====")
    print(metrics.to_string(index=False))
    metrics.to_csv(REPORTS / "metrics_w3.csv", index=False)
    print(f"\nSaved: {REPORTS / 'metrics_w3.csv'}")

    print("Generating comparison plots...")
    plot_roc_comparison(preds, REPORTS / "roc_comparison_w3.png")
    plot_pr_comparison(preds, REPORTS / "pr_comparison_w3.png")
    plot_calibration_comparison(preds, REPORTS / "calibration_comparison_w3.png")

    print("Generating per-model plots...")
    for name in MODELS:
        slug = _SLUG[name]
        y_true = preds[name]["y_true"]
        y_prob = preds[name]["y_prob"]
        plot_roc_single(y_true, y_prob, name, REPORTS / f"roc_{slug}_w3.png")
        plot_confusion(y_true, y_prob, name, REPORTS / f"confusion_{slug}_w3.png")
        plot_ks(y_true, y_prob, name, REPORTS / f"ks_{slug}_w3.png")

    pngs = sorted(REPORTS.glob("*.png"))
    print(f"\nDone. {len(pngs)} PNG files in {REPORTS}/")
    for p in pngs:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
