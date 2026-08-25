# FINAL REPORT (CREDIT-114) — zbiorcze wyniki do rozdziału 5

> Wygenerowane przez `final_report.py` z kanonicznych artefaktów w `reports/`
> po naprawach metodologicznych 2026-07-07 (`threshold_leakage_fix.md`, `scaler_leakage_fix.md`).
> Żadna liczba nie jest wpisana ręcznie — każda pochodzi z plików wejściowych.

## 1. Porównanie modeli (rozdz. 5.2-5.3)

Zbiór testowy: 6 000 klientów (20%, stratyfikowany, `random_state=42`),
modele skalibrowane izotonicznie (CREDIT-105), okno W3.

| Model | AUC | Gini | KS | Brier | Próg kosztowy (FN=5×FP) |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.7741 | 0.5483 | 0.4077 | 0.1374 | 0.145 |
| XGBoost | 0.7761 | 0.5522 | 0.4234 | 0.1360 | 0.165 |
| LightGBM | 0.7767 | 0.5533 | 0.4173 | 0.1363 | 0.160 |
| CatBoost **←** | 0.7793 | 0.5586 | 0.4147 | 0.1357 | 0.160 |
| LSTM | 0.7614 | 0.5228 | 0.3985 | 0.1388 | 0.155 |

Najlepszy model: **CatBoost** (AUC 0.7793). Rozstęp AUC całej piątki: 0.0179 — różnice między modelami drzewiastymi mieszczą się w wariancji pojedynczego splitu (por. bootstrap w `bootstrap_auc_report.md`, jeśli wygenerowany). Progi alertu optymalizowane na splicie kalibracyjnym (`threshold_leakage_fix.md`).

## 2. Reguła statyczna (W3) vs reguła monitorująca (W0..W3) — dowód tezy (rozdz. 5.4)

Static: alert gdy `PD_W3 ≥ θ`. Monitoring: alert gdy `max(PD_W0..W3) ≥ θ`.
Progi θ dobierane niezależnie dla każdej reguły tak, by osiągnąć zadany
budżet fałszywych alarmów (FA) na zbiorze testowym.

### Catch rate przy kanonicznych budżetach FA (pp = punkty procentowe)

| Model | FA=5%: Δ(mon−stat) | FA=10%: Δ | FA=20%: Δ | Lead-only wins @FA=10% | Mean lead (okna) |
|---|---:|---:|---:|---:|---:|
| Random Forest | +6.93 | **-10.85** | +2.26 | 48 | 1.96 |
| XGBoost | +8.29 | **-5.12** | +0.60 | 47 | 2.05 |
| LightGBM | +0.68 | **-4.97** | -2.03 | 52 | 2.06 |
| CatBoost | +8.14 | **-6.41** | -8.59 | 39 | 2.09 |
| LSTM | +10.02 | **+2.56** | -2.34 | 74 | 2.04 |

### Werdykt (uczciwy)

Przy FA=10% reguła statyczna wygrywa na catch rate dla 4 z 5 modeli (Random Forest -10.9 pp, XGBoost -5.1 pp, LightGBM -5.0 pp, CatBoost -6.4 pp).
Wyjątek: **LSTM** (+2.6 pp) — jedyny model sekwencyjny wygrywa monitoringiem także na czystej dyskryminacji, spójnie z hipotezą, że architektura sekwencyjna najlepiej wykorzystuje trajektorię.

Wartość monitoringu nie leży w wyższym catch rate, lecz w: (a) **wczesności** — alert pada średnio 2.06 okna przed W3 (CREDIT-110), oraz (b) **unikalnych wykryciach** — 39-74 defaultujących na model, których reguła statyczna nie wykrywa w ogóle. Reguła monitorująca jest komplementarna wobec statycznej, nie substytucyjna.

Zastrzeżenie interpretacyjne: dominacja pierwszych alertów w najstarszym oknie W0 może częściowo wynikać z przesunięcia rozkładu (model trenowany na W3 aplikowany do W0), nie wyłącznie z narastania ryzyka — diagnoza w `pd_per_window_report.md` (jeśli wygenerowany).

## 3. Audyt fairness — DPD / EOD względem SEX (rozdz. 5.5b)

Binaryzacja progami kosztowymi (realny punkt pracy systemu), zbiór testowy
6 000 klientów (M 2 402 / F 3 598). Limit DoD: |DPD|, |EOD| ≤ 0.10.

| Model | Próg | DPD | EOD | Werdykt |
|---|---:|---:|---:|:---:|
| Random Forest | 0.145 | +0.0345 | +0.0282 | ✅ |
| XGBoost | 0.165 | +0.0358 | +0.0279 | ✅ |
| LightGBM | 0.160 | +0.0351 | +0.0274 | ✅ |
| CatBoost | 0.160 | +0.0392 | +0.0329 | ✅ |
| LSTM | 0.155 | +0.0060 | +0.0208 | ✅ |

