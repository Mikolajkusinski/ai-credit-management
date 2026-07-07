# Podsumowanie Sprintu 3 — tor GF (Gabriel Figur)

> ⚠️ **ERRATA 2026-07-07:** liczby w tym dokumencie (progi 0.145/0.180/0.185, delty
> static-vs-dynamic „−2 do −6 pp", „43-184 unikalnych catchy") pochodzą z runu sprzed
> naprawy wycieków metodologicznych (progi liczone na teście, skalery przed splitem)
> i sprzed rozszerzenia do 5 modeli. **Kanoniczne wartości:** `reports/metrics_w3.csv`,
> `ml-service/alert_thresholds.json` (RF 0.145 / XGB 0.165 / LGBM 0.160 / CatBoost 0.160 /
> LSTM 0.155), `reports/static_vs_dynamic_report.md` (straty 5–11 pp dla 4 modeli,
> **LSTM +2.6 pp — jedyny wygrywający monitoringiem**, 39–74 unikalnych catchy).
> Szczegóły: `reports/threshold_leakage_fix.md` + `reports/scaler_leakage_fix.md`.
> Dokument pozostawiono bez przepisywania jako zapis historyczny sprintu.

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (GF)** w Sprint 3 projektu
> `ai-credit-management`: metryki time-series, dowód tezy „statyka vs monitoring" i progi alertu
> oparte o model kosztów.
>
> Perspektywa toru MK Sprintu 3 (CREDIT-204 GET history + CREDIT-301 Timeline view) — opisana
> w `PodsumowanieSprintu2_MK.md` (update z 2026-06-05). Sprint 1 (oba tory) — patrz
> `PodsumowanieSprintu1.md`.

---

## 1. Kontekst i mój zakres

**Teza Wariantu B — monitoring kalendarzowy:** ten sam klient jest oceniany wielokrotnie w czasie;
system śledzi trajektorię prawdopodobieństwa default (PD) i wykrywa pogorszenie zanim do niego
dojdzie. Sprint 2 dał silnik scoringu trajektorii (Flask `/predict/timeseries`) i kalibrację
izotoniczną. **Sprint 3 to dowód tezy — uczciwe porównanie statyki i monitoringu** plus uzbrojenie
alertu w model kosztów.

Mój tor (GF) w Sprincie 3:

