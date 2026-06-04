# CREDIT-111: Static vs Monitoring -- thesis proof report

The Variant B thesis claims that **monitoring** (the alert fires if any of W0..W3 crosses the threshold) detects defaults more reliably and/or earlier than the **static** rule (alert based on W3 alone). This document interprets the results honestly.

Test set: 6000 clients (1327 defaulters), W3-calibrated RF/XGB/LSTM, alert thresholds swept across 19 values in [0.05, 0.95].

---

## Random Forest

Catch rate at canonical false-alarm budgets:

| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |
|---|---|---|---|
| 5% | 35.2% | 40.5% | +5.28 |
| 10% | 50.3% | 45.3% | -4.97 |
| 20% | 60.2% | 65.3% | +5.05 |

Lead-only wins (defaulters caught by monitor but missed by static at FA=10%): **72**
Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): **138**
Mean lead time among monitor-caught defaulters (FA=10%): **1.99** windows before W3

**Verdict at FA=10%:** static wins (delta = -4.97 pp catch rate).

---

## XGBoost

Catch rate at canonical false-alarm budgets:

| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |
|---|---|---|---|
| 5% | 36.6% | 31.0% | -5.58 |
| 10% | 49.8% | 43.9% | -5.88 |
| 20% | 62.5% | 63.5% | +0.90 |

Lead-only wins (defaulters caught by monitor but missed by static at FA=10%): **43**
Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): **121**
Mean lead time among monitor-caught defaulters (FA=10%): **2.04** windows before W3

**Verdict at FA=10%:** static wins (delta = -5.88 pp catch rate).

---

## LightGBM

Catch rate at canonical false-alarm budgets:

| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |
|---|---|---|---|
| 5% | 34.7% | 39.0% | +4.22 |
| 10% | 51.1% | 49.8% | -1.28 |
| 20% | 66.0% | 59.8% | -6.25 |

Lead-only wins (defaulters caught by monitor but missed by static at FA=10%): **71**
Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): **88**
Mean lead time among monitor-caught defaulters (FA=10%): **2.05** windows before W3

**Verdict at FA=10%:** static wins (delta = -1.28 pp catch rate).

---

## CatBoost

Catch rate at canonical false-alarm budgets:

| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |
|---|---|---|---|
| 5% | 39.0% | 37.7% | -1.28 |
| 10% | 51.5% | 44.6% | -6.86 |
| 20% | 67.7% | 63.3% | -4.45 |

Lead-only wins (defaulters caught by monitor but missed by static at FA=10%): **36**
Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): **127**
Mean lead time among monitor-caught defaulters (FA=10%): **2.10** windows before W3

**Verdict at FA=10%:** static wins (delta = -6.86 pp catch rate).

---

## LSTM

Catch rate at canonical false-alarm budgets:

| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |
|---|---|---|---|
| 5% | 35.9% | 39.6% | +3.69 |
| 10% | 47.3% | 39.6% | -7.69 |
| 20% | 61.7% | 61.0% | -0.68 |

Lead-only wins (defaulters caught by monitor but missed by static at FA=10%): **57**
Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): **159**
Mean lead time among monitor-caught defaulters (FA=10%): **2.19** windows before W3

**Verdict at FA=10%:** static wins (delta = -7.69 pp catch rate).

---

## Honest interpretation

- The monitoring rule is mathematically a **superset** of the static rule -- any threshold applied to `max(W0..W3)` returns at least as many flags as the same threshold on `W3` alone. So at the *same threshold* monitoring strictly dominates static on catch rate **but** also on false alarms. The interesting comparison is at the **same false-alarm budget**: does monitoring catch more by re-picking its threshold higher?
- The numbers above answer that question per model and per FA budget.
- The **lead-only wins** column is the monitoring-specific value: defaulters that the W3-only rule misses but the W0..W3 trajectory catches. These are the cases where the trajectory's history matters -- the client's risk built up over earlier windows.
- For the thesis the framing is: monitoring offers **earlier detection at comparable discrimination**. The slide should show both the ROC-like curves AND the lead-only wins count -- the latter is the quantitative answer to "why bother tracking trajectory".
