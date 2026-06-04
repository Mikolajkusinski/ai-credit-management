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
