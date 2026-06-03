"""
CREDIT-104: pure monitoring logic (alert thresholds, trend computation).

Kept separate from app.py so tests can import these without triggering
model-artifact loading at module import time.
"""
from typing import Dict, List

SLOPE_THRESHOLD = 0.10  # see docs/api-contracts/monitoring.md section 2.3
WINDOW_NAMES = ["W0", "W1", "W2", "W3"]


def compute_alert(slope: float, threshold: float = SLOPE_THRESHOLD) -> str:
    """slope > +theta -> INCREASING_RISK; slope < -theta -> DECREASING_RISK; else STABLE.
    Boundary (slope == +/-theta) maps to STABLE (strict inequality)."""
    if slope > threshold:
        return "INCREASING_RISK"
    if slope < -threshold:
        return "DECREASING_RISK"
    return "STABLE"


def compute_trends(trajectory: List[Dict]) -> Dict[str, Dict[str, object]]:
    """Compute (slope, alert) per model from a 4-point trajectory.

    Each element of `trajectory` must have a 'predictions' dict with keys
    'randomForest', 'xgboost', 'lstm' and float values in [0, 1].

    slope = PD_W3 - PD_W0, rounded to 4 decimals.
    """
    pd_w0 = trajectory[0]["predictions"]
    pd_w3 = trajectory[3]["predictions"]
    return {
        model_key: {
            "slope": round(pd_w3[model_key] - pd_w0[model_key], 4),
            "alert": compute_alert(pd_w3[model_key] - pd_w0[model_key]),
        }
        for model_key in ("randomForest", "xgboost", "lstm")
    }
