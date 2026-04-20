"""Ładowanie danych i feature engineering zgodne z main.py."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).resolve().parents[2] / "default_of_credit_card_clients.csv"

PAY_COLS = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_COLS = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT_COLS = [f"PAY_AMT{i}" for i in range(1, 7)]


def load_credit_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Nie znaleziono zbioru danych: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["PAY_mean"] = df[PAY_COLS].mean(axis=1)
    df["PAY_max"] = df[PAY_COLS].max(axis=1)
    df["BILL_mean"] = df[BILL_COLS].mean(axis=1)
    df["PAY_AMT_mean"] = df[PAY_AMT_COLS].mean(axis=1)
    df["utilization_rate"] = df["BILL_mean"] / df["LIMIT_BAL"]
    df["BILL_std"] = df[BILL_COLS].std(axis=1)
    df["BILL_trend"] = df["BILL_AMT1"] - df["BILL_AMT6"]
    df["payment_ratio"] = df["PAY_AMT_mean"] / (df["BILL_mean"] + 1)
    df["late_count"] = (df[PAY_COLS] > 0).sum(axis=1)
    df["severe_late"] = (df[PAY_COLS] >= 2).any(axis=1).astype(int)
    df["recent_pay_status"] = df["PAY_0"]
    df = pd.get_dummies(df, columns=["EDUCATION", "MARRIAGE", "SEX"], drop_first=True)
    return df


def get_feature_list(df_engineered: pd.DataFrame) -> list[str]:
    categorical = [c for c in df_engineered.columns
                   if any(pref in c for pref in ("EDUCATION_", "MARRIAGE_", "SEX_"))]
    features = [
        "LIMIT_BAL", "AGE", "PAY_mean", "PAY_max", "BILL_mean",
        "PAY_AMT_mean", "utilization_rate", "BILL_std",
        "BILL_trend", "payment_ratio", "late_count", "severe_late", "recent_pay_status",
    ] + PAY_COLS + BILL_COLS + PAY_AMT_COLS + categorical
    return features


def get_train_test(seed: int = 42, test_size: float = 0.3, scale: bool = True):
    df = engineer_features(load_credit_data())
    features = get_feature_list(df)
    X = df[features].fillna(0).replace([np.inf, -np.inf], 0)
    y = df["Default"]
    if scale:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X.values
        scaler = None
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, stratify=y, random_state=seed
    )
    return X_train, X_test, y_train, y_test, features, scaler


def get_lstm_sequences():
    df = load_credit_data()
    pay_seq = ["PAY_6", "PAY_5", "PAY_4", "PAY_3", "PAY_2", "PAY_0"]
    bill_seq = ["BILL_AMT6", "BILL_AMT5", "BILL_AMT4", "BILL_AMT3", "BILL_AMT2", "BILL_AMT1"]
    pay_amt_seq = ["PAY_AMT6", "PAY_AMT5", "PAY_AMT4", "PAY_AMT3", "PAY_AMT2", "PAY_AMT1"]
    X_seq = np.zeros((len(df), 6, 3))
    for t in range(6):
        X_seq[:, t, 0] = df[pay_seq[t]]
        X_seq[:, t, 1] = df[bill_seq[t]]
        X_seq[:, t, 2] = df[pay_amt_seq[t]]
    from sklearn.preprocessing import StandardScaler
    scalers = []
    for f in range(3):
        feat = X_seq[:, :, f].reshape(-1, 1)
        sc = StandardScaler()
        X_seq[:, :, f] = sc.fit_transform(feat).reshape(len(df), 6)
        scalers.append(sc)
    y = df["Default"].values
    X_train, X_test, y_train, y_test = train_test_split(
        X_seq, y, test_size=0.3, stratify=y, random_state=42
    )
    return X_train, X_test, y_train, y_test, scalers
