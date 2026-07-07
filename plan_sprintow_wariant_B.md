# Plan sprintów — Wariant B (monitoring kalendarzowy) — system oceny ryzyka kredytowego

> Wariant tezy: **dynamika = monitoring kalendarzowy wielu migawek**. System ocenia tego samego klienta wielokrotnie w czasie i śledzi trajektorię PD. Źródło danych: UCI „Default of Credit Card Clients" (Taiwan 2005), przekształcony metodą sliding-window. Termin: wrzesień 2026 (6 sprintów + bufor).

---

## Zespół i zasady

**Gabriel Figur (GF)** i **Mikołaj Kusiński (MK)** — obaj fullstack. Zadania rozdzielone **równomiernie wg obciążenia**, nie wg sztywnych ról. Etykiety właściciela nie są wiążące: każde zadanie oznaczone `SWAP-OK` można przejąć nawzajem. Układ zaprojektowany tak, by w każdym sprincie obie osoby miały niezależny tor pracy i nie czekały na siebie.

### Branching (GitHub Flow)
- `main` — zawsze zielony, merge tylko przez PR z przechodzącym CI.
- Feature branche: `sprintN/krótka-nazwa` (np. `sprint1/sliding-window-panel`).
- Branche kontraktowe: `sprintN/contract-nazwa`.
- Każdy PR: review drugiej osoby.

### Klucz do równoległości — kontrakty API
Zadania `[CONTRACT]` to wspólne 30-minutowe sesje, na których ustalacie payload JSON i commitujecie go do `docs/api-contracts/`. Po tym jedna osoba implementuje backend, druga mockuje payload i buduje przeciwko niemu — bez czekania.

### Harmonogram sprintów
| Sprint | Daty | Cel | Thesis-critical? |
|---|---|---|---|
| 1 | 2 cze – 15 cze | Fundament danych (sliding-window + przetrenowanie) + fundament bazy | **Tak — bez danych panelowych nie ma Wariantu B** |
| 2 | 16 cze – 29 cze | Silnik monitoringu (trajektoria PD + trendy), kontrakty, zapis do bazy | **Tak** |
| 3 | 30 cze – 13 lip | Ewaluacja dynamiki (dowód tezy) + start frontendu | **Tak — to dowód tezy** |
| 4 | 14 lip – 27 lip | Integracja end-to-end + interpretowalność + tuning | Częściowo |
| 5 | 28 lip – 10 sie | UX migawek, alerty, rozszerzenie modeli, fairness | Nie |
| 6 | 11 sie – 24 sie | Polish, ensemble, raport końcowy, dokumentacja | Tak (raport) |
| Bufor | 25 sie – wrzesień | Pisanie pracy + przygotowanie do obrony | — |

---

## Fundament metodyczny — jak zlikwidować lukę danych z zachowaniem prawdziwości

To jest najważniejsza część całego Wariantu B. Czytaj uważnie, bo na tym opiera się obrona.

### Zasada nadrzędna: nie fabrykujemy danych
Sliding-window nie tworzy żadnych nowych wartości. Każda migawka używa **wyłącznie prawdziwych kolumn z prawdziwej historii klienta**. Zmieniamy jedynie to, *które* miesiące są „widoczne" w danym momencie. Każdy klient ma jeden prawdziwy wynik (default w październiku) — i ten jeden wynik jest wspólny dla wszystkich jego migawek. **Nie wymyślamy etykiet pośrednich.**

### Mapowanie kolumn UCI na czas
W zbiorze UCI najnowszy miesiąc ma indeks 1 (lub PAY_0), najstarszy indeks 6:

| Miesiąc | Status płatności | Rachunek | Wpłata |
|---|---|---|---|
| wrzesień (najnowszy) | PAY_0 | BILL_AMT1 | PAY_AMT1 |
| sierpień | PAY_2 | BILL_AMT2 | PAY_AMT2 |
| lipiec | PAY_3 | BILL_AMT3 | PAY_AMT3 |
| czerwiec | PAY_4 | BILL_AMT4 | PAY_AMT4 |
| maj | PAY_5 | BILL_AMT5 | PAY_AMT5 |
| kwiecień (najstarszy) | PAY_6 | BILL_AMT6 | PAY_AMT6 |

