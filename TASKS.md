Zapl# TASKS.md — Backlog wykonawczy (Wariant B: monitoring kalendarzowy)

> Plik dla Claude Code. Architektura, porty i komendy: patrz `CLAUDE.md`. Ten plik zawiera kompletny backlog z ID zadań, sprintami, branchami i zależnościami blokującymi.
>
> **REGUŁA NACZELNA:** Nie zaczynaj zadania, którego `blocked_by` nie jest jeszcze zmergowane do `main`. Jeśli zależność blokuje przez kontrakt API (`[CONTRACT]`), wystarczy że kontrakt jest w `main` — implementację backendu można mockować.

---

## Kontekst tezy (Wariant B)

Dynamika = **monitoring kalendarzowy**: ten sam klient oceniany wielokrotnie w czasie; system śledzi trajektorię PD i wykrywa pogorszenie zanim dojdzie do defaultu. Dowód tezy = eksperyment „statyka jednorazowa vs monitoring kalendarzowy" (CREDIT-111).

---

## ⚠️ Metodyka danych — PRZECZYTAJ przed CREDIT-101/102/104

Złamanie tych reguł unieważnia tezę. Stosuj bezwzględnie.

- Zbiór: UCI `default_of_credit_card_clients.csv` (Taiwan 2005), ładowany w `ml-learing-center/main.py` przez `pd.read_csv(..., header=1)`. Każdy klient = 1 wiersz, 6 mies. historii, 1 etykieta (`Default` = default w październiku).
- Mapowanie miesięcy (najnowszy → najstarszy):
  - `PAY_0`=wrzesień, `PAY_2`=sierpień, `PAY_3`=lipiec, `PAY_4`=czerwiec, `PAY_5`=maj, `PAY_6`=kwiecień (UWAGA: `PAY_1` NIE istnieje w zbiorze).
  - `BILL_AMT1`=wrzesień … `BILL_AMT6`=kwiecień; `PAY_AMT1`=wrzesień … `PAY_AMT6`=kwiecień.
- Sliding window 3-miesięczny → 4 okna na klienta (od najstarszego do najnowszego):
  - `W0`=[kwi,maj,cze] → PAY_6,PAY_5,PAY_4 / BILL 6,5,4 / PAY_AMT 6,5,4
  - `W1`=[maj,cze,lip] → PAY_5,PAY_4,PAY_3 / BILL 5,4,3 / PAY_AMT 5,4,3
  - `W2`=[cze,lip,sie] → PAY_4,PAY_3,PAY_2 / BILL 4,3,2 / PAY_AMT 4,3,2
  - `W3`=[lip,sie,wrz] → PAY_3,PAY_2,PAY_0 / BILL 3,2,1 / PAY_AMT 3,2,1
- **NIE fabrykuj danych ani etykiet pośrednich.** Używaj wyłącznie realnych kolumn. Jedna etykieta (październik) wspólna dla wszystkich okien danego klienta.
- **Trening:** na oknie `W3` (najnowsze 3 mies.), wyrównanym do etykiety. Przy inferencji TEN SAM model przesuwany na W0–W3 → trajektoria PD. Dzięki temu rozkład treningowy = inferencyjny (brak OOD).
- Cechy pochodne (`PAY_mean`, `BILL_trend`, `late_count` itd.) liczone na 3 punktach okna, nie na 6. Tensor LSTM: `(N, 3, 3)` zamiast `(N, 6, 3)`.

---

## Architektura warstw (Wariant B)

- **Flask (`ml-service/`)** — bezstanowy silnik scoringu. Bez bazy danych. Nowy endpoint `/predict/timeseries` (22 cechy → rozbicie na 4 okna → PD per okno per model → trendy).
- **.NET (`backend/WebApi/`)** — orkiestracja + TRWAŁOŚĆ. PostgreSQL + EF Core. Przechowuje Client/Snapshot/Prediction/Trend, składa i serwuje historię klienta.
- **React (`frontend/WebApp/`)** — zarządzanie klientami, wprowadzanie migawek w czasie, wykres trajektorii PD + alerty.

---

## Konwencje

