import json
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import shap
from tensorflow import keras
import logging

from sliding_window import WINDOW_DEFS
from features import UCI_CATEGORIES, engineer_features as engineer_features_w3_df
from monitoring import SLOPE_THRESHOLD, WINDOW_NAMES, compute_alert, compute_trends

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent

# Load legacy 6-month models (used by /predict) at startup
logger.info("Loading legacy 6-month models...")
rf_model = joblib.load(ROOT / "rf_model.pkl")
xgb_model = joblib.load(ROOT / "xgb_model.pkl")
scaler = joblib.load(ROOT / "scaler.pkl")
feature_names = joblib.load(ROOT / "features.pkl")
lstm_model = keras.models.load_model(ROOT / "lstm_model.keras")
lstm_scalers = joblib.load(ROOT / "lstm_scalers.pkl")

# Load W3 3-month models (used by /predict/timeseries) at startup.
# RF/XGB are CalibratedClassifierCV wrappers (CREDIT-105); .predict_proba is
# isotonic-calibrated. LSTM has an external IsotonicRegression in
# lstm_calibrator_w3.pkl that must be applied to the raw Keras outputs.
logger.info("Loading W3 3-month models...")
rf_w3 = joblib.load(ROOT / "rf_model_w3.pkl")
xgb_w3 = joblib.load(ROOT / "xgb_model_w3.pkl")
lgbm_w3 = joblib.load(ROOT / "lightgbm_model_w3.pkl")   # CREDIT-109
cat_w3 = joblib.load(ROOT / "catboost_model_w3.pkl")    # CREDIT-109
scaler_w3 = joblib.load(ROOT / "scaler_w3.pkl")
features_w3 = joblib.load(ROOT / "features_w3.pkl")
lstm_w3 = keras.models.load_model(ROOT / "lstm_model_w3.keras")
lstm_scalers_w3 = joblib.load(ROOT / "lstm_scalers_w3.pkl")
lstm_calibrator_w3 = joblib.load(ROOT / "lstm_calibrator_w3.pkl")


def _unwrap_calibrated(calibrated_model):
    """Unwrap CalibratedClassifierCV(FrozenEstimator(base)) -> base tree estimator.

    SHAP's TreeExplainer needs the underlying tree model; isotonic calibration
    on top is monotonic so it doesn't change which features matter -- it only
    rescales the score axis.
    """
    cc = calibrated_model.calibrated_classifiers_[0]
    return getattr(cc.estimator, "estimator", cc.estimator)


# Pre-build SHAP explainers once at startup (CREDIT-107). Tree-based only --
# LSTM is skipped because KernelExplainer with adequate background samples
# would blow the < 2s budget; tree models cover RF / XGB / LightGBM / CatBoost.
logger.info("Building SHAP explainers for W3 tree models...")
SHAP_EXPLAINERS = {
    "randomForest": shap.TreeExplainer(_unwrap_calibrated(rf_w3)),
    "xgboost":      shap.TreeExplainer(_unwrap_calibrated(xgb_w3)),
    "lightgbm":     shap.TreeExplainer(_unwrap_calibrated(lgbm_w3)),
    "catboost":     shap.TreeExplainer(_unwrap_calibrated(cat_w3)),
}


# Cost-optimized alert thresholds (CREDIT-106). Per-model PD threshold derived
# under an FN-heavy cost model; used in /predict/timeseries response so frontend
# can flag windows above the per-model threshold.
with (ROOT / "alert_thresholds.json").open() as _f:
    ALERT_THRESHOLDS = json.load(_f)
logger.info(
    "Cost-optimized alert thresholds: RF=%.3f XGB=%.3f LSTM=%.3f (FN cost = %sx FP cost)",
    ALERT_THRESHOLDS["randomForest"],
    ALERT_THRESHOLDS["xgboost"],
    ALERT_THRESHOLDS["lstm"],
    ALERT_THRESHOLDS["_meta"]["fn_to_fp_ratio"],
)
logger.info("All models loaded successfully")


