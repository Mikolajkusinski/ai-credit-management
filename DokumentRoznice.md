# DokumentRoznice.md — różnice między „Praca Magisterska-6.pdf" a stanem projektu

> Dokument porównuje wersję **Praca Magisterska-6.pdf** (21 stron, ~1440 linii tekstu po
> ekstrakcji) ze stanem implementacji w `main` na 2026-06-06 (po merge CREDIT-112 + Sprint 5).
> Źródła porównania po stronie projektu: `plan_sprintow_wariant_B.md`, `CHECKLIST.md`,
> `PodsumowanieSprintu{1..5}_*.md`, kod (`ml-learing-center/`, `ml-service/`, `backend/`,
> `frontend/`), kontrakt API (`docs/api-contracts/monitoring.md`) oraz raporty
> (`ml-learing-center/reports/`).
>
> **Cel:** zaplanować poprawę dokumentu tak, żeby treść pisemna odpowiadała temu, co system
> rzeczywiście robi. Każdy punkt zawiera *gdzie w PDF*, *jak jest w projekcie*, *propozycję poprawki*.

---

## 0. Status PDF na wejściu — co jest, a czego nie ma

**Spisany merytorycznie (Roz. 1, 2, 4):**
- Roz. 1 (kredyt i ocena zdolności kredytowej) — pełny.
- Roz. 2 (ML w finansach, charakterystyka 3 algorytmów, fairness/AI Act) — pełny.
- Roz. 4 (implementacja LSTM, RF, XGBoost) — pełny w sekcjach 4.1–4.5.
- Wstęp + Bibliografia + Spis rysunków — pełne.

**Tylko śródtytuły, BRAK treści:**
- **Roz. 3 (Metodologia badań i projekt systemu)** — sekcje 3.1–3.6 mają tylko tytuły (źródła danych,
  hipotezy, opis zmiennych, **projekt architektury systemu**, **integracja modeli z systemem**,
  obsługa wyjątków, narzędzia). **Cała architektura systemu eksperymentalnego (frontend + backend
  + ML service + DB) jest NIENAPISANA.**
- **Roz. 5 (Analiza wyników)** — sekcje 5.1–5.6 mają tylko tytuły (metryki, wyniki per model,
  porównanie, dyskusja, weryfikacja hipotez). **Cała ewaluacja modeli + dowód tezy jest
  NIENAPISANA.**
- **Zakończenie** — tylko tytuł, brak treści.

> To największe „makro-różnice": dwa kluczowe rozdziały (system + wyniki) są szkieletem do
> uzupełnienia. Reszta dokumentu wymaga *aktualizacji*, te dwa wymagają *napisania od zera*.

---

## 1. Teza, hipotezy, framing tytułu

### 1.1. „Dynamiczne" — dwa różne znaczenia

| Aspekt | PDF (wersja 6) | Projekt (Wariant B) |
|---|---|---|
| Sens słowa „dynamiczne" w tytule | „architektura LSTM, która z założenia traktuje ocenę jako funkcję sekwencji zdarzeń, a nie pomiar statyczny" (Roz. 4 intro) | **Monitoring kalendarzowy** — ten sam klient oceniany wielokrotnie w czasie; system śledzi trajektorię PD i wykrywa pogorszenie **zanim** wystąpi default |
| Co jest „dynamiczne" | architektura modelu (LSTM sekwencyjny vs RF/XGB statyczny) | **schemat oceny** (sliding-window W0..W3 + 4-punktowa trajektoria PD per model) |
| Co kontrastuje z czym | LSTM ↔ RF/XGB (porównanie *algorytmów*) | statyka W3 ↔ monitoring W0..W3 (porównanie *reguł decyzyjnych*) |

**Problem:** PDF mówi „LSTM > statyka", projekt udowadnia „monitoring W0..W3 > jednorazowa W3"
(CREDIT-111). To są **różne tezy**. PDF nie zna sliding-window, projekt nie ogranicza sequenced
porównania do LSTM-vs-tree.

**Propozycja:** przeredagować Wstęp (s. 1–2) i intro Roz. 4 (s. 21) — wprowadzić oba znaczenia
„dynamiczne":
1. **Dynamiczna architektura** (LSTM sekwencyjny — pozostawić obecne sformułowanie).
2. **Dynamiczna ocena (Wariant B)** — sliding-window 4-okienkowy → monitoring kalendarzowy →
   trajektoria PD per model → wczesne ostrzeganie. **To jest właściwa teza pracy.**

### 1.2. Hipotezy badawcze (Roz. 3.2 — pusty)

Roz. 3.2 ma tylko tytuł. **Brakuje formalnych hipotez.** Projekt ma 3 zweryfikowane:

| H | Treść | Gdzie udowodnione w projekcie |
|---|---|---|
| H1 | „Sliding-window 3-mies. (W3) zachowuje AUC blisko legacy 6-mies. (strata < 1 pp)" | CREDIT-102 — RF 0.7779 vs 0.7792, XGB 0.7794 vs 0.7818, LSTM 0.7637 vs 0.7686 |
| H2 | „Monitoring W0..W3 oferuje **wcześniejszą detekcję przy porównywalnej dyskryminacji** względem statyki W3" | CREDIT-110 (lead time ~2 okna) + CREDIT-111 (honest verdict @FA=10%) |
| H3 | „Modele zachowują się fair względem atrybutu chronionego SEX (|DPD|/|EOD| ≤ 0.10)" | CREDIT-112 — wszystkie 5 modeli |diff| ≤ 0.04 |

