"""
CREDIT-108: Optuna hyperparameter tuning + 5-fold CV for XGBoost and RandomForest
on W3 features (3-month window).

Standalone runner -- does NOT overwrite the W3 artifacts shipped from CREDIT-109.
Tuning is treated as academic exploration here. Promoting the tuned
hyperparameters to production would require re-running CREDIT-105 calibration,
CREDIT-106 cost-threshold optimization, and CREDIT-109 LightGBM/CatBoost on
the new pipeline -- explicitly out of scope for the seminarium deadline.

Output:
- reports/optuna_study.md      per-model best params + CV-AUC mean ± std
                               for default vs tuned + test-set AUC delta
- reports/optuna_trials.csv    full trial-by-trial sweep (n_trials × per-model)

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python optuna_tuning.py
"""
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from features import engineer_features
from sliding_window import WINDOW_DEFS

# Optuna can be chatty; pin to WARNING for clean logs.
optuna.logging.set_verbosity(optuna.logging.WARNING)

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
REPORTS.mkdir(exist_ok=True)

N_TRIALS = 30
N_FOLDS = 5
RANDOM_STATE = 42


def _load_csv() -> pd.DataFrame:
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    df["EDUCATION"] = df["EDUCATION"].astype(int)
    df["MARRIAGE"] = df["MARRIAGE"].astype(int)
    df["SEX"] = df["SEX"].astype(int)
    return df


def cv_auc(estimator_factory, X: np.ndarray, y: np.ndarray, n_folds: int = N_FOLDS) -> Tuple[float, float]:
    """Stratified k-fold mean +/- std of test-fold ROC AUC."""
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=RANDOM_STATE)
    aucs = []
    for train_idx, val_idx in cv.split(X, y):
        est = estimator_factory()
        est.fit(X[train_idx], y[train_idx])
        proba = est.predict_proba(X[val_idx])[:, 1]
        aucs.append(roc_auc_score(y[val_idx], proba))
    return float(np.mean(aucs)), float(np.std(aucs))


# ============ Default factories (= CREDIT-102 / CREDIT-105 hyperparameters) ============

def make_rf_default() -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=500, max_depth=10, min_samples_leaf=5,
        class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1,
    )


def make_xgb_default(spw: float) -> XGBClassifier:
    return XGBClassifier(
        n_estimators=800, learning_rate=0.02, max_depth=4,
        subsample=0.7, colsample_bytree=0.7,
        reg_alpha=0.1, reg_lambda=1.0,
        scale_pos_weight=spw,
        random_state=RANDOM_STATE, eval_metric="auc", n_jobs=-1,
    )


# ============ Optuna studies ============

def tune_rf(X_tr: np.ndarray, y_tr: np.ndarray) -> optuna.Study:
    def objective(trial: optuna.Trial) -> float:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 200, 800, step=100),
            max_depth=trial.suggest_int("max_depth", 5, 16),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 10),
            max_features=trial.suggest_categorical("max_features", ["sqrt", "log2", 0.5]),
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1,
        )
        mean_auc, _ = cv_auc(lambda: RandomForestClassifier(**params), X_tr, y_tr)
        return mean_auc

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        study_name="rf_w3",
    )
    study.optimize(objective, n_trials=N_TRIALS)
    return study


def tune_xgb(X_tr: np.ndarray, y_tr: np.ndarray, spw: float) -> optuna.Study:
    def objective(trial: optuna.Trial) -> float:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 300, 1200, step=100),
            learning_rate=trial.suggest_float("learning_rate", 0.005, 0.1, log=True),
            max_depth=trial.suggest_int("max_depth", 3, 8),
            subsample=trial.suggest_float("subsample", 0.5, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
            reg_alpha=trial.suggest_float("reg_alpha", 0.001, 1.0, log=True),
            reg_lambda=trial.suggest_float("reg_lambda", 0.1, 10.0, log=True),
            scale_pos_weight=spw, random_state=RANDOM_STATE, eval_metric="auc", n_jobs=-1,
        )
        mean_auc, _ = cv_auc(lambda: XGBClassifier(**params), X_tr, y_tr)
        return mean_auc

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        study_name="xgb_w3",
    )
    study.optimize(objective, n_trials=N_TRIALS)
    return study


