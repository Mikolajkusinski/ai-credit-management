spraw# RUNNING.md — Instrukcja uruchamiania projektu (krok po kroku)

> Plik dla developerów (GF i MK). Opisuje kompletną sekwencję kroków potrzebną, żeby postawić środowisko dev, odpalić cały stack (frontend + backend + ml-service) i zweryfikować, że zmiany działają.
>
> Architektura, porty i komendy referencyjne: patrz `CLAUDE.md`. Stan backlogu: `TASKS.md`. Postęp prac: `CHECKLIST.md`.
>
> **Stan na 2026-06-05** (po zamknięciu Sprintów 1-4 obu torów: 21/28 zadań 🟢; Sprint 4 GF backlog domknięty — patrz `PodsumowanieSprintu1.md`, `PodsumowanieSprintu2_MK.md`, `PodsumowanieSprintu3_GF.md`, `PodsumowanieSprintu4_GF.md`).

---

## 1. Wymagania wstępne (jednorazowo na maszynie)

| Narzędzie | Wersja | Do czego |
|---|---|---|
| Python | 3.10+ | `ml-service/`, `ml-learing-center/` |
| .NET SDK | 8.0 | `backend/WebApi/` |
| Node.js | 20+ (LTS) | `frontend/WebApp/` |
| npm | 10+ | razem z Node.js |
| Docker Desktop | aktualne | Postgres + backend przez `docker-compose` (frontend lokalnie) |
| Git | dowolne | klonowanie repo |

macOS / Windows / Linux — wszystkie wspierane. Na Windowsie zalecane PowerShell lub WSL2.

### 1.1. Klonowanie repozytorium

```bash
git clone https://github.com/<owner>/ai-credit-management.git
cd ai-credit-management
```

### 1.2. Globalne narzędzia .NET (jednorazowo)

EF Core CLI (wymagane do migracji bazy):

```bash
dotnet tool install --global dotnet-ef
```

---

## 2. ML Service (Flask, port 5001)

Bezstanowy silnik scoringu. **Dwie rodziny modeli:**

- **W3 calibrated (5 modeli):** RandomForest, XGBoost, LightGBM, CatBoost, LSTM — wszystkie skalibrowane izotonicznie (CREDIT-105) i z cost-optimized thresholdami (CREDIT-106). Serwowane na `/predict/timeseries`. **Artefakty są w gicie** (CREDIT-104/109).
- **Legacy 6-month (3 modele):** RandomForest, XGBoost, LSTM (bez kalibracji). Serwowane na legacy `/predict`. **Artefakty NIE są w gicie** — wymagają lokalnego treningu lub kopii (sekcja 2.2 Opcja A).

### 2.1. Wirtualne środowisko + zależności

```bash
cd ml-service
python -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

### 2.2. Skąd wziąć artefakty modeli

**Co jest w gicie (działają od razu po klonie):**

W `ml-service/` (committed przez `.gitignore` exceptions):
- `rf_model_w3.pkl`, `xgb_model_w3.pkl`, `lightgbm_model_w3.pkl`, `catboost_model_w3.pkl` — skalibrowane wrappery (`CalibratedClassifierCV` + `FrozenEstimator`)
- `lstm_model_w3.keras` + `lstm_scalers_w3.pkl` + `lstm_calibrator_w3.pkl` (sklearn `IsotonicRegression`)
- `scaler_w3.pkl`, `features_w3.pkl`
- `alert_thresholds.json` (CREDIT-106 per-model cost-optimized thresholds + `_meta`)

Endpoint `/predict/timeseries` i `/api/v1/monitoring/...` działają **bez żadnej dodatkowej pracy**.

**Co wymaga lokalnego treningu (do legacy `/predict`):**

Legacy 6-mies. artefakty (`rf_model.pkl`, `xgb_model.pkl`, `lstm_model.keras`, `scaler.pkl`, `lstm_scalers.pkl`, `features.pkl`) **NIE są w gicie**. Dwie opcje:

**Opcja A — wytrenuj lokalnie** (zalecane przy pierwszym setupie zespołowca):

```bash
cd ../ml-learing-center
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
# Trening trwa ~8-15 min na CPU. Wypisuje AUC dla 6-mies. legacy (RF/XGB/LSTM)
# ORAZ W3 calibrated (RF/XGB/LightGBM/CatBoost/LSTM uncal -> cal).
# Regeneruje też alert_thresholds.json (CREDIT-106) na wypadek zmiany cost ratio.
```

Po zakończeniu skopiuj **legacy artefakty** do `ml-service/`:

```bash
cp rf_model.pkl xgb_model.pkl lstm_model.keras scaler.pkl features.pkl ../ml-service/
# lstm_scalers.pkl jest zapisywany bezpośrednio do ../ml-service/ przez main.py.
# W3 artefakty (z sufiksem _w3) są już w gicie — main.py je nadpisuje lokalnie.
```

**Opcja B — pobierz od kolegi z zespołu** (jeśli ktoś już wytrenował).

> **Uwaga:** `/predict/timeseries` (W3 + monitoring) działa **bez** legacy artefaktów — można pominąć trening, jeśli nie używasz legacy endpointu.

### 2.3. Uruchomienie serwisu

```bash
cd ml-service
source venv/bin/activate
python app.py
# Słucha na http://localhost:5001
```

### 2.4. Sanity check

```bash
curl http://localhost:5001/health
# Oczekiwana odpowiedź: {"status":"healthy"}
```

---

## 3. Backend (.NET, port 5120)

### 3.1. Restore i build

```bash
cd backend/WebApi
dotnet restore
dotnet build
```

### 3.2. Konfiguracja

`backend/WebApi/appsettings.json` zawiera:
- `FlaskServiceUrl` — domyślnie `http://localhost:5001`.