**Propozycja:** napisać Roz. 3.2 wokół tych 3 hipotez. Roz. 5.6 (dyskusja + weryfikacja) ma się do
nich literalnie odnosić.

---

## 2. Dane i preprocessing

### 2.1. Sliding-window panel (CREDIT-101) — całkowicie NIEUWZGLĘDNIONY w PDF

**PDF:** opisuje 6-miesięczne okno bez sliding-window. LSTM ma input shape `(6, 3)` (sekcja 4.2.1,
s. 26):
```python
pay_seq_cols = ["PAY_6", "PAY_5", "PAY_4", "PAY_3", "PAY_2", "PAY_0"]   # 6 mies.
bill_seq_cols = ["BILL_AMT6", ..., "BILL_AMT1"]
pay_amt_seq_cols = ["PAY_AMT6", ..., "PAY_AMT1"]
```

**Projekt:** od CREDIT-101 (Sprint 1) jeden wiersz UCI → **4 okna 3-miesięczne** (W0..W3); modele
trenowane na W3 (najnowsze 3 mies., zgodne z etykietą październikową), inferencja na każdym z
W0..W3 ⇒ 4-punktowa trajektoria PD. LSTM input shape `(N, 3, 3)`. Pliki:
`ml-learing-center/sliding_window.py`, `features.py` (parametryzowane oknem), artefakty z sufiksem
`_w3` (`rf_model_w3.pkl`, `xgb_model_w3.pkl`, `lstm_model_w3.keras`, etc.).

**Propozycja:** **napisać nową sekcję 3.3.4 „Konstrukcja panelu sliding-window"** w Roz. 3 (lub
przenieść jako 4.0 przed treningiem). Wymagana zawartość:
1. Tabela 4 okien (W0..W3) wg `plan_sprintow_wariant_B.md` (PAY_6/5/4 → PAY_3/2/0).
2. Uzasadnienie zgodności rozkładów trening (W3) vs inferencja (W0..W3).
3. Dlaczego brak augmentacji wielo-okiennej (ryzyko wycieku etykiet).
4. **Zasada „nie fabrykujemy danych"** — każde okno to realny 3-mies. wycinek historii klienta.

### 2.2. Podział zbioru — 70/30 (PDF) vs 80/20 (projekt)

**PDF (sek. 4.1.1, s. 22):** test=30% (9 000), train=70% (21 000), z train odcięte 20% jako
walidacja LSTM ⇒ 56/14/30.

**Projekt:** test=20% (6 000), train=80% (24 000), `random_state=42`, `stratify=y`. Confirmed
w CREDIT-103, CREDIT-105 (3-way split train/calib/test dla kalibracji), CREDIT-110/111/112
(wszystkie reprodukują 80/20 split test = 6 000). Test set jest **byte-identyczny** w całym
pipeline'ie ewaluacyjnym.

**Propozycja:** zaktualizować sek. 4.1.1 — opisać 80/20; dodać informację, że dla CREDIT-105
(kalibracja) wprowadzono **3-way split** train/calib/test (np. 60/20/20), żeby kalibrator izotoniczny
nie widział danych treningowych modelu bazowego (FrozenEstimator + isotonic).

### 2.3. Niezbalansowanie klas — class weighting (PDF) vs cost thresholds + kalibracja (projekt)

**PDF (sek. 4.1.2, s. 24):** finalna decyzja = `class_weight="balanced"` (RF, LSTM) +
`scale_pos_weight` (XGB). SMOTE testowany i odrzucony — opis Rysunku 4.2 jako analiza
alternatyw.

**Projekt:** **NIE używa class_weight ani scale_pos_weight w finalnych modelach W3**. Zamiast tego:
1. **Kalibracja izotoniczna** (CREDIT-105) — `CalibratedClassifierCV(FrozenEstimator(base), isotonic)`
   dla RF/XGB/LightGBM/CatBoost; sklearn `IsotonicRegression` na raw LSTM output. Brier −19/−24/−23%.
2. **Cost-optimized thresholds** (CREDIT-106) — minimalizacja `cost = 5·FN + 1·FP` per model;
   progi 0.130–0.185 (vs hardcoded 0.5). Bias w stronę niskich progów odzwierciedla asymetrię
   kosztu (FN=5×FP).

**Propozycja:** **przepisać sek. 4.1.2** całkowicie:
- Usunąć/zminimalizować dyskusję class_weight/SMOTE jako „rozważone alternatywy".
- **Wprowadzić nową sek. 4.6 „Kalibracja prawdopodobieństw (isotonic)"** — opis CREDIT-105,
  uzasadnienie (w Wariancie B trajektoria PD ma sens tylko gdy bezwzględne PD odpowiadają
  częstościom empirycznym).
