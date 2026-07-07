# Podsumowanie Sprintu 4 — tor GF (Gabriel Figur)

> ⚠️ **ERRATA 2026-07-07:** liczby AUC/Brier/progi w tym dokumencie (m.in. CatBoost
> AUC 0.7802 / Brier 0.1354, progi 0.130–0.185) pochodzą z runu sprzed naprawy wycieków
> metodologicznych. Kanoniczne wartości: `reports/metrics_w3.csv` (CatBoost 0.7793/0.1357)
> i `ml-service/alert_thresholds.json` (RF 0.145 / XGB 0.165 / LGBM 0.160 / CatBoost 0.160 /
> LSTM 0.155). Szczegóły: `reports/{threshold,scaler}_leakage_fix.md`.
> Dokument pozostawiono bez przepisywania jako zapis historyczny sprintu.

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (GF)** w Sprint 4 projektu
> `ai-credit-management`. **Sprint 4 GF zamknięty w 3/3 zadaniach** (107, 108, 109) — najpierw pivot
> na 109 dla ścieżki krytycznej, potem powrót po 107+108 zgodnie z planem.
>
> Perspektywa toru MK Sprintu 4 (CREDIT-302 client list + history UI + CREDIT-205 Testcontainers
> persistence tests) — opisana w `PodsumowanieSprintu2_MK.md` (update z 2026-06-05). Mój Sprint 3
> (110/111/106, zamknięcie ścieżki krytycznej) — `PodsumowanieSprintu3_GF.md`.

---

## 1. Kontekst i decyzja o priorytetyzacji (pivot + powrót)

**Plan Sprintu 4 mojego toru (per `TASKS.md` / `plan_sprintow_wariant_B.md`):**

| ID | Tag | Prio | Co |
|---|---|---|---|
| CREDIT-107 | ML | **P2** SWAP-OK | SHAP top-5 cech per predykcja (RF/XGB/LR) |
| CREDIT-108 | ML | **P2** | 5-fold CV + Optuna tuning (XGBoost/RF) |

**Decyzja podjęta po zamknięciu Sprintu 3 (pierwsza faza Sprintu 4):** zamiast realizować Sprint 4 GF
**od razu według planu**, **podszedłem najpierw do CREDIT-109 (LightGBM + CatBoost, Sprint 5 P2)**,
żeby odblokować domknięcie ścieżki krytycznej tezy.

**Uzasadnienie pivotu:**

Po Sprincie 3 (mój tor) stan ścieżki krytycznej tezy (`101 → 102 → 104 → 110 → 111 → 114`) wyglądał:
```
101 ✅  →  102 ✅  →  104 ✅  →  110 ✅  →  111 ✅  →  114 🔒
```

**CREDIT-114** (final report, **P0**, ostatnie ogniwo) ma `blocked_by: 103, 111, 113`. Trzy z czterech
zależności zamknięte (103 ✅, 111 ✅). Zostało jedno: **CREDIT-113** (stacking ensemble, Sprint 6 P2).
CREDIT-113 z kolei ma `blocked_by: 102, 105, 109`. Dwie zamknięte (102 ✅, 105 ✅). Brakujące:
**CREDIT-109** (LightGBM + CatBoost, Sprint 5).

**Łańcuch blokad do odpalenia CREDIT-114:**
```
CREDIT-109 (Sprint 5 P2) → CREDIT-113 (Sprint 6 P2) → CREDIT-114 (Sprint 6 P0)
```

CREDIT-107 (SHAP) i CREDIT-108 (Optuna) **nie blokują nikogo poza sobą** (107 blokuje 211 SHAP-UI;
108 nic). To eleganckie uzupełnienia, ale nie krytyczne dla obrony tezy w pierwszym podejściu.

