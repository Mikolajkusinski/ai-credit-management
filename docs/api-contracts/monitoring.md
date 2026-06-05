# Monitoring API Contract — Wariant B

> Kontrakt API dla systemu monitoringu kalendarzowego (Wariant B). Źródło prawdy dla CREDIT-104 (Flask), CREDIT-202/203/204 (.NET backend) i CREDIT-301/303 (React frontend).
>
> **Wersja:** v1 (Sprint 2, 2026-06-03)
> **Status:** draft do uzgodnienia GF + MK

---

## 1. Overview

```
React (5173)
    POST/GET /api/v1/monitoring/...
        │
        ▼
.NET WebApi (5120)
    ├── Postgres (5432)   ← stan: Client, Snapshot, Prediction, Trend
    └── HTTP POST → Flask
            │
            ▼
        Flask ml-service (5001)
            stateless scoring (bez DB)
```

**Podział odpowiedzialności:**
- **Flask** — bezstanowy silnik scoringu. Otrzymuje 22 cechy, zwraca trajektorię PD + trendy. Bez DB. Bez `clientRef`.
- **Backend .NET** — orkiestracja + trwałość. Waliduje request, wywołuje Flask, zapisuje migawki/predykcje do Postgresa, serwuje historię klienta.
- **Frontend** — wprowadza migawki, wyświetla trajektorię PD + alerty.

**Wersjonowanie:** wszystkie publiczne endpointy backendu mają prefiks `/api/v1/`. Flask jest wewnętrzny — bez wersji.

---

## 2. Core concepts

### 2.1. Sliding window (W0..W3)

Każda predykcja generuje **4 punkty trajektorii** odpowiadające 4 nakładającym się oknom 3-miesięcznym. Mapowanie kolumn (zgodne z `sliding_window.WINDOW_DEFS`):

| Okno | Miesiące w oknie (najst. → najnow.) | Kolumny PAY / BILL / PAY_AMT |
|---|---|---|
| W0 | t−5, t−4, t−3 | PAY_6,5,4 / BILL_AMT6,5,4 / PAY_AMT6,5,4 |
| W1 | t−4, t−3, t−2 | PAY_5,4,3 / BILL_AMT5,4,3 / PAY_AMT5,4,3 |
| W2 | t−3, t−2, t−1 | PAY_4,3,2 / BILL_AMT4,3,2 / PAY_AMT4,3,2 |
| W3 | t−2, t−1, t   | PAY_3,2,0 / BILL_AMT3,2,1 / PAY_AMT3,2,1 |

Gdzie `t` = miesiąc najbliżej `snapshotDate` (najnowszy w danych). UCI nie ma `PAY_1` — kolejność: `PAY_0, PAY_2, ..., PAY_6`.

### 2.2. Window labels (string)

Każdy `TrajectoryPoint` ma pole `label` — czytelny zakres miesięcy obliczony przez **backend** z `snapshotDate`. Format: `"Mar-May 2026"` (3-literowy miesiąc EN + 3-literowy miesiąc EN + 4-cyfrowy rok). Frontend renderuje bez transformacji.

Przykład dla `snapshotDate = "2026-08-15"`:
- W0 → `"Mar-May 2026"`
- W1 → `"Apr-Jun 2026"`
- W2 → `"May-Jul 2026"`
- W3 → `"Jun-Aug 2026"`

### 2.3. Trend & alert rule

Dla każdego modelu liczymy slope = `PD_W3 - PD_W0` (zakres `[-1, +1]`). Próg `θ = 0.10` (10 punktów procentowych). Kategoria alertu:

| Warunek | Alert |
|---|---|
| `slope > +θ` | `INCREASING_RISK` |
| `slope < −θ` | `DECREASING_RISK` |
| `−θ ≤ slope ≤ +θ` | `STABLE` |

Próg `θ` jest **konfigurowalny** — domyślny w kontrakcie, w CREDIT-106 (Sprint 3) może być per-koszt różny i wczytywany z `alert_thresholds.json`.

---

## 3. Shared types

### 3.1. `Snapshot22Features`

Wejściowe 22 cechy klienta dla 1 migawki (zachowuje istniejący schemat `PredictRequest.cs` z legacy `/api/predict`):