- Owner: `GF` = Gabriel Figur, `MK` = Mikołaj Kusiński. Etykiety NIE są wiążące — zadania `SWAP-OK` można dowolnie zamieniać (obaj fullstack).
- Tag: `[DATA]` `[ML]` `[EVAL]` `[BE]` `[FE]` `[DB]` `[INFRA]` `[CONTRACT]` `[DOCS]`.
- Branch: `sprintN/krótka-nazwa`. Jeden PR = jedno zadanie. Review przez drugą osobę. Merge tylko przy zielonym CI.
- Definition of Done: kod + testy + zaktualizowana dokumentacja, jeśli zmienia kontrakt/architekturę.

---

## Zadania — pełne specyfikacje

### Sprint 1 — Fundament danych i trwałości (2 cze – 15 cze)

**CREDIT-101 · [DATA] · P0 · GF · branch `sprint1/sliding-window-panel`**
- blocked_by: —  |  blocks: 102, 103, 110, 111
- Cel: przekształcić wiersz UCI w 4 okna 3-mies. wg mapowania wyżej.
- Pliki: nowy `ml-learing-center/sliding_window.py`; modyfikacja `main.py`.
- DoD: funkcja `extract_windows(row)` zwraca 4 okna po 3 wartości w każdym kanale (pay/bill/amt); test pytest weryfikuje kształt i że W3 = najnowsze miesiące. Żadnych zmyślonych wartości.

**CREDIT-102 · [ML] · P0 · GF · branch `sprint1/retrain-3mo`**
- blocked_by: 101  |  blocks: 103,104,105,106,107,108,109,110,112,113
- Cel: przetrenować RF/XGBoost/LSTM na oknie W3 (3 mies.); LSTM input `(N,3,3)`.
- Pliki: `main.py`, `engineer_features` (parametr okna), zapis NOWYCH artefaktów z sufiksem `_w3`: `rf_model_w3.pkl`/`xgb_model_w3.pkl`/`lstm_model_w3.keras`/`scaler_w3.pkl`/`lstm_scalers_w3.pkl`/`features_w3.pkl`. **NIE nadpisywać** istniejących artefaktów bez sufiksu — zostają działające dla legacy `/predict` aż do CREDIT-104.
- Dodatkowo: wyrównać mismatche feature engineering między `main.py` a `ml-service/app.py` — `utilization_rate` (oba mają używać `BILL_mean / LIMIT_BAL`) oraz `severe_late` (oba mają używać `(df[pay_cols] >= 2).any(axis=1).astype(int)`).
- DoD: nowe artefakty `_w3` zgodne z oknem 3-mies.; AUC wypisane dla 3 modeli; stare artefakty nietknięte; feature engineering w `main.py` i `app.py` zgodny.

**CREDIT-103 · [EVAL] · P0 · GF · branch `sprint1/revalidate-metrics`**
- blocked_by: 102  |  blocks: 114
- Cel: rozszerzone metryki (AUC, Gini, KS, confusion matrix, ROC, PR, calibration) dla modeli 3-mies.
- Pliki: nowy `ml-learing-center/evaluation.py`; wykresy do `ml-learing-center/reports/`.
- DoD: ≥9 wykresów w `reports/`; tabela metryk w konsoli.

**CREDIT-401 · [DB] · P0 · MK · branch `sprint1/db-schema`**
- blocked_by: —  |  blocks: 402, 203, 204
- Cel: schemat PostgreSQL + EF Core: Client, Snapshot, Prediction, Trend (relacje 1:N).
- Pakiety NuGet do dodania w `WebApi.csproj`: `Microsoft.EntityFrameworkCore`, `Microsoft.EntityFrameworkCore.Design`, `Microsoft.EntityFrameworkCore.Tools`, `Npgsql.EntityFrameworkCore.PostgreSQL`. Rejestracja `DbContext` w `Program.cs`.
- Pliki: `backend/WebApi/WebApi.csproj` (pakiety), `backend/WebApi/Data/AppDbContext.cs`, `backend/WebApi/Models/Entities/*` (Client, Snapshot, Prediction, Trend), `backend/WebApi/Program.cs`, `backend/WebApi/appsettings.json` (connection string `Default`), `backend/WebApi/Migrations/*` (auto).
- DoD: `dotnet ef migrations add Init` przechodzi; schemat tworzy się w bazie.