(Uwaga: w UCI nie ma `PAY_1` — to znana cecha zbioru. Sekwencja to PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6.)

### Schemat 4 okien 3-miesięcznych
Z 6 miesięcy budujemy 4 nakładające się okna 3-miesięczne, tworzące pseudo-oś czasu od najstarszego do najnowszego:

| Okno | Zakres | Status | Rachunek | Wpłata |
|---|---|---|---|---|
| W0 (najstarsze) | kwi–cze | PAY_6, PAY_5, PAY_4 | BILL 6,5,4 | PAY_AMT 6,5,4 |
| W1 | maj–lip | PAY_5, PAY_4, PAY_3 | BILL 5,4,3 | PAY_AMT 5,4,3 |
| W2 | cze–sie | PAY_4, PAY_3, PAY_2 | BILL 4,3,2 | PAY_AMT 4,3,2 |
| W3 (najnowsze) | lip–wrz | PAY_3, PAY_2, PAY_0 | BILL 3,2,1 | PAY_AMT 3,2,1 |

Każde okno = realny 3-miesięczny wycinek historii klienta. Cztery okna = 4-punktowa trajektoria PD.

### Trening i zgodność rozkładów (kluczowe dla poprawności)
- Modele trenujemy na **najnowszym oknie W3** (lip–wrz), wyrównanym do etykiety defaultu z października. Model uczy się: „mając ostatnie 3 miesiące, czy klient zdefaultuje w następnym miesiącu?".
- W inferencji **ten sam model** stosujemy do każdego z okien W0–W3. Ponieważ każde okno to wycinek 3-miesięczny o identycznej strukturze, rozkład inferencyjny zgadza się z treningowym — **brak oceny out-of-distribution.**
- Trenujemy na jednym oknie na klienta (W3) → jedna etykieta na klienta, bez przeliczania defaultów. (Augmentacja wszystkimi 4 oknami jest możliwa jako eksperyment poboczny, ale niesie ryzyko wycieku — domyślnie trenujemy na W3.)
- `engineer_features()` i `prepare_lstm_input()` muszą zostać sparametryzowane oknem: statystyki (PAY_mean, BILL_trend, late_count itd.) liczone na 3 punktach, tensor LSTM ma kształt `(1, 3, 3)` zamiast `(1, 6, 3)`.

### Jak ewaluujemy samą dynamikę
- **Early-warning lead time** — dla klientów, którzy faktycznie zdefaultowali: w którym najwcześniejszym oknie PD przekroczyło próg alertu? Lead = liczba okien przed punktem decyzyjnym, w których system już ostrzegał.
- **Analiza trajektorii** — rozkład nachylenia (slope) trajektorii PD: defaultujący powinni mieć trajektorie rosnące, zdrowi płaskie.
- **Statyka vs monitoring** — porównanie: ile defaultów wyłapuje podejście monitorujące (rosnąca trajektoria przekracza próg w którymkolwiek oknie) vs ocena statyczna jednorazowa (jedno PD z W3 z progiem). To jest slajd rozstrzygający tezę.

---

## SPRINT 1 — Fundament danych i trwałości (2 cze – 15 cze)

Cel: zamknąć lukę danych (panel + przetrenowanie) ORAZ postawić bazę. Dwa w pełni niezależne tory.