REQUIRED_FIELDS = [
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    "PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6",
    "BILL_AMT1", "BILL_AMT2", "BILL_AMT3", "BILL_AMT4", "BILL_AMT5", "BILL_AMT6",
    "PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6",
]


def _validate_payload(data):
    """Return (field, reason) for the first invalid field, or (None, None).

    Presence alone is not enough: a present-but-null (or non-numeric) value
    would either crash the LSTM tensor build (500 instead of 400) or be
    silently imputed as 0 by fillna in the static path -- and 0 is a real
    PAY status ("paid on time"), so silent imputation lies about the client.
    """
    if not isinstance(data, dict):
        return "<body>", "request body must be a JSON object"
    for field in REQUIRED_FIELDS:
        if field not in data:
            return field, f"Missing required field: {field}"
        value = data[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return field, f"Field {field} must be a number, got: {value!r}"
    return None, None


# ===== Legacy 6-month feature engineering (used by /predict) =====

def engineer_features(data):
    """Engineer features for RF and XGBoost models (legacy 6-month window)."""
    df = pd.DataFrame([data])

    pay_cols = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
    bill_cols = [f"BILL_AMT{i}" for i in range(1, 7)]
    amt_cols = [f"PAY_AMT{i}" for i in range(1, 7)]

    df["PAY_mean"] = df[pay_cols].mean(axis=1)
    df["PAY_max"] = df[pay_cols].max(axis=1)
    df["BILL_mean"] = df[bill_cols].mean(axis=1)
    df["PAY_AMT_mean"] = df[amt_cols].mean(axis=1)
    df["utilization_rate"] = df["BILL_mean"] / df["LIMIT_BAL"]
    df["BILL_std"] = df[bill_cols].std(axis=1)
    df["BILL_trend"] = df["BILL_AMT1"] - df["BILL_AMT6"]
    df["payment_ratio"] = df["PAY_AMT_mean"] / (df["BILL_mean"] + 1)
    df["late_count"] = (df[pay_cols] > 0).sum(axis=1)
    df["severe_late"] = (df[pay_cols] >= 2).any(axis=1).astype(int)
    df["recent_pay_status"] = df["PAY_0"]

    # Fixed category domains -- without this a 1-row frame yields zero dummy
    # columns after drop_first (all demographics silently zeroed; see
    # features.UCI_CATEGORIES and Fable5-zmiany.md U1).
    for col, cats in UCI_CATEGORIES.items():
        df[col] = pd.Categorical(df[col].astype(int), categories=cats)
    df = pd.get_dummies(df, columns=["SEX", "EDUCATION", "MARRIAGE"], drop_first=True)

    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_names]

    # Parity with training cleanup (main.py legacy section): LIMIT_BAL=0 makes
    # utilization_rate inf, BILL_mean=-1 makes payment_ratio inf -- training
    # replaced those with 0, so inference must too (else sklearn raises -> 500).
    df = df.fillna(0).replace([np.inf, -np.inf], 0)

    return scaler.transform(df)


def prepare_lstm_input(data):
    """Prepare input for legacy LSTM model (1, 6, 3) tensor."""
    sequence = np.array([
        [data["PAY_6"], data["BILL_AMT6"], data["PAY_AMT6"]],
        [data["PAY_5"], data["BILL_AMT5"], data["PAY_AMT5"]],
        [data["PAY_4"], data["BILL_AMT4"], data["PAY_AMT4"]],
        [data["PAY_3"], data["BILL_AMT3"], data["PAY_AMT3"]],
        [data["PAY_2"], data["BILL_AMT2"], data["PAY_AMT2"]],
        [data["PAY_0"], data["BILL_AMT1"], data["PAY_AMT1"]],
    ], dtype=np.float32)

    sequence_scaled = sequence.copy()
    for f in range(3):
        feat_data = sequence[:, f].reshape(-1, 1)
        sequence_scaled[:, f] = lstm_scalers[f].transform(feat_data).ravel()

    return sequence_scaled.reshape(1, 6, 3)


