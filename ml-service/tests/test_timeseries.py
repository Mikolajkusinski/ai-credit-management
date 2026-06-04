"""
CREDIT-104: tests for /predict/timeseries.

Pure-function tests (compute_alert, compute_trends) always run. Endpoint
tests skip when model artifacts aren't available (e.g., in CI).
"""
from pathlib import Path

import pytest


# Pure-function tests -- no model artifacts required (import from monitoring.py
# rather than app.py to avoid triggering joblib.load at module init)

def test_compute_alert_thresholds():
    from monitoring import SLOPE_THRESHOLD, compute_alert

    assert compute_alert(SLOPE_THRESHOLD + 0.01) == "INCREASING_RISK"
    assert compute_alert(-SLOPE_THRESHOLD - 0.01) == "DECREASING_RISK"
    assert compute_alert(0.0) == "STABLE"
    assert compute_alert(SLOPE_THRESHOLD) == "STABLE"      # boundary: not strictly greater
    assert compute_alert(-SLOPE_THRESHOLD) == "STABLE"     # boundary: not strictly less


def test_compute_trends_per_model():
    from monitoring import compute_trends

    trajectory = [
        {"predictions": {"randomForest": 0.10, "xgboost": 0.10, "lstm": 0.10}},  # W0
        {"predictions": {"randomForest": 0.20, "xgboost": 0.20, "lstm": 0.20}},  # W1
        {"predictions": {"randomForest": 0.40, "xgboost": 0.40, "lstm": 0.40}},  # W2
        {"predictions": {"randomForest": 0.55, "xgboost": 0.25, "lstm": 0.05}},  # W3
    ]
    trends = compute_trends(trajectory)
    # RF: 0.55 - 0.10 = +0.45 -> INCREASING_RISK
    assert trends["randomForest"] == {"slope": 0.45, "alert": "INCREASING_RISK"}
    # XGB: 0.25 - 0.10 = +0.15 -> INCREASING_RISK (above 0.10 threshold)
    assert trends["xgboost"] == {"slope": 0.15, "alert": "INCREASING_RISK"}
    # LSTM: 0.05 - 0.10 = -0.05 -> STABLE (within +/- threshold)
    assert trends["lstm"] == {"slope": -0.05, "alert": "STABLE"}


def test_compute_trends_decreasing():
    from monitoring import compute_trends

    trajectory = [
        {"predictions": {"randomForest": 0.60, "xgboost": 0.60, "lstm": 0.60}},  # W0
        {"predictions": {"randomForest": 0.50, "xgboost": 0.50, "lstm": 0.50}},  # W1
        {"predictions": {"randomForest": 0.40, "xgboost": 0.40, "lstm": 0.40}},  # W2
        {"predictions": {"randomForest": 0.20, "xgboost": 0.20, "lstm": 0.20}},  # W3
    ]
    trends = compute_trends(trajectory)
    for model in ("randomForest", "xgboost", "lstm"):
        assert trends[model]["alert"] == "DECREASING_RISK"
        assert trends[model]["slope"] == -0.40


# Endpoint tests -- require model artifacts; skip in CI

ARTIFACTS = [
    "rf_model.pkl", "xgb_model.pkl", "scaler.pkl", "features.pkl",
    "lstm_model.keras", "lstm_scalers.pkl",
    "rf_model_w3.pkl", "xgb_model_w3.pkl", "scaler_w3.pkl", "features_w3.pkl",
    "lstm_model_w3.keras", "lstm_scalers_w3.pkl",
    "lstm_calibrator_w3.pkl",
    "alert_thresholds.json",
]
SERVICE_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def client():
    missing = [a for a in ARTIFACTS if not (SERVICE_ROOT / a).exists()]
    if missing:
        pytest.skip(f"Skipping endpoint tests; missing artifacts: {missing}")
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


SAMPLE_HEALTHY = {
    "LIMIT_BAL": 100000, "SEX": 1, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 35,
    "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
    "BILL_AMT1": 50000, "BILL_AMT2": 48000, "BILL_AMT3": 46000,
    "BILL_AMT4": 44000, "BILL_AMT5": 42000, "BILL_AMT6": 40000,
    "PAY_AMT1": 5000, "PAY_AMT2": 5000, "PAY_AMT3": 5000,
    "PAY_AMT4": 5000, "PAY_AMT5": 5000, "PAY_AMT6": 5000,
}