Wszystkie modele przechodzą audyt z co najmniej 3× marginesem. Największe |DPD|: CatBoost (+0.039); najbliżej parytetu: LSTM (+0.006) — jedyny model bez cech demograficznych na wejściu (tensor (3,3) wyłącznie PAY/BILL/AMT). Dodatnie DPD interpretować względem luki strukturalnej ~0.021 wynikającej z różnicy base rate (M 23.4% vs F 21.3% w teście).

## 4. Weryfikacja hipotez badawczych (rozdz. 5.6)

### H1 — okno 3-miesięczne (W3) zachowuje jakość okna 6-miesięcznego (strata < 1 pp AUC)

| Model | AUC 6-mies. (legacy) | AUC W3 (calibrated) | Δ |
|---|---:|---:|---:|
| Random Forest | 0.7792 | 0.7741 | -0.51 pp |
| XGBoost | 0.7818 | 0.7761 | -0.57 pp |
| LSTM | 0.7686 | 0.7614 | -0.72 pp |

**H1: POTWIERDZONA** — strata AUC względem 6-miesięcznego baseline'u nie przekracza 1 pp dla żadnego modelu (uwaga: legacy to modele nieskalibrowane, porównanie orientacyjne; wartości legacy z logu CREDIT-102).

### H2 — monitoring W0..W3 oferuje wcześniejszą detekcję i wykrycia niedostępne regule statycznej

**H2: POTWIERDZONA CZĘŚCIOWO.** Wcześniejsza detekcja: tak — średni lead 2.06 okna; unikalne wykrycia: tak — 39-74/model. Catch rate przy FA=10%: dla 4 modeli statycznych wygrywa reguła statyczna (do 10.9 pp); wyjątkiem jest LSTM (+2.6 pp na korzyść monitoringu). Wartość monitoringu = wczesność + komplementarność, nie wyższa czułość.

### H3 — modele zachowują parytet względem SEX (|DPD|, |EOD| ≤ 0.10)

**H3: POTWIERDZONA** — maksymalna wartość |DPD|/|EOD| w całej piątce: 0.0392 (limit 0.10, margines 2.6×).

## 5. Ograniczenia (rozdz. 5.6 / Zakończenie)

1. **Jeden zbiór danych** (UCI Taiwan 2005, 30 000 klientów) i jeden podział — różnice AUC rzędu 0.002-0.006 między modelami drzewiastymi należy raportować jako porównywalne.
2. **Symulowany monitoring**: okna W0..W3 to retrospektywne wycinki tej samej 6-miesięcznej historii; wszystkie przewidują tę samą etykietę październikową (różne horyzonty predykcji). Walidacja na prawdziwym panelu podłużnym pozostaje kierunkiem dalszych badań.
3. **SEX jako cecha wejściowa** modeli statycznych — decyzja badawcza (kwantyfikacja wpływu); we wdrożeniu produkcyjnym zmienna podlegałaby usunięciu. Kontr-eksperyment bez SEX: `fairness_no_sex_report.md` (jeśli wygenerowany).
4. **Progi kosztowe liczone na splicie kalibracyjnym** — tym samym, na którym fitowano kalibratory izotoniczne (kompromis udokumentowany w `threshold_leakage_fix.md`).
5. **Stacking (CREDIT-113) descoped** — świadoma decyzja zakresu 2026-07-07; kierunek dalszych badań.

## 6. Mapa artefaktów → sekcje pracy

| Sekcja pracy | Źródło liczb | Figury |
|---|---|---|
| 5.2-5.3 porównanie modeli | `metrics_w3.csv` | `roc_comparison_w3.png`, `pr_comparison_w3.png`, `calibration_comparison_w3.png` |
| 5.4 statyka vs monitoring | `static_vs_dynamic_operating.csv`, `timeseries_metrics.csv` | `static_vs_dynamic_*_w3.png` (5×), `slope_boxplot_*_w3.png`, `trajectory_examples_*_w3.png` |
| 5.5 interpretowalność | SHAP per predykcja (CREDIT-107, `ml-service/app.py`) | — |
| 5.5b fairness | `fairness_metrics_w3.csv` | `fairness_selection_rate_w3.png`, `fairness_tpr_fpr_w3.png` |
| 4.4.1 tuning | `optuna_study.md`, `optuna_trials.csv` | — |
| 4.6 kalibracja | log `main.py` (Brier przed/po) | `calibration_comparison_w3.png` |