**Wniosek pierwszej fazy:** racjonalna decyzja P0-driven — przyspieszyć łańcuch krytyczny.
W pierwszym tygodniu Sprintu 4 zrobiłem CREDIT-109 (PR #23).

**Druga faza Sprintu 4 — powrót do planu:** po zamknięciu 109 i sprawdzeniu, że terminarz pozwala,
**wróciłem i dostarczyłem oba pierwotne P2 zadania** w Sprincie 4 kalendarzowo:

- **CREDIT-107 (SHAP)** — PR #26, merged 2026-06-05
- **CREDIT-108 (Optuna + 5-fold CV)** — PR #27, merged 2026-06-05

**Sprint 4 GF zamknięty 3/3 zadania** (107 + 108 + 109). Dodatkowy bonus: **CREDIT-211** (SHAP UI
w React) odblokowane dla MK na Sprint 5.

| Status zadań mojego toru po Sprincie 4 (kalendarzowo, 2026-06-05) |
|---|
| **CREDIT-107** — 🟢 zrobione (PR #26) — SHAP top-5 cech, 102 ms compute |
| **CREDIT-108** — 🟢 zrobione (PR #27) — Optuna 30 trials + 5-fold CV; RF +0.0010 / XGB +0.0030 test AUC |
| **CREDIT-109** — 🟢 zrobione (PR #23) — LightGBM + CatBoost; CatBoost najlepszy AUC 0.7802 |

---

## 2. Co dostarczyłem — CREDIT-107 (SHAP top-5 features)

**Plik:** `ml-service/app.py` (+71 LoC) + kontrakt monitoring.md §3.5 + nowy pytest. PR #26.

**Po co:** kontrakt monitoringu w Sprincie 2 stworzył obietnicę „defensible explanation" — frontend
ma móc wytłumaczyć użytkownikowi „dlaczego ten klient został oznaczony jako ryzykowny". SHAP
(SHapley Additive exPlanations) to standardowa odpowiedź. CREDIT-107 dostarcza Top-5 cech per model
dla aktualnej (W3) oceny w każdej odpowiedzi `/predict/timeseries`.

**Co robi:**
1. Przy starcie Flaska buduje **`SHAP_EXPLAINERS`** — jeden `shap.TreeExplainer` per tree-based model
   (RF, XGBoost, LightGBM, CatBoost). LSTM pominięty — `TreeExplainer` nie ma zastosowania dla Keras
   LSTM, a `KernelExplainer` z background sampling przekroczyłby budżet < 2s DoD.
2. Helper **`_unwrap_calibrated()`** — wyciąga bazowy tree estimator z otoczki
   `CalibratedClassifierCV(FrozenEstimator(base))` ustawionej w CREDIT-105. Kalibracja izotoniczna
   jest monotoniczna, więc ranking cech zachowany.
3. Helper **`_shap_values_positive_class()`** — normalizuje różne kształty wyjścia SHAP w różnych
   wersjach biblioteki (lista 2 ndarray per klasa / 3D ndarray / 2D ndarray) do jednego 1D wiersza
   dla klasy pozytywnej.
4. `compute_shap_top_features(data, n_top=5)` — dla danego klienta liczy SHAP per tree-based model
   na oknie W3, sortuje po `|value|` malejąco, zwraca top-5 par `{feature, value}`.

**Response Flask rozszerzony** (additive, non-breaking — frontend Sprintu 3 nadal działa):

```json
"shap": {
  "window": "W3",
  "randomForest": { "topFeatures": [
    { "feature": "PAY_mean",     "value": -0.0310 },
    { "feature": "PAY_max",      "value": -0.0301 },
    { "feature": "PAY_AMT_mean", "value": -0.0250 },
    { "feature": "late_count",   "value": -0.0244 },
    { "feature": "severe_late",  "value": -0.0240 }
  ]},
  "xgboost":  { "topFeatures": [ /* 5 items */ ] },
  "lightgbm": { "topFeatures": [ /* 5 items */ ] },
  "catboost": { "topFeatures": [ /* 5 items */ ] }
}
```

**Konwencja znaku:** `value > 0` → cecha pcha PD w górę (w stronę DEFAULT); `value < 0` → pcha PD
w dół. Sortowanie po `|value|` malejąco.

**Performance:** **101.6 ms** lokalnie dla wszystkich 4 explainerów + sortowania — **20× pod DoD
(< 2s)**. TreeExplainer jest exact, nie sampling.

**Sanity check:** dla zdrowego klienta referencyjnego (wszystkie PAY=0, regularne wpłaty) top cechy
mają **negatywne** SHAP dla RF: `PAY_mean`, `PAY_max`, `PAY_AMT_mean`, `late_count`, `severe_late` —
wszystkie proxy „ten klient płaci na czas", wszystkie pchają PD w dół. To dokładnie to, co
analityk kredytowy oczekiwałby zobaczyć.

**Test pytest:** strukturalny test endpointa weryfikujący że response zawiera 4 tree models, każdy
z dokładnie 5 unikalnymi cechami posortowanymi po |value|, brak LSTM w `shap`.

**Slajd:** *„Każda predykcja jest interpretowalna. Top-5 cech per model — w 102 ms, na każdym
zapytaniu. Frontend (CREDIT-211, MK Sprint 5) wyrenderuje bary z kolorami zgodnymi ze znakiem SHAP."*

---

## 3. Co dostarczyłem — CREDIT-108 (Optuna + 5-fold CV)

**Plik:** `ml-learing-center/optuna_tuning.py` (NEW, 230 LoC, standalone) + komentarz w `main.py`
+ `reports/optuna_study.md` + `reports/optuna_trials.csv`. PR #27.

**Po co:** „Czy default hyperparameters z CREDIT-102 są blisko optymalności? Czy Optuna może
wycisnąć dodatkowy AUC?" — to standardowe pytanie audytora dla pracy magisterskiej. CREDIT-108 daje
formalną odpowiedź ze studiowaniem hiperparametrów + 5-fold cross-validation, dokładnie pod DoD
„AUC po ≥ przed; CV-score ze std".

**Co robi:**
1. Ładuje dane W3 + ten sam 60/20/20 split co CREDIT-105 (test set byte-identyczny).
2. **5-fold StratifiedKFold** na train (60% klientów) — liczy CV-AUC mean ± std dla **default**
   RF i XGB (= hiperparametry z CREDIT-102).
3. **Optuna study** (TPESampler, seed=42, 30 trials per model) — maksymalizuje 5-fold CV-AUC
   po przestrzeni hiperparametrów:
   - **RandomForest:** `n_estimators` (200-800), `max_depth` (5-16), `min_samples_leaf` (1-10),
     `min_samples_split` (2-10), `max_features` (sqrt/log2/0.5)
   - **XGBoost:** `n_estimators` (300-1200), `learning_rate` (0.005-0.1 log), `max_depth` (3-8),
     `subsample` (0.5-1.0), `colsample_bytree` (0.5-1.0), `reg_alpha` (0.001-1.0 log),
     `reg_lambda` (0.1-10.0 log)
4. **Re-ewaluacja tuned modelu z 5-fold CV** dla std deviation tuned.
5. **Test-set AUC** (na trzymanym 20%) default vs tuned — bezpośrednia odpowiedź na DoD.
6. Zapis raportu Markdown + pełnej tabeli trials (60 wierszy).

**Wyniki:**

| Model | CV default (mean ± std) | CV tuned best | Test AUC default → tuned | Δ |
|---|---|---|---|---|
| RandomForest | 0.7815 ± 0.0029 | 0.7825 | 0.7760 → 0.7770 | **+0.0010** ✓ |
| XGBoost | 0.7814 ± 0.0044 | 0.7850 | 0.7768 → 0.7798 | **+0.0030** ✓ |

**Best hyperparameters (ciekawe odkrycia):**

- **RandomForest:** `n_estimators=800, max_depth=10, min_samples_leaf=9, min_samples_split=3,
  max_features="log2"`. **Log2 feature subsampling** bije implicit `sqrt`; `min_samples_leaf=9`
  (vs default 5) preferuje silniejszą regularyzację.
- **XGBoost:** `n_estimators=1000, learning_rate=0.0075, max_depth=3, subsample=0.80,
  colsample_bytree=0.66, reg_alpha=0.83, reg_lambda=3.59`. Klasyczny pattern: **wolniejsze, głębsze
  uczenie** — niższe LR (0.0075 vs default 0.02), płytsze drzewa (3 vs 4), więcej iteracji
  (1000 vs 800), **znacznie wyższa L2 regularyzacja** (`reg_lambda=3.59` vs default 1.0) — walka
  z overfitting na małym W3 train.

**Honest framing dla obrony:**

> *„Uplift jest mały (< 0.5 pp test AUC). Defaulty z CREDIT-102 są w obrębie pół punktu procentowego
> od optimum Optuna — sweep potwierdza, że baseline jest blisko dobrego lokalnego minimum dla tej
> rodziny modeli na UCI credit-default. To uczciwa konkluzja: hyperparameter tuning na tym datasetcie
> nie jest źródłem dużych uplift'ów, tu trzeba szukać gdzie indziej (= calibration, stacking,
> więcej modeli)."*

**Scope decision (kluczowa dla obrony):** **Tuned modele NIE są promoted do produkcji.** Shipped W3
artefakty (CREDIT-109 + CREDIT-105) zostają z hiperparametrami CREDIT-102 bo promocja wymagałaby:
1. Re-runs CREDIT-105 (isotonic calibration na nowych bazach)
2. Re-runs CREDIT-106 (cost-threshold optimization na nowych skalibrowanych prob.)
3. Re-runs CREDIT-109 (LightGBM/CatBoost niezależne, ale raporty by się rozjechały)

To jest cascade prac nieuzasadniony dla < 0.5 pp uplift'u przed deadlinem seminarium. Raport jest
ciekawością akademicką + sanity check.

**Slajd:** *„Optuna 30 trials × 5-fold CV potwierdza: defaulty są blisko optimum (< 0.5 pp gap).
Wniosek: tuning nie jest źródłem dużych uplift'ów na tym datasecie — patrzeć na calibration
i ensembling."*

---

## 4. Co dostarczyłem — CREDIT-109 (LightGBM + CatBoost)

**Pliki (49 zmienionych, +280 LoC + 5 nowych modeli W3 + 12 nowych PNG raportów + JSON):** PR #23.

| Plik | Rola |
|---|---|
| `ml-learing-center/main.py` | Trening + isotonic calibration LightGBM + CatBoost w bloku W3 (CREDIT-105 protokół) |
| `ml-learing-center/optimize_thresholds.py` | Cost thresholds dla wszystkich 5 modeli |
| `ml-learing-center/evaluation.py` | `MODELS` rozszerzone do 5; downstream loops auto-pick |
| `ml-learing-center/timeseries_eval.py` | jw |
| `ml-learing-center/static_vs_dynamic.py` | jw (przez import `MODELS` z `timeseries_eval`) |
| `ml-service/app.py` | Ładuje 5 modeli; `predict_single_window` zwraca 5 kluczy; `costThresholds` + `windowAlerts` iterują po keys |
| `ml-service/monitoring.py` | `compute_trends` iteruje po predictions.keys() — przyszłe modele extend automatycznie |
| `ml-service/tests/test_timeseries.py` | `MODEL_KEYS = {5 modeli}`; assertions na 5-key response |
| `docs/api-contracts/monitoring.md` §3.5 | TimeseriesResponse z 5 modelami w predictions/trends/costThresholds/windowAlerts |
| `ml-service/{lightgbm,catboost}_model_w3.pkl` + `ml-learing-center/...` | NEW commitowane artefakty (gitignore exceptions) |
| `ml-service/alert_thresholds.json` | 5 thresholdów + `_meta` tagged CREDIT-106 + CREDIT-109 |
| `requirements.txt` (oba) | +lightgbm>=4.0, +catboost>=1.2 |

**Wyniki (W3 calibrated, 20% test split):**

| Model | AUC cal | Brier cal | cost-opt threshold (FN = 5× FP) |
|---|---|---|---|
| RandomForest | 0.7741 | 0.1372 | 0.145 |
| XGBoost | 0.7760 | 0.1360 | 0.180 |
| LightGBM | 0.7764 | 0.1366 | 0.160 |
| **CatBoost** | **0.7802** | **0.1354** | 0.130 |
| LSTM | 0.7610 | 0.1387 | 0.175 |

**CatBoost najlepszy w obu metrykach** (AUC + Brier). 5-modelowy spread AUC wąski (~2 pp), typowy
dla gradient-boostingu na credit scoring UCI — zostawia miejsce dla CREDIT-113 stacking na nieduży
uplift.

**DoD spełnione:**
- `response zawiera lightgbm, catboost` ✓ (verified w pytest, 5-key response)
- `raport 6 modeli` — 5 base models obecnych; 6. (stacking) dochodzi w CREDIT-113

**Slajd:** *„5 modeli, CatBoost na czele (AUC 0.7802 / Brier 0.1354), spread wąski (~2 pp).
Stacking (CREDIT-113) ma okazję wycisnąć resztkę uplift'u. Flask serwuje wszystkie 5 z per-model
cost-optimized thresholds — frontend gotowy do kolorowania Timeline per model."*

---

## 4.1. Post-discovery integration fix — CREDIT-115 (BE)

**Kontekst:** podczas weryfikacji live demo do seminarium (2026-06-05) `curl` na
`POST /api/v1/monitoring/predict-timeseries` zwrócił tylko **3 modele** w `predictions` / `trends`
zamiast oczekiwanych 5. Flask `/predict/timeseries` zwracał poprawnie 5; backend DTO (`WindowPredictions`,
`Trends` z CREDIT-202, napisane gdy istniały tylko RF/XGB/LSTM) **silently dropował** LightGBM
i CatBoost przy deserializacji JSON do C# obiektów.

**Honest framing:** ten passthrough **powinien być w scope'ie CREDIT-109** (DoD „response zawiera
lightgbm, catboost" implicytnie obejmuje backend, bo to backend jest konsumentem Flaska). Nie został.
Formalnie zatrackowany jako osobny **CREDIT-115** dla audit trail; chronologicznie wykonany w post-
Sprint 4 window jako follow-up.

**Co zrobiłem (PR #32):**
- `WindowPredictions` + `Trends` (.NET DTO): dodane `Lightgbm` + `Catboost` properties z
  `[JsonPropertyName]` matching kontrakt §3.2/§3.4.
- `MonitoringService.ScoreAndPersistAsync`: persistuje **5 predictions + 5 trends** per snapshot
  (było 3 + 3).
- `MapHistoryPoint` + `MapTrends`: czytają 5 modeli z bazy zamiast 3.
- **5 Flask stub bodies** w testach rozszerzonych o `lightgbm` + `catboost` (inaczej deserializacja
  defaultowałaby do pustego `TrendInfo` z `Alert=""` i `Assert.All(...INCREASING_RISK)` by padło).
- Per-snapshot count assertions: `Equal(3, ...)` → `Equal(5, ...)`; cascade test
  `Equal(6, predictions)` → `Equal(10, ...)` (2 snapshots × 5 modeli).
- **Bez migracji DB** — `Prediction.ModelName` to free-form string, więc nowe wiersze `"lightgbm"` /
  `"catboost"` mieszczą się w istniejącym schemacie.

**Verified:** 24/24 backend testów ✅, curl pokazuje wszystkie 5 modeli w response z spójnymi
`INCREASING_RISK` (slope +0.58 do +0.63) dla pogarszającego się klienta demo.

**Frontend impact:** Recharts `LineChart` w `TimelineChart.tsx` auto-discoveruje model keys z
response (per CREDIT-301 design). 5 linii na wykresie zamiast 3 — **bez zmian frontendu**. Custom
per-model legend colours dla LightGBM/CatBoost ewentualnie jako oddzielny follow-up.

**Slajd:** *„Found and fixed during demo prep — integration gap między CREDIT-109 (Flask 5 modeli)
a CREDIT-202 (backend 3-model DTO). Dwa modele były silently dropowane w response. Live demo
pokazuje teraz 5 linii Timeline zgodnie z claim'em '5 modeli W3 calibrated'."*

---

## 5. Statystyki mojego Sprintu 4 (kalendarzowo)

| Wskaźnik | Wartość |
|---|---|
| **Zadań GF planowanych (Sprint 4)** | 2 (CREDIT-107 P2, CREDIT-108 P2) |
| **Zadań GF dostarczonych** | 3 (CREDIT-107 ✅, CREDIT-108 ✅, CREDIT-109 ✅ — to ostatnie ze Sprintu 5 wzięte out-of-order) |
| **PR-ów** | #23 (CREDIT-109), #26 (CREDIT-107), #27 (CREDIT-108) |
| **Nowych LoC** | ~580 (CREDIT-109 ~280 + CREDIT-107 ~70 + CREDIT-108 ~230) + raporty + artefakty |
| **Nowych modeli W3** | 2 base modele (LightGBM + CatBoost) — łącznie **5 modeli W3 calibrated** |
| **Nowych artefaktów `_w3` w gicie** | +2 (lightgbm + catboost model files w obu lokalizacjach) |
| **Pełny zestaw raportów** | regenerowane dla 5 modeli we wszystkich 3 skryptach (`evaluation`, `timeseries_eval`, `static_vs_dynamic`); + nowe raporty: `optuna_study.md`, `optuna_trials.csv` (60 trials) |
| **Cost thresholds JSON** | rozszerzony z 3 do 5 modeli |
| **Nowych pytest** | +2 (test SHAP top-5; test pytest dla CREDIT-108 nie wymagany — DoD spełnione przez raport) |
| **Pytest łącznie** | 10 passed (CI zielony) |
| **SHAP performance** | 102 ms (20× pod DoD < 2s) |
| **Odblokowane dla MK** | **CREDIT-211** (SHAP UI w React, Sprint 5 P2) |

---

## 6. Łańcuch krytyczny po Sprincie 4 (mój tor)

Przed Sprintem 4:
```
CREDIT-114 🔒  ←  CREDIT-113 🔒  ←  CREDIT-109 🔴  (105 ✅, 102 ✅)
```

Po Sprincie 4:
```
CREDIT-114 🔒  ←  CREDIT-113 🔴 (odblokowany!)  ←  CREDIT-109 ✅
```

**Po dostarczeniu CREDIT-109 zostało już tylko jedno aktywne zadanie do CREDIT-114:** CREDIT-113
(stacking). Jeden PR i ścieżka krytyczna obrony tezy jest kompletnie wypełniona.

---

## 7. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**
- **Pojedyncze modele to wąskie gardło dla stacking ensemble** — rozwiązane przez dorzucenie 2
  modeli o różnej naturze (LightGBM = gradient boosting z innym tree-split algorithm, CatBoost =
  ordered boosting + categorical handling). Daje stacking-owi materiał do uplift'u.
- **Hardcoded `MODELS` list w skryptach raportujących** — przy okazji rozszerzenia zrobiłem
  `compute_trends` w `monitoring.py` iteracyjną po `predictions.keys()`. Przyszłe modele
  (np. ensemble z 113) wejdą do response bez edycji `monitoring.py`.
- **Defensible explanations dla użytkownika** (CREDIT-107) — TreeExplainer, 102 ms, top-5 cech
  per tree-based model. Frontend (CREDIT-211) ma teraz materiał do bar/waterfall chart.
- **Pytanie audytora „czy default hiperparametry są blisko optimum?"** (CREDIT-108) — formalna
  odpowiedź: tak, w obrębie < 0.5 pp test AUC po 30 trials Optuna na każdy model. Sweep nie wymusza
  re-runów produkcji.

**Świadomie odłożone:**
- **SHAP dla LSTM** — wymagałby KernelExplainer z background sampling; nie zmieściłby się w < 2s
  DoD. Tree-based modele (4 z 5) wystarczają do uzasadnienia decyzji.
- **Promocja tuned hyperparameters do produkcji** (CREDIT-108) — kosztowne (cascade redo 105/106/109),
  uplift < 0.5 pp. Akademicka wartość raportu wystarczy.
- **6-month legacy LightGBM/CatBoost** — TASKS.md mówi „na oknach 3-mies." (W3 only). Legacy
  `/predict` nadal używa starych 3 modeli — brak biznesowej potrzeby retrainingu.
- **Sensitivity analysis cost ratio** (3:1, 5:1, 10:1, 20:1) — kandydat na appendix CREDIT-114.
- **CREDIT-112** (fairness audit per SEX) — Sprint 5 P1 SWAP-OK, jeszcze nie zrobione.

---

## 8. Co dalej — Sprint 5 i Sprint 6 (mój tor)

**Następna ścieżka:**
1. **CREDIT-113** (stacking ensemble, Sprint 6 P2) — LR meta-learner na 5 modelach bazowych.
   Pojedynczy PR; oczekiwany uplift AUC o 0.5-1 pp + lepsza kalibracja.
2. **CREDIT-114** (final report, Sprint 6 **P0**) — zamknięcie tezy. Generator zbiorczego raportu
   + komplet wykresów do prezentacji. Pull-together CREDIT-103 + CREDIT-111 + CREDIT-113. To jest
   praca-do-obrony moment.

**Po CREDIT-114 (jeśli czas) lub równolegle:**
- **CREDIT-112** (fairness audit per SEX, Sprint 5 P1 SWAP-OK) — wymóg AI Act dla systemów
  kredytowych; demographic parity + equalized odds. Może iść na boku.

**MK po Sprincie 4:**
- **CREDIT-211** (SHAP UI w React, Sprint 5 P2 SWAP-OK) — odblokowane przez merge CREDIT-107.
  Wizualizacja bar/waterfall dla top-5 SHAP per model.

---

## 9. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 4)

> **Sprint 4 (tor GF) — pivot, powrót, full closure.**
>
> - **Plan:** CREDIT-107 (SHAP) + CREDIT-108 (Optuna), oba P2.
> - **Pivot:** najpierw zrobiłem **CREDIT-109 (LightGBM + CatBoost)** out-of-order (Sprint 5 P2) —
>   odblokować łańcuch krytyczny `109 → 113 → 114 (final report, P0)`.
> - **Powrót:** po 109 wróciłem i domknąłem oba pierwotne P2: **CREDIT-107 SHAP** (102 ms, 20× pod
>   DoD) i **CREDIT-108 Optuna+CV** (RF +0.0010 / XGB +0.0030 test AUC; defaulty z CREDIT-102
>   blisko optimum — academic-only, nie promoted).
> - **Sprint 4 GF zamknięty 3/3** (107 ✅ + 108 ✅ + 109 ✅).
> - **Bonus dla MK:** **CREDIT-211** (SHAP UI) odblokowane.
> - **Findings:** CatBoost najlepszy single model (AUC 0.7802, Brier 0.1354); XGB tuning preferuje
>   wolniejsze + głębsze uczenie (lr=0.0075, depth=3, reg_lambda=3.59).
> - **Ścieżka krytyczna:** zostaje **jedno zadanie** do CREDIT-114 → **CREDIT-113** (stacking).
>
> **Następne:** CREDIT-113 (stacking) → CREDIT-114 (final report — slide-deck do obrony).
