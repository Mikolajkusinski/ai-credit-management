# CREDIT-112: Fairness audit (DPD / EOD wrt SEX)

Audit dataset: **W3 test split** (random_state=42, test_size=0.2, stratify=y).
Test size: **6000** clients (male=2402, female=3598); SEX coding: 1=male, 2=female (UCI).
Binarization: per-model cost-optimized thresholds from `ml-service/alert_thresholds.json` (CREDIT-106, FN=5x FP).
Warning rule: **|DPD| > 0.1** or **|EOD| > 0.1**.

## Summary table

| Model | Threshold | DPD | EOD | DPD warn | EOD warn |
|---|---:|---:|---:|:---:|:---:|
| Random Forest | 0.145 | +0.0347 | +0.0289 | ok | ok |
| XGBoost | 0.180 | +0.0377 | +0.0333 | ok | ok |
| LightGBM | 0.160 | +0.0269 | +0.0215 | ok | ok |
| CatBoost | 0.130 | +0.0393 | +0.0334 | ok | ok |
| LSTM | 0.175 | +0.0068 | +0.0153 | ok | ok |

## Per-group breakdown

| Model | sel_rate male | sel_rate female | TPR male | TPR female | FPR male | FPR female |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0.4621 | 0.4275 | 0.7576 | 0.7389 | 0.3721 | 0.3432 |
| XGBoost | 0.4721 | 0.4344 | 0.7683 | 0.7350 | 0.3819 | 0.3531 |
| LightGBM | 0.4455 | 0.4186 | 0.7487 | 0.7272 | 0.3531 | 0.3351 |
| CatBoost | 0.5237 | 0.4844 | 0.8164 | 0.7924 | 0.4345 | 0.4011 |
| LSTM | 0.4796 | 0.4864 | 0.7594 | 0.7702 | 0.3944 | 0.4096 |

## Verdict

All 5 models pass the |diff| <= 0.1 threshold on both DPD and EOD. No fairness warnings raised.

## Artifacts

- `reports/fairness_metrics_w3.csv` -- full numeric table
- `reports/fairness_selection_rate_w3.png` -- selection rate by SEX
- `reports/fairness_tpr_fpr_w3.png` -- TPR / FPR by SEX
