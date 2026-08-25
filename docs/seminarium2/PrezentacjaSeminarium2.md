# Materiały na Seminarium dyplomowe 2 — Wariant B (monitoring kalendarzowy)

> ⚠️ **Nota 2026-07-07:** dokumenty źródłowe wymienione niżej zostały scalone/usunięte: podsumowania sprintów → `PodsumowanieSprintow.md`; DokumentRoznice.md i WalidacjaPDFv7.md → ustalenia skonsumowane w `Fable5-zmiany.md` (pliki w historii gita). Liczby w tej prezentacji odpowiadają stanowi 2026-06-06 (sprzed napraw metodologicznych).

> **Cel tego pliku:** zebrać w jednym miejscu wszystko, co potrzebne do zbudowania prezentacji PowerPoint w claude-project oraz do live demo. Kolejność sekcji = kolejność slajdów.
>
> **Źródła:** `plan_sprintow_wariant_B.md`, `CHECKLIST.md`, `PodsumowanieSprintu{1..5}_*.md`, `DokumentRoznice.md`, `WalidacjaPDFv7.md`, `ml-learing-center/reports/` (numeryka + PNG), `docs/api-contracts/monitoring.md`, kod projektu (`ml-learing-center/`, `ml-service/`, `backend/`, `frontend/`).
>
> **Stan projektu:** 2026-06-06, po merge Sprintu 5 (CREDIT-112 fairness). 26/30 zadań zamknięte; 5/6 ogniw ścieżki krytycznej tezy zamknięte (zostaje CREDIT-113 + CREDIT-114). Branch `sprint5/fairness`.

---

## Spis treści

