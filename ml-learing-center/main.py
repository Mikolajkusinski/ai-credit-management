import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

import tensorflow as tf
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.layers import GRU, Conv1D, GlobalMaxPooling1D, MultiHeadAttention, LayerNormalization, Flatten
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input
from xgboost import XGBClassifier

df = pd.read_csv("dataset/default_of_credit_card_clients.csv", header=1)
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

lr = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    solver="lbfgs"
)

lr.fit(X_train, y_train)
y_pred_lr = lr.predict_proba(X_test)[:, 1]

print("AUC Logistic:", roc_auc_score(y_test, y_pred_lr))

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

# NOWY MODEL: XGBoost
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

# MODEL DYNAMICZNY
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
for f in range(3):
    feat_data = X_seq[:, :, f].reshape(-1, 1)
    scaler_seq = StandardScaler()
    X_seq[:, :, f] = scaler_seq.fit_transform(feat_data).reshape(len(df), 6)

X_train_seq, X_test_seq, y_train_seq, y_test_seq = train_test_split(
    X_seq, y, test_size=0.3, stratify=y, random_state=42
)

model = Sequential([
    Input(shape=(6, 3)),
    LSTM(64, return_sequences=True),
    LSTM(32),
    Dropout(0.4),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["AUC"]
)

history = model.fit(
    X_train_seq,
    y_train_seq,
    validation_split=0.2,
    epochs=25,
    batch_size=256,
    verbose=1
)

y_pred_lstm = model.predict(X_test_seq).ravel()
print("AUC LSTM:", roc_auc_score(y_test_seq, y_pred_lstm))

# ========== MODEL GRU ==========
model_gru = Sequential([
    GRU(64, input_shape=(6, 3), return_sequences=True),
    GRU(32),
    Dropout(0.4),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model_gru.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["AUC"]
)

early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

model_gru.fit(
    X_train_seq, y_train_seq,
    validation_split=0.2,
    epochs=30,
    batch_size=256,
    callbacks=[early_stop],
    verbose=1
)

y_pred_gru = model_gru.predict(X_test_seq).ravel()
print("AUC GRU:", roc_auc_score(y_test_seq, y_pred_gru))

# ========== MODEL 1D CNN ==========
model_cnn = Sequential([
    Conv1D(64, kernel_size=2, activation='relu', input_shape=(6, 3)),
    Conv1D(32, kernel_size=2, activation='relu'),
    GlobalMaxPooling1D(),
    Dropout(0.4),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])

model_cnn.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["AUC"]
)

model_cnn.fit(
    X_train_seq, y_train_seq,
    validation_split=0.2,
    epochs=30,
    batch_size=256,
    callbacks=[early_stop],
    verbose=1
)

y_pred_cnn = model_cnn.predict(X_test_seq).ravel()
print("AUC 1D-CNN:", roc_auc_score(y_test_seq, y_pred_cnn))

# ========== MODEL TRANSFORMER (Simplified) ==========
inputs = tf.keras.Input(shape=(6, 3))

# Multi-Head Attention
attention_output = MultiHeadAttention(num_heads=2, key_dim=16)(inputs, inputs)
attention_output = LayerNormalization()(attention_output + inputs)

# Feed Forward
x = Dense(32, activation='relu')(attention_output)
x = Dropout(0.4)(x)
x = Flatten()(x)
x = Dense(16, activation='relu')(x)
outputs = Dense(1, activation='sigmoid')(x)

model_transformer = tf.keras.Model(inputs, outputs)

model_transformer.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["AUC"]
)

model_transformer.fit(
    X_train_seq, y_train_seq,
    validation_split=0.2,
    epochs=30,
    batch_size=256,
    callbacks=[early_stop],
    verbose=1
)

y_pred_transformer = model_transformer.predict(X_test_seq).ravel()
print("AUC Transformer:", roc_auc_score(y_test_seq, y_pred_transformer))

# ========== ULEPSZONY ENSEMBLE ==========
y_pred_ensemble = (
        0.25 * y_pred_rf +
        0.25 * y_pred_xgb +
        0.10 * y_pred_lstm +
        0.15 * y_pred_gru +
        0.10 * y_pred_cnn +
        0.10 * y_pred_transformer +
        0.05 * y_pred_lr
)

print("\n===== WYNIKI KOŃCOWE =====")
print(f"AUC Logistic:      {roc_auc_score(y_test, y_pred_lr):.4f}")
print(f"AUC Random Forest: {roc_auc_score(y_test, y_pred_rf):.4f}")
print(f"AUC XGBoost:       {roc_auc_score(y_test, y_pred_xgb):.4f}")
print(f"AUC LSTM:          {roc_auc_score(y_test_seq, y_pred_lstm):.4f}")
print(f"AUC GRU:           {roc_auc_score(y_test_seq, y_pred_gru):.4f}")
print(f"AUC 1D-CNN:        {roc_auc_score(y_test_seq, y_pred_cnn):.4f}")
print(f"AUC Transformer:   {roc_auc_score(y_test_seq, y_pred_transformer):.4f}")
print(f"AUC ENSEMBLE:      {roc_auc_score(y_test, y_pred_ensemble):.4f}")

# ========== SAVE MODELS ==========
import joblib


# Static models + scaler + features
joblib.dump(rf, "rf_model.pkl")
joblib.dump(xgb, "xgb_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(features, "features.pkl")

# LSTM (Keras model)
model.save("lstm_model.keras")

print("Models saved: rf_model.pkl, xgb_model.pkl, lstm_model.keras")