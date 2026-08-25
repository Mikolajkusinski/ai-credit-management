# PodsumowanieSprintow.md — zbiorczy zapis Sprintów 1–5

> Plik scala (2026-07-07) pięć podsumowań sprintowych:
> `PodsumowanieSprintu1.md`, `...2_MK.md`, `...3_GF.md`, `...4_GF.md`,
> `...5_GF.md` (oryginały usunięte — dostępne w historii gita). Treść per sprint
> zachowana wiernie jako **zapis historyczny procesu**; sprinty 3–5 mają banery
> ERRATA, bo część liczb pochodzi z runów sprzed napraw metodologicznych.
>
> ## Liczby kanoniczne (po naprawach 2026-07-07 — leakage-fix progów i skalerów)
>
> | Model | AUC | Brier | Próg kosztowy | DPD | EOD | Δ monitoring−statyka @FA=10% |
> |---|---:|---:|---:|---:|---:|---:|
> | Random Forest | 0,7741 | 0,1374 | 0,145 | +0,035 | +0,028 | −10,9 pp |
> | XGBoost | 0,7761 | 0,1360 | 0,165 | +0,036 | +0,028 | −5,1 pp |
> | LightGBM | 0,7767 | 0,1363 | 0,160 | +0,035 | +0,027 | −5,0 pp |
> | CatBoost | 0,7793 | 0,1357 | 0,160 | +0,039 | +0,033 | −6,4 pp |
> | LSTM | 0,7614 | 0,1388 | 0,155 | +0,006 | +0,021 | **+2,6 pp** |
>
> Źródło prawdy: `ml-learing-center/reports/FINAL_REPORT.md` + `reports/*.csv`.
> Kontekst napraw: `reports/{threshold,scaler}_leakage_fix.md`, `Fable5-zmiany.md`.
> Stan zadań po Sprincie 6: 28/30 🟢 (CREDIT-113 descoped, otwarty CREDIT-304) —
> patrz `CHECKLIST.md`.

---

<!-- ================== SPRINT 1 ================== -->

# Podsumowanie Sprintu 1 — fundament Wariantu B

> Dokument dla seminarium magisterskiego (2026). Streszcza wszystkie zmiany w projekcie `ai-credit-management` od planowania (2026-06-01) do zamknięcia Sprintu 1 (2026-06-02).

---

## 1. Kontekst i teza

**Projekt:** system predykcji ryzyka kredytowego (default w następnym miesiącu) oparty na zbiorze UCI „Default of Credit Card Clients" (Taiwan 2005, 30 000 klientów, 22 cechy wejściowe).

**Teza Wariantu B — monitoring kalendarzowy:** ten sam klient jest oceniany wielokrotnie w czasie; system śledzi trajektorię prawdopodobieństwa default (PD) i wykrywa pogorszenie zanim do niego dojdzie. Wskaźnik sukcesu = uczciwe porównanie „statyka jednorazowa vs. monitoring kalendarzowy" (CREDIT-111, Sprint 3).

**Sprint 1 (planowane 2 cze – 15 cze 2026, faktycznie zamknięte 2 cze 2026):** ułożyć fundament — *panel danych* (sliding-window) + *baza danych* (trwała historia klienta). Bez tego Wariant B nie jest możliwy.

---

## 2. Cele Sprintu 1 — co miało zostać dostarczone

Dwa niezależne tory pracy, planowane na 2 tygodnie:

| Tor | Owner | Zadania | Cel |
|---|---|---|---|
| **ML / dane** | Gabriel Figur (GF) | CREDIT-101, 102, 103 | Sliding-window 3-mies. + przetrenowanie 3 modeli na nowym oknie + rozszerzone metryki |
| **Infrastruktura** | Mikołaj Kusiński (MK) | CREDIT-201, 401, 402 | Testy + CI + schemat bazy Postgres + docker-compose |

**Wszystkie 6 zadań zamknięte i zmergeowane do `main`.** Statystyki na koniec sprintu: 5/27 zadań done (101, 102, 201, 401, 402, 103), 6 odblokowanych, 16 wciąż czeka na zależności (cykl Sprint 2+).

---

## 3. Co dostarczyliśmy — szczegóły per zadanie

### CREDIT-101 (DATA, GF) — Panel danych (sliding-window)

**Plik:** `ml-learing-center/sliding_window.py` (66 LoC) + `sliding_window_test.py` (79 LoC) + `requirements.txt`.

**Co robi:** funkcja `extract_windows(row)` zamienia 1 wiersz UCI (klient × 6 miesięcy historii) w 4 okna 3-miesięczne (W0 = kwi/maj/cze … W3 = lip/sie/wrz). Mapowanie respektuje znaną cechę zbioru UCI: kolumna `PAY_1` nie istnieje (kolejność: PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6).

**Mapowanie okien:**

| Okno | Miesiące (najst.→najnow.) | Status płatności | Rachunek | Wpłata |
|---|---|---|---|---|
| W0 | kwi · maj · cze | PAY_6, PAY_5, PAY_4 | BILL 6, 5, 4 | PAY_AMT 6, 5, 4 |
| W1 | maj · cze · lip | PAY_5, PAY_4, PAY_3 | BILL 5, 4, 3 | PAY_AMT 5, 4, 3 |
| W2 | cze · lip · sie | PAY_4, PAY_3, PAY_2 | BILL 4, 3, 2 | PAY_AMT 4, 3, 2 |
| W3 | lip · sie · wrz | PAY_3, PAY_2, PAY_0 | BILL 3, 2, 1 | PAY_AMT 3, 2, 1 |

**Slajd na seminarium:** *„Nie fabrykujemy danych. Każda migawka używa wyłącznie realnych kolumn z prawdziwej historii klienta. 4 okna = 4-punktowa trajektoria PD na tych samych 6 miesiącach."*

**Testy:** 4 pytesty (struktura, mapowanie W3, mapowanie W0, brak referencji do nieistniejącego `PAY_1`).

---

### CREDIT-102 (ML, GF) — Retrain RF/XGBoost/LSTM na oknie W3