Sekcja `ConnectionStrings:Default` (CREDIT-401) z URL-em do Postgresa. Domyślnie: `Host=localhost;Port=5432;Database=credit;Username=postgres;Password=postgres`.

### 3.3. Uruchomienie

```bash
dotnet run
# Swagger: http://localhost:5120/swagger
# API: http://localhost:5120/api
```

### 3.4. Sanity check

Otwórz `http://localhost:5120/swagger`. Dostępne endpointy (CREDIT-202/203/204/302):

- `POST /api/predict` — legacy single-snapshot scoring (6-mies. modele, wymaga legacy artefaktów)
- `POST /api/v1/monitoring/predict-timeseries` — bezstanowy proxy nad Flaskiem (trajektoria W0..W3 + trends + costThresholds + windowAlerts + shap)
- `POST /api/v1/monitoring/clients/{ref}/snapshots` — stateful: scoring + zapis migawki + predykcji W3 + upsert trendów (409 na duplikat `(ref, date)`)
- `GET /api/v1/monitoring/clients/{ref}/history` — chronologiczna trajektoria PD z bazy + bieżące trendy
- `GET /api/v1/monitoring/clients` — lista klientów z roll-up alert per ostatnia migawka

Kontrakt: `docs/api-contracts/monitoring.md`.

---

## 4. Frontend (React + Vite, port 5173)

### 4.1. Instalacja zależności

```bash
cd frontend/WebApp
npm install
```

### 4.2. Uruchomienie

```bash
npm run dev
# http://localhost:5173
```

Frontend woła backend pod `http://localhost:5120/api`. Jeśli backend siedzi pod innym URL-em, zmień w `src/api/predictApi.ts`.

### 4.3. Testowanie zmian wizualnych

Vite robi hot-module-reload. Edytuj plik w `src/` — przeglądarka odświeża sama. UI testuj ręcznie po golden path (wypełnij formularz, kliknij Predict, sprawdź wynik) **oraz** kilku edge cases (np. age = 18, limit = 10000).

---

## 5. PostgreSQL (schemat z CREDIT-401)

Dwie ścieżki:

### 5.1. Lokalnie bez Dockera

Zainstaluj Postgres 16 i utwórz bazę:

```bash
createdb credit
psql credit -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

Następnie aplikuj migracje:

```bash
cd backend/WebApi
dotnet ef database update
```

### 5.2. Przez docker-compose

```bash
docker-compose up -d db backend ml-service
# Frontend NIE jest w compose — uruchamiaj go osobno przez npm run dev.
docker-compose logs -f backend  # podgląd migracji
```

`docker-compose up` automatycznie wykonuje `db.Database.Migrate()` przy starcie backendu.

Wyłączenie:

```bash
docker-compose down
docker-compose down -v   # + usuwa wolumen z danymi bazy
```

---

## 6. Pełny stack — typowa sesja developerska

Trzy terminale (lub pełna izolacja przez docker-compose dla bazy+backendu+ml):

| Terminal | Komenda | Co |
|---|---|---|
| 1 | `cd ml-service && source venv/bin/activate && python app.py` | ML na :5001 |
| 2 | `cd backend/WebApi && dotnet run` | Backend na :5120 |
| 3 | `cd frontend/WebApp && npm run dev` | Frontend na :5173 |

Otwórz `http://localhost:5173`. Frontend ma 2 zakładki (CREDIT-301/302):

