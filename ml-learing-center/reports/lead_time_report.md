# CREDIT-110: Early-warning lead time report

Alert threshold: **PD >= 0.5** in any of the 4 windows (W0..W3).
Lead time = how many windows before W3 the alert first fired.
Caught at W3 = 0 lead (latest possible alert); caught at W0 = 3 leads (earliest).

## Random Forest

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **661** (49.8%)
- Mean lead time (caught only): **2.05** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=108 | W2=100 | W1=101 | W0=352

## XGBoost

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **671** (50.6%)
- Mean lead time (caught only): **2.05** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=109 | W2=106 | W1=98 | W0=358

## LightGBM

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **680** (51.2%)
- Mean lead time (caught only): **2.07** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=105 | W2=106 | W1=104 | W0=365

## CatBoost

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **697** (52.5%)
- Mean lead time (caught only): **2.08** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=105 | W2=106 | W1=111 | W0=375

## LSTM

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **705** (53.1%)
- Mean lead time (caught only): **2.07** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=103 | W2=115 | W1=119 | W0=368

