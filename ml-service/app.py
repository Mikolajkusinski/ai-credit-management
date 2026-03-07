from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
from tensorflow import keras
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models at startup
logger.info("Loading models...")
rf_model = joblib.load('rf_model.pkl')
xgb_model = joblib.load('xgb_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('features.pkl')
lstm_model = keras.models.load_model('lstm_model.keras')
logger.info("All models loaded successfully")


def engineer_features(data):
    """Engineer features for RF and XGBoost models"""
    df = pd.DataFrame([data])

    # Derived features
    df['PAY_mean'] = df[['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']].mean(axis=1)
    df['PAY_max'] = df[['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']].max(axis=1)
    df['BILL_mean'] = df[['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']].mean(axis=1)
    df['PAY_AMT_mean'] = df[['PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']].mean(axis=1)
    df['utilization_rate'] = df['BILL_AMT1'] / df['LIMIT_BAL']
    df['BILL_std'] = df[['BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6']].std(axis=1)
    df['BILL_trend'] = df['BILL_AMT1'] - df['BILL_AMT6']
    df['payment_ratio'] = df['PAY_AMT_mean'] / (df['BILL_mean'] + 1)
    df['late_count'] = (df[['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']] > 0).sum(axis=1)
    df['severe_late'] = (df[['PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6']] >= 2).sum(axis=1)
    df['recent_pay_status'] = df['PAY_0']

    # One-hot encoding for categorical features
    df = pd.get_dummies(df, columns=['SEX', 'EDUCATION', 'MARRIAGE'], drop_first=True)

    # Align with saved feature names
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_names]

    # Scale features
    scaled_features = scaler.transform(df)

    return scaled_features


def prepare_lstm_input(data):
    """Prepare input for LSTM model (1, 6, 3) tensor"""
    # Build sequences: [PAY, BILL_AMT, PAY_AMT] for 6 months (oldest to newest)
    # Order: April (PAY_6, BILL_AMT6, PAY_AMT6) -> September (PAY_0, BILL_AMT1, PAY_AMT1)
    sequence = np.array([
        [data['PAY_6'], data['BILL_AMT6'], data['PAY_AMT6']],
        [data['PAY_5'], data['BILL_AMT5'], data['PAY_AMT5']],
        [data['PAY_4'], data['BILL_AMT4'], data['PAY_AMT4']],
        [data['PAY_3'], data['BILL_AMT3'], data['PAY_AMT3']],
        [data['PAY_2'], data['BILL_AMT2'], data['PAY_AMT2']],
        [data['PAY_0'], data['BILL_AMT1'], data['PAY_AMT1']]
    ], dtype=np.float32)

    # Normalize each feature column independently using standardization
    # PAY values typically range from -2 to 9
    # BILL_AMT and PAY_AMT are monetary values
    sequence_scaled = sequence.copy()

    # Scale PAY column (column 0): standardize
    pay_mean = np.mean(sequence[:, 0])
    pay_std = np.std(sequence[:, 0]) + 1e-8
    sequence_scaled[:, 0] = (sequence[:, 0] - pay_mean) / pay_std

    # Scale BILL_AMT column (column 1): standardize
    bill_mean = np.mean(sequence[:, 1])
    bill_std = np.std(sequence[:, 1]) + 1e-8
    sequence_scaled[:, 1] = (sequence[:, 1] - bill_mean) / bill_std

    # Scale PAY_AMT column (column 2): standardize
    pay_amt_mean = np.mean(sequence[:, 2])
    pay_amt_std = np.std(sequence[:, 2]) + 1e-8
    sequence_scaled[:, 2] = (sequence[:, 2] - pay_amt_mean) / pay_amt_std

    # Reshape to (1, 6, 3)
    return sequence_scaled.reshape(1, 6, 3)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        logger.info(f"Received prediction request: {data}")

        # Validate required fields
        required_fields = [
            'LIMIT_BAL', 'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
            'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
            'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3', 'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
            'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Random Forest prediction
        rf_features = engineer_features(data)
        rf_proba = rf_model.predict_proba(rf_features)[0][1]
        rf_prediction = "DEFAULT" if rf_proba >= 0.5 else "NO DEFAULT"

        # XGBoost prediction
        xgb_features = engineer_features(data)
        xgb_proba = xgb_model.predict_proba(xgb_features)[0][1]
        xgb_prediction = "DEFAULT" if xgb_proba >= 0.5 else "NO DEFAULT"

        # LSTM prediction
        lstm_input = prepare_lstm_input(data)
        lstm_proba = float(lstm_model.predict(lstm_input, verbose=0)[0][0])
        lstm_prediction = "DEFAULT" if lstm_proba >= 0.5 else "NO DEFAULT"

        response = {
            "randomForest": {
                "defaultProbability": float(rf_proba),
                "prediction": rf_prediction
            },
            "xgboost": {
                "defaultProbability": float(xgb_proba),
                "prediction": xgb_prediction
            },
            "lstm": {
                "defaultProbability": float(lstm_proba),
                "prediction": lstm_prediction
            }
        }

        logger.info(f"Prediction response: {response}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