# ===== W3 3-month inference (used by /predict/timeseries) =====

W3 = WINDOW_DEFS[3]


def map_to_w3_columns(data, window):
    """Remap a row so that the W3 column slots (PAY_3/PAY_2/PAY_0, BILL_AMT3/2/1,
    PAY_AMT3/2/1) hold values from the given window's columns. Lets us reuse
    the W3-trained model on every sliding window."""
    mapped = dict(data)
    for i in range(3):
        mapped[W3["pay"][i]] = data[window["pay"][i]]
        mapped[W3["bill"][i]] = data[window["bill"][i]]
        mapped[W3["amt"][i]] = data[window["amt"][i]]
    return mapped


def engineer_features_w3(data, window):
    """Build the static feature matrix for one window, scaled with scaler_w3."""
    mapped = map_to_w3_columns(data, window)
    df = pd.DataFrame([mapped])
    X, _ = engineer_features_w3_df(df, W3)
    for col in features_w3:
        if col not in X.columns:
            X[col] = 0
    X = X[features_w3]
    return scaler_w3.transform(X)


def prepare_lstm_input_w3(data, window):
    """Build LSTM tensor (1, 3, 3) for a window using saved W3 scalers (transform, not refit)."""
    sequence = np.array([
        [data[window["pay"][t]], data[window["bill"][t]], data[window["amt"][t]]]
        for t in range(3)
    ], dtype=np.float32)

    sequence_scaled = sequence.copy()
    for f in range(3):
        feat_data = sequence[:, f].reshape(-1, 1)
        sequence_scaled[:, f] = lstm_scalers_w3[f].transform(feat_data).ravel()

    return sequence_scaled.reshape(1, 3, 3)


SHAP_TOP_N = 5


def _shap_values_positive_class(explainer, X):
    """Return SHAP values for the positive class as a 1D numpy array (one row).

    Different sklearn / SHAP versions return different shapes:
    - list of two arrays (one per class) -> take index 1
    - 3D array (samples, features, classes) -> take last axis
    - 2D array (samples, features) -> already positive-class
    """
    raw = explainer.shap_values(X)
    if isinstance(raw, list):
        arr = raw[1] if len(raw) == 2 else raw[0]
    else:
        arr = np.asarray(raw)
        if arr.ndim == 3:
            arr = arr[..., -1]
    return np.asarray(arr).reshape(-1)


def compute_shap_top_features(data, n_top=SHAP_TOP_N):
    """For each tree-based W3 model, return top-N features by absolute SHAP value
    on the W3 window for the given client data (CREDIT-107).

    Returns dict keyed by model name (camelCase). Each value is:
      { "topFeatures": [ { "feature": "<name>", "value": <float> }, ... ] }

    LSTM is intentionally skipped -- SHAP for sequence Keras model would need
    KernelExplainer with background samples (slow) and the < 2s DoD would not
    hold.
    """
    X_static = engineer_features_w3(data, W3)
    out = {}
    for model_key, explainer in SHAP_EXPLAINERS.items():
        sv = _shap_values_positive_class(explainer, X_static)
        order = np.argsort(np.abs(sv))[::-1][:n_top]
        top = [
            {"feature": str(features_w3[i]), "value": float(sv[i])}
            for i in order
        ]
        out[model_key] = {"topFeatures": top}
    return out