- **Wprowadzić nową sek. 4.7 „Progi alertu optymalne kosztowo"** — opis CREDIT-106,
  `alert_thresholds.json`, ratio FN:FP=5:1.

---

## 3. Modele — 3 vs 5

**PDF:** opisuje 3 modele (LSTM, RF, XGBoost) w sek. 2.3 + 4.2/4.3/4.4. Roz. 5 (struktura) ma 3
sekcje wyników per model.

**Projekt:** **5 modeli W3 calibrated** (RF, XGBoost, LightGBM, CatBoost, LSTM). CREDIT-109
(merged 2026-06-04) dodał LightGBM + CatBoost. CatBoost najlepszy single model (AUC 0.7802,
Brier 0.1354). 5-model passthrough end-to-end po CREDIT-115 (.NET DTO) + CREDIT-116
(React UI).

**Propozycja:**
1. **Rozszerzyć sek. 2.3** o:
   - 2.3.4 „LightGBM — gradient boosting z leaf-wise growth"
   - 2.3.5 „CatBoost — ordered boosting + native categorical handling"
2. **Dodać sek. 4.4a i 4.4b** (lub 4.5/4.6 — patrz §2.3 wyżej) z implementacją obu.
3. **Roz. 5 zaplanować na 5 modeli**, nie 3.
4. **Sekcja 5.3** (porównanie) powinna mieć tabelę 5×4 (5 modeli × AUC/Gini/KS/Brier) — wszystkie
   dane są w `ml-learing-center/reports/metrics_w3.csv` i podsumowaniach sprintów.

---

## 4. Inżynieria cech

### 4.1. Lista cech

**PDF (sek. 4.3.2, s. 32):** wymienia: PAY_max, late_count, recent_pay_status, utilization_rate,
BILL_trend, severe_late, payment_ratio + cechy demograficzne (AGE, EDUCATION, MARRIAGE, SEX).
Liczone na **6 miesiącach**.

**Projekt (`features.py`):** **32 cechy** dla RF/XGB/LightGBM/CatBoost: 13 pochodnych liczonych na
**3 miesiącach okna** (PAY_mean, PAY_max, BILL_mean, BILL_std, BILL_trend, payment_ratio,
late_count, severe_late, utilization_rate, recent_pay_status) + 9 surowych kolumn okna + one-hot
SEX/EDUCATION/MARRIAGE.

**Propozycja:** zaktualizować sek. 4.3.2 / dodać do nowego Roz. 3.3.3:
- Pełna lista 13 pochodnych cech + ich definicje (są w docstringach `engineer_features()`).
- Wyjaśnienie, że cechy są parametryzowane oknem (`engineer_features(df, window)`).
- LSTM otrzymuje surowy tensor `(3, 3)`, nie agregowane cechy — kontrast wyjaśnić explicite.

### 4.2. Bug-fix `utilization_rate` / `severe_late`

**PDF:** brak.

**Projekt:** w CREDIT-102 (Sprint 1) naprawiono 2 silent bugi w `ml-service/app.py` rozjazdu
między `main.py` (trening) a `app.py` (inferencja): `BILL_AMT1 / LIMIT_BAL` → `BILL_mean /
LIMIT_BAL`, `(...PAY... >= 2).sum()` → `(...PAY... >= 2).any().astype(int)`.

**Propozycja:** ten szczegół warto wzmiankować w Roz. 4.5 lub w „Implementacja" — jako przykład
disciplined fix podczas analizy pre-existing kodu (godne pracy magisterskiej, pokazuje rygor train/
serve consistency).

---

## 5. Walidacja i strojenie hiperparametrów

### 5.1. Cross-validation — schematyczny (PDF) vs prawdziwy (projekt)

**PDF (sek. 4.4.1, s. 34 i sek. 4.5):** „walidację krzyżową 5-fold zaprezentowano **schematycznie**,
natomiast do właściwej oceny modeli przyjęto pojedynczy, stratyfikowany podział 70/30".
Uzasadnienie: koszt obliczeniowy.

**Projekt:** **CREDIT-108 zrobił prawdziwe 5-fold StratifiedKFold** + Optuna 30 trials per model
(RF, XGB). Test AUC: RF +0.0010 / XGB +0.0030 vs default. Raport `reports/optuna_study.md` +
`optuna_trials.csv` (60 trials).

**Propozycja:** **przepisać sek. 4.4.1** + dodać nową sek. 4.5b „Strojenie Optuna (TPESampler) +
5-fold CV":
- Opisać przestrzeń hiperparametrów (RF: `n_estimators ∈ 200-800`, `max_depth ∈ 5-16`, etc.;
  XGB: `learning_rate ∈ 0.005-0.1 log`, etc. — szczegóły w `PodsumowanieSprintu4_GF.md §3`).
- Pokazać tabelę CV mean ± std default vs tuned.
- **Honest framing:** uplift < 0.5 pp test AUC, **tuned modele NIE promoted do produkcji** (cascade
  redo CREDIT-105/106/109 nieuzasadniony). Akademicki sweep.

### 5.2. Grid Search XGBoost