### CREDIT-101 [DATA] Budowa panelu sliding-window (okna 3-mies.)
- Priorytet: **P0** · Owner: GF · Branch: `sprint1/sliding-window-panel`
- Deps: — · Blokuje: 102, 103, 110, 111
- Pliki: utworzyć `ml-learing-center/sliding_window.py`; zmodyfikować `main.py`.
- Opis: Funkcja przekształcająca wiersz UCI w 4 okna wg tabeli wyżej. Zwraca strukturę `{client_id, windows: [W0..W3], default_label}`.
- Implementacja (szkic):
```python
WINDOW_MAP = {
    "W0": {"pay": ["PAY_6","PAY_5","PAY_4"], "bill": [6,5,4], "amt": [6,5,4]},
    "W1": {"pay": ["PAY_5","PAY_4","PAY_3"], "bill": [5,4,3], "amt": [5,4,3]},
    "W2": {"pay": ["PAY_4","PAY_3","PAY_2"], "bill": [4,3,2], "amt": [4,3,2]},
    "W3": {"pay": ["PAY_3","PAY_2","PAY_0"], "bill": [3,2,1], "amt": [3,2,1]},
}
def extract_windows(row):
    out = {}
    for w, m in WINDOW_MAP.items():
        out[w] = {
            "pay":  [row[c] for c in m["pay"]],
            "bill": [row[f"BILL_AMT{i}"] for i in m["bill"]],
            "amt":  [row[f"PAY_AMT{i}"]  for i in m["amt"]],
            "static": {k: row[k] for k in ["LIMIT_BAL","AGE","SEX","EDUCATION","MARRIAGE"]},
        }
    return out
```
- Acceptance: dla 5 losowych klientów ręcznie zweryfikowane, że W3 zawiera najnowsze 3 miesiące; test pytest sprawdza, że każde okno ma dokładnie 3 wartości w każdym kanale.
- Oczekiwany efekt: realny panel danych, na którym da się policzyć trajektorię. **Bez fabrykowania żadnej liczby.**

### CREDIT-102 [ML] Przetrenowanie RF/XGBoost/LSTM na oknach 3-mies.
- Priorytet: **P0** · Owner: GF · Branch: `sprint1/retrain-3mo`
- Deps: 101 · Blokuje: 103, 104, 105, 106, 107, 108, 109, 110, 112, 113
- Pliki: `main.py` (sekcja treningu), `engineer_features` (parametryzacja oknem), zapis NOWYCH artefaktów z sufiksem `_w3` — NIE nadpisywać istniejących.
- Opis: Trening na oknie W3 wyrównanym do etykiety. Feature engineering liczony na 3 punktach. LSTM przyjmuje `(N, 3, 3)`. **Artefakty zapisywane pod nową nazwą** z sufiksem `_w3` (np. `rf_model_w3.pkl`), żeby legacy `/predict` w Flasku (CREDIT-104, Sprint 2) nie psuł się między mergem 102 a 104.
- Dodatkowo (fix pre-existing): wyrównać mismatche feature engineering między `main.py` a `ml-service/app.py` — `utilization_rate` (oba mają używać `BILL_mean / LIMIT_BAL`, nie `BILL_AMT1 / LIMIT_BAL`); `severe_late` (oba mają używać `(df[pay_cols] >= 2).any(axis=1).astype(int)`, nie `.sum(axis=1)`).
- Acceptance: zapisane `rf_model_w3.pkl`, `xgb_model_w3.pkl`, `lstm_model_w3.keras`, `scaler_w3.pkl`, `lstm_scalers_w3.pkl`, `features_w3.pkl` zgodne z oknem 3-mies.; print AUC dla trzech modeli na teście; stare artefakty bez sufiksu nietknięte; feature engineering w `main.py` i `app.py` spójny.
- Oczekiwany efekt: modele dopasowane do okna 3-miesięcznego — gotowe do inferencji na każdym z okien W0–W3 bez OOD. Legacy `/predict` działa bez przerwy.

### CREDIT-103 [EVAL] Re-walidacja modeli + rozszerzone metryki
- Priorytet: **P0** · Owner: GF · Branch: `sprint1/revalidate-metrics`
- Deps: 102 · Blokuje: 114
- Pliki: utworzyć `ml-learing-center/evaluation.py`, generować wykresy do `ml-learing-center/reports/`.
- Opis: AUC, Gini, KS, confusion matrix, ROC, precision-recall, calibration curve dla modeli 3-miesięcznych. Punkt odniesienia względem starych modeli 6-miesięcznych (czy strata AUC akceptowalna).
- Acceptance: folder `reports/` z ≥9 wykresami; tabela metryk w konsoli.
- Oczekiwany efekt: udokumentowana jakość modeli po przejściu na okno 3-miesięczne.