# ============ Report writers ============

def trials_dataframe(study: optuna.Study, model_name: str) -> pd.DataFrame:
    df = study.trials_dataframe(attrs=("number", "value", "params"))
    df.insert(0, "model", model_name)
    return df


def write_markdown_report(results: Dict[str, dict], path: Path) -> None:
    lines = [
        "# CREDIT-108: Optuna hyperparameter tuning report\n\n",
        f"5-fold stratified CV on the W3 train split (60% of clients), TPESampler "
        f"seed={RANDOM_STATE}, n_trials={N_TRIALS}. Held-out test set (20% of clients) "
        f"is the same partition used by CREDIT-105 calibration so the test-AUC numbers "
        f"are directly comparable to CREDIT-103 / CREDIT-105 / CREDIT-109 reports.\n\n",
        f"**Scope:** academic exploration. Tuned models are NOT promoted to production "
        f"-- the shipped W3 artifacts (CREDIT-109 / CREDIT-105) stay with the CREDIT-102 "
        f"hyperparameters because re-running calibration + cost thresholds + "
        f"LightGBM/CatBoost on tuned bases is out of scope.\n\n",
        "---\n\n",
    ]
    for name, r in results.items():
        delta_pp = (r["test_auc_tuned"] - r["test_auc_default"]) * 100
        verdict = "improved" if delta_pp > 0 else ("regressed" if delta_pp < 0 else "tied")
        lines.append(f"## {name}\n\n")
        lines.append(
            f"- CV-AUC default: **{r['cv_default_mean']:.4f} ± {r['cv_default_std']:.4f}**\n"
        )
        lines.append(
            f"- CV-AUC tuned (best trial): **{r['cv_tuned_mean']:.4f} ± {r['cv_tuned_std']:.4f}**\n"
        )
        lines.append(f"- Test AUC default: **{r['test_auc_default']:.4f}**\n")
        lines.append(f"- Test AUC tuned:   **{r['test_auc_tuned']:.4f}**\n")
        lines.append(f"- Δ test AUC: **{delta_pp:+.4f} pp** ({verdict})\n\n")
        lines.append("Best hyperparameters:\n```json\n")
        lines.append(pd.Series(r["best_params"]).to_json(indent=2))
        lines.append("\n```\n\n---\n\n")
    path.write_text("".join(lines))


# ============ Main ============

