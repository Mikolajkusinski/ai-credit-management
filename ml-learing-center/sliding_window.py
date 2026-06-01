"""
CREDIT-101: Sliding-window panel for UCI credit-card-default dataset.

Builds 4 overlapping 3-month windows (W0..W3) from a single UCI row.
UCI column-to-month mapping (PAY_1 does not exist in the dataset):
    PAY_0 / BILL_AMT1 / PAY_AMT1  -> September (newest)
    PAY_2 / BILL_AMT2 / PAY_AMT2  -> August
    PAY_3 / BILL_AMT3 / PAY_AMT3  -> July
    PAY_4 / BILL_AMT4 / PAY_AMT4  -> June
    PAY_5 / BILL_AMT5 / PAY_AMT5  -> May
    PAY_6 / BILL_AMT6 / PAY_AMT6  -> April (oldest)

Each window contains exactly 3 months ordered oldest -> newest inside the window.
Training (CREDIT-102) uses W3 (aligned with the October default label).
Inference at monitoring time (CREDIT-104, Sprint 2) iterates W0..W3 on the same model
to produce a 4-point PD trajectory.
"""
from typing import Dict, List, Mapping

WINDOW_DEFS: List[Dict[str, List[str]]] = [
    # W0 = [Apr, May, Jun]
    {
        "pay":  ["PAY_6", "PAY_5", "PAY_4"],
        "bill": ["BILL_AMT6", "BILL_AMT5", "BILL_AMT4"],
        "amt":  ["PAY_AMT6", "PAY_AMT5", "PAY_AMT4"],
    },
    # W1 = [May, Jun, Jul]
    {
        "pay":  ["PAY_5", "PAY_4", "PAY_3"],
        "bill": ["BILL_AMT5", "BILL_AMT4", "BILL_AMT3"],
        "amt":  ["PAY_AMT5", "PAY_AMT4", "PAY_AMT3"],
    },
    # W2 = [Jun, Jul, Aug]
    {
        "pay":  ["PAY_4", "PAY_3", "PAY_2"],
        "bill": ["BILL_AMT4", "BILL_AMT3", "BILL_AMT2"],
        "amt":  ["PAY_AMT4", "PAY_AMT3", "PAY_AMT2"],
    },
    # W3 = [Jul, Aug, Sep] -- newest, used for training
    {
        "pay":  ["PAY_3", "PAY_2", "PAY_0"],
        "bill": ["BILL_AMT3", "BILL_AMT2", "BILL_AMT1"],
        "amt":  ["PAY_AMT3", "PAY_AMT2", "PAY_AMT1"],
    },
]


def extract_windows(row: Mapping) -> List[Dict[str, List[float]]]:
    """Return 4 sliding windows [W0, W1, W2, W3] from a single UCI row.

    Args:
        row: Mapping with UCI columns (pd.Series or dict). Must contain PAY_0,
             PAY_2..PAY_6, BILL_AMT1..6, PAY_AMT1..6.

    Returns:
        List of 4 dicts, each with keys 'pay', 'bill', 'amt'; every value is a
        list of exactly 3 floats ordered oldest -> newest inside the window.
    """
    return [
        {
            "pay":  [float(row[c]) for c in w["pay"]],
            "bill": [float(row[c]) for c in w["bill"]],
            "amt":  [float(row[c]) for c in w["amt"]],
        }
        for w in WINDOW_DEFS
    ]
