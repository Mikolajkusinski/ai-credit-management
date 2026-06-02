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