def main() -> None:
    print("Loading data + preparing W3 features...")
    df = _load_csv()
    y = df["Default"]
    W3 = WINDOW_DEFS[3]
    X, _ = engineer_features(df, W3)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 60/20/20 split -- same partition as CREDIT-105.
    X_tmp, X_te, y_tmp, y_te = train_test_split(
        X_scaled, y, test_size=0.2, stratify=y, random_state=42,
    )
    X_tr, _, y_tr, _ = train_test_split(
        X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42,
    )

    y_tr_arr = y_tr.to_numpy()
    y_te_arr = y_te.to_numpy()
    spw = float((len(y_tr_arr) - y_tr_arr.sum()) / y_tr_arr.sum())

    results = {}

    # --- RandomForest ---
    print("\n===== RANDOM FOREST =====")
    print(f"Default CV ({N_FOLDS}-fold)...")
    rf_cv_def_mean, rf_cv_def_std = cv_auc(make_rf_default, X_tr, y_tr_arr)
    print(f"  default RF CV-AUC = {rf_cv_def_mean:.4f} +/- {rf_cv_def_std:.4f}")

    print(f"Optuna tuning ({N_TRIALS} trials, TPE)...")
    rf_study = tune_rf(X_tr, y_tr_arr)
    print(f"  best CV-AUC = {rf_study.best_value:.4f}")
    print(f"  best params = {rf_study.best_params}")

    print(f"Re-evaluate tuned RF with 5-fold CV (for std)...")
    rf_best_factory = lambda: RandomForestClassifier(
        **rf_study.best_params, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
    )
    rf_cv_tuned_mean, rf_cv_tuned_std = cv_auc(rf_best_factory, X_tr, y_tr_arr)

    print("Test-set AUC...")
    rf_default = make_rf_default().fit(X_tr, y_tr_arr)
    rf_tuned = rf_best_factory().fit(X_tr, y_tr_arr)
    rf_test_default = float(roc_auc_score(y_te_arr, rf_default.predict_proba(X_te)[:, 1]))
    rf_test_tuned = float(roc_auc_score(y_te_arr, rf_tuned.predict_proba(X_te)[:, 1]))
    print(f"  test AUC default: {rf_test_default:.4f}")
    print(f"  test AUC tuned:   {rf_test_tuned:.4f}")
    print(f"  delta:            {rf_test_tuned - rf_test_default:+.4f}")

    results["RandomForest"] = dict(
        cv_default_mean=rf_cv_def_mean, cv_default_std=rf_cv_def_std,
        cv_tuned_mean=rf_cv_tuned_mean, cv_tuned_std=rf_cv_tuned_std,
        test_auc_default=rf_test_default, test_auc_tuned=rf_test_tuned,
        best_params=rf_study.best_params,
    )

    # --- XGBoost ---
    print("\n===== XGBOOST =====")
    print(f"Default CV ({N_FOLDS}-fold)...")
    xgb_cv_def_mean, xgb_cv_def_std = cv_auc(lambda: make_xgb_default(spw), X_tr, y_tr_arr)
    print(f"  default XGB CV-AUC = {xgb_cv_def_mean:.4f} +/- {xgb_cv_def_std:.4f}")

    print(f"Optuna tuning ({N_TRIALS} trials, TPE)...")
    xgb_study = tune_xgb(X_tr, y_tr_arr, spw)
    print(f"  best CV-AUC = {xgb_study.best_value:.4f}")
    print(f"  best params = {xgb_study.best_params}")

    print(f"Re-evaluate tuned XGB with 5-fold CV (for std)...")
    xgb_best_factory = lambda: XGBClassifier(
        **xgb_study.best_params, scale_pos_weight=spw, random_state=RANDOM_STATE,
        eval_metric="auc", n_jobs=-1,
    )
    xgb_cv_tuned_mean, xgb_cv_tuned_std = cv_auc(xgb_best_factory, X_tr, y_tr_arr)

    print("Test-set AUC...")
    xgb_default = make_xgb_default(spw).fit(X_tr, y_tr_arr)
    xgb_tuned = xgb_best_factory().fit(X_tr, y_tr_arr)
    xgb_test_default = float(roc_auc_score(y_te_arr, xgb_default.predict_proba(X_te)[:, 1]))
    xgb_test_tuned = float(roc_auc_score(y_te_arr, xgb_tuned.predict_proba(X_te)[:, 1]))
    print(f"  test AUC default: {xgb_test_default:.4f}")
    print(f"  test AUC tuned:   {xgb_test_tuned:.4f}")
    print(f"  delta:            {xgb_test_tuned - xgb_test_default:+.4f}")

    results["XGBoost"] = dict(
        cv_default_mean=xgb_cv_def_mean, cv_default_std=xgb_cv_def_std,
        cv_tuned_mean=xgb_cv_tuned_mean, cv_tuned_std=xgb_cv_tuned_std,
        test_auc_default=xgb_test_default, test_auc_tuned=xgb_test_tuned,
        best_params=xgb_study.best_params,
    )

    # --- Persist ---
    write_markdown_report(results, REPORTS / "optuna_study.md")
    trials = pd.concat([
        trials_dataframe(rf_study, "RandomForest"),
        trials_dataframe(xgb_study, "XGBoost"),
    ], ignore_index=True)
    trials.to_csv(REPORTS / "optuna_trials.csv", index=False)

    print(f"\nSaved: {REPORTS / 'optuna_study.md'}")
    print(f"Saved: {REPORTS / 'optuna_trials.csv'}  ({len(trials)} trials)")


if __name__ == "__main__":
    main()
