"""Wspólne obliczanie metryk modeli dla rozdziału 5 (cache)."""
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, roc_curve
)
from .cache import cached_pickle
from .data import get_train_test, get_lstm_sequences
from .models import load_rf, load_xgb, load_lstm


@cached_pickle("model_predictions")
def get_predictions():
    """Zwraca y_true oraz y_pred_proba dla każdego z trzech modeli (zgodne z testowym splitem main.py)."""
    # RF i XGB: ten sam split (seed=42) dla X, y
    X_train, X_test, y_train, y_test, _, _ = get_train_test()
    rf = load_rf()
    xgb = load_xgb()

    t0 = time.time()
    y_rf = rf.predict_proba(X_test)[:, 1]
    t_rf = time.time() - t0

    t0 = time.time()
    y_xgb = xgb.predict_proba(X_test)[:, 1]
    t_xgb = time.time() - t0

    # LSTM: osobne sekwencje (inny split ale ten sam seed, stratify → takie same indeksy)
    _, X_test_seq, _, y_test_seq, _ = get_lstm_sequences()
    lstm = load_lstm()
    t0 = time.time()
    y_lstm = lstm.predict(X_test_seq, verbose=0).ravel()
    t_lstm = time.time() - t0

    return {
        "y_test": np.asarray(y_test),
        "y_test_lstm": np.asarray(y_test_seq),
        "y_rf": y_rf.astype(float),
        "y_xgb": y_xgb.astype(float),
        "y_lstm": y_lstm.astype(float),
        "inference_time": {"Random Forest": t_rf, "XGBoost": t_xgb, "LSTM": t_lstm},
    }


def get_metrics_table(threshold: float = 0.5):
    p = get_predictions()
    models = {
        "Random Forest": (p["y_test"], p["y_rf"]),
        "XGBoost": (p["y_test"], p["y_xgb"]),
        "LSTM": (p["y_test_lstm"], p["y_lstm"]),
    }
    out = {}
    for name, (y_true, y_prob) in models.items():
        y_pred = (y_prob >= threshold).astype(int)
        out[name] = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "roc_auc": roc_auc_score(y_true, y_prob),
        }
    return out


def get_confusion_matrices(threshold: float = 0.5):
    p = get_predictions()
    cms = {}
    for name, y_prob_key, y_true_key in [
        ("Random Forest", "y_rf", "y_test"),
        ("XGBoost", "y_xgb", "y_test"),
        ("LSTM", "y_lstm", "y_test_lstm"),
    ]:
        y_true = p[y_true_key]; y_prob = p[y_prob_key]
        y_pred = (y_prob >= threshold).astype(int)
        cms[name] = confusion_matrix(y_true, y_pred)
    return cms


def get_roc_curves():
    p = get_predictions()
    curves = {}
    for name, y_prob_key, y_true_key in [
        ("Random Forest", "y_rf", "y_test"),
        ("XGBoost", "y_xgb", "y_test"),
        ("LSTM", "y_lstm", "y_test_lstm"),
    ]:
        fpr, tpr, _ = roc_curve(p[y_true_key], p[y_prob_key])
        auc = roc_auc_score(p[y_true_key], p[y_prob_key])
        curves[name] = {"fpr": fpr, "tpr": tpr, "auc": auc}
    return curves