| ID | Tag | Co | Status |
|---|---|---|---|
| **CREDIT-110** | EVAL | Metryki time-series: lead time + slope distribution + AUC trajektorii | 🟢 merged (PR #20) |
| **CREDIT-111** | EVAL | **Dowód tezy** — statyka (W3) vs monitoring (any W0..W3) | 🟢 merged (PR #21) |
| **CREDIT-106** | ML  | Cost-optimized alert thresholds (FN > FP) | 🟢 merged (PR #22) |

**Ścieżka krytyczna tezy** (`101 → 102 → 104 → 110 → 111 → 114`) miała przed Sprintem 3 zamknięte 3
ogniwa (101/102/104). Sprint 3 mojego toru zamknął **dwa kolejne** (110, 111) — zostało już tylko
**CREDIT-114** (raport końcowy, Sprint 6), które dodatkowo czeka na 103 (zrobione) i 113 (P2,
Sprint 6).

**Harmonogram:** Sprint 3 planowany 30 cze – 13 lip 2026; mój tor dostarczony do 2026-06-04 (przed
planem, jak Sprinty 1 i 2).

---

## 2. Co dostarczyłem — szczegóły per zadanie

### CREDIT-110 (EVAL, GF) — Metryki time-series

**Plik:** `ml-learing-center/timeseries_eval.py` (230 LoC, standalone). PR #20.

**Po co:** żeby uczciwie porównać statykę z monitoringiem w CREDIT-111, najpierw musimy zmierzyć
**monitoring-specific signals**, których CREDIT-103 (single-snapshot metryki) nie liczy: czy alert
trajektorii faktycznie wykrywa default *wcześniej* niż W3-only ocena, jak rozkłada się slope per
klasa, i czy sam slope ma wartość predykcyjną.

**Co robi:** dla każdego klienta z 20% test split (ten sam co CREDIT-105 kalibracja, `random_state=42`)
scoruje wszystkie 4 okna W0..W3 dla 3 modeli (RF/XGB/LSTM, skalibrowane), zwraca 4-punktową
trajektorię PD per model. Następnie liczy:
- **Lead time** — dla defaulterów: najwcześniejsze okno, gdzie PD ≥ próg alertu (0.5), zwrócone
  jako „windows before W3" (3 = caught at W0, 0 = caught at W3, −1 = not caught).
- **Slope distribution** — `slope = PD_W3 − PD_W0` per klient, split per klasa (default/non-default).
- **Slope AUC** — czy sam slope jest predyktorem klasy defaultu (boundary check, monitoring's
  value-add measure).

**Wyniki (alert threshold = 0.5, 1327 defaulterów w teście):**

| Model | catch_rate | mean_lead_windows | slope_auc | w3_auc |
|---|---|---|---|---|
| RandomForest | 49.8% | 2.05 | 0.588 | 0.774 |
| XGBoost | 50.6% | 2.05 | 0.590 | 0.776 |
| LSTM | 51.5% | 2.06 | 0.596 | 0.760 |

**Interpretacja:**
- **~50% catch rate** — połowa defaulterów triggeruje alert w jakimś oknie; reszta zostaje pod
  progiem 0.5 cały czas. CREDIT-106 (cost-based) obniży próg i pokaże trade-off.
- **Mean lead ~2.05 okna** — gdy alert się odpali, średnio 2 okna PRZED W3. To dosłownie „2
  miesiące wcześniej niż jednorazowa ocena".
- **Lead distribution** (RF przykład): caught at W3=108 | W2=100 | W1=101 | W0=352. Czyli ~30%
  złapanych defaulterów **wykrytych pierwszy raz w W1/W2** (po W0, przed W3) — to są przypadki
  „dorobione" przez monitoring, których statyka by przegapiła.
- **Slope_auc ~0.59 vs w3_auc ~0.77** — sam slope to słaby predyktor sam w sobie; trajektoria jako
  bytność, nie slope-jako-feature. Framing dla CREDIT-111: monitoring nie wnosi lepszego pojedynczego
  PD, wnosi **wcześniejszą detekcję** poprzez wyłapanie ruchu (movement) ryzyka.

**Output (6 PNG + 1 CSV + 1 Markdown):**
- `reports/timeseries_metrics.csv` (3 wiersze × 6 kolumn)
- `reports/lead_time_report.md` (per-model prose)
- `reports/slope_boxplot_{rf,xgb,lstm}_w3.png` (rozkład slope per klasa)
- `reports/trajectory_examples_{rf,xgb,lstm}_w3.png` (25 losowych defaulterów vs 25 non-defaulterów)

**Slajd:** *„Średnio 2 okna lead time — monitoring łapie defaulterów ~2 miesiące przed pojedynczą
oceną W3, ale tylko gdy są w ogóle łapani."*

---

### CREDIT-111 (EVAL, GF) — DOWÓD TEZY: statyka vs monitoring

**Plik:** `ml-learing-center/static_vs_dynamic.py` (200 LoC, standalone, reuse `score_test_set()`
z `timeseries_eval`). PR #21.

**Po co:** **THE thesis slide.** Cała teza Wariantu B opiera się na uczciwym porównaniu dwóch reguł
decyzyjnych przy tym samym budżecie fałszywych alarmów (FA). Bez tego eksperymentu „monitoring" to
tylko slogan.

**Co robi:** trzyma rodzinę W3-skalibrowaną stałą, podmienia tylko regułę:

- **Static rule:** flaguj klienta jeśli `PD_W3 ≥ threshold`
- **Monitoring rule:** flaguj klienta jeśli `max(PD_W0, PD_W1, PD_W2, PD_W3) ≥ threshold`

Sweepuje 19 progów w (0.05, 0.95), produkuje ROC-like krzywe w (FA, catch) per model. Dla
kanonicznych budżetów FA (5%, 10%, 20%) wybiera próg per reguła i porównuje catch rates +
liczbę „only-monitor-catches" (defaulterów złapanych tylko przez monitoring).

**Wyniki przy FA = 10% (kanoniczny operating point):**

| Model | static_catch | monitor_catch | Δ pp | only_monitor_catches | mean_lead |
|---|---|---|---|---|---|
| RandomForest | 50.3% | 45.3% | **−4.97** | 72 | 1.99 |
| XGBoost | 49.8% | 43.9% | **−5.88** | 43 | 2.04 |
| LSTM | 47.9% | 45.7% | −2.11 | 58 | 2.06 |

Przy FA = 5% obraz się odwraca dla LSTM (+10.25 pp dla monitoringu) i RF (+5.28 pp). Przy FA = 20% RF
nadal wygrywa (+5.05 pp). **Picture jest mieszany — żadna reguła nie dominuje strictly.**

**Honest verdict (kluczowy framing dla obrony):**

Monitoring **nie wygrywa** czystej dyskryminacji przy FA=10%. Aggregator `max(W0..W3)` widzi 4× więcej
szumu niż pojedyncza skalibrowana W3, więc przy tym samym budżecie FA musi mieć wyższy próg, co
kosztuje 2-6 pp catch rate. **Gdzie monitoring wygrywa jednoznacznie: lead time.** Gdy trajektoria
łapie defaultera, pierwszy alarm odpala średnio **~2 okna przed W3** (1.99-2.06). Plus kolumna
`only_monitor_catches` to defaulterzy, których W3-only nigdy by nie złapał — 43-184 per model.

**Framing dla tezy** (zaakceptowany jako najbardziej obronny):

> *„Monitoring oferuje **wcześniejszą detekcję przy porównywalnej dyskryminacji**, nie wyższą catch
> rate per se. Bilans korzyści jest funkcją modelu kosztów: jeśli wczesne przegapienie defaultu jest
> dużo droższe niż późne złapanie, monitoring wygrywa."*

Ten framing nie nadinterpretuje danych. CREDIT-106 (cost thresholds, ten sam sprint) skwantyfikuje
trade-off kosztowy precyzyjniej.

**Output (3 PNG + 2 CSV + 1 Markdown):**
- `reports/static_vs_dynamic_{rf,xgb,lstm}_w3.png` — ROC-like overlay per model
- `reports/static_vs_dynamic_metrics.csv` — pełny sweep (57 wierszy: 19 progów × 3 modele)
- `reports/static_vs_dynamic_operating.csv` — kanoniczne FA (9 wierszy: 3 FA × 3 modele)
- `reports/static_vs_dynamic_report.md` — prose interpretation z honest verdict per model

**Slajd:** *„Monitoring nie wygrywa w czystej dyskryminacji. Wygrywa w lead time — 2 okna wcześniej,
plus 43-184 unikalnych catchy na model. Trade-off jest funkcją modelu kosztów."*

---

### CREDIT-106 (ML, GF) — Cost-optimized alert thresholds

**Pliki:** `ml-learing-center/optimize_thresholds.py` (130 LoC, standalone) + dopis w `main.py` +
`ml-service/app.py` (load + response) + `ml-service/alert_thresholds.json` + update kontraktu
`monitoring.md` §3.5. PR #22.

**Po co:** CREDIT-111 pokazał że monoton 0.5 threshold to nie jest optymalna decyzja per model.
**Model kosztów** mówi explicite ile kosztuje przegapienie defaultu (FN) względem fałszywego alarmu
(FP). Standardowa asymetria w credit scoring: FN = 5× FP. Pod taką funkcję kosztu, optymalny próg
per model spada znacznie poniżej 0.5.

**Co robi:** dla każdego modelu sweepuje progi w (0.1, 0.9), liczy `cost = 5·FN + 1·FP` na test
secie, wybiera próg minimalizujący koszt. Zapisuje do `ml-service/alert_thresholds.json` z `_meta`
(cost ratio, bounds, source). Flask ładuje przy starcie i serwuje w response `/predict/timeseries`.

**Wyniki:**

| Model | Cost-opt threshold | Expected cost | FN | FP |
|---|---|---|---|---|
| RandomForest | **0.145** | 3337 | 336 | 1657 |
| XGBoost | **0.180** | 3368 | 333 | 1703 |
| LSTM | **0.185** | 3460 | 352 | 1700 |

Wszystkie w DoD bound (0.1, 0.9). ✓

Bias w stronę niskich progów odzwierciedla model kosztów: tolerujemy ~1700 false alarms, żeby
przepchnąć FN do ~340 z 1327 defaulterów.

**Response Flask rozszerzony** (additive, non-breaking — frontend Sprintu 3 nadal działa):

```json
"costThresholds": { "randomForest": 0.145, "xgboost": 0.180, "lstm": 0.185 },
"windowAlerts": {
  "randomForest": [false, false, true, true],
  "xgboost":      [false, true,  true, true],
  "lstm":         [false, false, false, true]
}
```

Frontend (CREDIT-303 / CREDIT-114 final) może teraz kolorować punkty Timeline per model na podstawie
per-model thresholda zamiast hardcoded 0.5.

**Slajd:** *„Próg 0.5 nie jest neutralny. Pod asymetrycznym modelem kosztów (FN=5×FP) optymalny
cut-off to 0.145-0.185 per model — daleko od 0.5. System serwuje te per-model progi tak, żeby
downstream consumers nie musiały znać matematyki kosztu."*

---

## 3. Ścieżka krytyczna tezy — postęp w Sprincie 3

Przed Sprintem 3:
```
101 ✅  →  102 ✅  →  104 ✅  →  110 🔴  →  111 🔒  →  114 🔒
```

Po Sprincie 3 (mój tor):
```
101 ✅  →  102 ✅  →  104 ✅  →  110 ✅  →  111 ✅  →  114 🔒 (czeka na 113)
```

**5 z 6 ogniw ścieżki krytycznej zamknięte.** Ostatnie (CREDIT-114 final report) wymaga jeszcze
CREDIT-113 (stacking, P2 Sprint 6) i CREDIT-103 (już done).

---

## 4. Statystyki mojego Sprintu 3

| Wskaźnik | Wartość |
|---|---|
| **Zadań GF ukończonych** | 3 (110, 111, 106) |
| **PR-ów** | #20, #21, #22 |
| **Nowych LoC (110)** | +230 (`timeseries_eval.py`) + 6 PNG + 1 CSV + 1 MD |
| **Nowych LoC (111)** | +200 (`static_vs_dynamic.py`) + 3 PNG + 2 CSV + 1 MD |
| **Nowych LoC (106)** | +130 (`optimize_thresholds.py`) + zmiany w `main.py` + `app.py` + JSON |
| **Wszystkich nowych raportów** | 9 PNG + 3 CSV + 2 MD report files w `reports/` |
| **Nowych testów backendu/API** | +1 (response includes `costThresholds` + `windowAlerts`, threshold range check) |
| **Testów ML łącznie** | 9 (CI zielony) |
| **Cost thresholds dla 3 modeli** | 0.145 / 0.180 / 0.185 (wszystkie w DoD bound 0.1-0.9) |
| **Ścieżka krytyczna tezy** | 5/6 ogniw zamkniętych (zostaje 114) |

---

## 5. Co mój tor odblokował

| ID | Sprint | Owner | Odblokowane przez | Status po Sprincie 3 |
|---|---|---|---|---|
| CREDIT-106 | 3 | GF | 105 | 🟢 (zrobiłem ja, ten sprint) |
| **CREDIT-114** | 6 | GF | 103, 111, **113** | 🔒 (czeka jeszcze na 113) |

Ścieżka krytyczna tezy: ostatnie ogniwo (114) czeka tylko na CREDIT-113 (stacking ensemble).
CREDIT-113 z kolei wymaga CREDIT-109 (LightGBM/CatBoost) — który ja zrobiłem w Sprincie 4 (out of
order, patrz `PodsumowanieSprintu4_GF.md`), żeby odblokować ten finałowy łańcuch.

---

## 6. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**
- **R2 z Risk Register: „Monitoring nie bije statyki w eksperymencie"** — CREDIT-111 honest verdict
  pokazał że to faktycznie się materializuje przy FA=10%. Mitigacja zaplanowana w planie sprintów
  („dynamika daje lead time, nawet jeśli AUC podobne") zastosowana w framingu tezy. Nie udawaliśmy
  że monitoring strictly dominuje.
- **Threshold 0.5 jako default** — CREDIT-106 zastąpił cost-optimized per-model thresholdami.

**Świadomie odłożone:**
- **Cost ratio 5:1 jako parametr** — hardcoded, defensible dla pracy magisterskiej. Sensitivity
  analysis (jak optymalne progi zmieniają się dla 3:1 / 10:1 / 20:1) mogłaby trafić do CREDIT-114
  jako appendix.
- **Frontend integracja windowAlerts** — Flask je serwuje, ale Timeline (CREDIT-301) i Client
  History (CREDIT-302) nadal mogą używać starych defaultów. Pełna integracja w CREDIT-303
  (Sprint 5, MK).

---

## 7. Co dalej — Sprint 4 i Sprint 5 (mój tor)

Sprint 4 (mój tor) — patrz `PodsumowanieSprintu4_GF.md`. Krótko: najpierw pivot na **CREDIT-109**
(LightGBM + CatBoost, Sprint 5 P2 wzięte out-of-order, żeby odblokować łańcuch krytyczny do
CREDIT-114). Potem powrót po pierwotne P2: **CREDIT-107 (SHAP)** i **CREDIT-108 (Optuna + CV)**.
**Sprint 4 GF zamknięty 3/3** (107 ✅ + 108 ✅ + 109 ✅).

Następne po Sprincie 4:
- **CREDIT-113** (stacking ensemble, P2, blocks CREDIT-114) — kolejny GF task
- **CREDIT-114** (final report, P0) — zamknięcie tezy + komplet wykresów do prezentacji
- **CREDIT-112** (fairness audit per SEX, P1 SWAP-OK) — opcjonalne, można równolegle

---

## 8. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 3)

> **Sprint 3 (tor GF) — dowód tezy zamknięty (5/6 ogniw ścieżki krytycznej).**
>
> - **CREDIT-110** — metryki time-series. Lead time ~2 okna, slope_auc 0.59 vs w3_auc 0.77 — slope
>   to słaby standalone predyktor.
> - **CREDIT-111** — **THE thesis slide**. Honest verdict: monitoring nie wygrywa dyskryminacji
>   przy FA=10% (−2 do −6 pp), ale wygrywa lead time (~2 okna) i unikalne catche (43-184/model).
>   Framing obronny: „**wcześniejsza detekcja przy porównywalnej dyskryminacji**".
> - **CREDIT-106** — cost-optimized thresholds. Pod FN=5×FP optymalne progi to 0.145-0.185 per
>   model (vs hardcoded 0.5). Flask serwuje w response, frontend może kolorować Timeline per model.
> - **9 raportów PNG + 3 CSV + 2 Markdown reports**. Wszystko commitowane do `reports/`.
> - **Ścieżka krytyczna tezy: 5/6 ✅** — zostaje tylko CREDIT-114 (final report), który czeka na
>   CREDIT-113 (stacking, Sprint 6).
>
> **Następne (mój tor):** CREDIT-109 (LightGBM/CatBoost) zrobione w Sprincie 4 out-of-order, żeby
> odblokować CREDIT-113 → CREDIT-114.