### CREDIT-401 [DB] Schemat bazy PostgreSQL + EF Core
- Priorytet: **P0** · Owner: MK · Branch: `sprint1/db-schema`
- Deps: — · Blokuje: 402, 203, 204
- Pakiety NuGet do dodania w `WebApi.csproj`: `Microsoft.EntityFrameworkCore`, `Microsoft.EntityFrameworkCore.Design`, `Microsoft.EntityFrameworkCore.Tools`, `Npgsql.EntityFrameworkCore.PostgreSQL`. Rejestracja `DbContext` w `Program.cs` (`builder.Services.AddDbContext<AppDbContext>(...)` z odczytem connection stringa `Default`).
- Pliki: `backend/WebApi/WebApi.csproj`, `backend/WebApi/Data/AppDbContext.cs`, `backend/WebApi/Models/Entities/` (Client, Snapshot, Prediction, Trend), `backend/WebApi/Program.cs`, `backend/WebApi/appsettings.json` (connection string `Default`), `backend/WebApi/Migrations/*` (auto).
- Opis: Encje: `Client(Id, ExternalRef, CreatedAt)`, `Snapshot(Id, ClientId, SnapshotDate, [22 cechy])`, `Prediction(Id, SnapshotId, ModelName, DefaultProbability, Label)`, `Trend(Id, ClientId, ModelName, Slope, Alert, ComputedAt)`. Relacje 1:N.
- Acceptance: `dotnet ef migrations add Init` przechodzi; schemat tworzy się w bazie.
- Oczekiwany efekt: warstwa danych gotowa pod prawdziwy monitoring (historia klienta przechowywana między pomiarami).

### CREDIT-402 [INFRA] docker-compose z PostgreSQL + migracje
- Priorytet: **P1** · Owner: MK · Branch: `sprint1/docker-postgres`
- Deps: 401 · Blokuje: —
- Pliki: `docker-compose.yml` (root), `backend/WebApi/Dockerfile`, drobny update `backend/WebApi/Program.cs` (auto-migracje przy starcie via `db.Database.Migrate()`).
- Opis: Usługi: `db` (postgres:16, healthcheck, named volume), `backend` (zależność `db: service_healthy`), `ml-service` (reuse istniejącego `ml-service/Dockerfile`). **Frontend POZA compose** — pozostaje uruchamiany lokalnie przez `npm run dev`. Backend czeka na zdrowie bazy, migracje aplikowane przy starcie.
- Acceptance: `docker-compose up` stawia bazę i backend łączy się z nią; migracje wykonują się automatycznie.
- Oczekiwany efekt: środowisko backendu uruchamialne jedną komendą; frontend dalej w dev-serverze dla wygody hot-reloadu.

### CREDIT-201 [INFRA] Infrastruktura testów + CI · `SWAP-OK`
- Priorytet: **P1** · Owner: MK · Branch: `sprint1/test-infra`
- Deps: — · Blokuje: 205
- Pliki: `backend/WebApi.Tests/`, `ml-service/tests/`, `frontend/WebApp/vitest.config.ts`, `.github/workflows/ci.yml`.
- Opis: Po jednym smoke teście na stack + CI blokujące czerwone PR.
- Acceptance: `dotnet test`, `pytest`, `npm run test` — każde 1 passed; CI zielone.
- Oczekiwany efekt: kultura jakości od początku.

---

## SPRINT 2 — Silnik monitoringu, kontrakty, zapis do bazy (16 cze – 29 cze)

