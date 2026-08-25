import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier

df = pd.read_csv("default_of_credit_card_clients.csv", header=1)
df.rename(
    columns={"default payment next month": "Default"},
    inplace=True
)
df.drop(columns=["ID"], inplace=True)
print(df.columns.tolist())

# Konwertujemy kolumny kategoryczne na int przed One-Hot Encodingiem
df["EDUCATION"] = df["EDUCATION"].astype(int)
df["MARRIAGE"] = df["MARRIAGE"].astype(int)
df["SEX"] = df["SEX"].astype(int)

# Model statyczny
pay_cols = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]
pay_amt_cols = [f"PAY_AMT{i}" for i in range(1, 7)]

df["PAY_mean"] = df[pay_cols].mean(axis=1)
df["PAY_max"] = df[pay_cols].max(axis=1)
df["BILL_mean"] = df[bill_cols].mean(axis=1)
df["PAY_AMT_mean"] = df[pay_amt_cols].mean(axis=1)
# NOWA CECHA: Wykorzystanie limitu (średni rachunek / limit)
df["utilization_rate"] = df["BILL_mean"] / df["LIMIT_BAL"]
# NOWA CECHA: Odchylenie standardowe rachunków (zmienność)
df["BILL_std"] = df[bill_cols].std(axis=1)

# DODATKOWE CECHY FINANSOWE
# Trend zadłużenia: czy rachunek rośnie? (wrzesień - kwiecień)
df["BILL_trend"] = df["BILL_AMT1"] - df["BILL_AMT6"]

# Stosunek wpłat do rachunków (payment ratio)
df["payment_ratio"] = df["PAY_AMT_mean"] / (df["BILL_mean"] + 1)  # +1 aby uniknąć dzielenia przez 0

# Ile razy klient miał opóźnienie > 0
df["late_count"] = (df[pay_cols] > 0).sum(axis=1)

# Czy klient miał kiedykolwiek poważne opóźnienie (2+ miesiące)
df["severe_late"] = (df[pay_cols] >= 2).any(axis=1).astype(int)

# Najnowszy status płatności (PAY_0) - bardzo silny predyktor
df["recent_pay_status"] = df["PAY_0"]

# ONE-HOT ENCODING dla EDUCATION i MARRIAGE
df = pd.get_dummies(df, columns=["EDUCATION", "MARRIAGE", "SEX"], drop_first=True)

categorical_cols = [c for c in df.columns if "EDUCATION_" in c or "MARRIAGE_" in c or "SEX_" in c]
features = [
    "LIMIT_BAL", "AGE", "PAY_mean", "PAY_max", "BILL_mean",
    "PAY_AMT_mean", "utilization_rate", "BILL_std",
    "BILL_trend", "payment_ratio", "late_count", "severe_late", "recent_pay_status"
] + pay_cols + bill_cols + pay_amt_cols + categorical_cols

X = df[features]
y = df["Default"]

# CZYSZCZENIE DANYCH: Usunięcie wierszy z NaN lub zastąpienie ich
X = X.fillna(0)

# Sprawdzenie czy są jeszcze NaN lub nieskończoności
X = X.replace([np.inf, -np.inf], 0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, stratify=y, random_state=42
)

rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=10,
    min_samples_leaf=5,
    class_weight="balanced",
    random_state=42
)

rf.fit(X_train, y_train)
y_pred_rf = rf.predict_proba(X_test)[:, 1]
print("AUC Random Forest:", roc_auc_score(y_test, y_pred_rf))

xgb = XGBClassifier(
    n_estimators=800,
    learning_rate=0.02,  # Wolniejsze uczenie = lepsze wyniki
    max_depth=4,  # Płytsze drzewa, ale więcej iteracji
    subsample=0.7,
    colsample_bytree=0.7,
    reg_alpha=0.1,  # Regularyzacja L1
    reg_lambda=1.0,  # Regularyzacja L2
    scale_pos_weight=(len(y) - sum(y)) / sum(y),
    random_state=42,
    eval_metric='auc'
)

xgb.fit(X_train, y_train)
y_pred_xgb = xgb.predict_proba(X_test)[:, 1]
print("AUC XGBoost:", roc_auc_score(y_test, y_pred_xgb))