- **Prediction** — formularz 22 pól, single-snapshot scoring (5 modeli W3 + 3 legacy).
- **Monitoring** — lista klientów (z roll-up alertem) → historia per klient (trajektoria PD + alerty semaforowe).

---

## 7. Testy

Infrastruktura CI z CREDIT-201:

```bash
# Backend (xUnit + Testcontainers Postgres dla CREDIT-205)
cd backend && dotnet test

# ML (pytest — 10 testów: pure-function alert math + endpoint tests dla
# /predict/timeseries + SHAP shape test)
cd ml-service && source venv/bin/activate && pytest

# Frontend (Vitest)
cd frontend/WebApp && npm run test
```

CI (`.github/workflows/ci.yml`) odpala wszystkie trzy na każdym PR-ze. **Czerwone CI = blokada merge'a.** Endpoint pytest skipuje się gracefully gdy brak artefaktów (CI nie ma legacy artefaktów, ale ma W3).

---

## 8. Workflow zmiany — od pomysłu do merge'a

1. **Sprawdź `CHECKLIST.md`** — kto co teraz robi i jaki jest następny dostępny (🔴) task na twoim torze.
2. **Stwórz brancha** wg konwencji `sprintN/krótka-nazwa` (patrz `TASKS.md`, kolumna `branch`).
3. **Implementuj** zgodnie z `Cel`/`Pliki`/`DoD` z `TASKS.md`.
4. **Lokalnie odpal testy** (sekcja 7) — wszystkie muszą być zielone.
5. **Otwórz PR** — request review od drugiej osoby. Tytuł: `[CREDIT-XXX] Krótki opis`. Opis: czego dotyczy, jak testować, ewentualne breaking changes.
6. **CI musi być zielone** zanim merge.
7. **Po merge'u do `main`:**
   - W `CHECKLIST.md` zmień status zadania z 🔴 na 🟢.
   - Sprawdź, które zadania mają zmergeowane WSZYSTKIE swoje `blocked_by` — zmień ich status z 🔒 na 🔴.
   - Zaktualizuj wiersz „Aktualne zadanie" dla swojej osoby (kolejne dostępne zadanie z toru).

---

## 9. Najczęstsze problemy

| Symptom | Przyczyna | Rozwiązanie |
|---|---|---|
| `FileNotFoundError: rf_model.pkl` przy starcie Flaska | Brak artefaktów w `ml-service/` | Wytrenuj modele (sekcja 2.2) i skopiuj |
| CORS error w przeglądarce | Frontend uruchomiony na innym porcie niż 5173 | Zaktualizuj `Program.cs` w backendzie (`AddCors`) lub uruchom front na 5173 |
| `dotnet ef` not found | Brak `dotnet-ef` globalnie | `dotnet tool install --global dotnet-ef` |
| Port 5001 / 5120 / 5173 zajęty | Inny proces na porcie | `lsof -i :PORT` → `kill <pid>` |
| Instalacja `tensorflow` trwa wieki | Pełny TensorFlow z GPU deps | W `requirements.txt` używamy `tensorflow-cpu`; sprawdź czy nie ciągniesz pełnego `tensorflow` osobno |
| `docker-compose up` zawisa na `db` | Healthcheck Postgresa nie przechodzi | `docker-compose down -v` i ponownie; sprawdź czy port 5432 jest wolny |
| Migracje EF Core nie wykonują się | Brak connection stringa / zły URL | Sprawdź `appsettings.json`/zmienne env w compose |

---

## 10. Co musisz przeczytać przed pierwszym PR-em

1. `CLAUDE.md` — architektura, porty, komendy referencyjne.
2. `TASKS.md` — sekcja „Metodyka danych" (mapowanie kolumn UCI, okno 3-mies., 4 okna sliding-window).
3. `plan_sprintow_wariant_B.md` — sekcja „Fundament metodyczny" (dlaczego okno 3-mies., dlaczego trening na W3).
4. `CHECKLIST.md` — kto co teraz robi.
5. `docs/api-contracts/monitoring.md` — pełna specyfikacja 4 endpointów monitoring API + typy współdzielone + reguła alertu.
6. **Sprint summaries** — historia dostarczonych zadań i kluczowe decyzje projektowe:
   - `PodsumowanieSprintu1.md` — sliding-window + schemat bazy (oba tory)
   - `PodsumowanieSprintu2_MK.md` — kontrakt API + .NET predict-timeseries + persistence
   - `PodsumowanieSprintu3_GF.md` — dowód tezy (statyka vs monitoring) + cost thresholds
   - `PodsumowanieSprintu4_GF.md` — LightGBM/CatBoost + SHAP + Optuna tuning

To wszystko. Powodzenia. 🚀
