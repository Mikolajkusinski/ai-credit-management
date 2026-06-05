# CREDIT-108: Optuna hyperparameter tuning report

5-fold stratified CV on the W3 train split (60% of clients), TPESampler seed=42, n_trials=30. Held-out test set (20% of clients) is the same partition used by CREDIT-105 calibration so the test-AUC numbers are directly comparable to CREDIT-103 / CREDIT-105 / CREDIT-109 reports.

**Scope:** academic exploration. Tuned models are NOT promoted to production -- the shipped W3 artifacts (CREDIT-109 / CREDIT-105) stay with the CREDIT-102 hyperparameters because re-running calibration + cost thresholds + LightGBM/CatBoost on tuned bases is out of scope.

---

## RandomForest

- CV-AUC default: **0.7815 ± 0.0029**
- CV-AUC tuned (best trial): **0.7825 ± 0.0031**
- Test AUC default: **0.7760**
- Test AUC tuned:   **0.7770**
- Δ test AUC: **+0.0983 pp** (improved)

Best hyperparameters:
```json
{
  "n_estimators":800,
  "max_depth":10,
  "min_samples_leaf":9,
  "min_samples_split":3,
  "max_features":"log2"
}
```

---

## XGBoost

- CV-AUC default: **0.7814 ± 0.0044**
- CV-AUC tuned (best trial): **0.7850 ± 0.0043**
- Test AUC default: **0.7768**
- Test AUC tuned:   **0.7798**
- Δ test AUC: **+0.2964 pp** (improved)

Best hyperparameters:
```json
{
  "n_estimators":1000.0,
  "learning_rate":0.0075277445,
  "max_depth":3.0,
  "subsample":0.8010751296,
  "colsample_bytree":0.6634060114,
  "reg_alpha":0.8310514872,
  "reg_lambda":3.5935801205
}
```

---