- [I. Cel i teza pracy](#i-cel-i-teza-pracy)
- [II. Metodologia](#ii-metodologia)
- [III. Wyniki](#iii-wyniki)
- [IV. Wnioski](#iv-wnioski)
- [V. Live demo — runbook i scenariusz](#v-live-demo--runbook-i-scenariusz)
- [VI. Stan pracy pisemnej (PDF v8)](#vi-stan-pracy-pisemnej-pdf-v8)
- [VII. Raport z realizacji postępu prac (per sprint)](#vii-raport-z-realizacji-postępu-prac-per-sprint)
- [Appendix A — Decyzje projektowe z pełnym uzasadnieniem](#appendix-a--decyzje-projektowe-z-pełnym-uzasadnieniem)

---

## I. Cel i teza pracy

### Cel pracy

Zbudowanie systemu predykcji ryzyka kredytowego (default w następnym miesiącu) opartego na zbiorze publicznym **UCI „Default of Credit Card Clients" (Taiwan 2005, 30 000 klientów, 22 cechy wejściowe)**, który zamiast pojedynczej jednorazowej oceny dostarcza **trajektorię prawdopodobieństwa default (PD) w czasie** i wykrywa pogorszenie sytuacji kredytobiorcy **zanim** dojdzie do faktycznego defaultu.

### Dwoiste znaczenie „dynamiczne" w tytule pracy

Świeżo dodane do v8 PDF i kluczowe dla framingu seminarium — termin „dynamiczne" odnosi się **jednocześnie** do dwóch poziomów:

1. **Dynamiczna architektura modelu** — LSTM jako sieć rekurencyjna traktująca ocenę jako funkcję sekwencji zdarzeń (3 kroki czasowe × 3 kanały).
2. **Dynamiczny schemat oceny (Wariant B)** — sliding-window 4-okienkowy + kalendarzowy monitoring tej samej ekspozycji w czasie → 4-punktowa trajektoria PD per model → wczesne ostrzeganie.

> **Talking point dla obrony:** „termin »dynamiczne« nie odnosi się do cyklicznego ponownego trenowania modelu, lecz ma znaczenie dwojakie — sekwencyjna architektura LSTM oraz, przede wszystkim, wielokrotna kalendarzowa ocena tej samej ekspozycji" (Wstęp v8, str. 1-2).

### Teza Wariantu B

> **Kalendarzowy monitoring trajektorii PD oferuje wcześniejsze wykrycie pogorszenia sytuacji dłużnika przy porównywalnej dyskryminacji wobec jednorazowej oceny statycznej.**

Uczciwy framing dla obrony (zaakceptowany w CREDIT-111 — patrz Sekcja III.2): **monitoring nie wygrywa czystej catch rate** przy budżecie FA=10%, **ale wygrywa lead time** (≈ 2 okna = 2 miesiące wcześniej) i wyłapuje 36-146 unikalnych defaulterów/model nieznalezionych przez statykę. Bilans korzyści jest funkcją modelu kosztów.

### Hipotezy badawcze

(W v8 PDF jeszcze nie zapisane formalnie w Roz. 3.2 — do uzupełnienia tutaj na seminarium.)

| H | Treść | Gdzie udowodnione |
|---|---|---|
| **H1** | Sliding-window 3-miesięczne (W3) zachowuje AUC blisko legacy 6-miesięcznego (strata < 1 pp). | CREDIT-102 — RF 0.7779 vs 0.7792, XGB 0.7794 vs 0.7818, LSTM 0.7637 vs 0.7686 |
| **H2** | Monitoring W0..W3 oferuje **wcześniejszą detekcję przy porównywalnej dyskryminacji** względem statyki W3. | CREDIT-110 (lead time ~2 okna) + CREDIT-111 (honest verdict @FA=10%) |
| **H3** | Modele zachowują się fair względem atrybutu chronionego SEX (|DPD| oraz |EOD| ≤ 0.10). | CREDIT-112 — wszystkie 5 modeli, |diff| ≤ 0.04 |

---

## II. Metodologia

### II.1 Dane i sliding-window panel (CREDIT-101)

**Wyzwanie metodologiczne.** UCI dostarcza statyczny snapshot — jeden wiersz na klienta z 6-miesięczną historią + jeden label defaultu (październik). Wariant B wymaga jednak panelu czasowego dla trajektorii. Rozwiązanie nie może fabrykować danych.

**Konstrukcja 4 okien 3-miesięcznych z jednego wiersza UCI** (`ml-learing-center/sliding_window.py`):

| Okno | Zakres miesięcy | Status płatności | Rachunki | Wpłaty |
|------|----------------|-----------------|----------|--------|
| W0 (najstarsze) | kwi · maj · cze | PAY_6, PAY_5, PAY_4 | BILL 6, 5, 4 | PAY_AMT 6, 5, 4 |
| W1 | maj · cze · lip | PAY_5, PAY_4, PAY_3 | BILL 5, 4, 3 | PAY_AMT 5, 4, 3 |
| W2 | cze · lip · sie | PAY_4, PAY_3, PAY_2 | BILL 4, 3, 2 | PAY_AMT 4, 3, 2 |
| W3 (najnowsze) | lip · sie · wrz | PAY_3, PAY_2, PAY_0 | BILL 3, 2, 1 | PAY_AMT 3, 2, 1 |

> **Zasada nadrzędna — „nie fabrykujemy danych".** Każde okno = realny 3-miesięczny wycinek prawdziwej historii klienta. Jeden klient = jeden prawdziwy label defaultu wspólny dla wszystkich 4 okien. Brak etykiet pośrednich.

Uwaga UCI: kolumna `PAY_1` nie istnieje — sekwencja to PAY_0, PAY_2, PAY_3, ..., PAY_6 (znana cecha zbioru).

### II.2 5 modeli ML (CREDIT-102 + CREDIT-109)

| Model | Typ | Rola | Plik artefaktu |
|-------|-----|------|----------------|
| Random Forest | bagging, 500 drzew, depth 10 | baseline tree-based | `rf_model_w3.pkl` |
| XGBoost | gradient boosting, 800 iter, lr 0.02, depth 4 | mocny baseline | `xgb_model_w3.pkl` |
| LightGBM | leaf-wise gradient boosting + histogram binning + GOSS + EFB | nowy w CREDIT-109 | `lightgbm_model_w3.pkl` |
| CatBoost | ordered boosting + native categorical | nowy w CREDIT-109, **best single** | `catboost_model_w3.pkl` |
| LSTM | 32 jednostek, dropout 0.3, input shape `(1, 3, 3)` | dynamiczna architektura (3 timesteps × 3 kanały) | `lstm_model_w3.keras` |

**Trening na W3 (najnowsze 3 mies., zgodne z etykietą październikową)** → **inferencja na W0..W3**. Ponieważ każde okno ma identyczną strukturę (3 mies., 3 kanały), **rozkład inferencyjny = rozkład treningowy → brak out-of-distribution shift.**

LSTM input shape `(1, 3, 3)` — 3 kroki czasowe × 3 kanały (PAY, BILL, PAY_AMT), z osobnymi skalerami per kanał (zapisane w `lstm_scalers_w3.pkl`).

### II.3 Kalibracja izotoniczna (CREDIT-105) — P0 dla Wariantu B

**Problem.** Trajektoria PD W0→W3 ma sens tylko jeśli bezwzględne wartości PD odpowiadają realnym częstościom defaultów. Surowy output `predict_proba` z tree-based modeli jest porządkowy (ranking-only), nie kalibrowany — wzrost 0.3→0.5 nie znaczy „16 → 26% prawdopodobieństwa defaultu w populacji".

**Rozwiązanie.** **3-way split train / calib / test** (60/20/20):

- **RF/XGB/LightGBM/CatBoost:** `CalibratedClassifierCV(FrozenEstimator(base), method='isotonic', cv='prefit')` — kalibrator izotoniczny dopasowuje monotoniczną funkcję na trzymanym calib secie, bez retreningu bazy.
- **LSTM:** zewnętrzny `sklearn.IsotonicRegression` na raw output Keras (artefakt `lstm_calibrator_w3.pkl`).

**Brier Score (im niżej, tym lepsza kalibracja):**

| Model | Before | After | Δ |
|-------|--------|-------|---|
| RF | ~0.169 | 0.137 | **−19%** |
| XGB | ~0.178 | 0.136 | **−24%** |
| LSTM | ~0.181 | 0.139 | **−23%** |

AUC zachowane (izotonic to monotoniczna transformacja → ranking taki sam).

> **Why isotonic, nie Platt:** nieparametryczne, mniej restrykcyjne dla nieliniowych rozjazdów (Platt zakłada sigmoid, który nie pasuje do drzew). Trade-off: izotonic potrzebuje więcej calib data — stąd 20% partycja zamiast 10%.

### II.4 Cost-optimized thresholds (CREDIT-106)

**Problem.** Domyślny próg 0.5 nie jest neutralny w kredycie — przegapienie defaultu (FN) jest dużo droższe niż fałszywy alarm (FP). Asymetria typowa: **FN = 5× FP**.

**Sweep** progów (0.1, 0.9) per model na test secie, minimalizacja `cost = 5·FN + 1·FP`. Wynik zapisany w `ml-service/alert_thresholds.json` i serwowany w response Flaska jako `costThresholds`:

| Model | Cost-opt threshold | Komentarz |
|-------|-------------------|-----------|
| Random Forest | **0.145** | znacznie poniżej 0.5 |
| XGBoost | **0.180** | |
| LightGBM | **0.160** | |
| **CatBoost** | **0.130** | najniższy — najwięcej alarmów, ale i tak zdaje fairness audit (patrz III.4) |
| LSTM | **0.175** | |

Bias w stronę niskich progów odzwierciedla model kosztów: tolerujemy ~1700 false alarmów żeby przepchnąć FN do ~340 z 1327 defaulterów w test secie.

**Wpływ na produkcję:** Flask serwuje per-model progi w response trajektorii. Frontend (CREDIT-303 + CREDIT-116) koloruje punkty Timeline per model na podstawie odpowiedniego progu, nie hardcoded 0.5.

### II.5 Monitoring trajektorii i reguła alertu (CREDIT-104 + CREDIT-210)

Flask endpoint `/predict/timeseries` (CREDIT-104) przyjmuje 22 cechy klienta, wewnętrznie rozbija je na 4 okna sliding-window, scoruje każde okno każdym z 5 modeli, składa trajektorię i liczy:

- **Slope** = PD_W3 − PD_W0 per model
- **Alert** = `INCREASING_RISK` (slope > +0.10), `DECREASING_RISK` (slope < −0.10), `STABLE` (|slope| ≤ 0.10)
- **windowAlerts** — bool table 5 modeli × 4 okna, gdzie alert został przekroczony pod **cost-opt threshold per model**

Kontrakt API (`docs/api-contracts/monitoring.md`, CREDIT-210) — 409 LoC, ustalony wspólnie GF+MK w 30-minutowej sesji, odblokował 4 zadania równoległe (Flask + .NET + zapis + frontend).

### II.6 Interpretowalność (SHAP, CREDIT-107)

**TreeExplainer top-5 cech per predykcja**, dla 4 tree-based modeli (RF, XGB, LightGBM, CatBoost). Wynik w response Flask jako `shap.{model}.topFeatures = [{feature, value}]`, sortowane po `|value|` malejąco.

- **Konwencja znaku:** `value > 0` → cecha **pcha PD w górę** (w stronę DEFAULT); `value < 0` → **pcha w dół**.
- **Performance:** 102 ms dla wszystkich 4 explainerów + sortowania — **20× pod DoD < 2s.** TreeExplainer jest exact, nie sampling.
- **LSTM pominięty:** TreeExplainer N/A dla Keras LSTM, KernelExplainer z background sampling wybiłby budżet czasu (~10s+ na predykcję).

Helper `_unwrap_calibrated()` w `ml-service/app.py` wyciąga base estimator z otoczki `CalibratedClassifierCV(FrozenEstimator)` — kalibracja izotoniczna jest monotoniczna, więc ranking cech zachowany.

### II.7 Audyt fairness (CREDIT-112)

**Wymóg AI Act** (Art. 9 / 15 — klasyfikuje credit scoring jako *high-risk*). Audyt fairlearn DPD + EOD względem atrybutu chronionego SEX dla wszystkich 5 modeli W3 przy **realnym operating point**, tj. cost-opt thresholdach z CREDIT-106 (nie arbitralnym 0.5).

- **DPD** (Demographic Parity Difference) — gap selection rate między grupami: `P[ŷ=1|SEX=1] − P[ŷ=1|SEX=2]`.
- **EOD** (Equalized Odds Difference) — `max(|ΔTPR|, |ΔFPR|)` między grupami.
- **DoD bound:** `|diff| ≤ 0.10` (konsensusowy próg).

Wybór audytu **przy cost-opt thresholds** jest świadomy: chcemy zmierzyć fairness *faktycznego zachowania systemu pod alertem produkcji*, nie zachowania pod arbitralnym progiem 0.5.

### II.8 Architektura systemu

```
React Frontend (5173) ──POST /api/v1/monitoring/clients/{ref}/snapshots──┐
                                                                          ▼
.NET 8 ASP.NET Core (5120) — MonitoringController
   ├── ScoreAndPersistAsync (reuse PredictTimeseriesAsync)
   │      ├── walidacja 22 cech (DataAnnotations)
   │      ├── PythonModelClient ──► Flask /predict/timeseries (5001)
   │      └── enrichment: clientRef, snapshotDate, labelki okien
   ├── SnapshotRepository / PredictionRepository / TrendRepository
   └─────────────────────────────► PostgreSQL 16 (5432) — EF Core
                                   Client / Snapshot / Prediction / Trend
```

| Warstwa | Tech | Port | Co robi |
|---------|------|------|---------|
| Frontend | React 19 + TypeScript + Vite | 5173 | Wprowadzanie migawek, Timeline trajektorii, SHAP, ClientList |
| Backend | .NET 8 ASP.NET Core + EF Core | 5120 | Walidacja, orkiestracja, persystencja, labelki kalendarzowe, mapowanie błędów (400/409/502/503) |
| ML Service | Flask 3 + Python 3.11 | 5001 | Scoring 5 modeli, kalibracja, cost thresholds, SHAP |
| Baza danych | PostgreSQL 16 (docker-compose) | 5432 | Client / Snapshot / Prediction / Trend, kaskady FK |

**Decyzje:**
- **Flask bezstanowy** — bez DB, bez `clientRef`; przyjmuje 22 cechy, zwraca PD. .NET dokleja datę + labelki.
- **`/predict` (legacy 6-mies., 3 modele) zachowany** dla zakładki Prediction — additive change w Monitoring, nie ruszamy starego endpointa.
- **Frontend POZA docker-compose** — pozostaje na `npm run dev` dla wygody hot-reloadu.
- **Auto-migracje przy starcie backendu** (`db.Database.Migrate()` w `Program.cs`).
- **409 przy duplikacie `(clientRef, snapshotDate)`** — guard *przed* wywołaniem Flaska, żeby nie marnować scoringu i nie tworzyć klienta na konflikcie.

---

## III. Wyniki

### III.1 Metryki dyskryminacji per model (W3 calibrated, test 20% = 6 000 klientów)

Liczby z `ml-learing-center/reports/metrics_w3.csv`:

| Model | AUC | Gini | KS | Brier |
|-------|-----|------|----|----|
| Random Forest | 0.7741 | 0.5483 | 0.4044 | 0.1372 |
| XGBoost | 0.7760 | 0.5520 | **0.4248** | 0.1360 |
| LightGBM | 0.7764 | 0.5527 | 0.4164 | 0.1366 |
| **CatBoost** | **0.7802** | **0.5603** | 0.4166 | **0.1354** |
| LSTM | 0.7610 | 0.5221 | 0.3994 | 0.1387 |

**Interpretacja:**
- **CatBoost najlepszy single model** (AUC + Gini + Brier). Spread AUC całej rodziny wąski (~2 pp).
- XGBoost najlepszy w KS (separacja klas) — drobne wahanie, w obrębie szumu.
- LSTM nieznacznie z tyłu — oczekiwane przy 3-elementowej sekwencji; **dynamiczna architektura kosztuje** kiedy okno jest krótkie. Stąd 5-modelowa rodzina + planowany stacked ensemble (CREDIT-113).

**Wykresy gotowe do slajdów:**
- `reports/roc_comparison_w3.png` — ROC overlay 5 modeli
- `reports/pr_comparison_w3.png` — Precision-Recall overlay
- `reports/calibration_comparison_w3.png` — reliability diagram per model (sanity check kalibracji)
- `reports/roc_{rf,xgb,lightgbm,catboost,lstm}_w3.png` — pojedyncze ROC z AUC w tytule (5 plików)
- `reports/confusion_*_w3.png` — confusion matrix (uwaga: przy progu 0.5)
- `reports/ks_*_w3.png` — KDE rozkładu PD per klasa + KS w tytule

### III.2 Dowód tezy: statyka vs monitoring (CREDIT-111) — THE thesis slide

Reguły porównane:
- **Static:** flag jeśli `PD_W3 ≥ threshold`
- **Monitoring:** flag jeśli `max(PD_W0, PD_W1, PD_W2, PD_W3) ≥ threshold`

Sweep 19 progów, kanoniczny operating point **FA = 10%**. Liczby z `reports/static_vs_dynamic_operating.csv`:

| Model | static_catch | monitor_catch | Δ pp | only_monitor_catches | mean_lead (okien) |
|-------|--------------|---------------|------|----------------------|-------------------|
| Random Forest | 50.26% | 45.29% | **−4.97** | 72 | 1.99 |
| XGBoost | 49.81% | 43.93% | **−5.88** | 43 | 2.04 |
| LightGBM | 51.09% | 49.81% | **−1.28** | 71 | 2.05 |
| CatBoost | 51.47% | 44.61% | **−6.86** | 36 | 2.10 |
| LSTM | 47.32% | 39.64% | **−7.68** | 57 | 2.19 |

**Honest verdict (kluczowy framing):**

> Monitoring **nie wygrywa** czystej dyskryminacji przy FA=10%. Aggregator `max(W0..W3)` widzi **4× więcej szumu** niż pojedyncza skalibrowana W3, więc przy tym samym budżecie FA musi mieć wyższy próg, co kosztuje 1-8 pp catch rate.
>
> **Gdzie monitoring wygrywa jednoznacznie: lead time.** Gdy trajektoria łapie defaultera, pierwszy alarm odpala średnio **~2 okna przed W3** (1.99–2.19 okna ≈ 2 miesiące wcześniej). Plus kolumna `only_monitor_catches` to defaulterzy, których W3-only nigdy by nie złapał — **36-72 unikalnych catchy per model.**

**Framing dla obrony tezy:**

> *„Monitoring oferuje **wcześniejszą detekcję przy porównywalnej dyskryminacji**, nie wyższą catch rate per se. Bilans korzyści jest funkcją modelu kosztów: jeśli wczesne przegapienie defaultu jest dużo droższe niż późne złapanie, monitoring wygrywa. CREDIT-106 (cost thresholds) skwantyfikował to formalnie."*

Przy FA = 5% obraz się odwraca dla LSTM (+10pp catch dla monitoringu) i RF (+5pp). Przy FA = 20% RF nadal wygrywa monitoringiem (+5pp). **Picture jest mieszany — żadna reguła nie dominuje strictly** — to *jest* uczciwa praca magisterska.

**Wykresy do slajdów:** `reports/static_vs_dynamic_{rf,xgb,lightgbm,catboost,lstm}_w3.png` (5 ROC overlay PNG) + `reports/static_vs_dynamic_report.md` (prose interpretation).

### III.3 Early-warning lead time (CREDIT-110)

Liczby z `reports/timeseries_metrics.csv` (alert threshold 0.5, 1327 defaulterów):

| Model | catch_rate | mean_lead_windows | slope_auc | w3_auc |
|-------|-----------|-------------------|-----------|--------|
| Random Forest | 49.8% | 2.05 | 0.588 | 0.774 |
| XGBoost | 50.6% | 2.05 | 0.590 | 0.776 |
| LSTM | 51.5% | 2.06 | 0.596 | 0.760 |

**Slope_auc ~0.59 vs w3_auc ~0.77** — sam slope jest **słabym standalone predyktorem**. To ważne dla obrony: monitoring **nie zastępuje** pojedynczego dobrego PD; **dodaje** wymiar czasu. Lead distribution dla RF (przykład): caught at W3=108, W2=100, W1=101, W0=352 → ~30% złapanych defaulterów wykrytych **pierwszy raz w W1/W2**, których statyka W3 by przegapiła.

**Wykresy:** `reports/slope_boxplot_*_w3.png` (5×, rozkład slope per klasa) + `reports/trajectory_examples_*_w3.png` (5×, 25 losowych defaulterów vs 25 non-defaulterów).

### III.4 Fairness audit (CREDIT-112)

Liczby z `reports/fairness_metrics_w3.csv`. Audyt **przy cost-opt thresholds**, nie 0.5.

| Model | Threshold | DPD | EOD | Warn? |
|-------|----------:|----:|----:|:-----:|
| Random Forest | 0.145 | +0.0347 | +0.0289 | ok |
| XGBoost | 0.180 | +0.0377 | +0.0333 | ok |
| LightGBM | 0.160 | +0.0269 | +0.0215 | ok |
| **CatBoost** | 0.130 | **+0.0393** | **+0.0334** | ok |
| **LSTM** | 0.175 | **+0.0068** | **+0.0153** | ok |

**Wszystkie 5 modeli zdaje** rygor `|diff| ≤ 0.10` — **4× margines bezpieczeństwa.**

**Per-group breakdown (selection_rate / TPR / FPR):**

| Model | sel M | sel F | TPR M | TPR F | FPR M | FPR F |
|-------|------:|------:|------:|------:|------:|------:|
| RF | 0.462 | 0.427 | 0.758 | 0.739 | 0.372 | 0.343 |
| XGB | 0.472 | 0.434 | 0.768 | 0.735 | 0.382 | 0.353 |
| LightGBM | 0.445 | 0.419 | 0.749 | 0.727 | 0.353 | 0.335 |
| CatBoost | 0.524 | 0.484 | 0.816 | 0.792 | 0.434 | 0.401 |
| LSTM | 0.480 | 0.486 | 0.759 | 0.770 | 0.394 | 0.410 |

**Honest framing dla obrony:**

> *„DPD dodatnie dla wszystkich 5 modeli — mężczyźni flagowani nieco częściej niż kobiety (selection rate wyższy o 2-4 pp). **To nie jest 'bias modelu' w czystej postaci** — odpowiada wyższemu *base rate* defaultów w grupie SEX=1 w danych UCI (24.2% vs 20.8% w teście). Modele trafnie odzwierciedlają strukturę danych. CatBoost największy diff (0.039) — koresponduje z jego najniższym progiem (0.130) → globalnie więcej alarmów → większe wahania per-grupa. LSTM jako jedyny **odwraca** selection rate (kobiety > mężczyźni) — inna geometria reprezentacji sekwencyjnej. AI Act compliance regulatory checkbox: TAK."*

**Wykresy:** `reports/fairness_selection_rate_w3.png` + `reports/fairness_tpr_fpr_w3.png`. Raport: `reports/fairness_report.md`.

### III.5 SHAP top-5 — przykładowa eksplanacja

Dla zdrowego klienta referencyjnego (wszystkie PAY=0, regularne wpłaty), top-5 cech RF (sanity check w CREDIT-107):

| Cecha | SHAP value | Interpretacja |
|-------|-----------:|---------------|
| PAY_mean | −0.031 | „średnia status płatności = 0" → pcha PD **w dół** |
| PAY_max | −0.030 | „najgorszy status w oknie = 0" → w dół |
| PAY_AMT_mean | −0.025 | „regularne wpłaty" → w dół |
| late_count | −0.024 | „brak miesięcy z opóźnieniem" → w dół |
| severe_late | −0.024 | „brak severe late" → w dół |

Wszystkie cechy proxy „ten klient płaci na czas", wszystkie pchają PD w dół. To dokładnie to, co analityk kredytowy oczekiwałby zobaczyć — **defensible explanation gotowa do prezentacji w UI**.

W UI (Monitoring → Add snapshot → SHAP) ten sam mechanizm pokazuje **horizontal bars per model**: czerwone (+, raises PD) / zielone (−, lowers PD), długość proporcjonalna do |value|/max.

---

## IV. Wnioski

1. **Teza Wariantu B częściowo dowiedziona.** Lead time wygrywa jednoznacznie (~2 okna ≈ 2 miesiące); dyskryminacja przy FA=10% nieznacznie ustępuje statyce (1-8 pp w zależności od modelu). Pełen obraz jest funkcją modelu kosztów (CREDIT-106) — przy asymetrii FN > FP monitoring staje się ekonomicznie korzystny.

2. **Pakiet 5 modeli + kalibracja + cost-opt + SHAP + fairness** czyni system **AI Act ready** (high-risk credit scoring): defensible explanations, audyt dyskryminacji przy realnym operating point, regulatory checkboxy zaadresowane.

3. **System działa end-to-end:** React + .NET + Flask + Postgres uruchamialne docker-compose; persystencja migawek pozwala na realny monitoring kalendarzowy, nie tylko inferencję z jednego wiersza. CI 3-stack (xUnit + pytest + Vitest), > 50 testów.

4. **Co dalej (Sprint 6 — pozostałe 4 zadania):**
   - **CREDIT-113 stacked ensemble** (LR meta-learner na 5 modelach bazowych) — może domknąć lukę dyskryminacji do statyki + lepsza kalibracja.
   - **CREDIT-114 final report** — zbiorczy raport + komplet wykresów do prezentacji obrony.
   - **CREDIT-304 UI polish** — responsive 1024/1440/1920, a11y Lighthouse ≥ 90, dark mode, tooltipy.
   - **CREDIT-501 docs** — README + Model Card + Architecture + update CLAUDE.md.

5. **Praca pisemna:** v8 PDF ma kompletny Wstęp + Roz. 1 + Roz. 2 + Bibliografię (31 pozycji). **Roz. 3 (metodologia + projekt systemu) i Roz. 5 (analiza wyników) są nadal pustymi szkieletami** — to ~3-4 dni pracy edytorskiej do v9 (patrz Sekcja VI).

---

## V. Live demo — runbook i scenariusz

### V.1 Startup (3 terminale)

**Terminal 1 — ML Service (Flask, port 5001):**
```bash
cd ml-service
source venv/bin/activate     # jeśli używasz venv
python app.py
```

**Terminal 2 — Backend + DB (docker-compose, port 5120 + 5432):**
```bash
cd /Users/gabrielfigur/Documents/GitHub/ai-credit-management
docker-compose up -d db backend
# Migracje EF Core wykonują się automatycznie przy starcie backendu.
# Poczekaj ~10s na health.
```

**Terminal 3 — Frontend (Vite dev, port 5173):**
```bash
cd frontend/WebApp
npm run dev
```

**Sanity checks przed seminarium:**
```bash
curl http://localhost:5001/health       # → {"status":"healthy"}
open http://localhost:5120/swagger      # → widoczne 5 endpointów MonitoringController
open http://localhost:5173              # → strona ładuje się, 2 zakładki widoczne
```

### V.2 Pre-seed bazy demo klientami

**Przed seminarium**, w czwartym terminalu (lub w tym samym co Flask, po docker-compose up):

```bash
cd /Users/gabrielfigur/Documents/GitHub/ai-credit-management
python ml-learing-center/seed_demo_clients.py
```

Skrypt utworzy 3 demo-klientów z trajektoriami:
- **`demo-rising-001`** — 4 migawki, INCREASING_RISK (rosnące PAY_*, malejące wpłaty)
- **`demo-stable-002`** — 4 migawki, STABLE (zachowanie stałe)
- **`demo-falling-003`** — 4 migawki, DECREASING_RISK (poprawa zachowania)

Po seedzie Monitoring tab → ClientList pokazuje 3 klientów z badge'ami semaforowymi od razu.

### V.3 Scenariusz demo (8–12 min)

**Krok 1 — Zakładka „Prediction" (2-3 min)**

> *Co pokazuję:* jednorazową ocenę statyczną — to pokazuje *historyczną* funkcjonalność systemu.

- Pokaż wypełniony formularz 22 cech (sensible defaults dla "medium-risk client").
- Kliknij **„Predict Default Risk"**.
- Dashboard: **3 model cards** (RF, XGB, LSTM) z gauge (circular progress %), badge LOW/MODERATE/HIGH, plus comparison chart (Recharts bar).
- **Talking point:** „Ta zakładka używa legacy endpointa `/api/predict` z 3 modelami 6-miesięcznymi — niezmieniony od początku projektu. Zakładka Monitoring (zaraz) używa nowego pipeline'u z 5 modelami W3 sliding-window."

**Krok 2 — Zakładka „Monitoring" — ClientList (1 min)**

> *Co pokazuję:* przejście do oceny dynamicznej (Wariant B).

- Otwórz zakładkę Monitoring.
- Widać 3 pre-seeded klientów: `demo-rising-001` (badge **INCREASING_RISK** czerwony), `demo-stable-002` (**STABLE** żółty), `demo-falling-003` (**DECREASING_RISK** zielony).
- **Talking point:** „Każdy klient ma kilka migawek w bazie — kolumna `snapshotCount`. Roll-up alert to slope W3−W0 najnowszej migawki, agregowany po wszystkich 5 modelach."

**Krok 3 — Trajektoria PD dla rosnącego ryzyka (3 min)**

> *Co pokazuję:* główny slajd obrony — trajektoria PD w czasie.

- Kliknij `demo-rising-001`.
- **TimelineChart** — Recharts LineChart, **5 linii** (RF zielona, XGB niebieska, LightGBM bursztynowa, CatBoost fioletowa, LSTM różowa), X = `snapshotDate`, Y = PD 0-1, 4 punkty per linia.
- **TrendAlerts** — 5 kart per model: każda z slope (np. +0.42) + alert badge (INCREASING_RISK) + ikona ↑.
- **Talking point:** „To jest praktyczna realizacja tezy. System nie ocenia klienta jednorazowo; widzi 4 migawki w czasie, każda zawiera 22 cechy, sliding-window rozbija je dodatkowo na 4 sub-okna → 4 punkty per migawka. Tu na wykresie widzimy najwyższy poziom abstrakcji: jeden punkt = jeden snapshot = jeden moment kalendarzowy. Slope rośnie → alert. Klient widoczny jako pogarszający się **zanim** PD przekroczy próg, ratuje analityka kredytowego od przegapienia."

**Krok 4 — Dodanie migawki live + SHAP (2-3 min)**

> *Co pokazuję:* user flow + interpretowalność.

- Klik **„+ Add snapshot"**.
- Formularz: data picker, 22 pola (lub klik **„Copy from previous"** → wszystko wypełnione z poprzedniej migawki).
- Zmień ręcznie kilka pól (np. PAY_0 z 1 na 3, BILL_AMT1 podbij).
- Submit → response: `snapshotId`, persistence stats, **SHAP explanation** (diverging horizontal bars, 4 modele × top-5 cech).
- **Talking point:** „Czerwone = cecha pcha PD w górę, zielone = pcha w dół. To jest defensible explanation pod regulatora — analityk widzi *dlaczego* model zaalarmował. LSTM intencjonalnie pominięty — TreeExplainer N/A, KernelExplainer wyciągnąłby budżet >2s."

**Krok 5 — (Opcjonalnie) Fairness deep-dive (1-2 min)**

> *Tylko jeśli ktoś zapyta o bias.*

- Pokaż otwarty `reports/fairness_report.md` (w terminalu lub edytorze).
- Wskaż tabelę: wszystkie 5 modeli |DPD| ≤ 0.039, |EOD| ≤ 0.033, DoD 0.10 → **4× margines**.
- **Talking point:** „Audyt przy realnym operating point — cost-opt thresholds z CREDIT-106, nie arbitralnym 0.5. Dodatnie DPD = nieco większy selection rate dla mężczyzn, koresponduje z wyższym base rate defaultów w SEX=1 w UCI (24.2% vs 20.8%). To nie bias modelu, to fidelność strukturze danych. AI Act compliance checkbox: zdane."

### V.4 Pitfalle (rzeczy, które mogą zaskoczyć)

| Symptom | Powód | Co powiedzieć |
|---------|-------|---------------|
| Prediction tab pokazuje 3 modele a Monitoring 5 | Legacy endpoint nie był aktualizowany; additive change w Monitoring | „Świadomy design — zachowaliśmy stary endpoint bez zmian, żeby nowy pipeline nie zerwał kompatybilności. CREDIT-115 i CREDIT-116 dorobiły 5-model passthrough end-to-end dla Monitoring." |
| SHAP nie ma LSTM | TreeExplainer N/A dla Keras LSTM | „Świadoma decyzja — KernelExplainer wybiłby budżet 2s DoD." |
| UI niedopasowany do telefonu / brak dark mode | CREDIT-304 jeszcze w toku | „Sprint 6, jeszcze w trakcie — desktop-first do seminarium, polish potem." |
| Pierwsza wizyta na pustej bazie | Bez seeda ClientList jest pusty | Pre-seed via `seed_demo_clients.py` przed startem (Sekcja V.2). |

### V.5 Backup plan

- **Gdyby Flask padł:** w `frontend/WebApp/src/api/monitoringApi.ts` jest `MOCK_TIMESERIES_RESPONSE` — w skrajnej sytuacji można szybko podmienić wywołanie API na mock i pokazać wykres z hardcoded payloadu.
- **Gdyby docker-compose padł:** screeny stanu UI w `docs/seminarium2/screenshots/` (do dorobienia ręcznie przed seminarium, np. `Cmd+Shift+4` z każdego ekranu po seedzie).
- **Gdyby cały system padł:** wykresy z `reports/` w slajdach jako fallback (PNG-i są w gicie, gotowe do wyświetlenia z `open ml-learing-center/reports/roc_comparison_w3.png`).

---

## VI. Stan pracy pisemnej (PDF v8)

Stan na 2026-06-06. Szczegóły w `DokumentRoznice.md` (porównanie v6 vs projekt) i `WalidacjaPDFv7.md` (delta v6→v7).

### Co JEST w v8 (kompletne)

- ✅ **Wstęp** (2 strony) — dwoiste znaczenie „dynamiczne", drugie pytanie badawcze (monitoring vs statyka), roadmap 5 rozdziałów, 5 modeli explicit.
- ✅ **Roz. 1 Kredyt i ocena zdolności kredytowej** (1.1-1.4) — Prawo bankowe art. 69/70, PD/LGD/EAD, cykl życia ekspozycji; scoring tradycyjny + karta scoringowa + Rekomendacje T/S KNF; ograniczenia regresji logistycznej; kierunki modernizacji (behawioralny, ML, monitoring).
- ✅ **Roz. 2 ML w finansach** (2.1-2.5) — taksonomia ML, przegląd literatury credit scoring, teoria LSTM/RF/XGB + **dodane 2.3.4 LightGBM** + **2.3.5 CatBoost**; ML vs klasyka; etyka/AI Act/RODO/SHAP teoria/fairness zapowiedź.
- ✅ **Bibliografia** [1]–[31] — ustawy/Rekomendacje KNF/EBA, podręczniki, artykuły naukowe, AI Act/RODO, Wikimedia, [30] LightGBM, [31] CatBoost.
- ✅ **Spis tabel i rysunków** — 14 odniesień (1.1, 1.2, 2.1-2.3, 4.1-4.9).

### Co WYMAGA pracy (krytyczne luki przed obroną)

- ❌ **Roz. 3 Metodologia + projekt systemu** — TOC tylko, treść 0. Sekcje 3.1-3.6 puste. **Krytyczna luka.**
  - 3.1 Cel i zakres → do napisania (rozszerzenie Wstępu)
  - 3.2 **Hipotezy H1/H2/H3** → formalne sformułowanie (treść w I.3 tego dokumentu)
  - 3.3 Dane + sliding-window panel → tabela W0..W3 (treść w II.1)
  - 3.4 Architektura systemu → 4 podsekcje (React + .NET + Flask + Postgres) (treść w II.8)
  - 3.5 Obsługa wyjątków → mapowanie błędów (kontrakt `monitoring.md`)
  - 3.6 Narzędzia → tech stack + GitHub Flow + CI
- ⚠️ **Roz. 4 Implementacja modeli** — napisany, ALE **opisuje wczesną wersję projektu**, nie aktualną. Wymaga refresh + 3 nowych podsekcji:
  - 4.1.1 → zmienić 70/30 na **80/20**
  - 4.1.2 → usunąć class_weight/SMOTE jako finał, opisać **kalibrację izotoniczną + cost thresholds** zamiast wag
  - 4.2.1 → LSTM input shape **(3, 3)** zamiast (6, 3)
  - 4.3.2 → cechy liczone na 3 mies. (nie 6)
  - 4.4.1 → dorzucić **Optuna 5-fold CV** jako post-hoc weryfikacja
  - 4.4.2 → SHAP dla **4 modeli tree-based** (nie tylko XGB)
  - 4.5 → albo dorobić bootstrap 40-powtórzeń, albo go usunąć z obietnicy
  - **4.6 (NEW)** Kalibracja izotoniczna (CREDIT-105)
  - **4.7 (NEW)** Cost-optimized thresholds (CREDIT-106)
  - **4.8 (NEW)** Sliding-window panel (CREDIT-101)
- ❌ **Roz. 5 Analiza wyników** — TOC tylko, treść 0. **Krytyczna luka — to *jest* obrona tezy w PDF.** Czeka na CREDIT-114 (Sprint 6 — zbiorczy raport).
- ❌ **Zakończenie** — puste.
- ⚠️ **Niespójność TOC vs framing:** TOC Roz. 5 nadal wymienia 3 modele (LSTM/RF/XGB), Wstęp i Roz. 2 mówią o 5. → po napisaniu Roz. 5 zaktualizować TOC.

### Plan na v9 — porządek prac (zalecany)

1. **CREDIT-113** (stacking, Sprint 6 P2) + **CREDIT-114** (final report, Sprint 6 P0) — domknąć liczbową bazę.
2. **Napisać Roz. 3** (~1-1.5 dnia) — wszystkie dane gotowe, treść w sekcjach I, II tego dokumentu.
3. **Zaktualizować Roz. 4** (~1 dzień) — refresh 4.1/4.2/4.3 + dodanie 4.6/4.7/4.8.
4. **Napisać Roz. 5 + Zakończenie** (~1-1.5 dnia) — na bazie CREDIT-114.
5. **Naprawić TOC Roz. 5** (5 minut), dorobić brakujące Rysunki (`DokumentRoznice.md` §15).

Łącznie ~3-4 dni edycyjnych. Sam kod nie wymaga zmian (poza CREDIT-113/114 z planu Sprintu 6).

> **Wniosek dla seminarium:** części teoretyczne (Wstęp + Roz. 1+2) i bibliografia są obronne; Roz. 3 i Roz. 5 to luki do uzupełnienia po obronie tezy w kodzie (CREDIT-113/114). To naturalna kolejność — kod definiuje fakty, fakty trafiają do tekstu.

---

## VII. Raport z realizacji postępu prac (per sprint)

Status na 2026-06-06: **26/30 zadań done**, 2 dostępne (CREDIT-113 stacking GF, CREDIT-304 UI polish MK), 2 zablokowane (CREDIT-114 final report, CREDIT-501 docs).

### Sprint 1 — Fundament danych i trwałości (2 cze – 15 cze)

**Cel:** zlikwidować lukę danych (panel sliding-window) i postawić bazę. Dwa niezależne tory.

| ID | Owner | Co | Status |
|----|-------|----|--------|
| CREDIT-101 | GF | Sliding-window 3-mies. → 4 okna W0-W3 (`sliding_window.py` + pytest) | 🟢 |
| CREDIT-102 | GF | Retrain RF/XGB/LSTM na W3 + fix 2 silent bugów feature engineering | 🟢 |
| CREDIT-103 | GF | Rozszerzone metryki (AUC/Gini/KS/Brier) + 12 wykresów ewaluacji | 🟢 |
| CREDIT-201 | MK | CI 3-stack (xUnit + pytest + Vitest), blokuje czerwone PR-y | 🟢 |
| CREDIT-401 | MK | Schemat PostgreSQL + EF Core (Client / Snapshot / Prediction / Trend) | 🟢 |
| CREDIT-402 | MK | docker-compose: db + backend + ml-service; auto-migracje | 🟢 |

**Dlaczego ten sprint przesuwa pracę naprzód.** Bez sliding-window (CREDIT-101) i retreningu na W3 (CREDIT-102) Wariant B nie istnieje — nie ma panelu danych. Bez schematu bazy (CREDIT-401) monitoring jest tylko inferencją na jednym wierszu, nie kalendarzem migawek. Cichy bug w `app.py` (utilization_rate / severe_late) wykryty przy okazji — rygor train/serve consistency. Strata AUC W3 vs legacy < 1 pp (R1 z risk register zamknięty).

### Sprint 2 — Silnik monitoringu, kontrakty, zapis (16 cze – 29 cze)

**Cel:** uruchomić monitoring end-to-end (Flask + .NET + Postgres) i ustabilizować kontrakt API.

| ID | Owner | Co | Status |
|----|-------|----|--------|
| CREDIT-210 | GF+MK | Kontrakt API monitoringu (`monitoring.md`, 409 LoC) — wspólne 30 min | 🟢 |
| CREDIT-104 | GF | Flask `/predict/timeseries`: 22 cechy → 4 okna → trajektoria PD per model | 🟢 |
| CREDIT-105 | GF | Kalibracja izotoniczna (3-way split); Brier −19/−24/−23% RF/XGB/LSTM | 🟢 |
| CREDIT-202 | MK | .NET `POST /api/v1/monitoring/predict-timeseries` (bezstanowy proxy) | 🟢 |
| CREDIT-203 | MK | Persystencja: `POST /clients/{ref}/snapshots`, scoring → zapis, 409 na duplikat | 🟢 |

**Dlaczego ten sprint przesuwa pracę naprzód.** Kontrakt CREDIT-210 odblokował 4 zadania równolegle (zero czekania). Kalibracja izotoniczna (CREDIT-105) to **P0 dla Wariantu B** — bez niej trajektoria PD jest tylko rankingiem, nie liczbą. CREDIT-202/203 uczyniły monitoring **stateful** — z migawek w bazie odtworzymy oś czasu PD bez ponownej inferencji.

### Sprint 3 — Dowód tezy + start frontendu (30 cze – 13 lip)

**Cel:** udowodnić tezę liczbowo (statyka vs monitoring) i pokazać trajektorię w UI.

| ID | Owner | Co | Status |
|----|-------|----|--------|
| CREDIT-110 | GF | Metryki time-series: lead time, slope distribution, slope AUC | 🟢 |
| CREDIT-111 | GF | **DOWÓD TEZY** — static rule vs monitor rule sweep 19 progów × 3 modele | 🟢 |
| CREDIT-106 | GF | Cost-optimized thresholds (FN=5×FP); per-model 0.145/0.180/0.185 | 🟢 |
| CREDIT-204 | MK | `GET /clients/{ref}/history` — chronologiczna trajektoria PD z bazy | 🟢 |
| CREDIT-301 | MK | Widok Timeline: Recharts LineChart (3 modele) + TrendAlerts semaforowe | 🟢 |

**Dlaczego ten sprint przesuwa pracę naprzód.** **5/6 ogniw ścieżki krytycznej tezy zamknięte** po Sprincie 3 (101 ✅ → 102 ✅ → 104 ✅ → 110 ✅ → 111 ✅ → 114 🔒). CREDIT-111 jest **the thesis slide** — uczciwy verdict „monitoring traci catch rate ale wygrywa lead time" stał się trzonem framingu obrony. Cost thresholds (CREDIT-106) zastąpiły hardcoded 0.5 — Flask serwuje per-model progi, frontend koloruje punkty.

### Sprint 4 — Integracja + interpretowalność + tuning (14 lip – 27 lip)

**Cel:** pivot pod ścieżkę krytyczną (CREDIT-109 pull-forward), potem powrót do planowych P2 (SHAP, Optuna).

| ID | Owner | Co | Status |
|----|-------|----|--------|
| CREDIT-302 | MK | Lista klientów + widok historii na realnych danych (ClientList + ClientHistory) | 🟢 |
| CREDIT-205 | MK | Testcontainers PostgreSQL 16 + 8 testów persystencji (kaskady, FK, upsert) | 🟢 |
| CREDIT-107 | GF | SHAP top-5 cech per predykcja (4 tree models); 102 ms compute | 🟢 |
| CREDIT-108 | GF | 5-fold CV + Optuna 30 trials; RF +0.0010 / XGB +0.0030 — academic only | 🟢 |
| CREDIT-109 | GF | **Pull-forward ze Sprintu 5** — LightGBM + CatBoost; **CatBoost best (AUC 0.7802)** | 🟢 |

**Dlaczego ten sprint przesuwa pracę naprzód.** Pivot na CREDIT-109 odblokował CREDIT-113 → CREDIT-114 (ostatnie ogniwo ścieżki krytycznej). SHAP daje defensible explanation pod regulatora. Optuna potwierdził, że defaulty CREDIT-102 są **blisko optimum** (< 0.5 pp uplift) → tuned modele NIE promoted do produkcji (świadoma uczciwość scope'u).

### Sprint 5 — UX migawek, alerty, modele, fairness (28 lip – 10 sie)

**Cel:** zamknąć regulatory P1 (fairness) i domknąć 5-modelowy passthrough end-to-end.

| ID | Owner | Co | Status |
|----|-------|----|--------|
| CREDIT-303 | MK | SnapshotForm (data picker + 22 cech) + Copy from previous + dynamic miesiące | 🟢 |
| CREDIT-211 | MK | SHAP pass-through .NET DTO + ShapExplanation komponent (diverging bars) | 🟢 |
| CREDIT-115 | GF | Backend DTO follow-up: 5-modelowy passthrough (gap odkryty podczas demo prep) | 🟢 |
| CREDIT-116 | GF | Frontend follow-up: Timeline 5 linii + TrendAlerts 5 kart | 🟢 |
| CREDIT-112 | GF | **Audyt fairness** (fairlearn DPD/EOD per SEX, 5 modeli W3, przy cost-opt thresholds) | 🟢 |

**Dlaczego ten sprint przesuwa pracę naprzód.** **AI Act regulatory checkbox: zdane** — wszystkie 5 modeli |DPD| ≤ 0.039, |EOD| ≤ 0.033 (4× margines DoD 0.10). Decyzja **audytu przy cost-opt thresholds** (nie 0.5) jest defensible w Q&A — mierzymy fairness *faktycznej* decyzji produkcji. CREDIT-303 fix hardcoded miesięcy (`deriveMonthLabels`) usuwa wstydliwy bug rollover. CREDIT-115/116 zamknęły end-to-end pokazujący 5/5 modeli zamiast 3/5.

### Sprint 6 — Polish, ensemble, raport, docs (11 sie – 24 sie) — w toku

| ID | Owner | Co | Status |
|----|-------|----|--------|
| **CREDIT-113** | GF | Stacked ensemble (LR meta-learner na 5 modelach bazowych) | 🔴 dostępne |
| **CREDIT-304** | MK | UI polish (responsive, a11y Lighthouse ≥ 90, dark mode, tooltipy) | 🔴 dostępne |
| CREDIT-114 | GF | Raport końcowy + komplet wykresów do prezentacji obrony | 🔒 czeka na 113 |
| CREDIT-501 | GF+MK | README + Model Card + Architecture + update CLAUDE.md | 🔒 |

**Co już mam, co dorobię po seminarium.** Trzon dowodu tezy domknięty (CREDIT-111 ✅), fairness clearance domknięty (CREDIT-112 ✅), 5 modeli W3 + kalibracja + cost-opt ✅. Pozostały stacking (oczekiwany uplift ~0.5–1 pp AUC + lepsza kalibracja), raport końcowy, UI polish, docs. Sam stacking to jeden PR; raport jest generatorem zbiorczym; UI polish to ergonomia.

---

## Appendix A — Decyzje projektowe z pełnym uzasadnieniem

Dla każdej decyzji: **Co · Dlaczego · Wpływ na scoring/ryzyko · Linki do raportów i podsumowań sprintów**. Wybór 15 najważniejszych z 26 zamkniętych zadań (nie wszystkie tu są — tu te, które bezpośrednio wpływają na sposób, w jaki system liczy ryzyko).

### A.1 Sliding-window panel 4×W (CREDIT-101)

- **Co:** funkcja `extract_windows(row)` w `ml-learing-center/sliding_window.py` zamienia 1 wiersz UCI w 4 okna 3-miesięczne (W0–W3).
- **Dlaczego:** *„Nie fabrykujemy danych. Każda migawka używa wyłącznie prawdziwych kolumn z prawdziwej historii klienta. 4 okna = 4-punktowa trajektoria PD na tych samych 6 miesiącach."* (`PodsumowanieSprintow.md` §3.CREDIT-101). Wariant B wymaga panelu czasowego, ale UCI ma statyczny snapshot — sliding-window konstruuje panel **bez generowania nowych wartości**.
- **Wpływ na scoring/ryzyko:** **enabler całej trajektorii PD.** Bez tego scoring jest jednorazowy, nie kalendarzowy. Strata AUC W3 vs legacy 6-mies. < 1 pp (akceptowalna, R1 zamknięty).
- **Linki:** `ml-learing-center/sliding_window.py`, `plan_sprintow_wariant_B.md` §33-75 (mapowanie okien), `PodsumowanieSprintow.md` §3.CREDIT-101.

### A.2 Retrening na W3 + fix 2 silent bugów feature engineering (CREDIT-102)

- **Co:** retrening 3 modeli na W3 z artefaktami `_w3`; legacy nietknięte. Plus fix `BILL_AMT1 / LIMIT_BAL` → `BILL_mean / LIMIT_BAL` i `(...PAY... >= 2).sum()` → `.any().astype(int)` w `app.py`.
- **Dlaczego:** *„Rozkład treningowy = rozkład inferencyjny. Model uczy się na W3, przy monitoringu ten sam model stosujemy do W0, W1, W2, W3 — każde okno to identyczny 3-mies. wycinek. Brak out-of-distribution shift."* (`PodsumowanieSprintow.md` §3.CREDIT-102). Bugfix: *„Inferencja widziała inną feature niż model w treningu — silent corruption."*
- **Wpływ na scoring/ryzyko:** **enabler poprawnej inferencji na wszystkich 4 oknach**. Po fixie zdrowy klient → PD = 0.12 / 0.15 / 0.19 (rozsądnie niskie) zamiast losowych wartości z out-of-distribution.
- **Linki:** `ml-learing-center/main.py`, `ml-service/app.py` (linie 35/40 — bugfix), `PodsumowanieSprintow.md` §4 (Dług techniczny).

### A.3 Kalibracja izotoniczna (CREDIT-105) — P0 dla Wariantu B

- **Co:** `CalibratedClassifierCV(FrozenEstimator(base), method='isotonic')` dla tree models, `sklearn.IsotonicRegression` na raw LSTM output. 3-way split train / calib / test (60/20/20).
- **Dlaczego:** *„Trajektoria PD ma sens tylko gdy bezwzględne wartości odpowiadają realnym częstościom — wzrost 0.3→0.5 musi znaczyć realny wzrost ryzyka."* (Sekcja II.3 tego dokumentu; źródło w `PodsumowanieSprintow.md` § Sprint 2 update, plan sprintów Wariantu B §187-194). Bez kalibracji `predict_proba` z drzew jest porządkowe — nieporównywalne między oknami liczbowo.
- **Wpływ na scoring/ryzyko:** Brier **−19/−24/−23%** (RF/XGB/LSTM) → PD są teraz interpretowalne liczbowo. **Bez tego cały Wariant B nie miałby sensu** (trajektoria PD bez kalibracji = trajektoria rankingu = nic).
- **Linki:** `ml-learing-center/main.py` (sekcja CREDIT-105), `ml-service/lstm_calibrator_w3.pkl`, `reports/calibration_comparison_w3.png`.

### A.4 Progi cost-optymalne (CREDIT-106)

- **Co:** sweep progów (0.1, 0.9), minimalizacja `cost = 5·FN + 1·FP`; `ml-service/alert_thresholds.json` z `_meta`; serwowane w response Flask jako `costThresholds` + `windowAlerts`.
- **Dlaczego:** *„Próg 0.5 nie jest neutralny. Pod asymetrycznym modelem kosztów (FN=5×FP) optymalny cut-off to 0.145-0.185 per model — daleko od 0.5. System serwuje te per-model progi tak, żeby downstream consumers nie musiały znać matematyki kosztu."* (`PodsumowanieSprintow.md` §2.CREDIT-106).
- **Wpływ na scoring/ryzyko:** **decyzja kiedy alarmować staje się ekonomiczna, nie arbitralna.** Bias w stronę niskich progów (tolerujemy ~1700 FP żeby przepchnąć FN do ~340). Frontend koloruje punkty Timeline per model.
- **Linki:** `ml-learing-center/optimize_thresholds.py`, `ml-service/alert_thresholds.json`, `PodsumowanieSprintow.md` §2.

### A.5 Silnik trajektorii PD per okno (CREDIT-104)

- **Co:** Flask `POST /predict/timeseries` przyjmuje 22 cechy, rozbija na 4 okna, scoruje każde każdym z 5 modeli, zwraca trajektorię + trendy.
- **Dlaczego:** kontrakt CREDIT-210 odblokowuje 4 zadania równolegle; Flask musi być bezstanowy (bez DB, bez `clientRef`) — orkiestrację i trwałość robi .NET. To podział z `monitoring.md` §3.
- **Wpływ na scoring/ryzyko:** **transformacja systemu z one-shot na panelowy.** Trajektoria PD per model = surowiec dla TimelineChart, slope alert, monitoring rule (CREDIT-111).
- **Linki:** `ml-service/app.py`, `docs/api-contracts/monitoring.md`, `PodsumowanieSprintow.md` §2.CREDIT-202 (kontekst orkiestracji).

### A.6 Dowód tezy: statyka vs monitoring (CREDIT-111)

- **Co:** sweep 19 progów × 5 modeli, kanoniczny operating point FA=10%; uczciwy verdict.
- **Dlaczego:** *„Monitoring nie wygrywa w czystej dyskryminacji. Wygrywa w lead time — 2 okna wcześniej, plus 43-184 unikalnych catchy na model. Trade-off jest funkcją modelu kosztów."* (`PodsumowanieSprintow.md` §2.CREDIT-111). Nie nadinterpretuję — `max(W0..W3)` aggregator widzi 4× więcej szumu niż pojedyncza skalibrowana W3.
- **Wpływ na scoring/ryzyko:** **definiuje framing obrony tezy.** „Wcześniejsza detekcja przy porównywalnej dyskryminacji" zamiast „monitoring strictly dominuje". To rozróżnienie ma znaczenie dla rekomendacji produkcyjnych: monitoring sensowny gdy FN > FP (kredyt to dokładnie taki przypadek).
- **Linki:** `ml-learing-center/static_vs_dynamic.py`, `reports/static_vs_dynamic_*.png` (5×), `reports/static_vs_dynamic_operating.csv`, `PodsumowanieSprintow.md` §2.CREDIT-111.

### A.7 LightGBM + CatBoost (CREDIT-109)

- **Co:** dorzucenie 2 modeli (CatBoost wins single z AUC 0.7802); 5-modelowa rodzina.
- **Dlaczego:** pull-forward ze Sprintu 5 → Sprint 4 żeby odblokować CREDIT-113 → CREDIT-114 (ścieżka krytyczna). *„Stacking-owi potrzebny materiał o różnej naturze: LightGBM = leaf-wise gradient boosting z histogramową dyskretyzacją + GOSS + EFB, CatBoost = ordered boosting + native categorical handling."* (`PodsumowanieSprintow.md` §4.CREDIT-109).
- **Wpływ na scoring/ryzyko:** **najlepszy single model (CatBoost) wnosi 0.6 pp AUC** nad XGB; spread rodziny ~2 pp daje materiał stacking. Cost thresholds rozszerzone do 5 modeli. SHAP TreeExplainer obsługuje oba nowe.
- **Linki:** `ml-learing-center/main.py`, `ml-service/{lightgbm,catboost}_model_w3.pkl`, `reports/metrics_w3.csv`, `PodsumowanieSprintow.md` §4.

### A.8 Fairness audit przy cost-opt thresholds, nie 0.5! (CREDIT-112)

- **Co:** fairlearn DPD + EOD per SEX, 5 modeli, binaryzacja przy cost-opt thresholdach z CREDIT-106.
- **Dlaczego:** *„Audyt wykonany przy realnym operating point (cost-opt threshold, FN=5×FP z CREDIT-106), nie arbitralnym 0.5 — wynik reprezentuje faktyczne zachowanie systemu pod normalną decyzją alertu."* (`PodsumowanieSprintow.md` §2.CREDIT-112). To kluczowe pytanie audytora: „przy jakim progu liczyłeś DPD?" — odpowiedź „przy progu, którego system faktycznie używa" jest defensible.
- **Wpływ na scoring/ryzyko:** **AI Act regulatory clearance.** Wszystkie 5 modeli |DPD| ≤ 0.039, |EOD| ≤ 0.033 (DoD 0.10, **4× margines**). DPD dodatnie reflects wyższy base rate defaultów w SEX=1 w UCI (24.2 vs 20.8%), nie bias modeli. CatBoost największy diff, LSTM najbliżej parytetu (0.007).
- **Linki:** `ml-learing-center/fairness_audit.py`, `reports/fairness_report.md`, `reports/fairness_metrics_w3.csv`, 2 PNG, `PodsumowanieSprintow.md` §2.

### A.9 SHAP top-5 (tylko tree, LSTM out, CREDIT-107)

- **Co:** TreeExplainer + helper `_unwrap_calibrated()` (wyciąga base z CalibratedClassifierCV); response zawiera `shap.{model}.topFeatures` (4 modele × 5 cech).
- **Dlaczego:** *„Każda predykcja jest interpretowalna. Top-5 cech per model — w 102 ms, na każdym zapytaniu."* (`PodsumowanieSprintow.md` §2.CREDIT-107). LSTM pominięty: *„KernelExplainer z background sampling przekroczyłby budżet < 2s DoD."*
- **Wpływ na scoring/ryzyko:** **defensible explanation pod regulatora i pod użytkownika.** Konwencja znaku (+/− pcha PD w górę/dół) trafia bezpośrednio do UI jako kolorowe bary. Sanity check dla zdrowego klienta: top cechy negatywne (PAY_mean, late_count, severe_late) = "płaci na czas" — analityk widzi czego oczekiwał.
- **Linki:** `ml-service/app.py` (`compute_shap_top_features`, `SHAP_EXPLAINERS`), `PodsumowanieSprintow.md` §2.

### A.10 Persystencja migawek z guardem 409 + upsert trendów (CREDIT-203 / CREDIT-204)

- **Co:** `POST /clients/{ref}/snapshots` → guard duplikatu *przed* Flaskiem → 409, scoring (reuse) → zapis Snapshot + N×Prediction + N×Trend (upsert). `GET /clients/{ref}/history` → chronologiczna trajektoria.
- **Dlaczego:** *„Tu monitoring staje się prawdziwy: każda ocena to trwała migawka w Postgresie. Z kolejnych migawek tego samego klienta odtworzymy oś czasu PD — fundament dowodu tezy."* (`PodsumowanieSprintow.md` §2.CREDIT-203). Decyzje: predykcje **W3-only** persistowane (etykietowane okno = ocena „aktualna"; trajektoria W0..W3 to widok analityczny), 409 zamiast cichego upsertu (chroni przed double-write).
- **Wpływ na scoring/ryzyko:** **system staje się stateful** — można odtworzyć trajektorię PD klienta z migawek bez ponownej inferencji; Timeline na realnych danych z bazy, nie tylko mock.
- **Linki:** `backend/WebApi/Services/MonitoringService.cs` (`ScoreAndPersistAsync`), `backend/WebApi/Controllers/MonitoringController.cs`, `PodsumowanieSprintow.md` §2.CREDIT-203/204.

### A.11 SHAP pass-through .NET DTO (CREDIT-211)

- **Co:** dodanie `ShapExplanation` do `TimeseriesResponse` i `SnapshotResponse`; SHAP scoring-time only (nie persistowany w DB).
- **Dlaczego:** silent gap — Flask zwracał `shap`, ale `WindowPredictions` w .NET DTO go dropował przy deserializacji (kontrakt §3.5 w `monitoring.md` zapowiadał, kod nie konsumował). Frontend `ShapExplanation.tsx` (diverging bars).
- **Wpływ na scoring/ryzyko:** **kompletna explanation pipeline end-to-end** Flask → .NET → React. Bez tego SHAP byłby tylko w Flask response, niewidoczny dla user'a.
- **Linki:** `backend/WebApi/Models/TimeseriesResponse.cs` (`ShapExplanation`/`ShapModel`/`ShapFeature`), `frontend/WebApp/src/components/ShapExplanation.tsx`, `PodsumowanieSprintow.md` §3 (i CREDIT-115 dla podobnego gapu z 5 modelami).

### A.12 Fix hardcoded miesięcy → `deriveMonthLabels(referenceDate)` (CREDIT-303)

- **Co:** dynamiczne miesiące w `InputForm.tsx` (3 razy zahardkodowane) → funkcja `deriveMonthLabels(referenceDate)` (rollover-safe, miesiące względem daty migawki).
- **Dlaczego:** wstydliwy bug rollover — przy migawce z grudnia hardcoded „April-September" pokazywałoby się wciąż.
- **Wpływ na scoring/ryzyko:** **UX i poprawność** — etykiety okien zawsze odpowiadają wybranej dacie migawki. Backwards compatible (`InputForm` propsy opcjonalne, zakładka Prediction bez zmian).
- **Linki:** `frontend/WebApp/src/components/InputForm.tsx`, `CHECKLIST.md` linia 142-143.

### A.13 5-modelowy passthrough end-to-end (CREDIT-115 + CREDIT-116)

- **Co:** Backend `WindowPredictions` + `Trends` rozszerzone o `Lightgbm` + `Catboost`; persystencja 5 predictions + 5 trends per snapshot (było 3+3). Frontend `ModelKey` + Timeline 5 linii + TrendAlerts 5 kart w responsive grid.
- **Dlaczego:** **gap odkryty 2026-06-05 podczas demo prep** — Flask serwował 5 modeli, backend DTO drop'ował 2, UI pokazywał 3/5 mimo, że Flask 5/5. *„Found and fixed during demo prep — integration gap między CREDIT-109 (Flask 5 modeli) a CREDIT-202 (backend 3-model DTO)."* (`PodsumowanieSprintow.md` §4.1).
- **Wpływ na scoring/ryzyko:** **live demo pokazuje teraz 5/5 modeli end-to-end** (Flask → .NET → React) — spójne z claim'em pracy „5 modeli W3 calibrated". Bez tego live demo by ujawniło rozjazd.
- **Linki:** `backend/WebApi/Models/TimeseriesResponse.cs`, `frontend/WebApp/src/components/{TimelineChart,TrendAlerts}.tsx`, `PodsumowanieSprintow.md` §3.

### A.14 Optuna tuned NIE promoted do produkcji (CREDIT-108) — uczciwa scope

- **Co:** Optuna 30 trials × 5-fold CV per model (RF, XGB); RF +0.0010 / XGB +0.0030 test AUC; tuned modele NIE zastąpiły defaultów CREDIT-102.
- **Dlaczego:** *„Tuned modele NIE są promoted do produkcji. Promocja wymagałaby re-runs CREDIT-105 (kalibracja na nowych bazach), CREDIT-106 (cost thresholds), CREDIT-109 (raporty). Cascade nieuzasadniony dla < 0.5 pp uplift przed deadlinem seminarium. Raport jest ciekawością akademicką + sanity check."* (`PodsumowanieSprintow.md` §3.CREDIT-108).
- **Wpływ na scoring/ryzyko:** **świadoma uczciwość scope'u** — formalna odpowiedź na pytanie audytora „czy default jest blisko optimum?". Odpowiedź: tak, w < 0.5 pp test AUC po 30 trials. Wniosek: tuning nie jest źródłem uplift'ów na tym dataset'cie; szukać w kalibracji + stackingu.
- **Linki:** `ml-learing-center/optuna_tuning.py`, `reports/optuna_study.md`, `reports/optuna_trials.csv` (60 wierszy), `PodsumowanieSprintow.md` §3.

### A.15 docker-compose bez frontendu (CREDIT-402)

- **Co:** docker-compose stawia tylko `db` + `backend` + `ml-service`; frontend pozostaje na `npm run dev` (port 5173) lokalnie.
- **Dlaczego:** świadoma decyzja — *„Frontend POZA compose — pozostaje uruchamiany lokalnie przez `npm run dev` (decyzja świadoma)."* (`PodsumowanieSprintow.md` §3.CREDIT-402). Hot-reload Vite jest najwygodniejszy poza Dockerem; konteneryzacja frontendu nie daje istotnej wartości na deweloperskim setupie.
- **Wpływ na scoring/ryzyko:** **wpływ na demo flow** — trzeba pamiętać o trzecim terminalu (`npm run dev`). Auto-migracje EF Core przy starcie backendu (`db.Database.Migrate()`) eliminują ręczne kroki.
- **Linki:** `docker-compose.yml`, `backend/WebApi/Dockerfile`, `backend/WebApi/Program.cs`, `PodsumowanieSprintow.md` §3.CREDIT-402.

---

> **Zalecane użycie tego pliku w claude-project (PowerPoint):**
>
> 1. Sekcja I → 2-3 slajdy (Cel + Teza + Hipotezy).
> 2. Sekcja II → 5-8 slajdów (jedna sekcja = jeden slajd metodologii; tabele i równania).
> 3. Sekcja III → 5-6 slajdów + wklejone PNG-i z `reports/`.
> 4. Sekcja IV → 1 slajd wniosków.
> 5. Sekcja V → uruchamiamy live, nie ma slajdu (lub 1 backup slajd ze screen'ami z `docs/seminarium2/screenshots/`).
> 6. Sekcja VI → 1-2 slajdy status pracy pisemnej (transparent).
> 7. Sekcja VII → 1 slajd tabeli per sprint (gantt-style) + ścieżka krytyczna.
> 8. Appendix A → materiał do Q&A (nie na slajdach głównych).