**PDF (sek. 4.4.1):** opisuje grid search heatmap (learning_rate × max_depth).

**Projekt:** initial defaulty z CREDIT-102, później Optuna w CREDIT-108. Brak grid search — wynik
jest spójny (XGB defaulty `lr=0.02, depth=4, n_est=800` ⊂ optimum znalezione przez Optuna).

**Propozycja:** zachować opis grid search jako *kontekst dla defaultów CREDIT-102*, ale dodać
sekcję Optuna jako *systematyczne strojenie* po fakcie. Reframing: „defaulty CREDIT-102 zostały
wybrane na podstawie heatmap; Optuna w CREDIT-108 zweryfikował, że są blisko optimum (< 0.5 pp)".

### 5.3. Bootstrap 40-powtórzeń (PDF) — nie istnieje w projekcie

**PDF (sek. 4.5, s. 38):** „raportowana w rozdziale 5 wariancja AUC, obliczona na podstawie 40
bootstrapowanych powtórzeń zbioru testowego".

**Projekt:** **nie ma bootstrapu.** Reports/CSVs są pojedynczymi runami (jeden split, jeden test
set, jedno AUC).

**Propozycja:** albo (a) **zrobić bootstrap** w CREDIT-114 (final report) — szybkie, sensowne dla
pracy magisterskiej; albo (b) **usunąć obietnicę** z sek. 4.5 i opisać że stabilność jest weryfikowana
przez 5-fold CV Optuna (CREDIT-108) zamiast bootstrap.

---

## 6. Kalibracja prawdopodobieństw — kompletnie POMINIĘTA w PDF

**PDF:** **brak** — ani jednej wzmianki o kalibracji w sek. 4.

**Projekt:** **CREDIT-105 (P0!)** — kluczowa decyzja Wariantu B. Bez kalibracji wartości PD są
porównywalne tylko w obrębie modelu (ranking-only), nie absolutnie ⇒ trajektoria PD W0..W3 nie
ma sensu liczbowego. Implementacja: `CalibratedClassifierCV(FrozenEstimator(base), method='isotonic')`
dla 4 tree-based + `sklearn.IsotonicRegression` na raw LSTM output. **Brier −19% (RF), −24%
(XGB), −23% (LSTM)**, AUC zachowane.

**Propozycja:** **dodać sek. 4.6 „Kalibracja izotoniczna" jako P0 w Roz. 4:**
- Uzasadnienie metodologiczne (Brier, reliability diagram, 3-way split).
- Dlaczego isotonic, nie Platt (nieparametryczne, mniej restrykcyjne dla nieliniowych
  rozjazdów).
- Implementacja `CalibratedClassifierCV(FrozenEstimator)` (sklearn ≥1.6).
- LSTM zewnętrzny kalibrator (`lstm_calibrator_w3.pkl`).
- **Tabela Brier przed/po** dla 5 modeli (CREDIT-109 rozszerzyło).

---

## 7. Monitoring kalendarzowy + dowód tezy „statyka vs dynamika" — POMINIĘTE w PDF

**PDF:** brak. Sek. 4 kończy się ewaluacją modeli W3, brak słowa o monitoringu trajektorii.

**Projekt (kluczowe!):**
1. **CREDIT-110** (`timeseries_eval.py`) — metryki time-series: catch_rate, lead_time, slope_auc.
   Wyniki: ~50% catch rate @ próg 0.5, mean lead ~2.05 okien, slope_auc ~0.59 vs w3_auc ~0.77.
2. **CREDIT-111** (`static_vs_dynamic.py`) — **THE thesis slide**. Static rule (PD_W3 ≥ θ) vs
   monitoring rule (max(PD_W0..W3) ≥ θ). Honest verdict @FA=10%: monitoring traci 2-6pp catch vs
   static (aggregator noise), ale wygrywa lead time (~2 okna) + 43-184 unique catches/model.
3. **Framing:** „monitoring oferuje wcześniejszą detekcję przy porównywalnej dyskryminacji".

**Propozycja:** **napisać Roz. 5.4-5.6 wokół tej tezy:**
- Sek. 5.4 reinterpretować z „porównanie z klasycznymi metodami scoringowymi" na **„statyka
  W3 vs monitoring W0..W3" (dowód Wariantu B)**.
- Pokazać ROC overlay per model z `reports/static_vs_dynamic_*.png` (3 PNG aktualnie + 2 brakujące
  dla LightGBM/CatBoost — w CSV są).
- Sek. 5.5 reinterpretować z „interpretowalność" na **„lead time + slope distribution"** (CREDIT-110
  reports/PNG).
- **Sek. 5.6 (dyskusja hipotez)** literalnie odnieść się do H1/H2/H3 z §1.2 wyżej.

---

## 8. Fairness — skromne w PDF, pełny audyt w projekcie

**PDF (sek. 2.5, s. 19):** ogólne uwagi etyczne, AI Act, RODO. W sek. 4.3.2 (s. 32) jednorazowe
zdanie: „ograniczona waga zmiennych chronionych [w RF feature importance] zmniejsza ryzyko
dyskryminacji pośredniej".