**CREDIT-402 · [INFRA] · P1 · MK · branch `sprint1/docker-postgres`**
- blocked_by: 401  |  blocks: —
- Cel: docker-compose z usługami db (postgres:16) + backend + ml-service; auto-migracje przy starcie backendu. **Frontend POZA compose** — pozostaje uruchamiany przez `npm run dev` lokalnie.
- Pliki: `docker-compose.yml` (root), `backend/WebApi/Dockerfile`, drobna zmiana `backend/WebApi/Program.cs` (auto-migracja przy starcie: `db.Database.Migrate()`).
- DoD: `docker-compose up` stawia bazę i backend; backend łączy się z bazą; migracje wykonują się automatycznie.

**CREDIT-201 · [INFRA] · P1 · MK · `SWAP-OK` · branch `sprint1/test-infra`**
- blocked_by: —  |  blocks: 205
- Cel: infrastruktura testów (xUnit + pytest + Vitest) + CI blokujące czerwone PR.
- Pliki: `backend/WebApi.Tests/`, `ml-service/tests/`, `frontend/WebApp/vitest.config.ts`, `.github/workflows/ci.yml`.
- DoD: po 1 smoke teście na stack przechodzi; CI zielone na PR.

### Sprint 2 — Silnik monitoringu, kontrakty, zapis (16 cze – 29 cze)

**CREDIT-210 · [CONTRACT] · P0 · GF+MK · branch `sprint2/contract-monitoring`**
- blocked_by: —  |  blocks: 104, 202, 203, 301
- Cel: payload trajektorii + zapisu migawki. Reguła alertu: slope(W3−W0) > próg → INCREASING_RISK; < −próg → DECREASING_RISK; inaczej STABLE.
- Pliki: `docs/api-contracts/monitoring.md`.
- DoD: kontrakt w `main`; obie strony potwierdzają wykonalność.

**CREDIT-104 · [ML] · P0 · GF · branch `sprint2/flask-timeseries`**
- blocked_by: 102, 210  |  blocks: 110, 202
- Cel: endpoint Flask `/predict/timeseries` — rozbicie na 4 okna, PD per okno per model, trendy. Refactor wspólnego `predict_single()`.
- Pliki: `ml-service/app.py`.
- DoD: rosnące opóźnienia → INCREASING_RISK; pytest weryfikuje 4 punkty trajektorii.

**CREDIT-105 · [ML] · P0 · GF · branch `sprint2/calibration`**
- blocked_by: 102  |  blocks: 106, 113
- Cel: kalibracja isotoniczna (3-way split train/calib/test); P0 bo trajektoria wymaga sensownych bezwzględnych PD.
- Pliki: `main.py`, nadpisanie `.pkl`.
- DoD: reliability diagram blisko diagonali; Brier po < przed.

**CREDIT-202 · [BE] · P0 · MK · branch `sprint2/dotnet-timeseries`**
- blocked_by: 210 (mock) / 104 (real)  |  blocks: —
- Cel: `.NET POST /api/monitoring/predict-timeseries` — walidacja, wywołanie Flask, mapowanie. Mockować do czasu 104.
- Pliki: `Controllers/MonitoringController.cs`, `Models/TimeseriesRequest.cs`, `Models/TimeseriesResponse.cs`, `Services/PythonModelClient.cs`.
- DoD: test integracyjny z mockowanym HttpMessageHandler; happy path 200.

**CREDIT-203 · [BE] · P0 · MK · branch `sprint2/persistence-write`**
- blocked_by: 401, 210  |  blocks: 204, 205
- Cel: repozytoria EF Core zapisujące migawkę (z datą) + predykcje przy każdej ocenie.
- Pliki: `Services/SnapshotRepository.cs`, `Services/PredictionRepository.cs`.
- DoD: po ocenie rekordy w tabelach Snapshot+Prediction; test integracyjny.

### Sprint 3 — Dowód tezy + start frontendu (30 cze – 13 lip)

**CREDIT-110 · [EVAL] · P0 · GF · branch `sprint3/timeseries-metrics`**
- blocked_by: 101, 102, 104  |  blocks: 111
- Cel: metryki time-series — early-warning lead time, rozkład slope (default vs non-default), AUC trajektorii.
- Pliki: `ml-learing-center/timeseries_eval.py`.
- DoD: raport lead time + boxplot slope obu klas.