# A client who started paying on time but recently fell into delay --
# this should produce an increasing PD trajectory, hence INCREASING_RISK.
SAMPLE_DETERIORATING = {
    "LIMIT_BAL": 50000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 30,
    # Oldest months: paid on time. Newest months: increasing delay.
    "PAY_0": 3, "PAY_2": 2, "PAY_3": 1, "PAY_4": 0, "PAY_5": -1, "PAY_6": -1,
    "BILL_AMT1": 48000, "BILL_AMT2": 45000, "BILL_AMT3": 30000,
    "BILL_AMT4": 20000, "BILL_AMT5": 10000, "BILL_AMT6": 5000,
    "PAY_AMT1": 500, "PAY_AMT2": 1000, "PAY_AMT3": 2000,
    "PAY_AMT4": 3000, "PAY_AMT5": 5000, "PAY_AMT6": 5000,
}


def test_predict_timeseries_returns_four_trajectory_points(client):
    resp = client.post("/predict/timeseries", json=SAMPLE_HEALTHY)
    assert resp.status_code == 200
    body = resp.get_json()

    assert "trajectory" in body
    assert len(body["trajectory"]) == 4
    assert [p["window"] for p in body["trajectory"]] == ["W0", "W1", "W2", "W3"]

    for point in body["trajectory"]:
        preds = point["predictions"]
        assert set(preds.keys()) == {"randomForest", "xgboost", "lstm"}
        for prob in preds.values():
            assert 0.0 <= prob <= 1.0


def test_predict_timeseries_returns_per_model_trends(client):
    resp = client.post("/predict/timeseries", json=SAMPLE_HEALTHY)
    body = resp.get_json()

    assert "trends" in body
    assert set(body["trends"].keys()) == {"randomForest", "xgboost", "lstm"}
    for trend in body["trends"].values():
        assert "slope" in trend
        assert "alert" in trend
        assert trend["alert"] in {"INCREASING_RISK", "DECREASING_RISK", "STABLE"}


def test_predict_timeseries_deteriorating_client_flags_increasing_risk(client):
    resp = client.post("/predict/timeseries", json=SAMPLE_DETERIORATING)
    assert resp.status_code == 200
    body = resp.get_json()

    # At least one of the three models must flag INCREASING_RISK on a clearly
    # deteriorating trajectory (rising bills + delays in recent months).
    alerts = {m: body["trends"][m]["alert"] for m in ("randomForest", "xgboost", "lstm")}
    assert "INCREASING_RISK" in alerts.values(), \
        f"Expected at least one INCREASING_RISK on deteriorating sample; got {alerts}"


def test_predict_timeseries_returns_cost_thresholds_and_window_alerts(client):
    """CREDIT-106: response must include costThresholds (echo of per-model thresholds
    from alert_thresholds.json) and windowAlerts (boolean per window per model)."""
    resp = client.post("/predict/timeseries", json=SAMPLE_HEALTHY)
    body = resp.get_json()

    assert "costThresholds" in body
    assert set(body["costThresholds"].keys()) == {"randomForest", "xgboost", "lstm"}
    for model_key, threshold in body["costThresholds"].items():
        assert 0.1 <= threshold <= 0.9, f"{model_key} threshold {threshold} outside DoD bounds (0.1, 0.9)"

    assert "windowAlerts" in body
    assert set(body["windowAlerts"].keys()) == {"randomForest", "xgboost", "lstm"}
    for model_key, alerts in body["windowAlerts"].items():
        assert len(alerts) == 4
        assert all(isinstance(a, bool) for a in alerts)
        # Cross-check: alerts must match (predictions >= threshold) for the same model
        threshold = body["costThresholds"][model_key]
        expected = [
            point["predictions"][model_key] >= threshold
            for point in body["trajectory"]
        ]
        assert alerts == expected


def test_predict_timeseries_missing_field_returns_400(client):
    incomplete = dict(SAMPLE_HEALTHY)
    del incomplete["PAY_0"]
    resp = client.post("/predict/timeseries", json=incomplete)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "VALIDATION_FAILED"
    assert "PAY_0" in body["error"]["message"]