**Pliki:** `ml-learing-center/features.py` (102 LoC, nowy moduł), `ml-learing-center/main.py` (+86 LoC, dopisany blok W3 retrain), `ml-service/app.py` (fix 2 linii — patrz „Dług techniczny").

**Co robi:**
1. Modeluje cechy parametryzowane oknem (`engineer_features(df, window)`): 13 cech pochodnych (PAY_mean/max, BILL_mean/std/trend, payment_ratio, late_count, severe_late, utilization_rate, recent_pay_status) + 9 surowych kolumn okna + one-hot SEX/EDUCATION/MARRIAGE → **32 cechy** dla RF/XGBoost.
2. Buduje tensor LSTM `(N, 3, 3)` — 3 timesteps, 3 kanały (PAY, BILL, PAY_AMT) skalowane osobno.
3. Trenuje **3 modele na oknie W3** (najnowsze 3 miesiące, zgodne z etykietą październikową): Random Forest (500 drzew, max depth 10), XGBoost (800 iter, lr 0.02, max depth 4), LSTM (32 units, dropout 0.3, 60 epok, EarlyStopping).
4. Zapisuje **6 nowych artefaktów** z sufiksem `_w3`:
   - `rf_model_w3.pkl` (27 MB), `xgb_model_w3.pkl` (1.3 MB), `lstm_model_w3.keras` (93 KB)
   - `scaler_w3.pkl`, `features_w3.pkl`, `ml-service/lstm_scalers_w3.pkl`
5. **Zachowuje legacy 6-mies. modele** — stare `rf_model.pkl` etc. nietknięte. Pozwoli to Flaskowi obsługiwać `/predict` bez przerwy aż do CREDIT-104 (Sprint 2), które przełączy runtime na W3.

**Slajd na seminarium:** *„Rozkład treningowy = rozkład inferencyjny. Model uczy się na W3 (najnowsze 3 mies. → etykieta defaultu w październiku). Przy monitoringu ten sam model stosujemy do W0, W1, W2, W3 — każde okno to identyczny 3-mies. wycinek. Brak out-of-distribution shift."*

**Wyniki AUC:**

| Model | Legacy (6-mies. okno) | **W3 (3-mies. okno)** | Δ AUC |
|---|---|---|---|
| Random Forest | 0.7792 | **0.7779** | −0.001 |
| XGBoost | 0.7818 | **0.7794** | −0.002 |
| LSTM | 0.7686 | **0.7637** | −0.005 |

**Strata AUC akceptowalna** (Risk register #1 z `plan_sprintow_wariant_B.md`). 3-mies. okno niesie mniej informacji niż 6-mies., ale spadek <1% to dobra cena za zgodność rozkładów treningowy/inferencyjny.

---

### CREDIT-103 (EVAL, GF) — Rozszerzone metryki + 12 wykresów

**Pliki:** `ml-learing-center/evaluation.py` (238 LoC, standalone), `ml-learing-center/reports/` (12 PNG + 1 CSV).

**Co robi:** ładuje artefakty W3, replikuje deterministyczny split treningowy (`random_state=42`), liczy 4 metryki per model i generuje 12 wykresów do prezentacji.

**Tabela metryk W3 (test set, 9000 klientów):**

| Model | AUC | Gini | KS | Brier |
|---|---|---|---|---|
| Random Forest | 0.7779 | 0.5559 | 0.4147 | **0.1688** ✓ |
| XGBoost | **0.7794** ✓ | **0.5588** ✓ | **0.4230** ✓ | 0.1778 |
| LSTM | 0.7637 | 0.5274 | 0.4114 | 0.1863 |

**Interpretacja:**
- **XGBoost najlepszy w dyskryminacji** (AUC, Gini, KS) — trzy najwyższe wartości statystyk separujących klasy.
- **Random Forest najlepiej skalibrowany** (najniższy Brier 0.1688) — prawdopodobieństwa najbliższe częstościom empirycznym.
- **LSTM lekko z tyłu** — oczekiwane przy 3-elementowej sekwencji (LSTM zyskuje na długich szeregach; W3 to minimum, jakim może operować). To zaadresujemy w CREDIT-109 (LightGBM + CatBoost, Sprint 5) i CREDIT-113 (stacking, Sprint 6).

**Wygenerowane wykresy (`ml-learing-center/reports/`):**

| Plik | Zawartość |
|---|---|
| `roc_comparison_w3.png` | ROC 3 modele na jednym wykresie |
| `pr_comparison_w3.png` | Precision-Recall 3 modele |
| `calibration_comparison_w3.png` | Reliability diagram (calibration curve) 3 modele |
| `roc_{rf,xgb,lstm}_w3.png` | Pojedyncze ROC z AUC w tytule (3 pliki) |
| `confusion_{rf,xgb,lstm}_w3.png` | Confusion matrix (próg 0.5, 3 pliki) |
| `ks_{rf,xgb,lstm}_w3.png` | KDE rozkładu PD dla def vs non-def + KS w tytule (3 pliki) |

**Wszystkie 12 PNG-ów + CSV są w gicie** i gotowe do wklejenia do slajdów / pracy.

---

### CREDIT-201 (INFRA, MK) — Infrastruktura testów + CI

**Pliki:** `backend/WebApi.Tests/SmokeTests.cs` (15 LoC), `ml-service/tests/test_smoke.py` (17 LoC), `frontend/WebApp/vitest.config.ts` + `src/test/setup.ts` + `src/components/__tests__/ModelCard.test.tsx`, `.github/workflows/ci.yml` (75 LoC).

**Co robi:** zakłada pełną infrastrukturę testową dla wszystkich 3 stacków:
- **Backend:** xUnit + WebApi.Tests/ z pierwszym smoke testem.
- **ML service:** pytest + ml-service/tests/ — smoke test sprawdza, że flask/numpy/pandas się importują (nie ładuje `app.py`, bo artefakty modeli nie są w gicie — projektowo unika brittleness).
- **Frontend:** Vitest + jsdom + Testing Library + 1 smoke test komponentu `ModelCard`.

**CI workflow (`.github/workflows/ci.yml`):** 3 niezależne joby (Backend / ML / Frontend) na GitHub Actions, uruchamiane na każdym PR i na push do main. **Czerwone CI = blokada merge'a.**

**Czasy CI (real measurements z PR #8 i #9):**

| Job | Czas |
|---|---|
| Backend .NET / xUnit | 25–42 s |
| Frontend React / Vitest | 13–15 s |
| ML Service Python / pytest | 58 s – 1 min 7 s |
| **Total wall clock (równolegle)** | **~1 min 10 s** |

---

### CREDIT-401 (DB, MK) — Schemat Postgres + EF Core

**Pliki:** `backend/WebApi/Data/AppDbContext.cs` (59 LoC), `backend/WebApi/Models/Entities/{Client,Snapshot,Prediction,Trend}.cs` (74 LoC łącznie), migracja `Migrations/20260601181900_Init` (~400 LoC auto-generated), update `Program.cs` + `WebApi.csproj` + `appsettings.json`, `backend/global.json`, `backend/AiCreditManagement.sln`.

**Schemat (4 encje, relacje 1:N):**

```
Client (Id, ExternalRef [unique], CreatedAt)
  ├── Snapshot (Id, ClientId, SnapshotDate, [22 cechy: LimitBal, Sex, ..., PayAmt6])
  │     └── Prediction (Id, SnapshotId, ModelName, DefaultProbability, Label)
  └── Trend (Id, ClientId, ModelName, Slope, Alert, ComputedAt)
```

**Decyzje projektowe:**
- `Client.ExternalRef` jako unique constraint — pozwala na human-readable klucz biznesowy (np. „klient-2024-001").
- `Snapshot` ma indeks `(ClientId, SnapshotDate)` — szybkie zapytania o historię w przedziale czasu.
- `Prediction.ModelName` jako string (max 32) — elastyczne (RF/XGB/LSTM dziś, LightGBM/CatBoost/ensemble jutro w Sprint 5–6).
- `Trend` osobno od `Prediction` — przechowuje slope (W3−W0) i kategorię alertu (INCREASING_RISK / DECREASING_RISK / STABLE) per klient per model, zaktualizowany po każdej nowej migawce.

**Pakiety NuGet dodane:** `Microsoft.EntityFrameworkCore` (.Design, .Tools), `Npgsql.EntityFrameworkCore.PostgreSQL`.

---

### CREDIT-402 (INFRA, MK) — docker-compose + auto-migracje

**Pliki:** `docker-compose.yml` (41 LoC), `backend/WebApi/Dockerfile` (14 LoC), `backend/WebApi/.dockerignore`, update `Program.cs` (auto-migracje przy starcie).

**Co stawia `docker-compose up`:**
- **db** — Postgres 16 (port 5432), named volume `pg_data`, healthcheck `pg_isready`.
- **ml-service** — Flask z `ml-service/Dockerfile` (port 5001).
- **backend** — .NET 8 z nowym `backend/WebApi/Dockerfile` (port 5120 → 8080 internal), zależy od `db: service_healthy`, automatycznie migruje bazę przy starcie.
- **Frontend POZA compose** — pozostaje na `npm run dev` dla wygody hot-reloadu (decyzja świadoma).

**Connection string przekazywany przez env var:** `Host=db;Port=5432;Database=credit;...` — DNS Dockera załatwia rozwiązanie nazwy.

---

## 4. Dług techniczny zlikwidowany

W trakcie analizy pre-existing kodu znaleźliśmy i naprawiliśmy **2 błędy w `ml-service/app.py`** (linie 35 i 40), które rozjeżdżały feature engineering między treningiem (`main.py`) a inferencją (Flask `/predict`):

| Linia | Bug w `app.py` | Faktyczna formuła z `main.py` | Skutek |
|---|---|---|---|
| 35 | `BILL_AMT1 / LIMIT_BAL` | `BILL_mean / LIMIT_BAL` (średnia z 6 mies.) | Inferencja widziała inną feature niż model w treningu |
| 40 | `(...PAY... >= 2).sum()` (liczba) | `(...PAY... >= 2).any().astype(int)` (bool) | Inferencja widziała inną feature niż model w treningu |

**Skutek przed fixem:** Flask `/predict` zwracał predykcje, ale wartości cech były spoza rozkładu treningowego (silent corruption). Modele „działały", ale podejmowały decyzje na danych, których nie widziały.

**Skutek po fixie:** spójność train/serve, identyczne wzory feature engineering po obu stronach. Smoke test (curl): zdrowy klient → wszystkie 3 modele „NO DEFAULT", PD = 0.12 / 0.15 / 0.19 (rozsądnie niskie).

---

## 5. Statystyki Sprintu 1

| Wskaźnik | Wartość |
|---|---|
| **Zadań ukończonych** | 6 / 6 (100%) |
| **PR-ów zmergeowanych** | 6 (#4, #5, #6, #7, #8, #9) |
| **Nowych LoC (kod, bez auto-generated)** | ~1 580 |
| **Plików utworzonych** | 24 |
| **Modeli ML wytrenowanych** | 6 (3 legacy 6-mies. + 3 nowe W3) |
| **Artefaktów ML w gicie** | 6 × `_w3` (~30 MB łącznie) |
| **Wykresów ewaluacji** | 12 PNG + 1 CSV |
| **Testów CI** | 3 joby (xUnit + pytest + Vitest) |
| **CI wall-clock** | ~1 min 10 s |
| **Encji bazy** | 4 (Client, Snapshot, Prediction, Trend) |
| **Bugów feature-engineering naprawionych** | 2 (utilization_rate, severe_late) |
| **Czas faktyczny vs planowany** | 1 dzień vs 2 tygodnie |

---

## 6. Co Sprint 1 odblokował dla dalszej pracy

Po zmergeowaniu 6 PR-ów Sprintu 1, **6 kolejnych zadań** zmieniło status z 🔒 zablokowane na 🔴 dostępne (wg tabeli zależności w `TASKS.md`):

| ID | Sprint | Owner | Zadanie | Odblokowane przez |
|---|---|---|---|---|
| CREDIT-103 | 1 | GF | (już zrobione) | 102 |
| CREDIT-105 | 2 | GF | Kalibracja izotoniczna (P0) | 102 |
| CREDIT-107 | 4 | GF | SHAP top-5 cech (P2) | 102 |
| CREDIT-108 | 4 | GF | Optuna + 5-fold CV (P2) | 102 |
| CREDIT-109 | 5 | GF | LightGBM + CatBoost (P2) | 102 |
| CREDIT-112 | 5 | GF | Audyt fairness (P1) | 102 |

**Kluczowy task czekający na Sprint 2:** `CREDIT-210` (kontrakt API monitoringu) — bez niego ani Flask `/predict/timeseries` (CREDIT-104), ani backend `.NET /api/monitoring/predict-timeseries` (CREDIT-202), ani widok Timeline w React (CREDIT-301) nie ruszą. **Pierwsze zadanie Sprintu 2 = 30-minutowe spotkanie GF+MK na uzgodnienie payloadu i reguły alertu (slope W3−W0).**

---

## 7. Ryzyka zaadresowane vs otwarte

### Zaadresowane w Sprincie 1
- **R1: „Okno 3-mies. tnie AUC zbyt mocno"** (Risk register #1) — w praktyce strata AUC −0.001 do −0.005, akceptowalne. **CLOSED.**
- **R4: „Postgres + tensorflow w docker-compose ciężkie"** — `tensorflow-cpu`, slim images, healthcheck Postgresa. **CLOSED.**
- **Pre-existing bugs feature engineering** (poza Risk registerem, znaleziony podczas analizy) — fix w app.py linie 35/40. **CLOSED.**

### Wciąż otwarte (do śledzenia w Sprincie 2+)
- **R2: „Monitoring nie bije statyki w eksperymencie"** (CREDIT-111) — rozstrzygnięcie w Sprincie 3. Mitigacja: framing „dynamika daje lead time, nawet jeśli AUC podobne".
- **R3: „LSTM (3,3) niestabilny przy krótkiej sekwencji"** — początkowo widoczne (LSTM AUC 0.7637 < XGB 0.7794), rozważamy GRU lub uproszczenie architektury w przyszłym retreningu.
- **R5: „Opóźnienie kontraktu 210 blokuje Sprint 2"** — wysokie prawdopodobieństwo i wysoki impact, ale mitigacja prosta: spotkanie w pierwszy poniedziałek Sprintu 2.

---

## 8. Co dalej — Sprint 2 (planowane: 16 cze – 29 cze)

**Cel:** silnik monitoringu (trajektoria PD), kontrakty API, zapis migawek do bazy.

| ID | Owner | Zadanie |
|---|---|---|
| CREDIT-210 | GF+MK | Kontrakt API monitoringu (PIERWSZE, ~30 min wspólnej sesji) |
| CREDIT-104 | GF | Flask `/predict/timeseries`: 22 cechy → 4 okna → trajektoria PD per model |
| CREDIT-105 | GF | Kalibracja izotoniczna (3-way split, reliability po blisko diagonali) |
| CREDIT-202 | MK | .NET `/api/monitoring/predict-timeseries` (mock do czasu 104) |
| CREDIT-203 | MK | EF Core repozytoria: zapis Snapshot + Prediction do Postgresa |

**Ścieżka krytyczna tezy:** `101 → 102 → 104 → 110 → 111 → 114`. Sprint 1 zamknął 101 i 102. Sprint 2 zamyka 104. Sprint 3 zamyka 110 i **111 (dowód tezy)**.

---

## 9. Highlight slajdy (1-slajd-podsumowanie)

> **Sprint 1 (1 dzień zamiast 2 tyg.) — fundament Wariantu B postawiony.**
>
> - **Panel danych:** UCI 6-mies. → 4 okna 3-mies. (W0..W3). Bez fabrykowania liczb. Test pytest.
> - **3 modele przetrenowane** na W3 (zgodność rozkładu trening/inferencja): RF 0.778, XGB 0.779, LSTM 0.764. Strata AUC <1% vs legacy 6-mies.
> - **12 wykresów ewaluacji** (ROC × 3, PR, calibration, confusion × 3, KS × 3) + tabela AUC/Gini/KS/Brier.
> - **Schemat bazy** Postgres + EF Core (Client/Snapshot/Prediction/Trend) → trwała historia klienta.
> - **docker-compose** stawia db + backend + ml-service jedną komendą; auto-migracje.
> - **CI** 3-stack (xUnit + pytest + Vitest), wall-clock ~1 min 10 s, blokuje czerwone PR.
> - **2 silent bugi** feature engineering w `app.py` naprawione → spójność train/serve.
>
> **Następne:** kontrakt API monitoringu (CREDIT-210) → Flask `/predict/timeseries` (104) → dowód tezy „statyka vs monitoring" (111).

---

<!-- ================== SPRINT 2 (tor MK) ================== -->

# Podsumowanie Sprintu 2 — tor MK (Mikołaj Kusiński)

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (MK)** w Sprint 2 projektu
> `ai-credit-management`: kontrakt API monitoringu (wspólnie z GF), bezstanowy proxy scoringu w .NET
> oraz warstwę trwałości (zapis migawek/predykcji/trendów do PostgreSQL).
>
> Perspektywa pełnego sprintu (z torem ML/GF) — patrz osobne podsumowanie GF. Stan bazy danych i
> infrastruktury z mojego Sprintu 1 — patrz `PodsumowanieSprintu1.md`.

---

## 1. Kontekst i mój zakres

**Teza Wariantu B — monitoring kalendarzowy:** ten sam klient jest oceniany wielokrotnie w czasie;
system śledzi trajektorię prawdopodobieństwa default (PD) i wykrywa pogorszenie, zanim do niego
dojdzie. Sprint 1 postawił fundament (panel sliding-window + schemat bazy). **Sprint 2 uruchamia
silnik monitoringu end-to-end.**

W podziale obciążenia (oba fullstack) mój tor (MK) w Sprincie 2 to **warstwa orkiestracji i
trwałości w .NET**:

| ID | Tag | Co | Status |
|---|---|---|---|
| **CREDIT-210** | CONTRACT | Kontrakt API monitoringu (wspólnie GF+MK) | 🟢 merged (PR #11) |
| **CREDIT-202** | BE | `.NET POST /api/v1/monitoring/predict-timeseries` — bezstanowy proxy nad Flaskiem | 🟢 merged (PR #13) |
| **CREDIT-203** | BE | Repozytoria EF Core + `POST /clients/{ref}/snapshots` — zapis migawki + predykcji + trendów | 🟢 merged (PR #14) |

Tor ML/GF w Sprincie 2 (CREDIT-104 Flask `/predict/timeseries` + CREDIT-105 kalibracja izotoniczna) biegł
równolegle. **Mój tor Sprintu 2 jest domknięty.**

**Update na 2026-06-05** (po napisaniu wersji pierwotnej tego dokumentu):
- CREDIT-203 zmergeowany do `main` jako PR #14 (commit `24d2067`).
- **Sprint 2 zamknięty w pełni po obu stronach:** GF dostarczył CREDIT-105 (kalibracja izotoniczna,
  Brier −19/−24/−23% dla RF/XGB/LSTM, PR #19) i CREDIT-104 (Flask `/predict/timeseries`, PR #12).
- Sprint 3 mojego toru również zamknięty (CREDIT-204 GET history PR #15, CREDIT-301 Timeline PR #16).
- Sprint 4 mojego toru również zamknięty (CREDIT-302 client list+history UI PR #17, CREDIT-205
  Testcontainers persistence tests PR #18).

**Harmonogram:** Sprint 2 planowany 16 cze – 29 cze 2026; mój tor dostarczony do 2026-06-03 (przed
planem, tak jak Sprint 1).

---

## 2. Co dostarczyłem — szczegóły per zadanie

### CREDIT-210 (CONTRACT, GF+MK) — Kontrakt API monitoringu

**Plik:** `docs/api-contracts/monitoring.md` (409 LoC). PR #11.

**Po co:** to „klucz do równoległości" z planu — wspólna 30-minutowa sesja, po której GF mógł
implementować Flask (`/predict/timeseries`), a ja backend i frontend mockować przeciwko jednemu
źródłu prawdy, bez wzajemnego czekania. Bez kontraktu blokuje się 4 zadania (104, 202, 203, 301).

**Co ustaliliśmy (i co potem implementowałem w 202/203):**
- **Podział odpowiedzialności:** Flask = bezstanowy scoring (bez DB, bez `clientRef`); .NET =
  orkiestracja + trwałość (Postgres) + składanie historii; React = wprowadzanie migawek + wykres.
- **4 okna sliding-window** (W0..W3) + reguła **labelek** miesięcy liczonych po stronie backendu z
  `snapshotDate` (format `"Mar-May 2026"`).
- **Reguła alertu trendu:** slope = `PD_W3 − PD_W0`, próg `θ = 0.10` → `INCREASING_RISK` /
  `DECREASING_RISK` / `STABLE`.
- **Typy współdzielone:** `Snapshot22Features`, `TrajectoryPoint`, `TrendInfo`, `Trends`,
  `TimeseriesResponse`, `ErrorEnvelope` (kody `VALIDATION_FAILED`/`ML_SERVICE_ERROR`/
  `ML_SERVICE_UNAVAILABLE`/`CONFLICT`/`CLIENT_NOT_FOUND`/`INTERNAL_ERROR`).
- **4 endpointy:** Flask `/predict/timeseries` (wewnętrzny); backend 4.2 `predict-timeseries`
  (bezstanowy, CREDIT-202), 4.3 `POST clients/{ref}/snapshots` (stateful, CREDIT-203), 4.4 `GET
  clients/{ref}/history` (CREDIT-204).
- **Konwencje:** JSON camelCase, enumy SCREAMING_SNAKE_CASE, wersjonowanie `/api/v1/`, wyjątek Flask
  na SCREAMING_SNAKE_CASE w body.
- **Tabela open questions** — dwie z nich rozstrzygnąłem w CREDIT-203 (patrz niżej).

**Slajd:** *„Jeden kontrakt = cztery zadania ruszają równolegle. Backend i frontend budują przeciwko
mockowi payloadu, ML implementuje silnik — nikt nie czeka."*

---

### CREDIT-202 (BE, MK) — `.NET POST /api/v1/monitoring/predict-timeseries`

**Pliki (12 zmienionych, +605 LoC):** PR #13.

| Plik | LoC | Rola |
|---|---|---|
| `Services/MonitoringService.cs` | 101 | Orkiestracja: map 22 cech → Flask, wzbogacenie odpowiedzi (clientRef, snapshotDate, labelki okien) |
| `Controllers/MonitoringController.cs` | 64 | Endpoint + mapowanie błędów 400/502/503 |
| `Models/TimeseriesResponse.cs` | 72 | DTO trajektorii (TrajectoryPoint/WindowPredictions/Trends/TrendInfo) |
| `Models/Snapshot22Features.cs` | 51 | 22 cechy + walidacja DataAnnotations |
| `Models/ErrorEnvelope.cs` | 44 | Wspólny format błędów (kontrakt 3.6) |
| `Services/PythonModelClient.cs` | +36 | `GetTimeseriesAsync` — wywołanie Flask, rozróżnienie „błąd 5xx" vs „nieosiągalny" |
| `Services/MlServiceException.cs` | 18 | Wyjątek z `UpstreamStatusCode` → mapowanie 502 vs 503 |
| `Models/TimeseriesRequest.cs` | 19 | Request (clientRef? + snapshotDate? + Features) |
| `Program.cs` | +26 | Rejestracja serwisów + `InvalidModelStateResponseFactory` (400 jako ErrorEnvelope) |
| `WebApi.Tests/MonitoringTimeseriesTests.cs` | 163 | **4 testy integracyjne** |

**Co robi:** bezstanowy gateway. Waliduje 22 cechy (zakresy z kontraktu przez DataAnnotations →
`VALIDATION_FAILED`), tłumaczy je na request Flaska, woła `/predict/timeseries`, a w odpowiedzi
**dolicza to, czego Flask nie zna**: echo `clientRef`, `snapshotDate` (domyślnie dziś UTC) i
**labelki okien** (`"Mar-May 2026"`) liczone z daty. Nic nie zapisuje (zgodnie z kontraktem 4.2).

**Mapowanie błędów (kluczowe dla UX i obrony):**

| Sytuacja | HTTP | Kod |
|---|---|---|
| Pole 22-cechowe poza zakresem | 400 | `VALIDATION_FAILED` |
| Flask zwrócił 5xx | 502 | `ML_SERVICE_ERROR` |
| Flask nieosiągalny (connection refused / timeout) | 503 | `ML_SERVICE_UNAVAILABLE` |

**Testy:** `WebApplicationFactory<Program>` + stub `HttpMessageHandler` (bez żywego Flaska): happy
path 200 z poprawnymi labelkami i trendami, 400 przy złym `age`, 502 przy Flask 500, 503 przy
nieosiągalnym Flasku.

**Slajd:** *„Backend = orkiestrator. Flask liczy PD, .NET dokłada kontekst kalendarzowy (daty,
labelki) i tłumaczy awarie ML na czytelne statusy HTTP."*

---

### CREDIT-203 (BE, MK) — Warstwa trwałości: zapis migawek + predykcji + trendów

**Pliki (13 zmienionych, +610 LoC):** PR #14 (🟢 merged).

| Plik | LoC | Rola |
|---|---|---|
| `WebApi.Tests/SnapshotPersistenceTests.cs` | 211 | **4 testy integracyjne** (EF InMemory + stub Flask) |
| `Services/MonitoringService.cs` | +128 | `ScoreAndPersistAsync` — orkiestracja scoring → zapis |
| `Controllers/MonitoringController.cs` | +56 | Endpoint `POST clients/{ref}/snapshots` + 409/400 |
| `Services/TrendRepository.cs` | 52 | Upsert 1 trendu per `(klient, model)` |
| `Services/SnapshotRepository.cs` | 47 | Find/create klienta, guard duplikatu, zapis migawki |
| `Models/SnapshotResponse.cs` | 44 | DTO odpowiedzi 201 (+ `persisted{clientCreated, predictionIds, trendIds}`) |
| `Services/PredictionRepository.cs` | 29 | Zapis 3 predykcji W3 |
| `Models/SnapshotRequest.cs` | 17 | Request (snapshotDate? + Features) |
| `Services/SnapshotConflictException.cs` | 11 | Sygnał duplikatu → 409 |

**Co robi (endpoint `POST /api/v1/monitoring/clients/{ref}/snapshots`, kontrakt 4.3):**
przekształca monitoring z **bezstanowego** w **stateful**. Przy ocenie klienta:
1. **Guard duplikatu** — jeśli klient + `snapshotDate` już istnieją → `409 CONFLICT` (sprawdzane
   *przed* wywołaniem Flaska, żeby nie marnować scoringu i nie tworzyć klienta na konflikcie).
2. **Scoring przez reuse** — wywołuję istniejący `PredictTimeseriesAsync` z CREDIT-202 (zero
   duplikacji logiki Flask/labelek).
3. **Auto-create klienta** jeśli `{ref}` nowy (`clientCreated` w odpowiedzi).
4. **Zapis migawki** (22 cechy + data) → `Snapshot`.
5. **Zapis predykcji W3** (3 wiersze, po jednym na model RF/XGB/LSTM) → `Prediction`.
6. **Upsert trendów** (slope/alert z Flaska, 1 wiersz per model) → `Trend`.
7. Zwraca `201` z `snapshotId` + id zapisanych rekordów.

**Decyzje (rozstrzygnięte open questions z kontraktu 210):**
- **#1 — Predykcje tylko dla W3** (etykietowane okno = ocena „aktualna"). Trajektoria W0..W3 to widok
  analityczny, nie historia; historia rekonstruuje się z kolejnych migawek klienta.
- **#2 — Duplikat `(clientRef, snapshotDate)` → 409 CONFLICT** (zamiast cichego upsertu) — chroni
  przed przypadkowym podwójnym zapisem tej samej daty.

**Bez nowej migracji** — wykorzystuję schemat z CREDIT-401 (Client/Snapshot/Prediction/Trend).

**Testy:** `WebApplicationFactory` + **EF Core InMemory** (zamiana providera Npgsql na czas testu) +
stub Flaska — bez Dockera i Postgresa w CI:
1. happy path → `201`; w bazie pojawia się 1 Client + 1 Snapshot + 3 Prediction (PD z W3) + 3 Trend;
2. ten sam `(ref, data)` dwa razy → `409 CONFLICT` (tylko pierwszy zapis trwały);
3. ten sam klient, inna data → 2 migawki, `clientCreated=false` za drugim razem, trendy
   zaktualizowane (nie zduplikowane);
4. niewalidne cechy (`age=10`) → `400`, **nic nie zapisane** (Flask nie wołany).

Pełny, wierny relacyjnie zestaw (Testcontainers, ≥6 testów: unikalność, kaskady, transakcja)
świadomie odłożony do **CREDIT-205**.

**Slajd:** *„Tu monitoring staje się prawdziwy: każda ocena to trwała migawka w Postgresie.
Z kolejnych migawek tego samego klienta odtworzymy oś czasu PD — fundament dowodu tezy."*

---

## 3. Architektura warstwy, którą zamknąłem

```
React (5173)  ── POST /api/v1/monitoring/clients/{ref}/snapshots ──┐
                                                                    ▼
.NET WebApi (5120)
   MonitoringController → MonitoringService.ScoreAndPersistAsync
        │                         │
        │  (reuse 202)            ├── SnapshotRepository   ┐
        ▼                         ├── PredictionRepository ├─►  PostgreSQL (5432)
   PythonModelClient ─► Flask     └── TrendRepository      ┘     Client/Snapshot/
   (/predict/timeseries, bezstanowo)                            Prediction/Trend
```

- **CREDIT-202** dał bezstanową ścieżkę scoringu (proxy + labelki + mapowanie błędów).
- **CREDIT-203** owinął ją w trwałość: ta sama ścieżka scoringu, ale wynik ląduje w bazie.
- Detal, który wychwyciłem w testach: kolumna `SnapshotDate` to `timestamp with time zone`, więc
  konwersja `DateOnly → DateTime` musi mieć `DateTimeKind.Utc` (inaczej Npgsql rzuca przy zapisie).
  Endpoint poprawnie też odrzuca `snapshotDate` z przyszłości (`400`).

---

## 4. Statystyki mojego Sprintu 2

| Wskaźnik | Wartość |
|---|---|
| **Zadań MK ukończonych** | 3 (210 wspólne, 202, 203) |
| **PR-ów** | #11 (wspólny), #13, #14 |
| **Nowych LoC (202)** | +605 (w tym 163 testy) |
| **Nowych LoC (203)** | +610 (w tym 211 testy) |
| **Kontrakt API** | 409 LoC (`monitoring.md`) |
| **Nowych testów backendu** | +8 (4× timeseries, 4× persystencja) |
| **Testów backendu łącznie** | 9 (1 smoke + 4 + 4), wszystkie zielone |
| **Endpointów .NET dostarczonych** | 2 (`predict-timeseries`, `clients/{ref}/snapshots`) |
| **Tabel zapisywanych** | 3 (Snapshot, Prediction, Trend) |
| **Nowa migracja** | 0 (reuse schematu CREDIT-401) |
| **CI wall-clock (PR #14)** | Backend 45 s · Frontend 17 s · ML 1 min 0 s |

---

## 5. Co mój tor odblokował

Po dostarczeniu 203 (i wcześniej 210) status zmieniło 5 zadań:

| ID | Sprint | Owner | Odblokowane przez | Co |
|---|---|---|---|---|
| CREDIT-104 | 2 | GF | 210 | Flask `/predict/timeseries` (już 🟢) |
| CREDIT-301 | 3 | MK | 210 | Frontend Timeline (mock z kontraktu) |
| CREDIT-202 | 2 | MK | 210, 104 | (zrobione) |
| **CREDIT-204** | 3 | MK | **203** | `GET /clients/{ref}/history` (odczyt trajektorii) |
| **CREDIT-205** | 4 | MK | **203**, 201 | Testy persystencji (Testcontainers, ≥6) |

---

## 6. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**
- **Spójność kontrakt ↔ implementacja** — 202/203 implementują dokładnie typy i kody z `monitoring.md`;
  reuse `PredictTimeseriesAsync` w 203 eliminuje rozjazd logiki scoringu między endpointami.
- **Pułapka `timestamptz` + `DateOnly`** — wychwycona w testach, naprawiona przez `Kind=Utc`.

**Świadomie odłożone:**
- **Atomowość zapisu (transakcja DB)** — repozytoria robią osobne `SaveChanges`; jawna transakcja
  obejmująca migawkę+predykcje+trendy wejdzie z CREDIT-205 (tam też prawdziwy Postgres przez
  Testcontainers, bo EF InMemory nie testuje constraintów/kaskad).
- **409 vs upsert** — wybrałem 409; jeśli UX zdecyduje inaczej, zmiana jest punktowa.

---

## 7. Co dalej — Sprint 3 (mój tor)

| ID | Prio | Co |
|---|---|---|
| **CREDIT-204** | P0 | `GET /api/v1/monitoring/clients/{ref}/history` — złożenie zapisanych migawek w chronologiczną trajektorię PD (kontrakt 4.4) |
| **CREDIT-301** | P0 | Frontend Timeline — Recharts LineChart trajektorii (3 modele) + karty alertów semaforowych (na mocku z kontraktu) |

Oba są Sprint 3 P0. 204 domyka pętlę zapis→odczyt (zaczętą w 203), 301 to **główny slajd obrony**
(trajektoria PD w czasie). GF na osi tezy: 110 → 111 (dowód „statyka vs monitoring").

---

## 8. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 2)

> **Sprint 2 (tor MK) — monitoring działa end-to-end i jest trwały.**
>
> - **Kontrakt API** (`monitoring.md`, 409 LoC) — jedno źródło prawdy odblokowujące 4 zadania równolegle.
> - **CREDIT-202** — bezstanowy `POST /predict-timeseries`: proxy nad Flaskiem + labelki kalendarzowe
>   + mapowanie awarii ML na 400/502/503. 4 testy integracyjne.
> - **CREDIT-203** — stateful `POST /clients/{ref}/snapshots`: scoring (reuse) → zapis migawki +
>   predykcji W3 + trendów do Postgresa; auto-create klienta; 409 na duplikat. 4 testy (EF InMemory).
> - **9 testów backendu, CI zielone** (45 s). Zero nowych migracji — reuse schematu z Sprintu 1.
> - **Decyzje:** predykcje W3-only (#1), 409 na duplikat (#2) — domknięte open questions kontraktu.
>
> **Następne:** `GET /history` (204) domyka zapis→odczyt; Timeline (301) to slajd trajektorii PD.

---

<!-- ================== SPRINT 3 (tor GF) ================== -->

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

---

<!-- ================== SPRINT 4 (tor GF) ================== -->

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

---

<!-- ================== SPRINT 5 (tor GF) ================== -->

# Podsumowanie Sprintu 5 — tor GF (Gabriel Figur)

> ⚠️ **ERRATA 2026-07-07:** liczby fairness i progi w tym dokumencie (m.in. XGB próg 0.180,
> CatBoost 0.130, DPD/EOD z tabeli §2) pochodzą z runu sprzed naprawy wycieków metodologicznych
> (progi liczone na zbiorze testowym — tym samym, na którym audytowano fairness). Kanoniczne
> wartości po naprawie: `reports/fairness_metrics_w3.csv` (wszystkie |DPD|/|EOD| ≤ 0.04,
> werdykt bez zmian; LSTM DPD 0.006/EOD 0.021, CatBoost DPD 0.039/EOD 0.033) przy progach
> z `ml-service/alert_thresholds.json`. Szczegóły: `reports/threshold_leakage_fix.md`.
> Dokument pozostawiono bez przepisywania jako zapis historyczny sprintu.

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (GF)** w Sprint 5 projektu
> `ai-credit-management`. **Sprint 5 GF zamknięty 1/1 zadania świeżego** (CREDIT-112 fairness audit)
> + 2 follow-upy do CREDIT-109 (CREDIT-115 BE i CREDIT-116 FE) potraktowane jako audit-trail tasks
> wykonane chronologicznie między Sprintem 4 a Sprintem 5.
>
> Perspektywa toru MK Sprintu 5 (CREDIT-303 SnapshotForm + CREDIT-211 SHAP UI) — w
> `PodsumowanieSprintu2_MK.md` (update z 2026-06-06). Mój Sprint 4 (107/108/109 — w tym CREDIT-109
> pull-forwarded z planu Sprintu 5) — `PodsumowanieSprintu4_GF.md`.

---

## 1. Kontekst i mój zakres

**Plan Sprintu 5 mojego toru (per `TASKS.md` / `plan_sprintow_wariant_B.md`):**

| ID | Tag | Prio | Co |
|---|---|---|---|
| CREDIT-109 | ML | **P2** | LightGBM + CatBoost na oknach 3-mies. |
| CREDIT-112 | EVAL | **P1** SWAP-OK | Fairness audit (DPD / EOD per SEX) |

**Sytuacja na początku Sprintu 5:** CREDIT-109 **już dostarczone** w Sprincie 4 (PR #23, pull-forward
out-of-order pod łańcuch krytyczny `109 → 113 → 114`). Pozostało jedno fresh zadanie planowe —
**CREDIT-112** — plus dwa follow-upy do CREDIT-109 dosłodzone w oknie międzysprintowym (CREDIT-115
BE 5-model DTO, CREDIT-116 FE 5-model UI).

**Status po Sprincie 5 (kalendarzowo, 2026-06-06):**

| Status zadań mojego toru po Sprincie 5 |
|---|
| **CREDIT-112** — 🟢 zrobione (PR #37) — fairness audit fairlearn, 5 modeli, |DPD|/|EOD| ≤ 0.1 |
| **CREDIT-109** — 🟢 zrobione w Sprincie 4 (PR #23, patrz `PodsumowanieSprintu4_GF.md` §4) |
| **CREDIT-115** — 🟢 zrobione w oknie post-Sprint 4 (PR #32, patrz `PodsumowanieSprintu4_GF.md` §4.1) |
| **CREDIT-116** — 🟢 zrobione w oknie post-Sprint 4 (PR #33 + audit-trail PR #34) |

Harmonogram: Sprint 5 planowany **28 lip – 10 sie 2026**; mój tor dostarczony do **2026-06-06**
(przed planem, kontynuując pattern Sprintów 1–4).

**Pozostałe zadanie GF na Sprint 6:** **CREDIT-113** (stacked ensemble, P2) — odblokowane przez
CREDIT-109 + CREDIT-105 + CREDIT-102 (wszystkie 🟢). To ostatnie ogniwo przed CREDIT-114 (final
report, P0).

---

## 2. Co dostarczyłem — CREDIT-112 (Fairness audit, fairlearn)

**Plik:** `ml-learing-center/fairness_audit.py` (334 LoC, standalone) + `reports/fairness_report.md`
+ `reports/fairness_metrics_w3.csv` + 2 PNG; `requirements.txt` += `fairlearn>=0.10`. PR #37, merged
2026-06-06.

**Po co:** **wymóg regulacyjny + obronny.** AI Act (Art. 9 / 15) klasyfikuje systemy credit scoringu
jako *high-risk* i wymaga ewaluacji dyskryminacyjnej wpływu względem atrybutów chronionych. Bez
fairness audit'u praca magisterska o systemie kredytowym ma niezaadresowane ryzyko reputacyjne
*i* prawne. CREDIT-112 dostarcza formalną odpowiedź ze standardowymi metrykami fairlearn (DPD, EOD)
przy realnych progach decyzyjnych użytkowanych w produkcji.

**Co robi:**

1. **Reprodukuje 80/20 test split** (random_state=42, stratify=y) — ten sam, co CREDIT-103 /
   CREDIT-105 / CREDIT-110 / CREDIT-111. **Test set byte-identyczny** w całym projekcie (6 000
   klientów: 2 402 mężczyzn, 3 598 kobiet; SEX=1/2 zgodnie z UCI).
2. **Ładuje wszystkie 5 modeli W3** (RF, XGB, LightGBM, CatBoost — `.pkl`; LSTM `.keras` +
   `lstm_calibrator_w3.pkl` izotoniczny z CREDIT-105) i liczy `predict_proba` na test secie.
3. **Binaryzacja per-model cost-opt threshold** z `ml-service/alert_thresholds.json` (CREDIT-106,
   FN=5×FP). To kluczowa decyzja: **audyt fairness liczony jest przy realnym operating point**
   produkcji, nie przy arbitralnym 0.5. (RF 0.145, XGB 0.180, LightGBM 0.160, CatBoost 0.130, LSTM
   0.175.)
4. **Metryki fairlearn:**
   - **DPD** — `demographic_parity_difference(y_true, y_pred, sensitive_features=SEX)` —
     gap selection rate między grupami (P[ŷ=1|SEX=1] − P[ŷ=1|SEX=2]).
   - **EOD** — `equalized_odds_difference(...)` — `max(|ΔTPR|, |ΔFPR|)` między grupami.
   - **MetricFrame breakdown** per-grupa: `selection_rate`, `true_positive_rate`,
     `false_positive_rate`, `accuracy`.
5. **Warning rule (DoD):** `|DPD| > 0.1` lub `|EOD| > 0.1` → flaga `WARN` w raporcie.

**Wyniki (W3 calibrated, 5 modeli, cost-opt thresholds):**

| Model | Threshold | DPD | EOD | DPD warn | EOD warn |
|---|---:|---:|---:|:---:|:---:|
| Random Forest | 0.145 | +0.0347 | +0.0289 | ok | ok |
| XGBoost | 0.180 | +0.0377 | +0.0333 | ok | ok |
| LightGBM | 0.160 | +0.0269 | +0.0215 | ok | ok |
| **CatBoost** | 0.130 | **+0.0393** | **+0.0334** | ok | ok |
| **LSTM** | 0.175 | **+0.0068** | **+0.0153** | ok | ok |

**Wszystkie 5 modeli zdaje** rygor `|diff| ≤ 0.1`. Brak warningów.

**Per-group breakdown (najistotniejsze):**

| Model | sel_rate M | sel_rate F | TPR M | TPR F | FPR M | FPR F |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0.4621 | 0.4275 | 0.7576 | 0.7389 | 0.3721 | 0.3432 |
| XGBoost | 0.4721 | 0.4344 | 0.7683 | 0.7350 | 0.3819 | 0.3531 |
| LightGBM | 0.4455 | 0.4186 | 0.7487 | 0.7272 | 0.3531 | 0.3351 |
| CatBoost | 0.5237 | 0.4844 | 0.8164 | 0.7924 | 0.4345 | 0.4011 |
| LSTM | 0.4796 | 0.4864 | 0.7594 | 0.7702 | 0.3944 | 0.4096 |

**Interpretacja:**

- **DPD dodatnie dla wszystkich 5 modeli** — mężczyźni są flagowani nieco częściej niż kobiety
  (selection rate wyższy o 2–4 pp). **To nie jest „bias modelu" w czystej postaci** — odpowiada
  wyższemu *base rate* defaultów w grupie SEX=1 w danych UCI (24.2% vs 20.8% w teście). Modele
  trafnie odzwierciedlają strukturę danych, a różnice selection rate redukują się gdy uwzględnić
  prior klasy.
- **CatBoost największy DPD/EOD** (0.039/0.033) — koresponduje z jego niższym threshold'em (0.130
  cost-opt → globalnie więcej alarmów → większe wahania per-grupa).
- **LSTM najbliżej parytetu** (DPD 0.007, EOD 0.015) — ciekawe: LSTM jako jedyny model **odwraca**
  selection rate (wyższa dla kobiet 0.486 vs mężczyzn 0.480). Inna geometria reprezentacji
  sekwencyjnej (3 timesteps × 3 kanały) widocznie inaczej reaguje na sygnał SEX/płci. To wartościowy
  defensive talking point.
- **Wszystkie modele |diff| ≤ 0.04** — **4× pod DoD bound (0.1).** Margines bezpieczeństwa solidny.

**Honest framing dla obrony:**

> *„Audyt fairness na atrybucie SEX nie wykazał disparate impact'u przekraczającego konsensusowy
> próg 10% dla żadnego z 5 modeli przy cost-optymalnych progach produkcji. DPD dodatnie odzwierciedla
> wyższy base rate defaultów w grupie SEX=1 w danych UCI, nie systematyczny bias modeli. CatBoost ma
> największe |diff| (0.039), LSTM najbliżej parytetu (0.007). Sweep wykonany przy realnym operating
> point (cost-opt threshold, FN=5×FP z CREDIT-106), nie arbitralnym 0.5 — wynik więc reprezentuje
> faktyczne zachowanie systemu pod normalną decyzją alertu."*

**Output (1 MD + 1 CSV + 2 PNG):**

- `reports/fairness_report.md` — summary table + per-group breakdown + verdict
- `reports/fairness_metrics_w3.csv` — pełna tabela numeryczna (DPD, EOD, sel_rate, TPR, FPR,
  accuracy, n per grupa, warn flagi)
- `reports/fairness_selection_rate_w3.png` — grouped bar chart sel_rate M vs F per model
- `reports/fairness_tpr_fpr_w3.png` — dwupanelowy wykres TPR + FPR per grupa per model

**Scope decision (świadomie odłożone):**

- **Fairness względem AGE / EDUCATION / MARRIAGE** — UCI ma te atrybuty ale `SEX` jest najbardziej
  standardowym chronionym atrybutem w literaturze credit scoring + DoD CREDIT-112 explicite wymienia
  „per SEX". Pozostałe to kandydaty na appendix CREDIT-114 (final report).
- **Mitigacja (np. `ExponentiatedGradient`, `ThresholdOptimizer`)** — niezdane modele wymagałyby
  re-runów; wszystkie zdały, więc mitigacja nie potrzebna. Sweep mitigacyjny jako akademicki
  exercise mógłby trafić do CREDIT-114 dla pokazania pełnego pipeline'u.
- **Inne progi binaryzacji** (np. 0.5, max-F1, max-Youden) — DoD mówi „przy progach z CREDIT-106",
  trzymam się literalnie. Sensitivity analysis poszedł by jako appendix.

**Slajd:** *„Wszystkie 5 modeli przechodzi audyt fairlearn DPD/EOD per SEX przy realnych
cost-optymalnych progach: |diff| ≤ 0.04 wobec DoD 0.10 (4× margines). LSTM najbliżej parytetu (DPD
0.007), CatBoost największy diff (0.039). Disparate impact nie zmaterializowany. AI Act regulatory
checkbox: TAK."*

---

## 3. Follow-upy do CREDIT-109 zrobione w oknie międzysprintowym

CREDIT-115 (BE 5-model DTO) i CREDIT-116 (FE 5-model UI) to integration gapy odkryte 2026-06-05
podczas verification do seminarium między CREDIT-109 (Flask serwował 5 modeli) a CREDIT-202 (backend
DTO znał tylko 3 modele) → frontend Monitoring tab pokazywał 3/5 mimo, że Flask zwracał 5/5.

**CREDIT-115 (PR #32)** szczegółowo opisany w `PodsumowanieSprintu4_GF.md` §4.1. Streszczenie:

- `WindowPredictions` + `Trends` (.NET DTO): `Lightgbm` + `Catboost` properties z `[JsonPropertyName]`.
- `MonitoringService.ScoreAndPersistAsync`: persistuje **5 predictions + 5 trends** per snapshot.
- 5 Flask stub bodies w testach rozszerzonych, count assertions `3 → 5`.
- Bez migracji DB — `Prediction.ModelName` to free-form string.
- 24/24 backend testów ✅; curl pokazuje 5 modeli end-to-end.

**CREDIT-116 (PR #33 + audit-trail PR #34)** — frontend follow-up zamykający gap:

- `ModelKey` + `WindowPredictions` + `Trends` (TS): dodane `lightgbm` + `catboost`.
- `TimelineChart` z 5 liniami zamiast 3 — distinct colors (amber dla LightGBM, violet dla CatBoost).
- `TrendAlerts` z 5 kartami w responsive grid (`repeat(auto-fit, minmax(220px, 1fr))`).
- `MOCK_TIMESERIES_RESPONSE` rozszerzony.
- 16/16 vitest passing.
- PR #34 (chore): formalny audit trail dodający CREDIT-116 do plan_sprintow_wariant_B.md + CHECKLIST.

**Honest framing:** zarówno CREDIT-115, jak i CREDIT-116 **powinny były być w scope'ie CREDIT-109**
(DoD „response zawiera lightgbm, catboost" implicytnie obejmuje całą warstwę aż do UI, bo to UI jest
końcowym konsumentem). Nie były. Formalnie zatrackowane jako osobne tickety dla audit trail; ścieżka
od „found during demo prep" do „live demo zgodne z claim'em 5 modeli" zajęła trzy PR-y (#32 BE, #33
FE, #34 chore-track).

---

## 4. Statystyki mojego Sprintu 5 (kalendarzowo)

| Wskaźnik | Wartość |
|---|---|
| **Zadań GF planowanych (Sprint 5)** | 2 (CREDIT-109 P2, CREDIT-112 P1 SWAP-OK) |
| **Zadań GF zrobionych w oknie Sprintu 5** | 1 świeże (CREDIT-112) + 2 follow-upy (CREDIT-115 BE, CREDIT-116 FE) |
| **CREDIT-109** | zrobione w Sprincie 4 out-of-order (PR #23) — patrz `PodsumowanieSprintu4_GF.md` |
| **PR-ów w oknie Sprintu 5** | #32 (CREDIT-115), #33 (CREDIT-116), #34 (chore audit-trail 116), #37 (CREDIT-112) |
| **Nowych LoC (CREDIT-112)** | +334 (`fairness_audit.py`) + 1 MD + 1 CSV + 2 PNG |
| **Nowych dependencies** | `fairlearn>=0.10` |
| **Modeli w fairness audicie** | 5 (RF, XGB, LightGBM, CatBoost, LSTM) |
| **Max |DPD| / |EOD|** | 0.039 / 0.033 (CatBoost) — wszystkie pod DoD 0.10 |
| **Min |DPD| / |EOD|** | 0.007 / 0.015 (LSTM) — najbliżej parytetu |
| **Test set** | 6 000 klientów (2 402 M / 3 598 K) — ten sam, co CREDIT-103/105/110/111 |
| **Operating point audytu** | cost-opt thresholds per model z CREDIT-106 (nie arbitralne 0.5) |
| **Ścieżka krytyczna tezy** | bez zmiany (5/6 ogniw — CREDIT-114 czeka na CREDIT-113) |

---

## 5. Ścieżka krytyczna tezy — postęp po Sprincie 5 (mój tor)

Przed Sprintem 5:
```
101 ✅ → 102 ✅ → 104 ✅ → 110 ✅ → 111 ✅ → 114 🔒
                                              ↑ czeka na 113
```

Po Sprincie 5:
```
101 ✅ → 102 ✅ → 104 ✅ → 110 ✅ → 111 ✅ → 114 🔒
                                              ↑ czeka na 113 (Sprint 6, **moja kolejna piłka**)
```

**Bez zmiany w ścieżce krytycznej** — CREDIT-112 jest poza nią (P1 SWAP-OK, regulatory compliance,
nie blokuje nikogo). Ale **CREDIT-113 jest teraz jedynym pozostałym taskiem GF** który blokuje
CREDIT-114. Jeden PR i ścieżka krytyczna obrony tezy zamknięta.

---

## 6. Co mój tor odblokował

| ID | Sprint | Owner | Odblokowane przez | Status po Sprincie 5 |
|---|---|---|---|---|
| CREDIT-112 | 5 | GF | 102 | 🟢 (zrobiłem ja, ten sprint) |
| CREDIT-113 | 6 | GF | 102, 105, 109 | 🔴 dostępne (moja kolejna piłka) |
| CREDIT-114 | 6 | GF | 103, 111, **113** | 🔒 nadal czeka na 113 |

CREDIT-112 nie odblokowało nikogo — to było zadanie samodzielne. Ale fairness audit zamknął
**regulatory P1 obowiązek** przed CREDIT-114, więc final report będzie mógł odwołać się do gotowego
zdanego audytu bez warunku „assumed/skipped".

---

## 7. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**

- **AI Act fairness compliance** — CREDIT-112 dostarczył formalny audyt DPD/EOD fairlearn dla 5
  modeli, wszystkie zdane z 4× marginesem (|diff| ≤ 0.04 vs DoD 0.10). CREDIT-114 może odwołać się
  do raportu bez warunku.
- **Audyt przy realnym operating point** — wybór cost-opt thresholdów (CREDIT-106) zamiast
  arbitralnego 0.5 sprawia, że wynik fairness audit'u jest reprezentatywny dla *faktycznego*
  zachowania systemu pod alertem produkcji. Defensible przy „why these thresholds?" w Q&A.
- **5-model UI gap** (CREDIT-115/116) — closed end-to-end. Live demo pokazuje wszystkie 5 modeli
  w trajektorii Timeline + 5 kart Trend Alert zamiast poprzednich 3.

**Świadomie odłożone:**

- **Fairness audit innych atrybutów chronionych** (AGE, EDUCATION, MARRIAGE) — DoD CREDIT-112
  wymienia SEX explicite. Pozostałe to kandydaty na appendix CREDIT-114.
- **Mitigacja fairness (`ExponentiatedGradient`, `ThresholdOptimizer`)** — niepotrzebna, wszystkie
  modele zdane. Akademicki sweep mitigacyjny mógłby pójść do CREDIT-114 jako „bonus".
- **Sensitivity analysis różnych progów decyzyjnych** dla fairness (0.5, max-F1, max-Youden)
  — DoD trzymane literalnie.
- **Stacked ensemble (CREDIT-113)** — następna piłka, Sprint 6. LR meta-learner na 5 base modelach
  (RF/XGB/LightGBM/CatBoost/LSTM); oczekiwany uplift AUC 0.5–1 pp + lepsza kalibracja. Stos jest
  gotowy — wszystkie 5 modeli W3 + isotonic calibration + cost thresholds + fairness clearance.

---

## 8. Co dalej — Sprint 6 (mój tor)

**Ostatnie dwie piłki obrony tezy:**

1. **CREDIT-113** (stacked ensemble, P2, blocks 114) — LR meta-learner na 5 modelach bazowych.
   Wszystkie zależności zdane (CREDIT-102 ✅, CREDIT-105 ✅, CREDIT-109 ✅). Pojedynczy PR; trening
   meta-learnera na out-of-fold predykcjach 5 base modeli, ewaluacja na trzymanym test secie,
   porównanie z najlepszym single modelem (CatBoost AUC 0.7802).
2. **CREDIT-114** (final report, **P0**) — **zamknięcie tezy**. Generator zbiorczego raportu
   + komplet wykresów do slide-deck'a obrony. Pull-together CREDIT-103 (W3 metryki) + CREDIT-111
   (proof slide: static vs dynamic) + CREDIT-112 (fairness compliance) + CREDIT-113 (stacking
   uplift). To jest *the praca-do-obrony moment*.

**MK po Sprincie 5:**

- **CREDIT-304** (UI polish, P2, Sprint 6) — responsive (1024/1440/1920), a11y Lighthouse ≥ 90,
  dark mode, tooltipy modeli. Ostatni task toru MK.
- **CREDIT-501** (docs, P0, Sprint 6) — README + Model Card + Architecture + update CLAUDE.md.
  Wspólne (GF+MK), zależy ~od wszystkiego.

---

## 9. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 5)

> **Sprint 5 (tor GF) — fairness compliance + end-to-end 5-model closure.**
>
> - **Plan:** CREDIT-109 (LightGBM/CatBoost, P2) + CREDIT-112 (fairness, P1 SWAP-OK).
> - **CREDIT-109** zrobione w Sprincie 4 out-of-order pod łańcuch krytyczny — patrz Sprint 4.
> - **CREDIT-112 (fairlearn DPD/EOD per SEX, 5 modeli W3, cost-opt thresholds):**
>   - **Wszystkie 5 modeli zdane** — |DPD| ≤ 0.039, |EOD| ≤ 0.033, vs DoD 0.10 (**4× margines**).
>   - **CatBoost największy** |diff| (0.039), **LSTM najbliżej parytetu** (0.007).
>   - DPD dodatnie odzwierciedla **wyższy base rate defaultów w grupie SEX=1 w UCI**, nie bias modeli.
>   - Audyt przy **realnym operating point** (cost-opt threshold CREDIT-106, FN=5×FP) — nie 0.5.
> - **Follow-upy do CREDIT-109 zamknięte** (CREDIT-115 BE 5-model DTO + CREDIT-116 FE 5-model UI):
>   live demo pokazuje teraz 5/5 modeli end-to-end (Flask → .NET → React) zamiast 3/5.
> - **Ścieżka krytyczna:** bez zmiany (5/6); pozostaje **jedna piłka** do CREDIT-114 →
>   **CREDIT-113** (stacking).
>
> **Następne (mój tor):** CREDIT-113 (stacking ensemble) → CREDIT-114 (final report — slide-deck do
> obrony).