# MODEL DYNAMICZNY (LSTM)
# Mapujemy kolumny tak, aby odpowiadały kolejnym miesiącom (od najstarszego do najnowszego)
# Wrzesień (0), Sierpień (2), Lipiec (3), Czerwiec (4), Maj (5), Kwiecień (6)
pay_seq_cols = ["PAY_6", "PAY_5", "PAY_4", "PAY_3", "PAY_2", "PAY_0"]
bill_seq_cols = ["BILL_AMT6", "BILL_AMT5", "BILL_AMT4", "BILL_AMT3", "BILL_AMT2", "BILL_AMT1"]
pay_amt_seq_cols = ["PAY_AMT6", "PAY_AMT5", "PAY_AMT4", "PAY_AMT3", "PAY_AMT2", "PAY_AMT1"]

# Przygotowanie danych do LSTM: (sample, timesteps, features)
X_seq = np.zeros((len(df), 6, 3))

for t in range(6):
    X_seq[:, t, 0] = df[pay_seq_cols[t]]
    X_seq[:, t, 1] = df[bill_seq_cols[t]]
    X_seq[:, t, 2] = df[pay_amt_seq_cols[t]]

# SKALOWANIE: Skalujemy każdą cechę z osobna (0=PAY, 1=BILL, 2=PAY_AMT)
lstm_scalers = []
for f in range(3):
    feat_data = X_seq[:, :, f].reshape(-1, 1)
    scaler_seq = StandardScaler()
    X_seq[:, :, f] = scaler_seq.fit_transform(feat_data).reshape(len(df), 6)
    lstm_scalers.append(scaler_seq)

X_train_seq, X_test_seq, y_train_seq, y_test_seq = train_test_split(
    X_seq, y, test_size=0.3, stratify=y, random_state=42
)

model = Sequential([
    Input(shape=(6, 3)),
    LSTM(32),
    Dropout(0.3),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["AUC"]
)

lstm_class_weights = compute_class_weight(
    class_weight="balanced",
    classes=np.array([0, 1]),
    y=y_train_seq.values
)
lstm_class_weight_dict = {0: lstm_class_weights[0], 1: lstm_class_weights[1]}

lstm_callbacks = [
    EarlyStopping(monitor="val_auc", mode="max", patience=5, restore_best_weights=True),
    ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=3, min_lr=1e-5),
]

history = model.fit(
    X_train_seq,
    y_train_seq,
    validation_split=0.2,
    epochs=60,
    batch_size=256,
    class_weight=lstm_class_weight_dict,
    callbacks=lstm_callbacks,
    verbose=1
)

y_pred_lstm = model.predict(X_test_seq).ravel()
print("AUC LSTM:", roc_auc_score(y_test_seq, y_pred_lstm))

print("\n===== WYNIKI KOŃCOWE =====")
print(f"AUC Random Forest: {roc_auc_score(y_test, y_pred_rf):.4f}")
print(f"AUC XGBoost:       {roc_auc_score(y_test, y_pred_xgb):.4f}")
print(f"AUC LSTM:          {roc_auc_score(y_test_seq, y_pred_lstm):.4f}")

# ========== SAVE MODELS ==========
import joblib