**Projekt:** **CREDIT-112 (P1, świeżo merged 2026-06-06)** — pełny audyt fairlearn DPD/EOD per
SEX dla **5 modeli W3** przy **cost-opt thresholds** z CREDIT-106. Wyniki:

| Model | DPD | EOD |
|---|---|---|
| RF | +0.0347 | +0.0289 |
| XGBoost | +0.0377 | +0.0333 |
| LightGBM | +0.0269 | +0.0215 |
| **CatBoost** | **+0.0393** | **+0.0334** (max) |
| **LSTM** | **+0.0068** | **+0.0153** (min, najbliżej parytetu) |

Wszystkie |diff| ≤ 0.04 (DoD 0.10, **4× margines**). Pliki: `reports/fairness_report.md`,
`fairness_metrics_w3.csv`, 2 PNG (`fairness_selection_rate_w3.png`, `fairness_tpr_fpr_w3.png`).

**Propozycja:** **dodać do Roz. 5 nową sek. 5.5b „Audyt fairness względem atrybutów chronionych":**
- Definicje DPD i EOD (z fairlearn).
- Decyzja metodologiczna: **binaryzacja przy cost-opt threshold, nie 0.5** (defensible).
- Tabela wyników 5×2.
- Per-group breakdown (sel_rate, TPR, FPR per SEX) — wszystkie są w `fairness_metrics_w3.csv`.
- **Framing dla obrony:** DPD dodatnie odzwierciedla wyższy base rate defaultów w grupie SEX=1
  w UCI, nie bias modeli. CatBoost największy diff, LSTM najbliżej parytetu.
- Odniesienie do H3 z §1.2.

---

## 9. SHAP — tylko XGB w PDF, 4 modele w projekcie

**PDF (sek. 4.4.2, s. 36):** SHAP tylko dla XGBoost. Rysunek 4.8 (beeswarm + bar plot).

**Projekt:** **CREDIT-107** — SHAP top-5 cech per predykcja dla **4 tree-based models**: RF, XGB,
LightGBM, CatBoost. LSTM pominięty (TreeExplainer N/A, KernelExplainer >2s DoD).
`compute_shap_top_features()` w `ml-service/app.py` zwraca w response Flask. Performance: **102 ms
(20× pod DoD)**. Wpięte do .NET DTO (CREDIT-211) + React `ShapExplanation.tsx`.