**CREDIT-111 · [EVAL] · P0 · GF · branch `sprint3/static-vs-dynamic`**
- blocked_by: 110  |  blocks: 114
- Cel: DOWÓD TEZY — porównanie statyka jednorazowa (PD z W3) vs monitoring (alert gdy trajektoria przekracza próg). Catch rate vs fałszywe alarmy.
- Pliki: `ml-learing-center/static_vs_dynamic.py`, wykres do `reports/`.
- DoD: tabela + wykres z uczciwą interpretacją.

**CREDIT-106 · [ML] · P1 · GF · `SWAP-OK` · branch `sprint3/cost-thresholds`**
- blocked_by: 105  |  blocks: —
- Cel: próg alertu minimalizujący koszt oczekiwany (FN > FP) zamiast 0,5.
- Pliki: `main.py`, `alert_thresholds.json`, `app.py`.
- DoD: progi w (0,1; 0,9); Flask ich używa.

**CREDIT-204 · [BE] · P0 · MK · branch `sprint3/client-history-get`**
- blocked_by: 203  |  blocks: 302
- Cel: `GET /api/monitoring/clients/{ref}/history` — zwraca zapisaną trajektorię klienta.
- Pliki: `Controllers/MonitoringController.cs`.
- DoD: po 3 migawkach GET zwraca 3 punkty posortowane po dacie.

**CREDIT-301 · [FE] · P0 · MK · branch `sprint3/timeline-view`**
- blocked_by: 210  |  blocks: 302, 303
- Cel: widok Timeline — Recharts LineChart (X=okno/data, Y=PD, 3 linie) + karty alertów. Praca na mocku z kontraktu.
- Pliki: `components/TimelineChart.tsx`, `components/TrendAlerts.tsx`, `api/monitoringApi.ts`, `App.tsx`.
- DoD: rysuje 4 punkty/model + alerty; test Vitest.

### Sprint 4 — Integracja + interpretowalność + tuning (14 lip – 27 lip)

**CREDIT-302 · [FE] · P1 · MK · branch `sprint4/client-history-ui`**
- blocked_by: 204, 301  |  blocks: 304
- Cel: lista klientów + widok historii na realnych danych z bazy.
- Pliki: `components/ClientList.tsx`, `components/ClientHistory.tsx`.
- DoD: end-to-end zapis migawki → widoczna w historii klienta.

**CREDIT-205 · [BE] · P1 · MK · `SWAP-OK` · branch `sprint4/persistence-tests`**
- blocked_by: 203, 201  |  blocks: —
- Cel: testy integracyjne persystencji (Testcontainers lub SQLite in-memory).
- Pliki: `WebApi.Tests/PersistenceTests.cs`.
- DoD: ≥6 testów zapis→odczyt.

**CREDIT-107 · [ML] · P2 · GF · `SWAP-OK` · branch `sprint4/shap`**
- blocked_by: 102  |  blocks: 211
- Cel: SHAP top-5 cech per predykcja (RF/XGB/LR).
- Pliki: `ml-service/requirements.txt`, `app.py` (`compute_shap`).
- DoD: response zawiera `shap.topFeatures` (5); czas < 2s.

**CREDIT-108 · [ML] · P2 · GF · branch `sprint4/optuna-cv`**
- blocked_by: 102  |  blocks: —
- Cel: 5-fold CV + tuning Optuna (XGBoost/RF) na oknach 3-mies.
- Pliki: `main.py`, `requirements.txt`.
- DoD: AUC po ≥ przed; CV-score ze std.

### Sprint 5 — UX migawek, alerty, modele, fairness (28 lip – 10 sie)

**CREDIT-303 · [FE] · P1 · MK · branch `sprint5/snapshot-entry`**
- blocked_by: 210, 301  |  blocks: 304
- Cel: wprowadzanie migawek (reuse InputForm + datepicker) + UI alertów + fix zahardkodowanych miesięcy w `InputForm.tsx` (TODO) + „kopiuj z poprzedniej".
- Pliki: `components/SnapshotForm.tsx`, `components/InputForm.tsx`.
- DoD: dodanie migawki z datą → zapis → widoczne w historii; miesiące dynamiczne.

**CREDIT-211 · [BE/FE] · P2 · MK · `SWAP-OK` · branch `sprint5/shap-ui`**
- blocked_by: 107, 210  |  blocks: —
- Cel: pass-through SHAP w .NET DTO + komponent wizualizacji (bar/waterfall).
- Pliki: `Models/PredictResponse.cs`, `components/ShapExplanation.tsx`.
- DoD: 5 pasków (czerwone +, zielone −) dla payloadu SHAP.

