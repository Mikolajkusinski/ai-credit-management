"""
CREDIT-101: pytest tests for sliding_window.extract_windows.

Run from ml-learing-center/:
    pytest sliding_window_test.py -v
"""
import pandas as pd
import pytest

from sliding_window import WINDOW_DEFS, extract_windows


@pytest.fixture
def sample_row() -> pd.Series:
    # Realistic UCI row (values from the first row of default_of_credit_card_clients.csv).
    return pd.Series({
        "LIMIT_BAL": 20000, "SEX": 2, "EDUCATION": 2, "MARRIAGE": 1, "AGE": 24,
        "PAY_0": 2, "PAY_2": 2, "PAY_3": -1, "PAY_4": -1, "PAY_5": -2, "PAY_6": -2,
        "BILL_AMT1": 3913, "BILL_AMT2": 3102, "BILL_AMT3": 689,
        "BILL_AMT4": 0, "BILL_AMT5": 0, "BILL_AMT6": 0,
        "PAY_AMT1": 0, "PAY_AMT2": 689, "PAY_AMT3": 0,
        "PAY_AMT4": 0, "PAY_AMT5": 0, "PAY_AMT6": 0,
    })


def test_extract_windows_returns_four_windows(sample_row):
    windows = extract_windows(sample_row)
    assert len(windows) == 4
    for w in windows:
        assert set(w.keys()) == {"pay", "bill", "amt"}
        assert len(w["pay"]) == 3
        assert len(w["bill"]) == 3
        assert len(w["amt"]) == 3


def test_w3_contains_newest_months(sample_row):
    # W3 = [Jul, Aug, Sep] -> PAY_3, PAY_2, PAY_0 / BILL 3,2,1 / PAY_AMT 3,2,1
    w3 = extract_windows(sample_row)[3]
    assert w3["pay"] == [
        float(sample_row["PAY_3"]),
        float(sample_row["PAY_2"]),
        float(sample_row["PAY_0"]),
    ]
    assert w3["bill"] == [
        float(sample_row["BILL_AMT3"]),
        float(sample_row["BILL_AMT2"]),
        float(sample_row["BILL_AMT1"]),
    ]
    assert w3["amt"] == [
        float(sample_row["PAY_AMT3"]),
        float(sample_row["PAY_AMT2"]),
        float(sample_row["PAY_AMT1"]),
    ]


def test_w0_contains_oldest_months(sample_row):
    # W0 = [Apr, May, Jun] -> PAY_6, PAY_5, PAY_4 / BILL 6,5,4 / PAY_AMT 6,5,4
    w0 = extract_windows(sample_row)[0]
    assert w0["pay"] == [
        float(sample_row["PAY_6"]),
        float(sample_row["PAY_5"]),
        float(sample_row["PAY_4"]),
    ]
    assert w0["bill"] == [
        float(sample_row["BILL_AMT6"]),
        float(sample_row["BILL_AMT5"]),
        float(sample_row["BILL_AMT4"]),
    ]
    assert w0["amt"] == [
        float(sample_row["PAY_AMT6"]),
        float(sample_row["PAY_AMT5"]),
        float(sample_row["PAY_AMT4"]),
    ]


def test_no_pay_1_referenced():
    # PAY_1 does not exist in UCI -- no window may reference it.
    for w in WINDOW_DEFS:
        assert "PAY_1" not in w["pay"]
