"""
CREDIT-106: cost-optimized alert thresholds (FN cost > FP cost).

Replaces the default 0.5 threshold with per-model values that minimize expected
cost on the W3 test split. Cost model: missing a default (FN) is 5x worse than
falsely alerting a good client (FP). Thresholds constrained to (0.1, 0.9) per
TASKS.md DoD.

Output:
- ml-service/alert_thresholds.json  per-model thresholds + cost-model meta

Standalone runner -- loads existing calibrated artifacts from CREDIT-105 so we
don't have to retrain. The same code is mirrored at the end of main.py W3
block (so re-running main.py from scratch also regenerates thresholds).

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python optimize_thresholds.py
"""
from pathlib import Path
from typing import Tuple

import joblib
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from features import engineer_features, prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
ML_SERVICE = HERE.parent / "ml-service"

FN_COST = 5.0
FP_COST = 1.0
THRESHOLD_BOUNDS = (0.1, 0.9)
THRESHOLD_RESOLUTION = 0.005  # 161 candidate thresholds in (0.1, 0.9)


def find_optimal_threshold(
    y_true: np.ndarray, y_proba: np.ndarray,
    fn_cost: float = FN_COST, fp_cost: float = FP_COST,
    bounds: Tuple[float, float] = THRESHOLD_BOUNDS,
) -> Tuple[float, float, int, int]:
    """Sweep thresholds in `bounds` and return (best_threshold, best_cost, fn_at_best, fp_at_best)."""
    n_candidates = int((bounds[1] - bounds[0]) / THRESHOLD_RESOLUTION) + 1
    candidates = np.linspace(bounds[0], bounds[1], n_candidates)

    best_thr, best_cost = bounds[0], float("inf")
    best_fn, best_fp = -1, -1
    for thr in candidates:
        pred = y_proba >= thr
        fn = int(((y_true == 1) & ~pred).sum())
        fp = int(((y_true == 0) & pred).sum())
        cost = fn_cost * fn + fp_cost * fp
        if cost < best_cost:
            best_thr, best_cost, best_fn, best_fp = float(thr), cost, fn, fp
    return best_thr, best_cost, best_fn, best_fp


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def score_test_set() -> dict:
    """Return {model: y_proba_calibrated} + y_true on the 20% test split."""
    df = _load_csv()
    y = df["Default"]
    W3 = WINDOW_DEFS[3]

    X_w3, _ = engineer_features(df, W3)
    scaler_w3 = joblib.load(HERE / "scaler_w3.pkl")
    features_w3 = joblib.load(HERE / "features_w3.pkl")
    X_scaled = scaler_w3.transform(X_w3)
    for col in features_w3:
        if col not in X_w3.columns:
            X_w3[col] = 0
    X_scaled = scaler_w3.transform(X_w3[features_w3])
    _, X_te, _, y_te = train_test_split(X_scaled, y, test_size=0.2, stratify=y, random_state=42)

    rf = joblib.load(HERE / "rf_model_w3.pkl")
    xgb = joblib.load(HERE / "xgb_model_w3.pkl")
    rf_proba = rf.predict_proba(X_te)[:, 1]
    xgb_proba = xgb.predict_proba(X_te)[:, 1]

    X_seq, _ = prepare_lstm_sequences(df, W3)
    _, Xs_te, _, ys_te = train_test_split(X_seq, y, test_size=0.2, stratify=y, random_state=42)
    lstm = load_model(HERE / "lstm_model_w3.keras")
    lstm_cal = joblib.load(ML_SERVICE / "lstm_calibrator_w3.pkl")
    lstm_proba = lstm_cal.predict(lstm.predict(Xs_te, verbose=0).ravel())

    return {
        "y_true": y_te.to_numpy(),
        "randomForest": rf_proba,
        "xgboost": xgb_proba,
        "lstm": lstm_proba,
    }


def main() -> None:
    print(f"Optimizing alert thresholds (FN cost = {FN_COST}, FP cost = {FP_COST}, bounds = {THRESHOLD_BOUNDS})...")
    scores = score_test_set()
    y_true = scores["y_true"]

    results = {}
    for model_key in ("randomForest", "xgboost", "lstm"):
        thr, cost, fn, fp = find_optimal_threshold(y_true, scores[model_key])
        results[model_key] = {"threshold": thr, "cost": cost, "fn": fn, "fp": fp}
        print(
            f"  {model_key:14s} threshold={thr:.3f}  expected_cost={cost:.0f}  "
            f"FN={fn:4d}  FP={fp:4d}"
        )

    payload = {
        "_meta": {
            "fn_cost": FN_COST,
            "fp_cost": FP_COST,
            "fn_to_fp_ratio": FN_COST / FP_COST,
            "bounds": list(THRESHOLD_BOUNDS),
            "resolution": THRESHOLD_RESOLUTION,
            "source": (
                "CREDIT-106: optimized on W3 calibrated test split "
                "(random_state=42, test_size=0.2)"
            ),
        },
        "randomForest": results["randomForest"]["threshold"],
        "xgboost": results["xgboost"]["threshold"],
        "lstm": results["lstm"]["threshold"],
    }

    out = ML_SERVICE / "alert_thresholds.json"
    with out.open("w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