### CREDIT-210 [CONTRACT] Kontrakt API: monitoring time-series + zapis migawek
- Priorytet: **P0** · Owner: GF+MK (wspólnie) · Branch: `sprint2/contract-monitoring`
- Deps: — · Blokuje: 104, 202, 203, 301
- Pliki: `docs/api-contracts/monitoring.md`.
- Opis: Payload dla (a) oceny trajektorii i (b) zapisu migawki. Przykład odpowiedzi trajektorii:
```json
{
  "clientRef": "abc-123",
  "trajectory": [
    { "window": "W0", "label": "kwi-cze", "predictions": { "randomForest": 0.18, "xgboost": 0.20, "lstm": 0.15 } },
    { "window": "W1", "label": "maj-lip", "predictions": { "randomForest": 0.27, "xgboost": 0.29, "lstm": 0.24 } },
    { "window": "W2", "label": "cze-sie", "predictions": { "randomForest": 0.41, "xgboost": 0.44, "lstm": 0.39 } },
    { "window": "W3", "label": "lip-wrz", "predictions": { "randomForest": 0.58, "xgboost": 0.61, "lstm": 0.55 } }
  ],
  "trends": {
    "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
    "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
    "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
  }
}
```
- Reguła alertu: slope (W3 − W0) > próg → `INCREASING_RISK`; < −próg → `DECREASING_RISK`; inaczej `STABLE`.
- Acceptance: dokument w `main`, obie strony potwierdzają wykonalność.

### CREDIT-104 [ML] Flask /predict/timeseries: trajektoria PD + trendy
- Priorytet: **P0** · Owner: GF · Branch: `sprint2/flask-timeseries`
- Deps: 102, 210 · Blokuje: 110, 202
- Pliki: `ml-service/app.py` (nowy endpoint), refactor `predict_single()` wspólny dla `/predict` i `/predict/timeseries`.
- Opis: Endpoint przyjmuje 22 cechy klienta, wewnętrznie rozbija na 4 okna (logika z CREDIT-101 przeniesiona do serwisu), ocenia każde okno, składa trajektorię, liczy trendy.
- Acceptance: dla klienta z rosnącymi opóźnieniami trend = INCREASING_RISK; test pytest weryfikuje 4 punkty w trajektorii.
- Oczekiwany efekt: silnik monitoringu działa po stronie ML.

### CREDIT-105 [ML] Kalibracja prawdopodobieństw (isotonic) — P0 dla B
- Priorytet: **P0** · Owner: GF · Branch: `sprint2/calibration`
- Deps: 102 · Blokuje: 106, 113
- Pliki: `main.py` (3-way split train/calib/test, owinięcie `CalibratedClassifierCV`), nadpisanie `.pkl`.
- Opis: W Wariancie B kalibracja jest P0 — trajektoria ma sens tylko, gdy bezwzględne PD odpowiadają realnym częstościom. Wzrost 0,3→0,5 musi znaczyć realny wzrost ryzyka.
- Acceptance: reliability diagram blisko diagonali; Brier score po < przed.
- Oczekiwany efekt: trajektoria PD jest interpretowalna liczbowo.

### CREDIT-202 [BE] .NET /api/monitoring/predict-timeseries
- Priorytet: **P0** · Owner: MK · Branch: `sprint2/dotnet-timeseries`
- Deps: 210 (mock), 104 (real) · Blokuje: —
- Pliki: `Controllers/MonitoringController.cs`, `Models/TimeseriesRequest.cs`, `Models/TimeseriesResponse.cs`, `Services/PythonModelClient.cs` (nowa metoda).
- Opis: Walidacja wejścia, wywołanie Flask, mapowanie odpowiedzi. Praca równoległa: do czasu CREDIT-104 mockować odpowiedź zgodną z kontraktem.
- Acceptance: test integracyjny z mockowanym `HttpMessageHandler`; happy path 200.

### CREDIT-203 [BE] Repozytoria EF Core: zapis migawek i predykcji
- Priorytet: **P0** · Owner: MK · Branch: `sprint2/persistence-write`
- Deps: 401, 210 · Blokuje: 204, 205
- Pliki: `Services/SnapshotRepository.cs`, `Services/PredictionRepository.cs`.
- Opis: Zapis migawki (z datą) i powiązanych predykcji do bazy przy każdej ocenie.
- Acceptance: po ocenie klienta rekordy pojawiają się w tabelach Snapshot i Prediction; test integracyjny na bazie testowej.
- Oczekiwany efekt: historia klienta jest trwale przechowywana.

---

## SPRINT 3 — Dowód tezy (ewaluacja) + start frontendu (30 cze – 13 lip)