**Propozycja:**
- **Rozszerzyć sek. 4.4.2** na 4 modele (lub przenieść SHAP do osobnej sek. 4.8 jako wspólny
  feature pipeline'u).
- Opisać convention znaku (wartość > 0 ⇒ pcha PD w górę).
- Dodać `_unwrap_calibrated()` (wyciąga base estimator z `CalibratedClassifierCV` — kalibracja
  monotoniczna, ranking cech zachowany).
- Wskazać LSTM pominięty + uzasadnienie.

---

## 10. Architektura systemu (Roz. 3.4) — całkowicie PUSTE w PDF

Sekcje 3.4.1–3.4.4 + 3.5 + 3.6 to same tytuły. **Cała architektura eksperymentalna** musi zostać
spisana. Projekt ma:

### 10.1. Architektura ogólna (3.4.1)

```
React Frontend (5173) ──POST /api/v1/monitoring/clients/{ref}/snapshots──┐
                                                                          ▼
.NET 8 ASP.NET Core (5120) — MonitoringController
   ├── ScoreAndPersistAsync (reuse PredictTimeseriesAsync z CREDIT-202)
   │      ├── walidacja 22 cech (DataAnnotations)
   │      ├── PythonModelClient ──► Flask /predict/timeseries (5001)
   │      └── enrichment: clientRef, snapshotDate, labelki okien
   ├── SnapshotRepository / PredictionRepository / TrendRepository
   └─────────────────────────────► PostgreSQL 16 (5432) — EF Core
                                   Client / Snapshot / Prediction / Trend
```

### 10.2. Warstwa backendowa (3.4.2)

- .NET 8 ASP.NET Core (port 5120). CORS dla `http://localhost:5173`.
- Kontrolery: `MonitoringController` (3 endpointy: `predict-timeseries`,
  `POST clients/{ref}/snapshots`, `GET clients/{ref}/history`, `GET clients`).
- DTOs: `Snapshot22Features`, `TimeseriesResponse` (z 5-model `WindowPredictions` + `Trends` +
  `ShapExplanation` po CREDIT-115/211), `ErrorEnvelope` z kodami `VALIDATION_FAILED`/`ML_SERVICE_ERROR`
  /`ML_SERVICE_UNAVAILABLE`/`CONFLICT`/`CLIENT_NOT_FOUND`/`INTERNAL_ERROR`.
- EF Core + Npgsql, auto-migracje przy starcie.
- **Pełny opis** w `docs/api-contracts/monitoring.md` (409 LoC, CREDIT-210) — to jest *de facto*
  rozdział 3.4.2 napisany w stylu kontraktu API. Wystarczy go zacytować/zwięźle streścić.

### 10.3. Integracja modeli AI (3.4.3) — serwis Flask

- Flask 5001 — ładuje 5 modeli W3 (4×`.pkl` + 1×`.keras`) + 2 scalery + `alert_thresholds.json`
  + LSTM isotonic calibrator + SHAP TreeExplainers (CREDIT-107).
- Endpointy: `GET /health`, `POST /predict` (legacy 6-mies., zachowany), `POST /predict/timeseries`
  (główny — Wariant B).
- `engineer_features(df, window)` parametryzowane oknem, `prepare_lstm_input()` tensor (1, 3, 3).
- Response zawiera: `predictions` (5 modeli × 4 okna), `trends` (5 modeli — slope + alert),
  `costThresholds` (5 modeli), `windowAlerts` (5 modeli × 4 bool), `shap` (4 tree modeli × top-5).

### 10.4. Warstwa frontendowa (3.4.4)

- React 19 + TypeScript + Vite (port 5173).
- Komponenty: `InputForm.tsx` (22 cechy + datepicker po CREDIT-303), `TimelineChart.tsx`
  (Recharts LineChart 5 linii), `TrendAlerts.tsx` (5 kart semaforowych), `ClientList.tsx`,
  `ClientHistory.tsx`, `SnapshotForm.tsx`, `ShapExplanation.tsx`, `ModelCard.tsx`,
  `ProbabilityGauge.tsx` (react-circular-progressbar), `ComparisonChart.tsx`.
- `predictApi.ts` + `monitoringApi.ts` (Axios).
- Vitest + RTL — 34 testy (po CREDIT-211, 16→27→34).

### 10.5. Obsługa wyjątków (3.5)

- Mapowanie błędów Flask ↔ .NET: 400/502/503 + 409 CONFLICT przy duplikacie `(clientRef, snapshotDate)`.
- Pełne tabele w kontrakcie `monitoring.md`.

### 10.6. Narzędzia (3.6)

- Tech stack: React 19 / Vite / TS / .NET 8 / Flask 3 / Python 3.11 / PostgreSQL 16 / Docker
  Compose / GitHub Actions CI / pytest / xUnit / Vitest / Testcontainers.
- ML: scikit-learn / TensorFlow (Keras) / xgboost / lightgbm / catboost / shap / fairlearn /
  optuna / joblib / pandas / numpy.
- Methodology: GitHub Flow z PR-review + CI blokującym czerwone (CREDIT-201), 30+ tasków
  CREDIT-XXX, 6 sprintów × 2 tygodnie kalendarzowo.

---

## 11. Wyniki (Roz. 5) — CAŁY ROZDZIAŁ DO NAPISANIA

Sekcje 5.1–5.6 mają same tytuły. Dane są wszystkie gotowe:

| Sekcja | Źródło danych w projekcie |
|---|---|
| 5.1.1 Dokładność, precyzja, czułość, F1 | brak w `metrics_w3.csv` — **trzeba dorobić** (lub argument: Brier > F1 dla credit scoring) |
| 5.1.2 ROC / AUC | `reports/metrics_w3.csv`, `roc_*_w3.png` (5×), `roc_comparison_w3.png` |
| 5.1.3 Macierz pomyłek | `reports/confusion_*_w3.png` (5×) — **uwaga: przy progu 0.5, nie cost-opt** |
| 5.2.x Wyniki per model | per-model w `metrics_w3.csv` (AUC, Gini, KS, Brier), confusion, KS plot |
| 5.3 Porównanie 5 modeli | `metrics_w3.csv` + `roc_comparison_w3.png` + `pr_comparison_w3.png` + `calibration_comparison_w3.png` |
| 5.4 Klasyczne vs nowoczesne (PDF) ⇒ **statyka vs monitoring (Wariant B)** | `reports/static_vs_dynamic_*.png` + `static_vs_dynamic_report.md` + 2 CSV |
| 5.5 Interpretowalność ⇒ **+ fairness** | SHAP (część w PDF) + dodać CREDIT-112 (`fairness_report.md`) |
| 5.6 Dyskusja + hipotezy | finalna synteza H1/H2/H3 (zob. §1.2) — będzie częścią CREDIT-114 (final report) |

**Propozycja:** uzgodnić, że Roz. 5 zostanie napisany na bazie outputu **CREDIT-114** (Sprint 6,
P0) — generator zbiorczego raportu + komplet wykresów do prezentacji. CREDIT-114 jest jedynym
otwartym ogniwem ścieżki krytycznej tezy.

---

## 12. Rysunki — referencje vs faktyczne pliki

PDF odwołuje się do 9 rysunków (1.1, 1.2, 2.1, 2.2, 2.3, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8,
4.9). Stan plików w projekcie:

| Rys. | PDF | Plik w `reports/` | Status |
|---|---|---|---|
| 1.1, 1.2 | cykl życia ekspozycji, ewolucja metod | (brak, opracowanie własne diagrams) | **Do dorobienia** |
| 2.1 | taksonomia ML | (brak) | **Do dorobienia** |
| 2.2 | komórka LSTM | [27] Wikimedia | OK (linkowane) |
| 2.3 | bagging/boosting | [28]/[29] Wikimedia | OK (linkowane) |
| 4.1 | podział train/val/test | (brak) | **Do dorobienia** (musi pokazywać 80/20, nie 70/30!) |
| 4.2 | wpływ SMOTE | (brak `smote_*.png`) | **Wycofać** (SMOTE odrzucony) lub uzasadnić jako analiza alternatyw |
| 4.3 | krzywe uczenia LSTM | (brak `lstm_history_*.png`) | **Do dorobienia** (wymaga retraining z history dump) |
| 4.4 | hiperparametry LSTM (epoch/batch/units) | (brak) | **Do dorobienia** (wymaga skryptu sweep) |
| 4.5 | RF heatmap n_estimators × max_depth | (brak) | **Do dorobienia** lub usunąć (Optuna zastąpiło) |
| 4.6 | top 20 RF features | (brak `rf_importance_*.png`) | **Do dorobienia** (szybkie, sklearn) |
| 4.7 | XGB grid search lr × depth | (brak) | **Do dorobienia** lub zastąpić Optuna trial plot |
| 4.8 | XGB SHAP beeswarm/bar | (brak `shap_*.png` global, mamy tylko per-prediction top-5) | **Do dorobienia** (shap.summary_plot na test set, jednorazowo) |
| 4.9 | 5-fold CV schemat | (brak) | **Do dorobienia** lub usunąć (Optuna 5-fold w CREDIT-108) |

**Brakujące w `reports/` ale opisane w projekcie — DO DODANIA W PRACY:**
- ROC overlay 5 modeli: `roc_comparison_w3.png` (już jest) — wstawić do 5.3.
- PR overlay: `pr_comparison_w3.png` (jest) — 5.3.
- Calibration curve overlay: `calibration_comparison_w3.png` (jest) — sek. 4.6 + 5.3.
- Static-vs-dynamic ROC: `static_vs_dynamic_{rf,xgb,lstm}_w3.png` (3 z 5 — **dorobić dla
  lightgbm/catboost**) — sek. 5.4.
- Slope boxplot per model: `slope_boxplot_*_w3.png` (5×) — sek. 5.4 lub 5.5.
- Trajectory examples: `trajectory_examples_*_w3.png` (5×) — sek. 5.4.
- Fairness: `fairness_selection_rate_w3.png` + `fairness_tpr_fpr_w3.png` — sek. 5.5b.
- Lead time histogram + slope_auc per model — w `lead_time_report.md`, dorobić PNG.

---

## 13. Plan poprawy dokumentu — proponowane priorytety

### P0 (must) — bez tego praca nie odzwierciedla projektu

1. **Roz. 3.2 — hipotezy badawcze.** Sformułować H1 (sliding-window zachowuje AUC), H2 (monitoring
   > statyka pod lead time), H3 (fairness).
2. **Roz. 3.3 + Roz. 3.4 — dane + architektura systemu.** Pełne uzupełnienie szkieletu (źródła
   UCI + sliding-window panel + architektura React/.NET/Flask/Postgres).
3. **Wstęp — przeredagować framing „dynamiczne".** Wprowadzić podwójny sens: dynamiczna
   architektura (LSTM) + dynamiczna ocena (Wariant B sliding-window).
4. **Roz. 4 — dodać sek. 4.6 (Kalibracja izotoniczna), 4.7 (Cost-opt thresholds), 4.8 (Sliding-window
   panel)**, zaktualizować 4.1.1 (80/20), 4.1.2 (no class_weight, isotonic + cost), 4.2.1 (LSTM (3,3)
   nie (6,3)).
5. **Roz. 5 — napisać od zera** na podstawie CREDIT-114 (gdy będzie gotowy).
6. **Aktualizacja sek. 2.3 + 4 — dodać LightGBM + CatBoost.** 5 modeli, nie 3.

### P1 (should) — znacznie poprawi obronę

7. **Roz. 5.4 reframing**: „klasyczne vs nowoczesne" ⇒ „statyka W3 vs monitoring W0..W3" (dowód
   Wariantu B).
8. **Roz. 5.5b — fairness audit** (CREDIT-112 fairlearn DPD/EOD per SEX, 5 modeli).
9. **Roz. 4.4.2 — rozszerzyć SHAP** na 4 modele tree-based (nie tylko XGB).
10. **Roz. 4.5 — zastąpić bootstrap** opisem Optuna 5-fold CV (CREDIT-108).
11. **Rysunki — dorobić 4.1 (80/20), 4.6 (RF top-20), 4.8 (XGB SHAP beeswarm)** + globalne SHAP
    summary per model.
12. **Roz. 3.6 — opisać tech stack + GitHub Flow + CI** (rygor metodologiczny pracy magisterskiej).

### P2 (nice-to-have) — uczciwość + drobne

13. **Roz. 4.1.2 — przemodelować dyskusję imbalance**: usunąć SMOTE jako finalną decyzję,
    podkreślić że projekt operuje cost-asymmetry przez progi (CREDIT-106), nie wagi.
14. **Roz. 4.4.1 — Grid Search zachować jako historię**, ale dopisać Optuna jako systematyczną
    weryfikację post-hoc.
15. **Sek. 4.5 — dorobić bootstrap** (jeśli chcemy zachować obietnicę 40 powtórzeń), albo go
    wycofać.
16. **Bug-fix `utilization_rate`/`severe_late` (CREDIT-102)** — wzmiankować jako przykład rygoru
    train/serve consistency.

---

## 14. Co dokument **dobrze ujmuje** i nie wymaga zmian

- Roz. 1 (kredyt, scoring, regulacje) — pełny, dobrze osadzony w aktach prawnych (Prawo bankowe,
  Rekomendacje T/S, EBA wytyczne).
- Sek. 2.1 + 2.2 (taksonomia ML, applications) — solid.
- Sek. 2.3.1 (LSTM teoria) — dobre, do reuse.
- Sek. 2.3.2 (RF teoria) — dobre.
- Sek. 2.3.3 (XGBoost teoria) — dobre.
- Sek. 2.4 (porównanie ML vs klasyczne) — defensible framing.
- Sek. 2.5 (etyka + AI Act + RODO + SHAP teoria) — dobre intro; w Roz. 5 trzeba domknąć
  praktycznie (fairness audit).
- Roz. 4.1.1 (rationale 3-way split — wybór ROC-AUC) — argumentacja dobra, do reuse z liczbami
  80/20 zamiast 70/30.
- Roz. 4.2.1 (LSTM architecture rationale — 32 jednostek, Dropout 0.3, EarlyStopping) — szczegóły
  użyteczne, tylko input shape do zmiany.
- Roz. 4.4.2 (SHAP teoria + interpretacja biznesowa) — bardzo dobre, rozszerzyć na 4 modele.
- Bibliografia 29 pozycji — solidna, [10][11][13] są dokładnie naszym benchmarkiem; [21] Clements
  et al. (sequential deep learning for credit risk monitoring) wprost wspiera Wariant B.

---

## 15. Działania techniczne potrzebne do uzupełnienia pracy

Następujące skrypty/raporty wymaga dorobienia, żeby Roz. 5 można było napisać liczbowo:

| Co | Skąd dane | Komentarz |
|---|---|---|
| Globalny SHAP summary per model (beeswarm + bar) | retrain SHAP na całym test set, `shap.summary_plot()` | nowy skrypt `ml-learing-center/shap_global.py`, ~50 LoC |
| RF feature_importance top-20 plot | `rf.feature_importances_` + matplotlib bar | nowy skrypt, ~30 LoC |
| LSTM training curves (history dump) | TF/Keras `model.fit().history` ⇒ accuracy + loss train/val | retrain z `history.json` dump |
| Bootstrap 40-powtórzeń AUC variance | sample with replacement test set, recompute AUC | nowy skrypt, ~50 LoC; **lub usunąć obietnicę** |
| Static-vs-dynamic dla LightGBM + CatBoost | wzbogacić `static_vs_dynamic.py` (już iteruje `MODELS`) | re-run skryptu — może już to robi, sprawdzić |
| Reliability diagram per model przed/po kalibracji | `CalibrationDisplay` z sklearn | retrain z calib data — może już w `calibration_comparison_w3.png` |
| Hyperparameter sweep plots (RF heatmap, XGB heatmap, LSTM units/batch/epochs) | nowy sweep | lub wycofać te Rysunki — dziś robi to Optuna |

Wszystkie szybkie, < 1 dzień łącznie. Najwięcej pracy to **napisanie Roz. 3 + Roz. 5** (kilka–kilkanaście
stron tekstu), nie kod.

---

## 16. Zalecana kolejność prac edytorskich

1. **Sprint 6 PR-y projektu** (CREDIT-113 stacking + CREDIT-114 final report) — dają domkniętą bazę
   liczbową dla Roz. 5.
2. **Wstęp + Roz. 3** (po projektowej stronie wszystko gotowe — można pisać dziś).
3. **Aktualizacja Roz. 4** (sek. 4.1 + 4.2 + dodanie 4.6/4.7/4.8 — sliding-window + kalibracja
   + cost thresholds + LightGBM/CatBoost).
4. **Aktualizacja Roz. 2.3** (dodać 2.3.4 LightGBM + 2.3.5 CatBoost — krótkie sekcje teoretyczne).
5. **Roz. 5 + Zakończenie** (po CREDIT-114, na podstawie zbiorczego raportu).
6. **Rysunki** — dorobić wg listy w §15 (równolegle z pisaniem rozdziału referującego).

> **Wniosek nadrzędny:** PDF jest dobrym fundamentem teoretycznym (Roz. 1+2), ale **opisuje
> pierwotną wersję projektu (6-mies. okno, 3 modele, class_weight, brak kalibracji, brak monitoringu)**.
> Po Sprintach 1–5 projekt jest istotnie inny: **sliding-window 4-okienkowy, 5 modeli, kalibracja
> izotoniczna, cost-opt thresholds, monitoring trajektorii PD, fairness audit fairlearn,
> end-to-end React+.NET+Flask+Postgres**. Aktualizacja PDF do tego stanu = ~3-4 dni pracy edytorskiej,
> bez nowego kodu (poza dorobieniem brakujących wykresów per §15).