# Static models + scaler + features
joblib.dump(rf, "rf_model.pkl")
joblib.dump(xgb, "xgb_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(features, "features.pkl")

# LSTM (Keras model) + scalers
model.save("lstm_model.keras")
joblib.dump(lstm_scalers, "../ml-service/lstm_scalers.pkl")

print("Models saved: rf_model.pkl, xgb_model.pkl, lstm_model.keras, lstm_scalers.pkl")


# ========== W3 RETRAIN + CALIBRATION (CREDIT-102 / CREDIT-105) ==========
# CREDIT-102: train RF/XGBoost/LSTM on the W3 sliding window (newest 3 months,
# Jul/Aug/Sep), aligned with the October default label. Same train/inference
# distribution lets CREDIT-104 iterate W0..W3 at inference without OOD shift.
# CREDIT-105: wrap each model with isotonic calibration on a held-out calib
# split (60/20/20: train/calib/test). RF/XGB use CalibratedClassifierCV
# (cv='prefit'); LSTM gets a sklearn IsotonicRegression applied to raw outputs.
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

from sliding_window import WINDOW_DEFS
from features import engineer_features, prepare_lstm_sequences

# Reload CSV fresh -- the legacy section above already one-hot encoded df, so
# engineer_features can't get_dummies("EDUCATION") on it anymore.
df_w3 = pd.read_csv("default_of_credit_card_clients.csv", header=1)
df_w3.rename(columns={"default payment next month": "Default"}, inplace=True)
df_w3.drop(columns=["ID"], inplace=True)
df_w3["EDUCATION"] = df_w3["EDUCATION"].astype(int)
df_w3["MARRIAGE"] = df_w3["MARRIAGE"].astype(int)
df_w3["SEX"] = df_w3["SEX"].astype(int)
y_w3 = df_w3["Default"]

W3 = WINDOW_DEFS[3]

# Static features on W3 (RF / XGBoost)
X_w3, features_w3 = engineer_features(df_w3, W3)

# 3-way split (60 / 20 / 20): test first (20% held out for final eval), then
# split the remaining 80% into 75/25 -> 60% train / 20% calib of total.
# Split BEFORE scaling (leakage fix 2026-07-07): the scaler must see training
# rows only -- fitting on the full panel leaked test-row mean/std into
# preprocessing. Row assignment is unchanged: a stratified split depends only
# on y, sizes and random_state, not on X values.
X_tmp_raw, X_te_raw, y_tmp, y_te_w3 = train_test_split(
    X_w3, y_w3, test_size=0.2, stratify=y_w3, random_state=42
)
X_tr_raw, X_cal_raw, y_tr_w3, y_cal_w3 = train_test_split(
    X_tmp_raw, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42
)
scaler_w3 = StandardScaler().fit(X_tr_raw)
X_tr_w3 = scaler_w3.transform(X_tr_raw)
X_cal_w3 = scaler_w3.transform(X_cal_raw)
X_te_w3 = scaler_w3.transform(X_te_raw)

# RF -- train on 60%, calibrate on 20%, evaluate on 20%
rf_base = RandomForestClassifier(
    n_estimators=500, max_depth=10, min_samples_leaf=5,
    class_weight="balanced", random_state=42,
).fit(X_tr_w3, y_tr_w3)
rf_uncal_proba = rf_base.predict_proba(X_te_w3)[:, 1]
auc_rf_uncal = roc_auc_score(y_te_w3, rf_uncal_proba)
brier_rf_uncal = brier_score_loss(y_te_w3, rf_uncal_proba)

rf_w3 = CalibratedClassifierCV(FrozenEstimator(rf_base), method="isotonic").fit(X_cal_w3, y_cal_w3)
rf_cal_proba = rf_w3.predict_proba(X_te_w3)[:, 1]
auc_rf_cal = roc_auc_score(y_te_w3, rf_cal_proba)
brier_rf_cal = brier_score_loss(y_te_w3, rf_cal_proba)

# XGBoost -- same protocol
xgb_base = XGBClassifier(
    n_estimators=800, learning_rate=0.02, max_depth=4,
    subsample=0.7, colsample_bytree=0.7,
    reg_alpha=0.1, reg_lambda=1.0,
    scale_pos_weight=(len(y_w3) - sum(y_w3)) / sum(y_w3),
    random_state=42, eval_metric="auc",
).fit(X_tr_w3, y_tr_w3)
xgb_uncal_proba = xgb_base.predict_proba(X_te_w3)[:, 1]
auc_xgb_uncal = roc_auc_score(y_te_w3, xgb_uncal_proba)
brier_xgb_uncal = brier_score_loss(y_te_w3, xgb_uncal_proba)

xgb_w3 = CalibratedClassifierCV(FrozenEstimator(xgb_base), method="isotonic").fit(X_cal_w3, y_cal_w3)
xgb_cal_proba = xgb_w3.predict_proba(X_te_w3)[:, 1]
auc_xgb_cal = roc_auc_score(y_te_w3, xgb_cal_proba)
brier_xgb_cal = brier_score_loss(y_te_w3, xgb_cal_proba)

# LightGBM -- CREDIT-109; same 3-way split + isotonic calibration protocol as RF/XGB
lgbm_base = LGBMClassifier(
    n_estimators=800, learning_rate=0.02, max_depth=4,
    subsample=0.7, colsample_bytree=0.7,
    reg_alpha=0.1, reg_lambda=1.0,
    class_weight="balanced",
    random_state=42, verbose=-1,
).fit(X_tr_w3, y_tr_w3)
lgbm_uncal_proba = lgbm_base.predict_proba(X_te_w3)[:, 1]
auc_lgbm_uncal = roc_auc_score(y_te_w3, lgbm_uncal_proba)
brier_lgbm_uncal = brier_score_loss(y_te_w3, lgbm_uncal_proba)

lgbm_w3 = CalibratedClassifierCV(FrozenEstimator(lgbm_base), method="isotonic").fit(X_cal_w3, y_cal_w3)
lgbm_cal_proba = lgbm_w3.predict_proba(X_te_w3)[:, 1]
auc_lgbm_cal = roc_auc_score(y_te_w3, lgbm_cal_proba)
brier_lgbm_cal = brier_score_loss(y_te_w3, lgbm_cal_proba)

# CatBoost -- CREDIT-109; same protocol
cat_base = CatBoostClassifier(
    iterations=800, learning_rate=0.02, depth=4,
    subsample=0.7, colsample_bylevel=0.7,
    l2_leaf_reg=3.0,
    auto_class_weights="Balanced",
    random_state=42, verbose=False,
    bootstrap_type="Bernoulli",
).fit(X_tr_w3, y_tr_w3)
cat_uncal_proba = cat_base.predict_proba(X_te_w3)[:, 1]
auc_cat_uncal = roc_auc_score(y_te_w3, cat_uncal_proba)
brier_cat_uncal = brier_score_loss(y_te_w3, cat_uncal_proba)

cat_w3 = CalibratedClassifierCV(FrozenEstimator(cat_base), method="isotonic").fit(X_cal_w3, y_cal_w3)
cat_cal_proba = cat_w3.predict_proba(X_te_w3)[:, 1]
auc_cat_cal = roc_auc_score(y_te_w3, cat_cal_proba)
brier_cat_cal = brier_score_loss(y_te_w3, cat_cal_proba)

# LSTM -- tensor (N, 3, 3), same 3-way split via shared random_state=42.
# Channel scalers fitted on TRAIN rows only (leakage fix 2026-07-07): derive
# the train-row indices with the same double stratified split, fit there,
# then transform the full panel with the frozen scalers.
_idx_all = np.arange(len(df_w3))
_idx_tmp, _idx_te = train_test_split(
    _idx_all, test_size=0.2, stratify=y_w3, random_state=42
)
_idx_tr, _idx_cal = train_test_split(
    _idx_tmp, test_size=0.25, stratify=y_w3.iloc[_idx_tmp], random_state=42
)
assert np.array_equal(y_w3.iloc[_idx_te].to_numpy(), y_te_w3.to_numpy()), \
    "index split diverged from the array split -- seeds out of sync"

_, lstm_scalers_w3 = prepare_lstm_sequences(df_w3.iloc[_idx_tr], W3)
X_seq_w3, _ = prepare_lstm_sequences(df_w3, W3, scalers=lstm_scalers_w3)
Xs_tmp, Xs_te_w3, ys_tmp, ys_te_w3 = train_test_split(
    X_seq_w3, y_w3, test_size=0.2, stratify=y_w3, random_state=42
)
Xs_tr_w3, Xs_cal_w3, ys_tr_w3, ys_cal_w3 = train_test_split(
    Xs_tmp, ys_tmp, test_size=0.25, stratify=ys_tmp, random_state=42
)

# Reproducible W3 LSTM weights across retrains (thesis numbers must be
# regenerable); the legacy LSTM above predates this and stays as-is.
import tensorflow as _tf
_tf.keras.utils.set_random_seed(42)

model_w3 = Sequential([
    Input(shape=(3, 3)),
    LSTM(32),
    Dropout(0.3),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid"),
])
model_w3.compile(optimizer="adam", loss="binary_crossentropy", metrics=["AUC"])

cw_w3 = compute_class_weight(class_weight="balanced", classes=np.array([0, 1]), y=ys_tr_w3.values)
model_w3.fit(
    Xs_tr_w3, ys_tr_w3,
    validation_split=0.2, epochs=60, batch_size=256,
    class_weight={0: cw_w3[0], 1: cw_w3[1]},
    callbacks=[
        EarlyStopping(monitor="val_auc", mode="max", patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=3, min_lr=1e-5),
    ],
    verbose=1,
)

lstm_uncal_proba = model_w3.predict(Xs_te_w3, verbose=0).ravel()
auc_lstm_uncal = roc_auc_score(ys_te_w3, lstm_uncal_proba)
brier_lstm_uncal = brier_score_loss(ys_te_w3, lstm_uncal_proba)

# Fit IsotonicRegression on raw LSTM probabilities from the calibration split.
lstm_calib_proba = model_w3.predict(Xs_cal_w3, verbose=0).ravel()
lstm_calibrator_w3 = IsotonicRegression(out_of_bounds="clip").fit(
    lstm_calib_proba, ys_cal_w3.to_numpy()
)
lstm_cal_proba = lstm_calibrator_w3.predict(lstm_uncal_proba)
auc_lstm_cal = roc_auc_score(ys_te_w3, lstm_cal_proba)
brier_lstm_cal = brier_score_loss(ys_te_w3, lstm_cal_proba)

print("\n===== WYNIKI W3 (3-mies., 60/20/20 split) =====")
print("Model         AUC uncal -> AUC cal     Brier uncal -> Brier cal")
print(f"RandomForest  {auc_rf_uncal:.4f}    -> {auc_rf_cal:.4f}     {brier_rf_uncal:.4f}      -> {brier_rf_cal:.4f}")
print(f"XGBoost       {auc_xgb_uncal:.4f}    -> {auc_xgb_cal:.4f}     {brier_xgb_uncal:.4f}      -> {brier_xgb_cal:.4f}")
print(f"LightGBM      {auc_lgbm_uncal:.4f}    -> {auc_lgbm_cal:.4f}     {brier_lgbm_uncal:.4f}      -> {brier_lgbm_cal:.4f}")
print(f"CatBoost      {auc_cat_uncal:.4f}    -> {auc_cat_cal:.4f}     {brier_cat_uncal:.4f}      -> {brier_cat_cal:.4f}")
print(f"LSTM          {auc_lstm_uncal:.4f}    -> {auc_lstm_cal:.4f}     {brier_lstm_uncal:.4f}      -> {brier_lstm_cal:.4f}")

# Save calibrated artifacts (overwrite per TASKS.md CREDIT-105 DoD).
joblib.dump(rf_w3,              "rf_model_w3.pkl")
joblib.dump(xgb_w3,             "xgb_model_w3.pkl")
joblib.dump(lgbm_w3,            "lightgbm_model_w3.pkl")  # CREDIT-109
joblib.dump(cat_w3,             "catboost_model_w3.pkl")   # CREDIT-109
joblib.dump(scaler_w3,          "scaler_w3.pkl")
joblib.dump(features_w3,        "features_w3.pkl")
model_w3.save("lstm_model_w3.keras")
joblib.dump(lstm_scalers_w3,    "../ml-service/lstm_scalers_w3.pkl")
joblib.dump(lstm_calibrator_w3, "../ml-service/lstm_calibrator_w3.pkl")

print(
    "\nW3 calibrated models saved: rf_model_w3.pkl, xgb_model_w3.pkl, "
    "lightgbm_model_w3.pkl, catboost_model_w3.pkl, lstm_model_w3.keras, "
    "scaler_w3.pkl, features_w3.pkl, lstm_scalers_w3.pkl, "
    "lstm_calibrator_w3.pkl"
)


# ========== COST-OPTIMIZED ALERT THRESHOLDS (CREDIT-106) ==========
# Replace the default 0.5 threshold with per-model values that minimize
# expected cost. Cost model: missing a default (FN) is 5x worse than
# a false alert (FP). Bounds (0.1, 0.9) per TASKS.md DoD.
import json as _json

_FN_COST_106, _FP_COST_106 = 5.0, 1.0
_THR_BOUNDS_106 = (0.1, 0.9)
_THR_RES_106 = 0.005


def _find_optimal_threshold(y_true, y_proba, fn_cost=_FN_COST_106, fp_cost=_FP_COST_106, bounds=_THR_BOUNDS_106):
    n = int((bounds[1] - bounds[0]) / _THR_RES_106) + 1
    candidates = np.linspace(bounds[0], bounds[1], n)
    best_thr, best_cost = float(bounds[0]), float("inf")
    for thr in candidates:
        pred = y_proba >= thr
        fn = int(((y_true == 1) & ~pred).sum())
        fp = int(((y_true == 0) & pred).sum())
        cost = fn_cost * fn + fp_cost * fp
        if cost < best_cost:
            best_thr, best_cost = float(thr), cost
    return best_thr, best_cost


# Leakage fix 2026-07-07: thresholds used to be optimized on the TEST split --
# the same data later used for evaluation, the fairness audit (CREDIT-112) and
# the static-vs-dynamic comparison (CREDIT-111). They are now optimized on the
# CALIBRATION split. Accepted compromise: the isotonic calibrators were fitted
# on this split too, so calibrated probabilities here are in-sample for the
# calibrator -- still strictly better than picking thresholds on the test set.
_y_cal_arr = y_cal_w3.to_numpy()
_ys_cal_arr = ys_cal_w3.to_numpy()

_rf_calsplit_proba = rf_w3.predict_proba(X_cal_w3)[:, 1]
_xgb_calsplit_proba = xgb_w3.predict_proba(X_cal_w3)[:, 1]
_lgbm_calsplit_proba = lgbm_w3.predict_proba(X_cal_w3)[:, 1]
_cat_calsplit_proba = cat_w3.predict_proba(X_cal_w3)[:, 1]
_lstm_calsplit_proba = lstm_calibrator_w3.predict(lstm_calib_proba)

_rf_thr_106, _rf_cost_106 = _find_optimal_threshold(_y_cal_arr, _rf_calsplit_proba)
_xgb_thr_106, _xgb_cost_106 = _find_optimal_threshold(_y_cal_arr, _xgb_calsplit_proba)
_lgbm_thr_106, _lgbm_cost_106 = _find_optimal_threshold(_y_cal_arr, _lgbm_calsplit_proba)
_cat_thr_106, _cat_cost_106 = _find_optimal_threshold(_y_cal_arr, _cat_calsplit_proba)
_lstm_thr_106, _lstm_cost_106 = _find_optimal_threshold(_ys_cal_arr, _lstm_calsplit_proba)

print(f"\n===== CREDIT-106 cost-optimized alert thresholds (FN={_FN_COST_106}x FP) =====")
print(f"  RandomForest  threshold={_rf_thr_106:.3f}   expected_cost={_rf_cost_106:.0f}")
print(f"  XGBoost       threshold={_xgb_thr_106:.3f}   expected_cost={_xgb_cost_106:.0f}")
print(f"  LightGBM      threshold={_lgbm_thr_106:.3f}   expected_cost={_lgbm_cost_106:.0f}")
print(f"  CatBoost      threshold={_cat_thr_106:.3f}   expected_cost={_cat_cost_106:.0f}")
print(f"  LSTM          threshold={_lstm_thr_106:.3f}   expected_cost={_lstm_cost_106:.0f}")

_thr_payload = {
    "_meta": {
        "fn_cost": _FN_COST_106,
        "fp_cost": _FP_COST_106,
        "fn_to_fp_ratio": _FN_COST_106 / _FP_COST_106,
        "bounds": list(_THR_BOUNDS_106),
        "resolution": _THR_RES_106,
        "source": "CREDIT-106 + CREDIT-109: optimized on the W3 CALIBRATION split (60/20/20, random_state=42); leakage fix 2026-07-07 -- previously optimized on the test split",
    },
    "randomForest": _rf_thr_106,
    "xgboost": _xgb_thr_106,
    "lightgbm": _lgbm_thr_106,
    "catboost": _cat_thr_106,
    "lstm": _lstm_thr_106,
}

with open("../ml-service/alert_thresholds.json", "w") as _f:
    _json.dump(_thr_payload, _f, indent=2)
print("Saved: ../ml-service/alert_thresholds.json")


# ========== CREDIT-108: HYPERPARAMETER TUNING ==========
# 5-fold CV + Optuna sweep for XGBoost and RandomForest lives in a separate
# standalone runner so `python main.py` stays a ~5-min production retrain.
# Tuning is academic exploration only (best params do NOT get promoted to the
# shipped W3 artifacts without redoing CREDIT-105 calibration + CREDIT-106
# thresholds + CREDIT-109 LightGBM/CatBoost).
#
# Run with:
#   python optuna_tuning.py
#
# Output:
#   reports/optuna_study.md     -- per-model CV-AUC mean +/- std (default vs tuned)
#                                  + test-AUC delta + best hyperparameters
#   reports/optuna_trials.csv   -- full n_trials x per-model sweep