### CREDIT-110 [EVAL] Metryki time-series: early-warning lead time
- Priorytet: **P0** · Owner: GF · Branch: `sprint3/timeseries-metrics`
- Deps: 101, 102, 104 · Blokuje: 111
- Pliki: `ml-learing-center/timeseries_eval.py`.
- Opis: Dla zbioru testowego policz trajektorie wszystkich klientów. Metryki: średni lead time dla defaultujących, rozkład slope (default vs non-default), AUC trajektorii.
- Acceptance: raport z lead time + boxplot slope dla obu klas.
- Oczekiwany efekt: liczbowy dowód, że trajektoria niesie sygnał.

### CREDIT-111 [EVAL] Eksperyment „statyka vs monitoring" (dowód tezy B)
- Priorytet: **P0** · Owner: GF · Branch: `sprint3/static-vs-dynamic`
- Deps: 110 · Blokuje: 114
- Pliki: `ml-learing-center/static_vs_dynamic.py`, wykres do `reports/`.
- Opis: Statyka = jedno PD z W3, próg, decyzja. Monitoring = alert, jeśli trajektoria przekracza próg w którymkolwiek oknie. Porównaj catch rate defaultów i liczbę fałszywych alarmów.
- Acceptance: tabela + wykres pokazujące przewagę (lub jej brak) monitoringu; uczciwa interpretacja.
- Oczekiwany efekt: **to jest slajd rozstrzygający tezę.**

### CREDIT-106 [ML] Progi kosztowe dla alertów · `SWAP-OK`
- Priorytet: **P1** · Owner: GF · Branch: `sprint3/cost-thresholds`
- Deps: 105 · Blokuje: —
- Pliki: `main.py`, zapis `alert_thresholds.json`, użycie w `app.py`.
- Opis: Próg alertu minimalizujący koszt oczekiwany (FN droższy niż FP), zamiast 0,5.
- Acceptance: `alert_thresholds.json` z progami w (0,1; 0,9); Flask używa ich.

### CREDIT-204 [BE] Endpoint odczytu historii klienta (GET trajektoria)
- Priorytet: **P0** · Owner: MK · Branch: `sprint3/client-history-get`
- Deps: 203 · Blokuje: 302
- Pliki: `Controllers/MonitoringController.cs` (GET `/api/monitoring/clients/{ref}/history`).
- Opis: Zwraca zapisaną historię migawek i predykcji klienta jako trajektorię.
- Acceptance: po zapisaniu 3 migawek GET zwraca 3 punkty posortowane po dacie.

### CREDIT-301 [FE] Widok Timeline: wykres trajektorii PD
- Priorytet: **P0** · Owner: MK · Branch: `sprint3/timeline-view`
- Deps: 210 · Blokuje: 302, 303
- Pliki: `frontend/WebApp/src/components/TimelineChart.tsx`, `TrendAlerts.tsx`, `api/monitoringApi.ts`, `App.tsx` (zakładka).
- Opis: `LineChart` (Recharts), X = okno/data, Y = PD 0–1, 3 linie (modele). Pod spodem karty alertów semaforowych. Praca równoległa na mocku z kontraktu.
- Acceptance: dla payloadu z kontraktu rysuje 4 punkty/model + alerty; test Vitest.
- Oczekiwany efekt: **główny slajd obrony — trajektoria PD w czasie.**

---

## SPRINT 4 — Integracja end-to-end + interpretowalność + tuning (14 lip – 27 lip)

### CREDIT-302 [FE] Lista klientów + widok historii (realne dane)
- Priorytet: **P1** · Owner: MK · Branch: `sprint4/client-history-ui`
- Deps: 204, 301 · Blokuje: 304
- Pliki: `components/ClientList.tsx`, `components/ClientHistory.tsx`.
- Opis: Lista monitorowanych klientów; klik → widok historii (TimelineChart na realnych danych z bazy).
- Acceptance: end-to-end — zapis migawki → pojawia się w historii klienta.

