"""
CREDIT-110: time-series evaluation metrics for the W3 model family.

For every client in the W3 test set (same 20% test split as CREDIT-105):
- Score each of the 4 sliding windows (W0..W3) with calibrated RF/XGB/LSTM
  -> 4-point PD trajectory per model.
- Compute early-warning lead time, slope distribution, and slope-as-predictor AUC.

Output:
- reports/timeseries_metrics.csv     summary table (catch rate, mean lead, slope AUC, W3 AUC)
- reports/lead_time_report.md        per-model breakdown in prose
- reports/slope_boxplot_{model}.png  slope distribution by outcome class (3 files)
- reports/trajectory_examples_{model}.png random defaulter vs non-defaulter trajectories (3 files)

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python timeseries_eval.py
"""
from pathlib import Path
from typing import Dict, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

from features import engineer_features, prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
REPORTS.mkdir(exist_ok=True)

MODELS = ["Random Forest", "XGBoost", "LightGBM", "CatBoost", "LSTM"]
SLUG = {
    "Random Forest": "random_forest",
    "XGBoost": "xgboost",
    "LightGBM": "lightgbm",
    "CatBoost": "catboost",
    "LSTM": "lstm",
}
WINDOW_LABELS = ["W0", "W1", "W2", "W3"]
ALERT_THRESHOLD = 0.5  # PD threshold for "alert raised" (absolute, calibrated)


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def _remap_to_w3(df: pd.DataFrame, window: Dict) -> pd.DataFrame:
    """Remap window's columns into W3 slots so engineer_features(W3) operates on
    the right monthly slice. Same trick used in ml-service/app.py."""
    w3 = WINDOW_DEFS[3]
    out = df.copy()
    for i in range(3):
        out[w3["pay"][i]] = df[window["pay"][i]]
        out[w3["bill"][i]] = df[window["bill"][i]]
        out[w3["amt"][i]] = df[window["amt"][i]]
    return out


def score_test_set() -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """Score the W3 test set across all 4 windows for all 3 models.

    Returns (y_test, {model_name: trajectories shape=(n_test, 4)}).
    Trajectory columns are ordered W0, W1, W2, W3 (oldest -> newest).
    """
    df = _load_csv()
    y = df["Default"]

    # Same 60/20/20 split as CREDIT-105 -- this isolates the same 20% test set
    df_tmp, df_te, _, y_te = train_test_split(df, y, test_size=0.2, stratify=y, random_state=42)

    rf = joblib.load(HERE / "rf_model_w3.pkl")
    xgb = joblib.load(HERE / "xgb_model_w3.pkl")
    lgbm = joblib.load(HERE / "lightgbm_model_w3.pkl")
    cat = joblib.load(HERE / "catboost_model_w3.pkl")
    scaler_w3 = joblib.load(HERE / "scaler_w3.pkl")
    features_w3 = joblib.load(HERE / "features_w3.pkl")
    lstm = load_model(HERE / "lstm_model_w3.keras")
    lstm_calibrator = joblib.load(HERE.parent / "ml-service" / "lstm_calibrator_w3.pkl")

    n_test = len(df_te)
    traj = {name: np.zeros((n_test, 4)) for name in MODELS}
    w3 = WINDOW_DEFS[3]

    for w_idx, window in enumerate(WINDOW_DEFS):
        df_remapped = _remap_to_w3(df_te, window)

        # Static path -- RF / XGBoost / LightGBM / CatBoost
        X_df, _ = engineer_features(df_remapped, w3)
        for col in features_w3:
            if col not in X_df.columns:
                X_df[col] = 0
        X_df = X_df[features_w3]
        X_scaled = scaler_w3.transform(X_df)

        traj["Random Forest"][:, w_idx] = rf.predict_proba(X_scaled)[:, 1]
        traj["XGBoost"][:, w_idx] = xgb.predict_proba(X_scaled)[:, 1]
        traj["LightGBM"][:, w_idx] = lgbm.predict_proba(X_scaled)[:, 1]
        traj["CatBoost"][:, w_idx] = cat.predict_proba(X_scaled)[:, 1]

        # LSTM path
        X_seq, _ = prepare_lstm_sequences(df_remapped, w3)
        lstm_raw = lstm.predict(X_seq, verbose=0).ravel()
        traj["LSTM"][:, w_idx] = lstm_calibrator.predict(lstm_raw)

    return y_te.to_numpy(), traj


def compute_lead_time(trajectory: np.ndarray, y_true: np.ndarray, threshold: float = ALERT_THRESHOLD) -> Dict:
    """For defaulters: find earliest window where PD >= threshold.
    Lead time = (3 - first_alert_window_index); not caught = -1.
    Returns: catch_rate, mean_lead (caught only), and distribution per window.
    """
    defaulters = trajectory[y_true == 1]
    leads = np.full(len(defaulters), -1, dtype=int)
    for i, row in enumerate(defaulters):
        triggered = np.where(row >= threshold)[0]
        if len(triggered) > 0:
            leads[i] = 3 - int(triggered[0])

    caught_mask = leads >= 0
    caught_leads = leads[caught_mask]
    distribution = np.bincount(caught_leads, minlength=4)  # index 0 = caught at W3, 3 = caught at W0
    return {
        "n_defaulters": int(len(defaulters)),
        "n_caught": int(caught_mask.sum()),
        "catch_rate": float(caught_mask.mean()) if len(defaulters) else 0.0,
        "mean_lead": float(caught_leads.mean()) if len(caught_leads) else 0.0,
        "median_lead": float(np.median(caught_leads)) if len(caught_leads) else 0.0,
        "distribution": distribution.tolist(),  # [caught@W3, @W2, @W1, @W0]
    }


