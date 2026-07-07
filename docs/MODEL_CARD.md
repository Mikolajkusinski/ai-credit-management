# Model Card — W3 Credit Default Monitoring Models

> Wzorowana na szablonie Model Cards for Model Reporting (Mitchell et al., 2019).
> Liczby pochodzą z kanonicznych artefaktów `ml-learing-center/reports/` (stan po
> naprawach metodologicznych 2026-07-07; `FINAL_REPORT.md` agreguje całość).

## Przegląd

| | |
|---|---|
| **Zadanie** | Klasyfikacja binarna: prawdopodobieństwo niewykonania zobowiązania (PD) w następnym miesiącu |
| **Modele** | Random Forest, XGBoost, LightGBM, CatBoost (statyczne, 32 cechy) + LSTM (sekwencyjny, tensor 3×3) |
| **Zastosowanie** | **Wczesne ostrzeganie / monitoring** — alert kieruje ekspozycję do przeglądu analityka; NIE jest to zautomatyzowany silnik decyzji kredytowych (człowiek w pętli, por. art. 22 RODO) |
| **Wersja** | W3 calibrated, retrain 2026-07-07 |
| **Autorzy** | Gabriel Figur, Mikołaj Kusiński (praca magisterska) |

## Dane

- **Źródło:** UCI "Default of Credit Card Clients" (Tajwan, 2005) — 30 000 klientów,
  6 miesięcy historii (kwiecień–wrzesień), etykieta: default w październiku (22.1%).
- **Panel przesuwny:** z 6 miesięcy budowane są 4 nakładające się okna 3-miesięczne
  (W0..W3). Trening wyłącznie na W3 (lipiec–wrzesień, wyrównane z etykietą);
  inferencja na wszystkich czterech → trajektoria PD. Żadna wartość nie jest
  fabrykowana — każde okno to realny wycinek historii.
- **Podział:** 60% trening / 20% kalibracja / 20% test (stratyfikowany,
  `random_state=42`). Skalery fitowane wyłącznie na treningu; progi alertu
  na splicie kalibracyjnym; test nietknięty do finalnej ewaluacji.
- **Cechy:** 13 pochodnych (PAY_mean/max, BILL_mean/std/trend, utilization_rate,
  payment_ratio, late_count, severe_late, recent_pay_status…) + 9 surowych kolumn
  okna + demografia (one-hot ze stałymi domenami kategorii). LSTM: wyłącznie
  surowa sekwencja PAY/BILL/AMT — bez cech demograficznych.

## Trening i kalibracja

- Hiperparametry: heurystyczne (CREDIT-102), zweryfikowane post-hoc Optuną
  (5-fold CV, 30 prób/model; uplift < 0.5 pp — `optuna_study.md`).
- Ważenie klas (`class_weight="balanced"` / `scale_pos_weight` / `auto_class_weights`)
  poprawia ranking przy niezbalansowaniu 78/22; deformację skali PD koryguje
  **kalibracja izotoniczna** na osobnym splicie (`CalibratedClassifierCV(FrozenEstimator)`;
  LSTM: zewnętrzny `IsotonicRegression`). Brier po kalibracji lepszy o 19–25%.
- LSTM W3: `set_random_seed(42)` — retrain odtwarzalny.

## Metryki (zbiór testowy: 6 000 klientów, 1 327 defaultów)

| Model | AUC | Gini | KS | Brier | Próg alertu (FN=5×FP) |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.7741 | 0.548 | 0.408 | 0.1374 | 0.145 |
| XGBoost | 0.7761 | 0.552 | 0.423 | 0.1360 | 0.165 |
| LightGBM | 0.7767 | 0.553 | 0.417 | 0.1363 | 0.160 |
| **CatBoost** | **0.7793** | 0.559 | 0.415 | **0.1357** | 0.160 |
| LSTM | 0.7614 | 0.523 | 0.399 | 0.1388 | 0.155 |

Monitoring (reguła `max(PD_W0..W3) ≥ θ`) vs statyka (`PD_W3 ≥ θ`) przy FA=10%:
statyka wygrywa na catch rate dla 4 modeli statycznych (−5.0…−10.9 pp), **LSTM
wygrywa monitoringiem (+2.6 pp)**; monitoring daje średnio ~2 okna lead time
i 39–74 unikalnych wykryć/model (`FINAL_REPORT.md` §2).

## Fairness (fairlearn, atrybut chroniony: SEX; progi kosztowe)

| Model | DPD | EOD | Limit |
|---|---:|---:|---|
| Random Forest | +0.035 | +0.028 | 0.10 ✅ |
| XGBoost | +0.036 | +0.028 | 0.10 ✅ |
| LightGBM | +0.035 | +0.027 | 0.10 ✅ |
| CatBoost | +0.039 | +0.033 | 0.10 ✅ |
| LSTM | +0.006 | +0.021 | 0.10 ✅ |

Dodatnie DPD interpretować względem luki strukturalnej ~0.021 (base rate defaultu:
M 23.4% vs F 21.3% w teście). LSTM — jedyny model bez wejść demograficznych —
jest najbliżej parytetu (naturalny dowód ablacyjny). Mechanizm mitygacji
warunkowej (ThresholdOptimizer, equalized odds) opisany w `Fable5_Task2.md` §4.

## Ograniczenia i właściwe użycie

1. **Jeden zbiór, jedna geografia, rok 2005** — generalizacja na inne portfele
   niezweryfikowana; przed użyciem na innych danych wymagany pełny re-trening
   i re-audyt.
2. **Symulowany monitoring:** okna W0..W3 to retrospektywne wycinki tej samej
   historii; wszystkie przewidują tę samą etykietę (różne horyzonty predykcji).
3. **SEX jest cechą wejściową modeli statycznych** — decyzja badawcza
   (kwantyfikacja wpływu); w wdrożeniu produkcyjnym zmienną należy usunąć.
4. **Nie używać jako samodzielnego silnika decyzji kredytowych** — system jest
   narzędziem wczesnego ostrzegania z przeglądem ludzkim; AI Act klasyfikuje
   scoring kredytowy jako zastosowanie wysokiego ryzyka.
5. Legacy endpoint `/predict` (6-mies., bez kalibracji, próg 0.5) to baseline
   historyczny — nie mieszać z wynikami W3.

## Artefakty

`ml-service/`: `{rf,xgb,lightgbm,catboost}_model_w3.pkl`, `lstm_model_w3.keras`,
`scaler_w3.pkl`, `features_w3.pkl`, `lstm_scalers_w3.pkl`, `lstm_calibrator_w3.pkl`,
`alert_thresholds.json`. Reprodukcja: `ml-learing-center/main.py` (jeden run).
