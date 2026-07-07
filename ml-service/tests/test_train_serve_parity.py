"""Train/serve parity tests (Fable5-zmiany.md O2).

Guards against the U1/U2 regression: pd.get_dummies(drop_first=True) on a
single-row frame used to yield ZERO dummy columns (the only observed category
is also the "first" one), silently zeroing all demographics at inference.
Fixed by casting to pd.Categorical with the full UCI domain
(features.UCI_CATEGORIES) before get_dummies.

These tests pin:
  1. feature-matrix parity: batch vs single-row (Flask-style) engineering,
  2. PD parity through the real W3 artifacts via the Flask test client,
  3. LSTM tensor axes (time oldest->newest, channels PAY/BILL/AMT),
  4. the SHAP positive-class contract,
  5. null-payload validation (400, not 500 / silent zero-imputation).
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest

SERVICE_ROOT = Path(__file__).resolve().parent.parent

ARTIFACTS = [
    "rf_model_w3.pkl", "xgb_model_w3.pkl",
    "lightgbm_model_w3.pkl", "catboost_model_w3.pkl",
    "scaler_w3.pkl", "features_w3.pkl",
    "lstm_model_w3.keras", "lstm_scalers_w3.pkl", "lstm_calibrator_w3.pkl",
    "alert_thresholds.json",
]


def _require_artifacts():
    missing = [a for a in ARTIFACTS if not (SERVICE_ROOT / a).exists()]
    if missing:
        pytest.skip(f"missing artifacts: {missing}")


@pytest.fixture(scope="module")
def client():
    _require_artifacts()
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _base_payload(**overrides):
    payload = {
        "LIMIT_BAL": 120000, "SEX": 1, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 35,
        "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
        "BILL_AMT1": 50000, "BILL_AMT2": 48000, "BILL_AMT3": 46000,
        "BILL_AMT4": 44000, "BILL_AMT5": 42000, "BILL_AMT6": 40000,
        "PAY_AMT1": 5000, "PAY_AMT2": 5000, "PAY_AMT3": 5000,
        "PAY_AMT4": 5000, "PAY_AMT5": 5000, "PAY_AMT6": 5000,
    }
    payload.update(overrides)
    return payload


# 20 synthetic clients spanning both sexes, EDUCATION 0-6 and MARRIAGE 0-3 --
# composition chosen so no batch-vs-single-row category asymmetry can hide.
DIVERSE_CLIENTS = [
    _base_payload(SEX=sex, EDUCATION=edu, MARRIAGE=mar,
                  PAY_0=pay, BILL_AMT1=40000 + 1000 * i, PAY_AMT1=1000 + 200 * i)
    for i, (sex, edu, mar, pay) in enumerate([
        (1, 0, 0, 0), (2, 0, 1, 1), (1, 1, 2, 0), (2, 1, 3, 2),
        (1, 2, 0, 0), (2, 2, 1, 0), (1, 3, 2, 1), (2, 3, 3, 0),
        (1, 4, 0, 2), (2, 4, 1, 0), (1, 5, 2, 0), (2, 5, 3, 3),
        (1, 6, 0, 0), (2, 6, 1, 0), (1, 2, 1, 0), (2, 3, 2, 1),
        (1, 4, 3, 0), (2, 5, 0, 0), (1, 6, 1, 2), (2, 1, 0, 0),
    ])
]


def test_single_row_dummies_match_batch():
    """Feature matrix from row-by-row engineering (Flask path) must be identical
    to batch engineering after selection to the saved feature list."""
    _require_artifacts()
    from features import engineer_features
    from sliding_window import WINDOW_DEFS

    feats = joblib.load(SERVICE_ROOT / "features_w3.pkl")
    W3 = WINDOW_DEFS[3]

    batch_df = pd.DataFrame(DIVERSE_CLIENTS)
    X_batch, _ = engineer_features(batch_df, W3)
    for col in feats:
        if col not in X_batch.columns:
            X_batch[col] = 0
    X_batch = X_batch[feats].to_numpy(dtype=float)

    single_rows = []
    for payload in DIVERSE_CLIENTS:
        Xi, _ = engineer_features(pd.DataFrame([payload]), W3)
        for col in feats:
            if col not in Xi.columns:
                Xi[col] = 0
        single_rows.append(Xi[feats].to_numpy(dtype=float)[0])
    X_single = np.array(single_rows)

    np.testing.assert_allclose(X_single, X_batch, atol=0, rtol=0)


def test_female_client_gets_sex_dummy():
    """Regression pin for U1: a SEX=2 client engineered from a 1-row frame MUST
    have SEX_2 == 1 (pre-fix it was silently 0 for everyone)."""
    _require_artifacts()
    from features import engineer_features
    from sliding_window import WINDOW_DEFS

    Xi, _ = engineer_features(
        pd.DataFrame([_base_payload(SEX=2, EDUCATION=3, MARRIAGE=2)]),
        WINDOW_DEFS[3],
    )
    assert int(Xi["SEX_2"].iloc[0]) == 1
    assert int(Xi["EDUCATION_3"].iloc[0]) == 1
    assert int(Xi["MARRIAGE_2"].iloc[0]) == 1
    assert int(Xi["EDUCATION_1"].iloc[0]) == 0


def test_predict_parity_static(client):
    """PD returned by /predict/timeseries for W3 must equal the direct
    batch-path computation on the same artifacts."""
    from features import engineer_features
    from sliding_window import WINDOW_DEFS

    payload = _base_payload(SEX=2, EDUCATION=3, MARRIAGE=2)
    resp = client.post("/predict/timeseries", json=payload)
    assert resp.status_code == 200
    served = resp.get_json()["trajectory"][3]["predictions"]["randomForest"]

    feats = joblib.load(SERVICE_ROOT / "features_w3.pkl")
    scaler = joblib.load(SERVICE_ROOT / "scaler_w3.pkl")
    rf = joblib.load(SERVICE_ROOT / "rf_model_w3.pkl")
    X, _ = engineer_features(pd.DataFrame([payload]), WINDOW_DEFS[3])
    for col in feats:
        if col not in X.columns:
            X[col] = 0
    expected = float(rf.predict_proba(scaler.transform(X[feats]))[0, 1])

    assert abs(served - expected) < 1e-9


def test_demographics_reach_the_model_input():
    """Pre-fix, SEX/EDUCATION/MARRIAGE were zeroed for every request, so any
    two clients differing only in demographics produced an IDENTICAL scaled
    feature vector. Assert the serving layer passes demographics through to
    the model input. (Deliberately NOT asserting on PD differences: trees may
    legitimately not split on demographics along a given path, which made a
    model-level canary flaky across retrains.)"""
    _require_artifacts()
    import app as service

    feats = joblib.load(SERVICE_ROOT / "features_w3.pkl")
    dummy_idx = [i for i, f in enumerate(feats)
                 if f.startswith(("SEX_", "EDUCATION_", "MARRIAGE_"))]

    Xa = service.engineer_features_w3(_base_payload(SEX=1, EDUCATION=1, MARRIAGE=1), service.W3)
    Xb = service.engineer_features_w3(_base_payload(SEX=2, EDUCATION=6, MARRIAGE=3), service.W3)

    non_dummy = [i for i in range(len(feats)) if i not in dummy_idx]
    np.testing.assert_allclose(Xa[0, non_dummy], Xb[0, non_dummy], atol=1e-12)
    assert np.abs(Xa[0, dummy_idx] - Xb[0, dummy_idx]).max() > 0, (
        "demographic dummies identical for different SEX/EDUCATION/MARRIAGE "
        "-- U1 regression?"
    )


def test_lstm_axes():
    """Time axis oldest->newest, channels 0=PAY 1=BILL 2=AMT, shape (1, 3, 3)."""
    _require_artifacts()
    import app as service

    payload = _base_payload(PAY_3=1, PAY_2=2, PAY_0=3,
                            BILL_AMT3=10000, BILL_AMT2=20000, BILL_AMT1=30000,
                            PAY_AMT3=100, PAY_AMT2=200, PAY_AMT1=300)
    tensor = service.prepare_lstm_input_w3(payload, service.W3)
    assert tensor.shape == (1, 3, 3)

    scalers = joblib.load(SERVICE_ROOT / "lstm_scalers_w3.pkl")
    # channel 0 = PAY: t=0 must be scaled PAY_3 (oldest), t=2 scaled PAY_0 (newest)
    assert tensor[0, 0, 0] == pytest.approx(scalers[0].transform([[1]])[0][0])
    assert tensor[0, 2, 0] == pytest.approx(scalers[0].transform([[3]])[0][0])
    # channel 1 = BILL, channel 2 = AMT at the newest step
    assert tensor[0, 2, 1] == pytest.approx(scalers[1].transform([[30000]])[0][0])
    assert tensor[0, 2, 2] == pytest.approx(scalers[2].transform([[300]])[0][0])


def test_shap_positive_class_contract():
    """SHAP vector length == len(features_w3); for a client with a terrible
    recent payment history, PAY_max must push PD UP (positive value) -- pins
    the positive-class selection across shap versions."""
    _require_artifacts()
    import app as service

    payload = _base_payload(PAY_0=8, PAY_2=7, PAY_3=6, PAY_AMT1=0, PAY_AMT2=0, PAY_AMT3=0)
    feats = joblib.load(SERVICE_ROOT / "features_w3.pkl")
    out = service.compute_shap_top_features(payload)

    assert set(out.keys()) == {"randomForest", "xgboost", "lightgbm", "catboost"}
    X = service.engineer_features_w3(payload, service.W3)
    for model_key, explainer in service.SHAP_EXPLAINERS.items():
        sv = service._shap_values_positive_class(explainer, X)
        assert sv.shape == (len(feats),)
        pay_max_val = sv[feats.index("PAY_max")]
        assert pay_max_val > 0, (
            f"{model_key}: SHAP(PAY_max)={pay_max_val} for a max-delinquency "
            "client -- wrong class selected?"
        )


def test_null_payload_returns_400(client):
    """A present-but-null field must be rejected with 400 VALIDATION_FAILED,
    not 500 (LSTM path) or silent zero-imputation (static path)."""
    payload = _base_payload()
    payload["PAY_6"] = None
    resp = client.post("/predict/timeseries", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"]["code"] == "VALIDATION_FAILED"