```json
{
  "limitBal": 100000,
  "sex": 1,
  "education": 2,
  "marriage": 1,
  "age": 35,
  "pay0": 0, "pay2": 0, "pay3": 0, "pay4": 0, "pay5": 0, "pay6": 0,
  "billAmt1": 50000, "billAmt2": 48000, "billAmt3": 46000,
  "billAmt4": 44000, "billAmt5": 42000, "billAmt6": 40000,
  "payAmt1": 5000, "payAmt2": 5000, "payAmt3": 5000,
  "payAmt4": 5000, "payAmt5": 5000, "payAmt6": 5000
}
```

**Walidacja (.NET DataAnnotations w CREDIT-202):**
- `limitBal`: 10000–1000000
- `sex`: 1 lub 2
- `education`: 1–4
- `marriage`: 1–3
- `age`: 18–100
- `pay0, pay2..pay6`: −2 do 8 (-2 = no consumption, -1 = paid in full, 0..8 = months of delay)
- `billAmt1..6`, `payAmt1..6`: liczby (mogą być ujemne dla nadpłat)

### 3.2. `TrajectoryPoint`

Pojedynczy punkt trajektorii (jedno okno):

```json
{
  "window": "W2",
  "label": "May-Jul 2026",
  "predictions": {
    "randomForest": 0.41,
    "xgboost": 0.44,
    "lstm": 0.39
  }
}
```

- `window`: enum `"W0" | "W1" | "W2" | "W3"`
- `label`: string (computed by backend)
- `predictions`: obiekt z PD per model, wartości w `[0.0, 1.0]`. Klucze modeli: `randomForest`, `xgboost`, `lightgbm`, `catboost`, `lstm` (camelCase — zgodne z istniejącym `PredictResponse.cs`). LightGBM + CatBoost dodane w CREDIT-109; modele klienckie mogą ignorować nowe klucze dla backward compatibility.

### 3.3. `TrendInfo`

Tendencja PD dla jednego modelu w obrębie jednej trajektorii:

```json
{
  "slope": 0.40,
  "alert": "INCREASING_RISK"
}
```

- `slope`: number, `[-1.0, +1.0]`, dokładność 4 miejsca po przecinku
- `alert`: enum `"INCREASING_RISK" | "DECREASING_RISK" | "STABLE"`

### 3.4. `Trends`

```json
{
  "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
  "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
  "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
}
```

### 3.5. `TimeseriesResponse`

Pełna odpowiedź scoringu (z trajektorią + trendami + alertami kosztowymi z CREDIT-106):

```json
{
  "clientRef": "client-001",     // optional, echo z requestu (null gdy stateless)
  "snapshotDate": "2026-06-03",  // ISO 8601 date
  "trajectory": [                // dokładnie 4 elementy, W0..W3
    { "window": "W0", "label": "Jan-Mar 2026", "predictions": { ... } },
    { "window": "W1", "label": "Feb-Apr 2026", "predictions": { ... } },
    { "window": "W2", "label": "Mar-May 2026", "predictions": { ... } },
    { "window": "W3", "label": "Apr-Jun 2026", "predictions": { ... } }
  ],
  "trends": { "randomForest": { ... }, "xgboost": { ... }, "lightgbm": { ... }, "catboost": { ... }, "lstm": { ... } },

  // CREDIT-106 (optional, dodane w Sprincie 3) — cost-optimized PD thresholds
  // per model i flagi alertu per okno per model. CREDIT-109 rozszerzył o
  // lightgbm + catboost. Modele klienckie mogą je ignorować dla backward
  // compatibility, ale frontend powinien je używać do semaforowych alertów
  // per okno (zamiast hardcoded 0.5).
  "costThresholds": {
    "randomForest": 0.145,
    "xgboost":      0.180,
    "lightgbm":     0.150,
    "catboost":     0.160,
    "lstm":         0.185
  },
  "windowAlerts": {
    "randomForest": [false, false, true,  true],
    "xgboost":      [false, true,  true,  true],
    "lightgbm":     [false, false, true,  true],
    "catboost":     [false, false, true,  true],
    "lstm":         [false, false, false, true]
  },

  // CREDIT-107 (optional, dodane w Sprincie 4) — top-5 cech per model wpływających
  // najmocniej na predykcję W3 (najnowszego okna). Wartość `value` to surowy SHAP
  // (znak: + zwiększa PD, - zmniejsza). Tylko modele tree-based (TreeExplainer);
  // LSTM pominięty (KernelExplainer nie zmieściłby się w budżecie czasu < 2s).
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
}
```

