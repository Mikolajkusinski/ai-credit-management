"""
B4/F1 (Fable5_Task1/Task2 / plan 2026-07-07): fairness counter-experiment
WITHOUT the protected attribute in the feature vector.

Repeats the exact W3 training protocol from main.py (60/20/20 split,
random_state=42, isotonic calibration, cost thresholds on the calibration
split) for the 4 tree models with the SEX_* one-hot columns REMOVED
(EDUCATION/MARRIAGE stay). LSTM is skipped: its (3,3) tensor never contained
demographics, so the shipped LSTM already IS the no-demographics reference.

SEX from the raw data is used ONLY to slice the fairness metrics, never as
a model input. Nothing in production is overwritten -- outputs go to reports/.

Expected reading (the ablation thesis): removing SEX barely moves DPD/EOD,
because the signal partially leaks through correlates -- and the gaps were
mostly structural (base-rate difference) to begin with.

Outputs:
    reports/fairness_no_sex_metrics.csv
    reports/fairness_no_sex_report.md
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from features import engineer_features
from sliding_window import WINDOW_DEFS

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
W3 = WINDOW_DEFS[3]

_FN, _FP = 5.0, 1.0
_BOUNDS, _RES = (0.1, 0.9), 0.005


def _find_optimal_threshold(y_true, y_proba):
    n = int((_BOUNDS[1] - _BOUNDS[0]) / _RES) + 1
    best_thr, best_cost = _BOUNDS[0], float("inf")
    for thr in np.linspace(_BOUNDS[0], _BOUNDS[1], n):
        pred = y_proba >= thr
        cost = _FN * ((y_true == 1) & ~pred).sum() + _FP * ((y_true == 0) & pred).sum()
        if cost < best_cost:
            best_thr, best_cost = float(thr), cost
    return best_thr


def main() -> None:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    y = df["Default"]
    sex_all = df["SEX"].to_numpy()

    X_full, feats = engineer_features(df, W3)
    feats_no_sex = [f for f in feats if not f.startswith("SEX_")]
    X = X_full[feats_no_sex]

    # Identical split protocol to main.py (leakage-fixed): split raw, scale on train.
    X_tmp, X_te, y_tmp, y_te, sex_tmp, sex_te = train_test_split(
        X, y, sex_all, test_size=0.2, stratify=y, random_state=42
    )
    X_tr, X_cal, y_tr, y_cal = train_test_split(
        X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42
    )
    scaler = StandardScaler().fit(X_tr)
    X_tr_s, X_cal_s, X_te_s = (scaler.transform(a) for a in (X_tr, X_cal, X_te))
    y_te_arr, y_cal_arr = y_te.to_numpy(), y_cal.to_numpy()

    bases = {
        "Random Forest": RandomForestClassifier(
            n_estimators=500, max_depth=10, min_samples_leaf=5,
            class_weight="balanced", random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=800, learning_rate=0.02, max_depth=4,
            subsample=0.7, colsample_bytree=0.7, reg_alpha=0.1, reg_lambda=1.0,
            scale_pos_weight=(len(y) - sum(y)) / sum(y),
            random_state=42, eval_metric="auc"),
        "LightGBM": LGBMClassifier(
            n_estimators=800, learning_rate=0.02, max_depth=4,
            subsample=0.7, colsample_bytree=0.7, reg_alpha=0.1, reg_lambda=1.0,
            class_weight="balanced", random_state=42, verbose=-1),
        "CatBoost": CatBoostClassifier(
            iterations=800, learning_rate=0.02, depth=4,
            subsample=0.7, colsample_bylevel=0.7, l2_leaf_reg=3.0,
            auto_class_weights="Balanced", random_state=42, verbose=False,
            bootstrap_type="Bernoulli"),
    }

    baseline = pd.read_csv(REPORTS / "fairness_metrics_w3.csv").set_index("model")
    base_metrics = pd.read_csv(REPORTS / "metrics_w3.csv").set_index("model")

    rows = []
    for name, base in bases.items():
        print(f"Training {name} without SEX...")
        base.fit(X_tr_s, y_tr)
        cal = CalibratedClassifierCV(FrozenEstimator(base), method="isotonic").fit(X_cal_s, y_cal)
        p_cal = cal.predict_proba(X_cal_s)[:, 1]
        p_te = cal.predict_proba(X_te_s)[:, 1]
        thr = _find_optimal_threshold(y_cal_arr, p_cal)
        y_pred = (p_te >= thr).astype(int)
        rows.append({
            "model": name,
            "AUC_no_sex": roc_auc_score(y_te_arr, p_te),
            "Brier_no_sex": brier_score_loss(y_te_arr, p_te),
            "threshold_no_sex": thr,
            "DPD_no_sex": demographic_parity_difference(y_te_arr, y_pred, sensitive_features=sex_te),
            "EOD_no_sex": equalized_odds_difference(y_te_arr, y_pred, sensitive_features=sex_te),
            "AUC_with_sex": base_metrics.loc[name, "AUC"],
            "Brier_with_sex": base_metrics.loc[name, "Brier"],
            "DPD_with_sex": baseline.loc[name, "DPD"],
            "EOD_with_sex": baseline.loc[name, "EOD"],
        })
    out = pd.DataFrame(rows)
    out.to_csv(REPORTS / "fairness_no_sex_metrics.csv", index=False)

    lines = [
        "# B4: Kontr-eksperyment fairness — modele bez atrybutu SEX",
        "",
        "Protokół identyczny z produkcyjnym W3 (60/20/20, seed 42, kalibracja "
        "izotoniczna, progi kosztowe na splicie kalibracyjnym); jedyna różnica: "
        "kolumny `SEX_*` usunięte z wektora cech. SEX służy wyłącznie do slicingu "
        "metryk. LSTM pominięty — jego tensor (3,3) nigdy nie zawierał demografii, "
        "więc produkcyjny LSTM (DPD +0.006) już jest punktem odniesienia bez SEX.",
        "",
        "| Model | AUC z SEX → bez | Brier z → bez | DPD z SEX → bez | EOD z SEX → bez |",
        "|---|---|---|---|---|",
    ]
    for _, r in out.iterrows():
        lines.append(
            f"| {r['model']} | {r['AUC_with_sex']:.4f} → {r['AUC_no_sex']:.4f} "
            f"| {r['Brier_with_sex']:.4f} → {r['Brier_no_sex']:.4f} "
            f"| {r['DPD_with_sex']:+.4f} → {r['DPD_no_sex']:+.4f} "
            f"| {r['EOD_with_sex']:+.4f} → {r['EOD_no_sex']:+.4f} |"
        )

    d_auc = (out["AUC_no_sex"] - out["AUC_with_sex"]).abs().max()
    d_dpd = (out["DPD_no_sex"] - out["DPD_with_sex"]).abs().max()
    d_eod = (out["EOD_no_sex"] - out["EOD_with_sex"]).abs().max()
    lines += [
        "",
        f"Maksymalne przesunięcia: |ΔAUC| = {d_auc:.4f}, |ΔDPD| = {d_dpd:.4f}, "
        f"|ΔEOD| = {d_eod:.4f}.",
        "",
        "**Odczyt do obrony:** "
        + (
            "usunięcie zmiennej chronionej nie zmienia istotnie ani jakości, ani "
            "parytetu — luki DPD/EOD mają pochodzenie strukturalne (różnica base "
            "rate) i korelacyjne, nie wynikają z bezpośredniego użycia SEX. To "
            "empiryczne domknięcie argumentu ablacyjnego: wariant produkcyjny można "
            "pozbawić SEX bez kosztu (zalecenie wdrożeniowe), a audyt fairness "
            "pozostaje konieczny niezależnie od obecności atrybutu w cechach."
            if d_dpd < 0.01 and d_auc < 0.003 else
            "usunięcie SEX przesuwa metryki w stopniu widocznym — patrz tabela; "
            "wynik wymaga omówienia w pracy (kierunek zmian wskaże, czy SEX działał "
            "bezpośrednio, czy przez korelaty)."
        ),
        "",
    ]
    (REPORTS / "fairness_no_sex_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Saved: fairness_no_sex_metrics.csv, fairness_no_sex_report.md")
    print(out[["model", "AUC_no_sex", "DPD_no_sex", "EOD_no_sex"]].to_string(index=False))


if __name__ == "__main__":
    main()
