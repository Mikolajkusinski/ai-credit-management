"""
CREDIT-102: feature engineering parameterized by a 3-month sliding window.

`engineer_features(df, window)` builds the static feature matrix consumed by
RF/XGBoost. `prepare_lstm_sequences(df, window)` builds the (N, 3, 3) tensor +
per-channel scalers consumed by the LSTM. Both take one of the 4 windows from
`sliding_window.WINDOW_DEFS` (oldest -> newest column order inside each window).

The same logic is mirrored in `ml-service/app.py` for inference; keep them in
sync (the legacy 6-month feature engineering in app.py was patched in this
PR to match main.py).
"""
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Fixed category domains from the UCI dataset. get_dummies derives dummy columns
# from values OBSERVED in the frame, so a single-row frame (Flask inference) would
# produce exactly one dummy per column and drop_first=True would remove it --
# silently zeroing all demographics (train/serve skew, Fable5-zmiany.md U1/U2).
# Casting to Categorical with the full domain makes the dummy set independent of
# batch composition; values outside the domain become NaN -> all-zero dummies
# (baseline category), never a shifted column.
UCI_CATEGORIES: Dict[str, List[int]] = {
    "SEX": [1, 2],
    "EDUCATION": [0, 1, 2, 3, 4, 5, 6],
    "MARRIAGE": [0, 1, 2, 3],
}


def engineer_features(
    df: pd.DataFrame, window: Dict[str, List[str]]
) -> Tuple[pd.DataFrame, List[str]]:
    """Build the static feature matrix for one 3-month window.

    Args:
        df: Full UCI dataframe (one row per client, original column names).
        window: One element of `sliding_window.WINDOW_DEFS`, e.g. WINDOW_DEFS[3]
                for W3. Keys: 'pay', 'bill', 'amt'; values: 3 column names each,
                ordered oldest -> newest inside the window.

    Returns:
        (X, features) where X is the feature dataframe (after one-hot encoding
        and NaN/inf cleanup) and `features` is the ordered list of column names
        used (also saved as features_w3.pkl by the training script).
    """
    pay_cols = window["pay"]
    bill_cols = window["bill"]
    amt_cols = window["amt"]

    out = df.copy()
    out["PAY_mean"] = out[pay_cols].mean(axis=1)
    out["PAY_max"] = out[pay_cols].max(axis=1)
    out["BILL_mean"] = out[bill_cols].mean(axis=1)
    out["PAY_AMT_mean"] = out[amt_cols].mean(axis=1)
    out["utilization_rate"] = out["BILL_mean"] / out["LIMIT_BAL"]
    out["BILL_std"] = out[bill_cols].std(axis=1)
    # Trend = newest month in window - oldest month in window.
    out["BILL_trend"] = out[bill_cols[-1]] - out[bill_cols[0]]
    out["payment_ratio"] = out["PAY_AMT_mean"] / (out["BILL_mean"] + 1)
    out["late_count"] = (out[pay_cols] > 0).sum(axis=1)
    # Boolean indicator: any month in the window with delay >= 2.
    out["severe_late"] = (out[pay_cols] >= 2).any(axis=1).astype(int)
    # Most recent payment status inside the window.
    out["recent_pay_status"] = out[pay_cols[-1]]

    for col, cats in UCI_CATEGORIES.items():
        out[col] = pd.Categorical(out[col].astype(int), categories=cats)
    out = pd.get_dummies(out, columns=["EDUCATION", "MARRIAGE", "SEX"], drop_first=True)
    categorical_cols = [
        c for c in out.columns
        if c.startswith(("EDUCATION_", "MARRIAGE_", "SEX_"))
    ]

    features = [
        "LIMIT_BAL", "AGE",
        "PAY_mean", "PAY_max", "BILL_mean", "PAY_AMT_mean",
        "utilization_rate", "BILL_std", "BILL_trend",
        "payment_ratio", "late_count", "severe_late", "recent_pay_status",
    ] + pay_cols + bill_cols + amt_cols + categorical_cols

    X = out[features].fillna(0).replace([np.inf, -np.inf], 0)
    return X, features


def prepare_lstm_sequences(
    df: pd.DataFrame,
    window: Dict[str, List[str]],
    scalers: List[StandardScaler] | None = None,
) -> Tuple[np.ndarray, List[StandardScaler]]:
    """Build the LSTM input tensor (N, 3, 3) and the per-channel scalers.

    Channels: 0 = PAY status, 1 = BILL amount, 2 = PAY amount.
    Time axis: oldest -> newest inside the window.

    Args:
        scalers: When provided, the 3 per-channel scalers are used with
            `transform` only (no refit) -- pass scalers fitted on the training
            rows to avoid preprocessing leakage. When None (legacy behaviour),
            scalers are fitted on `df` itself.

    Returns:
        (X_seq, scalers) where X_seq has shape (len(df), 3, 3) and `scalers`
        is the list of 3 StandardScalers actually used (one per channel).
    """
    pay_cols = window["pay"]
    bill_cols = window["bill"]
    amt_cols = window["amt"]

    X_seq = np.zeros((len(df), 3, 3), dtype=np.float32)
    for t in range(3):
        X_seq[:, t, 0] = df[pay_cols[t]].to_numpy()
        X_seq[:, t, 1] = df[bill_cols[t]].to_numpy()
        X_seq[:, t, 2] = df[amt_cols[t]].to_numpy()

    if scalers is None:
        scalers = []
        for f in range(3):
            sc = StandardScaler()
            sc.fit(X_seq[:, :, f].reshape(-1, 1))
            scalers.append(sc)

    for f in range(3):
        flat = X_seq[:, :, f].reshape(-1, 1)
        X_seq[:, :, f] = scalers[f].transform(flat).reshape(len(df), 3)

    return X_seq, scalers