`costThresholds`: per-model próg PD, ponad który Flask flaguje okno jako alert. Wartości są obliczone w `optimize_thresholds.py` (lub `main.py`) i shipping w `ml-service/alert_thresholds.json` z `_meta` (cost ratio, bounds). Re-optymalizacja: zmień `_FN_COST_106` w `main.py` lub stałe w `optimize_thresholds.py`, uruchom skrypt, commit nowy JSON.

`windowAlerts[model]` ma długość 4 (W0..W3), każda wartość to `predictions[model] >= costThresholds[model]` dla tego okna.

### 3.6. `ErrorEnvelope`

Wspólny format błędów 4xx/5xx:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "limitBal must be between 10000 and 1000000",
    "details": {
      "field": "limitBal",
      "value": 5000
    }
  }
}
```

- `code`: string SCREAMING_SNAKE_CASE
- `message`: human-readable
- `details`: optional object z kontekstem

**Standardowe kody:**

| Code | HTTP | Kiedy |
|---|---|---|
| `VALIDATION_FAILED` | 400 | Wejściowe pole poza dozwolonym zakresem / brakujące |
| `CLIENT_NOT_FOUND` | 404 | `GET /history` — `clientRef` nie istnieje |
| `ML_SERVICE_UNAVAILABLE` | 503 | Backend nie może dotrzeć do Flask |
| `ML_SERVICE_ERROR` | 502 | Flask zwrócił 5xx |
| `INTERNAL_ERROR` | 500 | Wszystko inne |

---

## 4. Endpoints

### 4.1. Flask: `POST /predict/timeseries`

**Internal, bez wersjonowania.** Bezstanowy scoring.

**Request:**
```http
POST http://ml-service:5001/predict/timeseries
Content-Type: application/json

{
  "limitBal": 100000, "sex": 1, ...  // Snapshot22Features (3.1) z snake_case kluczami
                                       // ml-service tradycyjnie przyjmuje snake_case (LIMIT_BAL itd.)
                                       // dla zgodności z istniejącym /predict
}
```

> **UWAGA:** Flask `/predict` używa `SCREAMING_SNAKE_CASE` (`LIMIT_BAL`, `PAY_0`, `BILL_AMT1`) — patrz `app.py` `required_fields`. Dla spójności `/predict/timeseries` używa tego samego schematu. Backend (.NET) tłumaczy z camelCase na SCREAMING_SNAKE_CASE w `Services/PythonModelClient.cs` (już istnieje konwersja w `FlaskPredictRequest.cs`).

**Response 200:** `TimeseriesResponse` (3.5) **bez** `clientRef` (Flask jest stateless):
```json
{
  "snapshotDate": null,
  "trajectory": [...],
  "trends": {...}
}
```

> Flask nie zna `snapshotDate` — to backend dodaje labelki na podstawie własnej daty. Flask zwraca `null` lub pole jest pomijane.

**Errors:**
- `400 VALIDATION_FAILED` — brakujące pole 22-cechowe
- `500 INTERNAL_ERROR` — błąd modelu

### 4.2. Backend: `POST /api/v1/monitoring/predict-timeseries`

**Bezstanowy proxy nad Flaskiem.** Frontend używa do trybu „score one-off" (bez zapisu).

**Request:**
```http
POST http://localhost:5120/api/v1/monitoring/predict-timeseries
Content-Type: application/json

{
  "clientRef": "client-001",        // optional — echo do response, NIE zapisuje
  "snapshotDate": "2026-06-03",     // optional — domyślnie dzisiaj, używane do labeli
  "features": {                     // wymagane, Snapshot22Features (3.1)
    "limitBal": 100000, "sex": 1, "education": 2, ...
  }
}
```

**Response 200:** `TimeseriesResponse` (3.5) z `clientRef` jako echo i `snapshotDate` wypełnionym:
```json
{
  "clientRef": "client-001",
  "snapshotDate": "2026-06-03",
  "trajectory": [
    { "window": "W0", "label": "Jan-Mar 2026", "predictions": {...} },
    ...
  ],
  "trends": {...}
}
```

**Errors:**
- `400 VALIDATION_FAILED` — pole `features` brakujące lub niewalidne
- `502 ML_SERVICE_ERROR` — Flask zwrócił 5xx
- `503 ML_SERVICE_UNAVAILABLE` — Flask niedostępny

**Co NIE robi:** nie zapisuje do bazy. Klient nie zostaje utworzony nawet jeśli `clientRef` podany.

### 4.3. Backend: `POST /api/v1/monitoring/clients/{ref}/snapshots`

**Stateful.** Tworzy migawkę, scoruje, zapisuje predykcje, oblicza nowy `Trend`. **Auto-tworzy `Client` jeśli `{ref}` nie istnieje.**

**Path param:** `{ref}` — string max 64 znaki (mapuje na `Client.ExternalRef`).

**Request:**
```http
POST http://localhost:5120/api/v1/monitoring/clients/client-001/snapshots
Content-Type: application/json

