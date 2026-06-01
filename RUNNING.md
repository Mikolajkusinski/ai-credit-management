# RUNNING.md — Instrukcja uruchamiania projektu (krok po kroku)

> Plik dla developerów (GF i MK). Opisuje kompletną sekwencję kroków potrzebną, żeby postawić środowisko dev, odpalić cały stack (frontend + backend + ml-service) i zweryfikować, że zmiany działają.
>
> Architektura, porty i komendy referencyjne: patrz `CLAUDE.md`. Stan backlogu: `TASKS.md`. Postęp prac: `CHECKLIST.md`.
>
> **Stan na początek Sprintu 1 (2 cze 2026).** Po wjeździe poszczególnych zadań Sprintu 1 odpowiednie sekcje zostaną oznaczone jako aktywne.

---

## 1. Wymagania wstępne (jednorazowo na maszynie)

| Narzędzie | Wersja | Do czego |
|---|---|---|
| Python | 3.10+ | `ml-service/`, `ml-learing-center/` |
| .NET SDK | 8.0 | `backend/WebApi/` |
| Node.js | 20+ (LTS) | `frontend/WebApp/` |
| npm | 10+ | razem z Node.js |
| Docker Desktop | aktualne | po CREDIT-402 — Postgres + backend |
| Git | dowolne | klonowanie repo |

macOS / Windows / Linux — wszystkie wspierane. Na Windowsie zalecane PowerShell lub WSL2.

### 1.1. Klonowanie repozytorium

```bash
git clone https://github.com/<owner>/ai-credit-management.git
cd ai-credit-management
```

### 1.2. Globalne narzędzia .NET (jednorazowo)

Po CREDIT-401 (Sprint 1) będzie potrzebne CLI EF Core:

```bash
dotnet tool install --global dotnet-ef
```

---

## 2. ML Service (Flask, port 5001)

Bezstanowy silnik scoringu z 3 modelami (RF, XGBoost, LSTM). Wymaga przedtrenowanych artefaktów.

### 2.1. Wirtualne środowisko + zależności

```bash
cd ml-service
python -m venv venv
source venv/bin/activate          # macOS / Linux
# .\venv\Scripts\Activate.ps1     # Windows PowerShell
pip install -r requirements.txt
```

### 2.2. Skąd wziąć artefakty modeli

Artefakty (`rf_model.pkl`, `xgb_model.pkl`, `lstm_model.keras`, `scaler.pkl`, `lstm_scalers.pkl`, `features.pkl`) **NIE są w gicie**. Trzy opcje:

**Opcja A — wytrenuj lokalnie** (zalecane przy pierwszym setupie zespołowca):

```bash
cd ../ml-learing-center
python -m venv venv
source venv/bin/activate
pip install -r ../ml-service/requirements.txt
# (jeśli brakuje libów do treningu — dopisać do venv: pandas, scikit-learn, xgboost, tensorflow)
python main.py
# Trening trwa ~3–8 min na CPU. Wypisuje AUC dla RF / XGB / LSTM.
```

Po zakończeniu skopiuj artefakty do `ml-service/`:

```bash
cp rf_model.pkl xgb_model.pkl lstm_model.keras scaler.pkl features.pkl ../ml-service/
# lstm_scalers.pkl jest już zapisywany bezpośrednio do ../ml-service/ przez main.py
```

**Opcja B — pobierz od kolegi z zespołu** (jeśli ktoś już wytrenował).

**Po CREDIT-102 (Sprint 1):** pojawią się DODATKOWE artefakty z sufiksem `_w3` (np. `rf_model_w3.pkl`) — używane przy oknie 3-miesięcznym i nowym endpointcie `/predict/timeseries` (CREDIT-104, Sprint 2). Stare artefakty bez sufiksu **pozostają działające** dla legacy `/predict`.

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

**Po CREDIT-401 (Sprint 1):** dojdzie sekcja `ConnectionStrings:Default` z URL-em do Postgresa. Domyślnie: `Host=localhost;Port=5432;Database=credit;Username=postgres;Password=postgres`.

### 3.3. Uruchomienie

```bash
dotnet run
# Swagger: http://localhost:5120/swagger
# API: http://localhost:5120/api
```

### 3.4. Sanity check

Otwórz `http://localhost:5120/swagger` i wyślij testowe `POST /api/predict` z przykładowym payloadem 22 cech.

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

## 5. PostgreSQL (po CREDIT-401 / Sprint 1)

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

### 5.2. Przez docker-compose (po CREDIT-402)

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

Otwórz `http://localhost:5173`. Wypełnij formularz (22 pola), kliknij Predict, zobacz wyniki 3 modeli.

---

## 7. Testy

Po wjeździe CREDIT-201 (Sprint 1):

```bash
# Backend (xUnit)
cd backend && dotnet test

# ML (pytest)
cd ml-service && source venv/bin/activate && pytest

# Frontend (Vitest)
cd frontend/WebApp && npm run test
```

CI (`.github/workflows/ci.yml`) odpala wszystkie trzy na każdym PR-ze. **Czerwone CI = blokada merge'a.**

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

To wszystko. Powodzenia. 🚀