**CREDIT-109 · [ML] · P2 · GF · branch `sprint5/lgbm-catboost`**
- blocked_by: 102  |  blocks: 113
- Cel: LightGBM + CatBoost na oknach 3-mies.
- Pliki: `main.py`, `app.py`, `requirements.txt`.
- DoD: response zawiera `lightgbm`,`catboost`; raport 6 modeli.

**CREDIT-112 · [EVAL] · P1 · GF · `SWAP-OK` · branch `sprint5/fairness`**
- blocked_by: 102  |  blocks: —
- Cel: audyt fairness (fairlearn) — demographic parity + equalized odds względem SEX.
- Pliki: `ml-learing-center/fairness_audit.py`, `reports/fairness_report.md`.
- DoD: DPD/EOD per model; ostrzeżenie gdy |różnica| > 0,1.

**CREDIT-115 · [BE] · P2 · GF · branch `feat/backend-5model-dtos`**
- blocked_by: 109, 202  |  blocks: 116
- Cel: integration follow-up do CREDIT-109. Backend DTO (`WindowPredictions`, `Trends`) z CREDIT-202 są 3-modelowe; po dodaniu LightGBM/CatBoost w Flasku (CREDIT-109) backend silently dropował 2 modele z każdego response. Rozszerzyć DTO + persistence + history mapping o `lightgbm` i `catboost` (passthrough z Flaska). Bez migracji DB (`Prediction.ModelName` to free-form string).
- Pliki: `backend/WebApi/Models/TimeseriesResponse.cs`, `Models/SnapshotResponse.cs`, `Services/MonitoringService.cs`, 5 plików testowych (Flask stub bodies + per-snapshot count assertions 3 → 5).
- DoD: `/api/v1/monitoring/predict-timeseries` zwraca 5 modeli w `predictions` + `trends`; `POST .../snapshots` zapisuje 5 predictions + 5 trends per snapshot; `GET .../history` zwraca 5-modelowe punkty trajektorii; 24/24 backend testów zielone.
- Kontekst: gap odkryty 2026-06-05 podczas weryfikacji live demo do seminarium (curl pokazał 3 model keys zamiast 5). Formalnie powinien być częścią scope'u CREDIT-109; tu osobny task dla audit trail.

**CREDIT-116 · [FE] · P2 · GF · branch `feat/frontend-5model-monitoring`**
- blocked_by: 115, 301  |  blocks: —
- Cel: dokończenie 5-model UI w zakładce Monitoring po CREDIT-115. Frontend (`ModelKey` w TS + `MODELS` w Recharts + grid columns w TrendAlerts) hardcodowane na 3 modele — UI pokazywało 3 linie / 3 karty zamiast 5 mimo że backend zwracał 5. Rozszerzyć typy + Timeline chart + TrendAlerts + MOCK_TIMESERIES_RESPONSE.
- Pliki: `frontend/WebApp/src/types/monitoring.ts`, `components/TimelineChart.tsx`, `components/TrendAlerts.tsx`, `api/monitoringApi.ts` (MOCK), 3 test files (`TimelineChart.test.tsx`, `TrendAlerts.test.tsx`, `ClientHistory.test.tsx`).
- DoD: Timeline rysuje 5 linii (RF/XGB/LightGBM/CatBoost/LSTM z distinct colors — amber/violet dla 2 nowych); TrendAlerts pokazuje 5 kart w responsive grid (`repeat(auto-fit, minmax(220px, 1fr))`); 16/16 vitest passing.
- Kontekst: odkryty 2026-06-05 podczas re-runu live demo po merge CREDIT-115. Naturalne rozszerzenie scope'u CREDIT-115; osobny task dla audit trail. Prediction tab (legacy `/predict`) nietknięty — endpoint nadal 3-modelowy (LightGBM/CatBoost = W3-only per CREDIT-109).

### Sprint 6 — Polish, ensemble, raport, docs (11 sie – 24 sie)

