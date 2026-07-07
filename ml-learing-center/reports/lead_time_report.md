# CREDIT-110: Early-warning lead time report

Alert threshold: **PD >= 0.5** in any of the 4 windows (W0..W3).
Lead time = how many windows before W3 the alert first fired.
Caught at W3 = 0 lead (latest possible alert); caught at W0 = 3 leads (earliest).

## Random Forest

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **661** (49.8%)
- Mean lead time (caught only): **2.05** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=108 | W2=102 | W1=100 | W0=351

## XGBoost

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **673** (50.7%)
- Mean lead time (caught only): **2.05** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=109 | W2=107 | W1=100 | W0=357

## LightGBM

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **685** (51.6%)
- Mean lead time (caught only): **2.08** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=106 | W2=102 | W1=107 | W0=370

## CatBoost

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **684** (51.5%)
- Mean lead time (caught only): **2.08** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=106 | W2=102 | W1=108 | W0=368

## LSTM

- Defaulters in test set: **1327**
- Caught (alert raised in >=1 window): **680** (51.2%)
- Mean lead time (caught only): **2.06** windows before W3
- Median lead time (caught only): **3** windows before W3
- Lead distribution: caught at W3=109 | W2=103 | W1=104 | W0=364