def predict_single_window(data, window):
    """Score one window with RF/XGBoost/LightGBM/CatBoost/LSTM (CREDIT-109).
    Returns dict of calibrated probabilities keyed by model name."""
    X_static = engineer_features_w3(data, window)
    rf_prob = float(rf_w3.predict_proba(X_static)[0][1])
    xgb_prob = float(xgb_w3.predict_proba(X_static)[0][1])
    lgbm_prob = float(lgbm_w3.predict_proba(X_static)[0][1])
    cat_prob = float(cat_w3.predict_proba(X_static)[0][1])

    X_seq = prepare_lstm_input_w3(data, window)
    lstm_raw = float(lstm_w3.predict(X_seq, verbose=0)[0][0])
    lstm_prob = float(lstm_calibrator_w3.predict([lstm_raw])[0])

    return {
        "randomForest": rf_prob,
        "xgboost": xgb_prob,
        "lightgbm": lgbm_prob,
        "catboost": cat_prob,
        "lstm": lstm_prob,
    }


# ===== Routes =====

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Legacy 6-month single-window scoring."""
    try:
        data = request.json
        logger.info(f"Received prediction request: {data}")

        bad_field, reason = _validate_payload(data)
        if bad_field is not None:
            return jsonify({"error": reason}), 400

        rf_features = engineer_features(data)
        rf_proba = rf_model.predict_proba(rf_features)[0][1]
        xgb_proba = xgb_model.predict_proba(rf_features)[0][1]
        lstm_input = prepare_lstm_input(data)
        lstm_proba = float(lstm_model.predict(lstm_input, verbose=0)[0][0])

        response = {
            "randomForest": {
                "defaultProbability": float(rf_proba),
                "prediction": "DEFAULT" if rf_proba >= 0.5 else "NO DEFAULT",
            },
            "xgboost": {
                "defaultProbability": float(xgb_proba),
                "prediction": "DEFAULT" if xgb_proba >= 0.5 else "NO DEFAULT",
            },
            "lstm": {
                "defaultProbability": float(lstm_proba),
                "prediction": "DEFAULT" if lstm_proba >= 0.5 else "NO DEFAULT",
            },
        }
        logger.info(f"Prediction response: {response}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/predict/timeseries", methods=["POST"])
def predict_timeseries():
    """Sliding-window trajectory scoring (CREDIT-104).

    Input: 22 features (Snapshot22Features in SCREAMING_SNAKE_CASE, parity with /predict).
    Output: trajectory of 4 points (W0..W3) per model + per-model trends (slope + alert).
    See docs/api-contracts/monitoring.md section 4.1 for the contract.
    """
    try:
        data = request.json
        logger.info(f"Received timeseries request: {data}")

        bad_field, reason = _validate_payload(data)
        if bad_field is not None:
            return jsonify({
                "error": {
                    "code": "VALIDATION_FAILED",
                    "message": reason,
                    "details": {"field": bad_field},
                }
            }), 400

        trajectory = [
            {
                "window": WINDOW_NAMES[i],
                "label": None,  # backend (.NET) computes label from snapshotDate
                "predictions": predict_single_window(data, window),
            }
            for i, window in enumerate(WINDOW_DEFS)
        ]

        trends = compute_trends(trajectory)

        # Cost-optimized per-window per-model alerts (CREDIT-106 / CREDIT-109).
        # True = PD at this window crosses the model-specific cost-optimized threshold.
        cost_thresholds = {
            model_key: ALERT_THRESHOLDS[model_key]
            for model_key in trajectory[0]["predictions"].keys()
        }
        window_alerts = {
            model_key: [
                point["predictions"][model_key] >= cost_thresholds[model_key]
                for point in trajectory
            ]
            for model_key in cost_thresholds
        }

        # SHAP top-5 features per tree-based model on the W3 window (CREDIT-107).
        shap_payload = compute_shap_top_features(data)

        response = {
            "snapshotDate": None,  # Flask is stateless; backend fills this
            "trajectory": trajectory,
            "trends": trends,
            "costThresholds": cost_thresholds,
            "windowAlerts": window_alerts,
            "shap": {
                "window": "W3",
                **shap_payload,
            },
        }
        logger.info(f"Timeseries trends: {trends} | windowAlerts: {window_alerts}")
        return jsonify(response), 200

    except Exception as e:
        logger.exception("Error during timeseries prediction")
        return jsonify({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e),
            }
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
