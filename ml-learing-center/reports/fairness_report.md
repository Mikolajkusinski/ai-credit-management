# CREDIT-112: Fairness audit (DPD / EOD wrt SEX)

Audit dataset: **W3 test split** (random_state=42, test_size=0.2, stratify=y).
Test size: **6000** clients (male=2402, female=3598); SEX coding: 1=male, 2=female (UCI).
Binarization: per-model cost-optimized thresholds from `ml-service/alert_thresholds.json` (CREDIT-106, FN=5x FP).
Warning rule: **|DPD| > 0.1** or **|EOD| > 0.1**.

## Summary table

| Model | Threshold | DPD | EOD | DPD warn | EOD warn |
|---|---:|---:|---:|:---:|:---:|
| Random Forest | 0.145 | +0.0345 | +0.0282 | ok | ok |
| XGBoost | 0.165 | +0.0358 | +0.0279 | ok | ok |
| LightGBM | 0.160 | +0.0351 | +0.0274 | ok | ok |
| CatBoost | 0.160 | +0.0392 | +0.0329 | ok | ok |
| LSTM | 0.155 | +0.0060 | +0.0208 | ok | ok |

## Per-group breakdown

| Model | sel_rate male | sel_rate female | TPR male | TPR female | FPR male | FPR female |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0.4650 | 0.4305 | 0.7594 | 0.7389 | 0.3753 | 0.3471 |
| XGBoost | 0.4596 | 0.4238 | 0.7558 | 0.7285 | 0.3694 | 0.3415 |
| LightGBM | 0.4609 | 0.4258 | 0.7558 | 0.7298 | 0.3710 | 0.3436 |
| CatBoost | 0.4850 | 0.4458 | 0.7843 | 0.7598 | 0.3938 | 0.3609 |
| LSTM | 0.4484 | 0.4544 | 0.7273 | 0.7480 | 0.3634 | 0.3750 |

## Verdict

All 5 models pass the |diff| <= 0.1 threshold on both DPD and EOD. No fairness warnings raised.

## Artifacts

- `reports/fairness_metrics_w3.csv` -- full numeric table
- `reports/fairness_selection_rate_w3.png` -- selection rate by SEX
- `reports/fairness_tpr_fpr_w3.png` -- TPR / FPR by SEX