**CREDIT-113 · [ML] · P2 · GF · branch `sprint6/stacking`**
- blocked_by: 102, 105, 109  |  blocks: 114
- Cel: stacked ensemble (LR meta-learner na predykcjach modeli bazowych).
- Pliki: `main.py`, `app.py`.
- DoD: AUC ensemble ≥ najlepszy pojedynczy; klucz `ensemble` w response.

**CREDIT-114 · [EVAL] · P0 · GF · branch `sprint6/final-report`**
- blocked_by: 103, 111, 113  |  blocks: —
- Cel: raport końcowy + eksport wykresów do prezentacji.
- Pliki: `ml-learing-center/generate_final_report.py`, `reports/final_report.md`.
- DoD: zbiorczy raport + komplet wykresów do slajdów.

**CREDIT-304 · [FE] · P2 · MK · branch `sprint6/ui-polish`**
- blocked_by: 302, 303  |  blocks: —
- Cel: responsive, a11y, dark mode, tooltipy modeli.
- Pliki: `frontend/WebApp/src/components/*`.
- DoD: responsywność 1024/1440/1920; Lighthouse a11y ≥ 90.

**CREDIT-501 · [DOCS] · P0 · GF+MK · branch `sprint6/docs`**
- blocked_by: ~wszystko  |  blocks: —
- Cel: README, Model Card, Architecture, aktualizacja `CLAUDE.md` (nowe endpointy, baza, okno 3-mies.).
- Pliki: `README.md`, `docs/MODEL_CARD.md`, `docs/ARCHITECTURE.md`, `CLAUDE.md`.
- DoD: README z uruchomieniem przez docker-compose; model card wg szablonu Google.

---

## Tabela zależności (szybki przegląd dla schedulera)

| ID | Sprint | Prio | Tag | Owner | blocked_by | blocks |
|----|--------|------|-----|-------|------------|--------|
| 101 | 1 | P0 | DATA | GF | — | 102,103,110,111 |
| 102 | 1 | P0 | ML | GF | 101 | 103,104,105,106,107,108,109,110,112,113 |
| 103 | 1 | P0 | EVAL | GF | 102 | 114 |
| 401 | 1 | P0 | DB | MK | — | 402,203,204 |
| 402 | 1 | P1 | INFRA | MK | 401 | — |
| 201 | 1 | P1 | INFRA | MK | — | 205 |
| 210 | 2 | P0 | CONTRACT | GF+MK | — | 104,202,203,301 |
| 104 | 2 | P0 | ML | GF | 102,210 | 110,202 |
| 105 | 2 | P0 | ML | GF | 102 | 106,113 |
| 202 | 2 | P0 | BE | MK | 210,104 | — |
| 203 | 2 | P0 | BE | MK | 401,210 | 204,205 |
| 110 | 3 | P0 | EVAL | GF | 101,102,104 | 111 |
| 111 | 3 | P0 | EVAL | GF | 110 | 114 |
| 106 | 3 | P1 | ML | GF | 105 | — |
| 204 | 3 | P0 | BE | MK | 203 | 302 |
| 301 | 3 | P0 | FE | MK | 210 | 302,303 |
| 302 | 4 | P1 | FE | MK | 204,301 | 304 |
| 205 | 4 | P1 | BE | MK | 203,201 | — |
| 107 | 4 | P2 | ML | GF | 102 | 211 |
| 108 | 4 | P2 | ML | GF | 102 | — |
| 303 | 5 | P1 | FE | MK | 210,301 | 304 |
| 211 | 5 | P2 | BE/FE | MK | 107,210 | — |
| 109 | 5 | P2 | ML | GF | 102 | 113 |
| 112 | 5 | P1 | EVAL | GF | 102 | — |
| 115 | 5 | P2 | BE | GF | 109,202 | 116 |
| 116 | 5 | P2 | FE | GF | 115,301 | — |
| 113 | 6 | P2 | ML | GF | 102,105,109 | 114 |
| 114 | 6 | P0 | EVAL | GF | 103,111,113 | — |
| 304 | 6 | P2 | FE | MK | 302,303 | — |
| 501 | 6 | P0 | DOCS | GF+MK | ~all | — |

## Ścieżka krytyczna (oś tezy)
`101 → 102 → 104 → 110 → 111 → 114`. Priorytet bezwzględny. Tor persystencji (`401 → 203 → 204`) i tor frontendu (`210 → 301 → 302/303`) biegną równolegle.
