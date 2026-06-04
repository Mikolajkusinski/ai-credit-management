# Podsumowanie Sprintu 4 — tor GF (Gabriel Figur)

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (GF)** w Sprint 4 projektu
> `ai-credit-management`. **Krótki dokument** — Sprint 4 dla GF był celowo odchudzony na rzecz
> priorytetyzacji ścieżki krytycznej tezy.
>
> Perspektywa toru MK Sprintu 4 (CREDIT-302 client list + history UI + CREDIT-205 Testcontainers
> persistence tests) — opisana w `PodsumowanieSprintu2_MK.md` (update z 2026-06-05). Mój Sprint 3
> (110/111/106, zamknięcie ścieżki krytycznej) — `PodsumowanieSprintu3_GF.md`.

---

## 1. Kontekst i decyzja o priorytetyzacji

**Plan Sprintu 4 mojego toru (per `TASKS.md` / `plan_sprintow_wariant_B.md`):**

| ID | Tag | Prio | Co |
|---|---|---|---|
| CREDIT-107 | ML | **P2** SWAP-OK | SHAP top-5 cech per predykcja (RF/XGB/LR) |
| CREDIT-108 | ML | **P2** | 5-fold CV + Optuna tuning (XGBoost/RF) |

**Decyzja podjęta po zamknięciu Sprintu 3:** zamiast realizować Sprint 4 GF według planu,
**zamieniłem oba P2 tasks na CREDIT-109 (LightGBM + CatBoost, Sprint 5 P2)**, żeby odblokować
domknięcie ścieżki krytycznej tezy.

**Uzasadnienie:**

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
108 nic). To eleganckie uzupełnienia, ale nie krytyczne dla obrony tezy.

**Wniosek:** racjonalna decyzja P0-driven — przyspieszyć łańcuch krytyczny kosztem dwóch P2
nice-to-haves. Ramy czasowe Sprintu 4 (14-27 lip) wykorzystałem na CREDIT-109; CREDIT-107/108
zostają w backlogu jako opcjonalne uzupełnienia po CREDIT-114, jeśli zostanie czas.

| Status zadań mojego toru po Sprincie 4 (kalendarzowo) |
|---|
| CREDIT-107 — 🔴 odłożone (P2 SWAP-OK; nie blokuje krytycznej ścieżki) |
| CREDIT-108 — 🔴 odłożone (P2; nie blokuje nikogo) |
| **CREDIT-109** — 🟢 zrobione w Sprincie 4 kalendarzowo (PR #23, merged 2026-06-05) |

---

## 2. Co dostarczyłem — CREDIT-109 (LightGBM + CatBoost)

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

## 3. Statystyki mojego Sprintu 4 (kalendarzowo)

| Wskaźnik | Wartość |
|---|---|
| **Zadań GF planowanych (Sprint 4)** | 2 (CREDIT-107 P2, CREDIT-108 P2) |
| **Zadań GF dostarczonych** | 1 (CREDIT-109, technicznie Sprint 5 P2, ale wykonany w oknie Sprintu 4) |
| **PR-ów** | #23 |
| **Nowych LoC** | +280 (kod) + 49 plików zmienionych (z artefaktami i raportami) |
| **Nowych modeli** | 2 (LightGBM, CatBoost) — łącznie 5 modeli W3 |
| **Nowych artefaktów `_w3` w gicie** | +2 (lightgbm + catboost model files w obu lokalizacjach) |
| **Pełny zestaw raportów** | regenerowane dla 5 modeli we wszystkich 3 skryptach (`evaluation`, `timeseries_eval`, `static_vs_dynamic`) |
| **Cost thresholds JSON** | rozszerzony z 3 do 5 modeli |
| **Pytest** | 9 passed (CI zielony, ML pytest ~1 min 12 s — pip cache miss przez nowe libki) |

---

## 4. Łańcuch krytyczny po Sprincie 4 (mój tor)

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

## 5. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**
- **Pojedyncze modele to wąskie gardło dla stacking ensemble** — rozwiązane przez dorzucenie 2
  modeli o różnej naturze (LightGBM = gradient boosting z innym tree-split algorithm, CatBoost =
  ordered boosting + categorical handling). Daje stacking-owi materiał do uplift'u.
- **Hardcoded `MODELS` list w skryptach raportujących** — przy okazji rozszerzenia zrobiłem
  `compute_trends` w `monitoring.py` iteracyjną po `predictions.keys()`. Przyszłe modele
  (np. ensemble z 113) wejdą do response bez edycji `monitoring.py`.

**Świadomie odłożone:**
- **CREDIT-107 (SHAP)** — defensible explanation per predykcji to nice-to-have dla obrony, ale nie
  blokuje tezy. Wartościowy jako dodatek slidów po CREDIT-114.
- **CREDIT-108 (Optuna + 5-fold CV)** — hyperparameter tuning może podnieść AUC o 1-2 pp, ale nie
  zmienia framingu tezy. Jeśli będzie czas — można dodać przed obroną.
- **6-month legacy LightGBM/CatBoost** — TASKS.md mówi „na oknach 3-mies." (W3 only). Legacy
  `/predict` nadal używa starych 3 modeli — brak biznesowej potrzeby retrainingu.
- **Sensitivity analysis cost ratio** (3:1, 5:1, 10:1, 20:1) — kandydat na appendix CREDIT-114.

---

## 6. Co dalej — Sprint 5 i Sprint 6 (mój tor)

**Następna ścieżka:**
1. **CREDIT-113** (stacking ensemble, Sprint 6 P2) — LR meta-learner na 5 modelach bazowych.
   Pojedynczy PR; oczekiwany uplift AUC o 0.5-1 pp + lepsza kalibracja.
2. **CREDIT-114** (final report, Sprint 6 **P0**) — zamknięcie tezy. Generator zbiorczego raportu
   + komplet wykresów do prezentacji. Pull-together CREDIT-103 + CREDIT-111 + CREDIT-113. To jest
   praca-do-obrony moment.

**Po CREDIT-114 (jeśli czas):**
- **CREDIT-107** (SHAP top-5 cech) — Sprint 4 P2 SWAP-OK, odłożone
- **CREDIT-108** (Optuna + CV) — Sprint 4 P2, odłożone
- **CREDIT-112** (fairness audit per SEX) — Sprint 5 P1 SWAP-OK, odłożone

Wszystkie trzy są P1/P2 i mogą wejść do appendixu pracy/slidów.

---

## 7. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 4)

> **Sprint 4 (tor GF) — pivot na ścieżkę krytyczną.**
>
> - **Plan:** CREDIT-107 (SHAP) + CREDIT-108 (Optuna), oba P2.
> - **Faktycznie:** zamiast P2 nice-to-haves zrobiłem **CREDIT-109 (LightGBM + CatBoost)** —
>   technicznie Sprint 5 P2, ale w łańcuchu blokad do CREDIT-114 (final report, P0).
> - **Wynik:** 5 modeli W3 z calibration + cost thresholds; **CatBoost** najlepszy (AUC 0.7802,
>   Brier 0.1354). Flask response 5-key, `compute_trends` iteracyjne po keys.
> - **Łańcuch krytyczny:** po Sprincie 4 zostaje tylko **jedno** zadanie do CREDIT-114 →
>   **CREDIT-113** (stacking ensemble).
> - **Świadomy trade-off:** CREDIT-107/108 (SHAP, Optuna) w backlogu jako opcjonalne uzupełnienia
>   po CREDIT-114.
>
> **Następne:** CREDIT-113 (stacking) → CREDIT-114 (final report — slide-deck do obrony).