def plot_slope_boxplot(slopes_def: np.ndarray, slopes_nondef: np.ndarray, model_name: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(data=[slopes_nondef, slopes_def], ax=ax, palette=["C0", "C3"])
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"NO DEFAULT (n={len(slopes_nondef)})", f"DEFAULT (n={len(slopes_def)})"])
    ax.set_ylabel("slope = PD_W3 - PD_W0")
    ax.set_title(f"Slope distribution by outcome -- {model_name} (W3 calibrated)")
    ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def plot_trajectory_examples(trajectory: np.ndarray, y_true: np.ndarray, model_name: str, path: Path, n: int = 25) -> None:
    rng = np.random.default_rng(42)
    def_idx = np.where(y_true == 1)[0]
    non_idx = np.where(y_true == 0)[0]
    sampled_def = rng.choice(def_idx, min(n, len(def_idx)), replace=False)
    sampled_non = rng.choice(non_idx, min(n, len(non_idx)), replace=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    for i in sampled_non:
        ax.plot(WINDOW_LABELS, trajectory[i], color="C0", alpha=0.25, linewidth=0.9)
    for i in sampled_def:
        ax.plot(WINDOW_LABELS, trajectory[i], color="C3", alpha=0.5, linewidth=1.2)
    ax.plot([], [], color="C0", linewidth=2, label=f"NO DEFAULT (n={len(sampled_non)})")
    ax.plot([], [], color="C3", linewidth=2, label=f"DEFAULT (n={len(sampled_def)})")
    ax.axhline(ALERT_THRESHOLD, color="gray", linestyle="--", linewidth=0.8,
               label=f"Alert threshold = {ALERT_THRESHOLD}")
    ax.set_xlabel("Window (oldest -> newest)")
    ax.set_ylabel("PD")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"PD trajectory examples -- {model_name}")
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def write_lead_time_report(per_model: Dict[str, Dict], path: Path) -> None:
    lines = [
        "# CREDIT-110: Early-warning lead time report\n",
        "\n",
        f"Alert threshold: **PD >= {ALERT_THRESHOLD}** in any of the 4 windows (W0..W3).\n",
        "Lead time = how many windows before W3 the alert first fired.\n",
        "Caught at W3 = 0 lead (latest possible alert); caught at W0 = 3 leads (earliest).\n",
        "\n",
    ]
    for name, info in per_model.items():
        d = info["distribution"]
        lines.append(f"## {name}\n\n")
        lines.append(f"- Defaulters in test set: **{info['n_defaulters']}**\n")
        lines.append(f"- Caught (alert raised in >=1 window): **{info['n_caught']}** ({info['catch_rate']:.1%})\n")
        lines.append(f"- Mean lead time (caught only): **{info['mean_lead']:.2f}** windows before W3\n")
        lines.append(f"- Median lead time (caught only): **{info['median_lead']:.0f}** windows before W3\n")
        lines.append(f"- Lead distribution: caught at W3={d[0]} | W2={d[1]} | W1={d[2]} | W0={d[3]}\n\n")
    path.write_text("".join(lines))


def main() -> None:
    print("Scoring W3 test set across all 4 sliding windows...")
    y_test, trajectories = score_test_set()
    print(f"Scored {len(y_test)} clients ({int(y_test.sum())} defaulters)")

    rows = []
    per_model_lead = {}
    print("\n===== TIME-SERIES METRICS (W3 calibrated, alert threshold 0.5) =====")
    for name in MODELS:
        traj = trajectories[name]
        slopes = traj[:, 3] - traj[:, 0]
        lead = compute_lead_time(traj, y_test)
        per_model_lead[name] = lead

        slope_auc = float(roc_auc_score(y_test, slopes))
        w3_auc = float(roc_auc_score(y_test, traj[:, 3]))

        rows.append({
            "model": name,
            "n_defaulters": lead["n_defaulters"],
            "catch_rate": round(lead["catch_rate"], 4),
            "mean_lead_windows": round(lead["mean_lead"], 4),
            "slope_auc": round(slope_auc, 4),
            "w3_auc": round(w3_auc, 4),
        })

        slug = SLUG[name]
        plot_slope_boxplot(
            slopes[y_test == 1], slopes[y_test == 0], name,
            REPORTS / f"slope_boxplot_{slug}_w3.png",
        )
        plot_trajectory_examples(
            traj, y_test, name, REPORTS / f"trajectory_examples_{slug}_w3.png",
        )

    metrics = pd.DataFrame(rows)
    print(metrics.to_string(index=False))
    metrics.to_csv(REPORTS / "timeseries_metrics.csv", index=False)
    print(f"\nSaved: {REPORTS / 'timeseries_metrics.csv'}")

    write_lead_time_report(per_model_lead, REPORTS / "lead_time_report.md")
    print(f"Lead time report: {REPORTS / 'lead_time_report.md'}")
    print(f"Plots: 6 PNG files in {REPORTS}/")


if __name__ == "__main__":
    main()