{
  "snapshotDate": "2026-06-03",     // optional — domyślnie dzisiaj
  "features": {                     // wymagane, Snapshot22Features (3.1)
    "limitBal": 100000, "sex": 1, "education": 2, ...
  }
}
```

**Response 201:**
```json
{
  "snapshotId": 42,
  "clientRef": "client-001",
  "snapshotDate": "2026-06-03",
  "trajectory": [...],              // 4 punkty
  "trends": {...},                  // 3 modele
  "persisted": {
    "clientCreated": true,          // true jeśli auto-create, false jeśli już istniał
    "predictionIds": [128, 129, 130],   // 3 (po 1 per model — TYLKO dla W3 zapisywane?)
    "trendIds": [55, 56, 57]
  }
}
```

> **DECYZJA do dyskusji:** zapisujemy `Prediction` tylko dla **W3** (etykietowanego okna) czy dla wszystkich **W0..W3**? Rekomendacja: tylko W3 (Prediction = ocena „aktualna"). Trajektoria W0..W3 jest tylko widokiem analitycznym, nie historią. Stara historia rekonstruowana z poprzednich migawek tego klienta.

**Errors:**
- `400 VALIDATION_FAILED` — `features` niewalidne, `snapshotDate` w przyszłości
- `409 CONFLICT` — `{ref}` istnieje + `snapshotDate` ten sam dzień (duplikat) — *opcjonalnie, do dyskusji*
- `502 ML_SERVICE_ERROR` — Flask zwrócił 5xx
- `503 ML_SERVICE_UNAVAILABLE` — Flask niedostępny

### 4.4. Backend: `GET /api/v1/monitoring/clients/{ref}/history`

**Stateful read.** Zwraca chronologiczną historię migawek + predykcji dla klienta. Implementowane w CREDIT-204; kontrakt definiowany tutaj, żeby frontend (CREDIT-301) mógł zacząć na mocku.

**Path param:** `{ref}` — string.

**Query params (optional):**
- `from`: ISO date (default: brak — od początku)
- `to`: ISO date (default: brak — do dziś)
- `limit`: int 1–500 (default: 100)

**Response 200:**
```json
{
  "clientRef": "client-001",
  "createdAt": "2026-05-10T08:23:00Z",
  "history": [
    {
      "snapshotId": 12,
      "snapshotDate": "2026-05-10",
      "predictions": {
        "randomForest": 0.18,
        "xgboost": 0.20,
        "lstm": 0.15
      }
    },
    {
      "snapshotId": 28,
      "snapshotDate": "2026-05-24",
      "predictions": {
        "randomForest": 0.27,
        "xgboost": 0.29,
        "lstm": 0.24
      }
    }
    // ...
  ],
  "trends": {                       // bieżący trend per model (z ostatnich 4 migawek)
    "randomForest": { "slope": 0.40, "alert": "INCREASING_RISK" },
    "xgboost":      { "slope": 0.41, "alert": "INCREASING_RISK" },
    "lstm":         { "slope": 0.40, "alert": "INCREASING_RISK" }
  }
}
```

> **Różnica vs trajektoria W0..W3:** `history` to oś czasu realnych migawek wprowadzonych przez użytkownika (potencjalnie nieregularnie rozłożone). `trajectory` to oś czasu wewnętrznych okien jednej migawki. Frontend (CREDIT-301) wyświetla `history` jako główny wykres trajektorii PD; widok `trajectory` może być w „expand details" dla wybranej migawki (opcjonalnie).

**Errors:**
- `404 CLIENT_NOT_FOUND` — `{ref}` nie istnieje
- `400 VALIDATION_FAILED` — niewalidny `from`/`to`/`limit`

---

### 4.5. Backend: `GET /api/v1/monitoring/clients`

**Stateful read (dodane w CREDIT-302).** Zwraca listę wszystkich monitorowanych klientów ze statystykami
zbiorczymi — zasila widok listy klientów (`ClientList`); klik w wiersz ładuje pełną historię przez 4.4.
Non-breaking addition do kontraktu (nowy endpoint, bez zmiany istniejących).

**Query params:** brak.

**Response 200:**
```json
{
  "clients": [
    {
      "clientRef": "client-001",
      "createdAt": "2026-05-10T08:23:00Z",
      "snapshotCount": 4,
      "latestSnapshotDate": "2026-05-24",
      "latestAlert": "INCREASING_RISK"
    },
    {
      "clientRef": "client-002",
      "createdAt": "2026-05-12T09:00:00Z",
      "snapshotCount": 1,
      "latestSnapshotDate": "2026-04-15",
      "latestAlert": "STABLE"
    }
  ]
}
```

- **Sortowanie:** najpierw klienci z migawkami, najnowsza aktywność na górze (`latestSnapshotDate` desc),
  potem `createdAt` desc.
- **`latestAlert`** = roll-up trendów per model dla pojedynczego badge: `INCREASING_RISK`, gdy
  którykolwiek model sygnalizuje wzrost; inaczej `DECREASING_RISK`, gdy którykolwiek spada; inaczej
  `STABLE`. Pełny rozbicie per model jest w odpowiedzi 4.4.
- **`latestSnapshotDate`** = `null`, gdy klient nie ma jeszcze migawek.
- Pusta baza → `{ "clients": [] }` (200, nie 404).

---

## 5. Naming conventions

- **Wszystkie publiczne JSON** używają **camelCase** (`clientRef`, `snapshotDate`, `defaultProbability`).
- **Klucze modeli** w response: `randomForest`, `xgboost`, `lstm` (camelCase, spójne z `PredictResponse.cs`).
- **URL path params/query strings:** `kebab-case` (`predict-timeseries`).
- **Enum values:** `SCREAMING_SNAKE_CASE` (`INCREASING_RISK`, `STABLE`, `VALIDATION_FAILED`).
- **Window names:** `W0`, `W1`, `W2`, `W3` (uppercase + cyfra).
- **Daty:** ISO 8601 string (`"2026-06-03"` dla daty, `"2026-06-03T08:23:00Z"` dla datetime UTC).
- **Wyjątek Flask:** `/predict/timeseries` request body używa `SCREAMING_SNAKE_CASE` (`LIMIT_BAL`, `PAY_0`) dla spójności z istniejącym `/predict`. Backend tłumaczy w `Services/PythonModelClient.cs`.

---

## 6. Versioning policy

- Backend publiczne endpointy: prefiks `/api/v1/...`
- Breaking changes wymuszają nowy prefiks (`/api/v2/...`); v1 utrzymywane min. 1 sprint po wypuszczeniu v2
- Non-breaking additions (nowe pola optional) bez zmiany wersji
- Flask: brak wersjonowania (wewnętrzne; zmiany koordynowane atomowo z backendem)

---

## 7. Open questions / future

| # | Pytanie | Decyzja na teraz | Kiedy domknąć |
|---|---|---|---|
| 1 | Czy `Prediction` zapisuje tylko W3, czy też W0..W3? | Tylko W3 (etykietowane okno) | CREDIT-203 (Sprint 2) implementacja |
| 2 | Czy 409 CONFLICT przy duplikatach `(clientRef, snapshotDate)`? | Tak (rekomendacja) | CREDIT-203 — można zmienić, jeśli UX woli upsert |
| 3 | Próg slope per koszt | Stała 0.10 | CREDIT-106 (Sprint 3) — może wczytywać z `alert_thresholds.json` |
| 4 | Auth | Brak | Spike po Sprincie 6 |
| 5 | Rate limiting | Brak | Spike po Sprincie 6 |
| 6 | OpenAPI/Swagger spec | Auto-generowane przez Swashbuckle w CREDIT-202 | Sprint 2 |

---

## 8. Confirmation

Kontrakt zatwierdzony przez (przez approve PR-a):

- [ ] Gabriel Figur (GF) — implementuje Flask `/predict/timeseries` (CREDIT-104)
- [ ] Mikołaj Kusiński (MK) — implementuje backend endpointy 4.2, 4.3, 4.4 (CREDIT-202, 203, 204) i frontend Timeline (CREDIT-301)

Po merge: wszystkie 4 zadania (104, 202, 203, 301) ruszają równolegle. Implementacja MUSI być zgodna z tym kontraktem.