### CREDIT-205 [BE] Testy integracyjne persystencji + E2E smoke · `SWAP-OK`
- Priorytet: **P1** · Owner: MK · Branch: `sprint4/persistence-tests`
- Deps: 203, 201 · Blokuje: —
- Pliki: `WebApi.Tests/PersistenceTests.cs`.
- Opis: Testy zapis→odczyt na bazie testowej (Testcontainers lub SQLite in-memory).
- Acceptance: ≥6 testów pokrywających zapis migawki, predykcji, odczyt historii.

### CREDIT-107 [ML] Interpretowalność SHAP (RF/XGB/LR) · `SWAP-OK`
- Priorytet: **P2** · Owner: GF · Branch: `sprint4/shap`
- Deps: 102 · Blokuje: 211
- Pliki: `ml-service/requirements.txt` (+shap), `app.py` (`compute_shap`).
- Opis: Top-5 cech per predykcja. W Wariancie B to dodatek (deprioritized), ale wartościowy w prezentacji.
- Acceptance: response zawiera `shap.topFeatures` (5 elementów); czas < 2s.

### CREDIT-108 [ML] Cross-validation + tuning Optuna
- Priorytet: **P2** · Owner: GF · Branch: `sprint4/optuna-cv`
- Deps: 102 · Blokuje: —
- Pliki: `main.py` (+optuna), `requirements.txt`.
- Opis: 5-fold CV + tuning XGBoost/RF na oknach 3-mies.
- Acceptance: AUC po tuningu ≥ przed; CV-score z odchyleniem std.

---

## SPRINT 5 — UX migawek, alerty, rozszerzenie modeli, fairness (28 lip – 10 sie)

### CREDIT-303 [FE] Wprowadzanie migawek + UI alertów + fix miesięcy
- Priorytet: **P1** · Owner: MK · Branch: `sprint5/snapshot-entry`
- Deps: 210, 301 · Blokuje: 304
- Pliki: `components/SnapshotForm.tsx` (reuse InputForm + datepicker), fix zahardkodowanych miesięcy w `InputForm.tsx` (TODO), przycisk „kopiuj z poprzedniej migawki".
- Acceptance: dodanie migawki z datą → zapis → widoczne w historii; miesiące dynamiczne wg `new Date()`.

### CREDIT-211 [BE/FE] SHAP DTO passthrough + komponent wizualizacji · `SWAP-OK`
- Priorytet: **P2** · Owner: MK · Branch: `sprint5/shap-ui`
- Deps: 107, 210 · Blokuje: —
- Pliki: `Models/PredictResponse.cs` (+ShapExplanation), `components/ShapExplanation.tsx`.
- Opis: Pass-through SHAP przez .NET + waterfall/bar chart w React.
- Acceptance: dla payloadu SHAP komponent rysuje 5 pasków (czerwone +, zielone −).

### CREDIT-109 [ML] LightGBM + CatBoost
- Priorytet: **P2** · Owner: GF · Branch: `sprint5/lgbm-catboost`
- Deps: 102 · Blokuje: 113
- Pliki: `main.py`, `app.py`, `requirements.txt`.
- Opis: Dwa dodatkowe modele na oknach 3-mies., do porównania.
- Acceptance: response zawiera `lightgbm`, `catboost`; raport ma 6 modeli.

### CREDIT-112 [EVAL] Audyt fairness (fairlearn) · `SWAP-OK`
- Priorytet: **P1** · Owner: GF · Branch: `sprint5/fairness`
- Deps: 102 · Blokuje: —
- Pliki: `ml-learing-center/fairness_audit.py`, `reports/fairness_report.md`.
- Opis: Demographic parity + equalized odds względem SEX. Wymóg AI Act dla systemów kredytowych.
- Acceptance: raport z DPD/EOD per model; ostrzeżenie gdy |różnica| > 0,1.

---

## SPRINT 6 — Polish, ensemble, raport, dokumentacja (11 sie – 24 sie)

### CREDIT-113 [ML] Stacked ensemble (meta-learner) — ⚪ DESCOPED 2026-07-07 (backlog po obronie; nie blokuje już CREDIT-114)
- Priorytet: **P2** · Owner: GF · Branch: `sprint6/stacking`
- Deps: 102, 105, 109 · Blokuje: 114
- Pliki: `main.py`, `app.py`.
- Opis: Regresja logistyczna na predykcjach 5–6 modeli bazowych.
- Acceptance: AUC ensemble ≥ najlepszy pojedynczy; w response klucz `ensemble`.

### CREDIT-114 [EVAL] Raport końcowy + wykresy do prezentacji
- Priorytet: **P0** · Owner: GF · Branch: `sprint6/final-report`
- Deps: 103, 111, 113 · Blokuje: —
- Pliki: `ml-learing-center/generate_final_report.py`, `reports/final_report.md`.
- Opis: Zbiorczy raport: porównanie modeli, dowód statyka-vs-monitoring, lead time, fairness. Eksport PNG do slajdów.
- Acceptance: jeden raport zbierający wszystkie wyniki + komplet wykresów do prezentacji.

### CREDIT-304 [FE] UI polish (responsive, a11y, dark mode, tooltipy)
- Priorytet: **P2** · Owner: MK · Branch: `sprint6/ui-polish`
- Deps: 302, 303 · Blokuje: —
- Pliki: cały `frontend/WebApp/src/components/`.
- Acceptance: responsywność na 1024/1440/1920; Lighthouse a11y ≥ 90.

### CREDIT-501 [DOCS] README, Model Card, Architecture, aktualizacja CLAUDE.md
- Priorytet: **P0** · Owner: GF+MK · Branch: `sprint6/docs`
- Deps: ~wszystko · Blokuje: —
- Pliki: `README.md`, `docs/MODEL_CARD.md`, `docs/ARCHITECTURE.md`, aktualizacja `CLAUDE.md` (nowe endpointy, baza, okno 3-mies.).
- Acceptance: README z uruchomieniem przez docker-compose; model card wg szablonu Google.

---

## Macierz obciążenia (równomierna)

| Sprint | Gabriel Figur | Mikołaj Kusiński |
|---|---|---|
| 1 | CREDIT-101, 102, 103 | CREDIT-401, 402, 201 |
| 2 | CREDIT-210*, 104, 105 | CREDIT-210*, 202, 203 |
| 3 | CREDIT-110, 111, 106 | CREDIT-204, 301 |
| 4 | CREDIT-107, 108 | CREDIT-302, 205 |
| 5 | CREDIT-109, 112 | CREDIT-303, 211 |
| 6 | CREDIT-113, 114, 501* | CREDIT-304, 501* |

\* zadania wspólne. Razem ~14/14. Etykiety właściciela nie są wiążące — `SWAP-OK` oznacza zadania szczególnie łatwe do zamiany.

## Ścieżka krytyczna
`101 → 102 → 104 → 110 → 111 → 114`. To jest oś tezy. Opóźnienie któregokolwiek przesuwa dowód. Tor persystencji (`401 → 402 / 203 → 204`) i tor frontendu (`210 → 301 → 302/303`) biegną równolegle i nie blokują osi tezy aż do integracji w Sprincie 4.

## Risk register
| Ryzyko | Prawd. | Impact | Mitigacja |
|---|---|---|---|
| Okno 3-mies. tnie AUC zbyt mocno | Średnie | Wysoki | Porównać z W=4 (3 punkty trajektorii); wybrać lepszy kompromis resolution/AUC |
| Monitoring nie bije statyki w eksperymencie | Średnie | Wysoki | To i tak jest uczciwy wynik do obrony; framing: „dynamika daje lead time, nawet jeśli AUC podobne" |
| LSTM (3,3) niestabilny przy krótkiej sekwencji | Średnie | Średni | Uprościć architekturę; rozważyć GRU; LSTM nie jest już jedynym nośnikiem dynamiki w Wariancie B |
| Postgres + tensorflow w docker-compose ciężkie | Niskie | Średni | `tensorflow-cpu`, slim images; SQLite jako fallback dev |
| Opóźnienie kontraktu 210 blokuje sprint | Wysokie | Wysoki | Zrobić 210 w pierwszy poniedziałek Sprintu 2 |
