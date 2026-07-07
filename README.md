# AI Credit Management — monitoring ryzyka niewypłacalności (Wariant B)

System oceny i **kalendarzowego monitoringu** ryzyka niewypłacalności klientów kart
kredytowych. Ten sam klient jest oceniany wielokrotnie na przesuwanym oknie
3-miesięcznej historii płatniczej (okna W0..W3), co daje **4-punktową trajektorię PD**
per model — podstawę wczesnego ostrzegania, zamiast jednorazowej oceny statycznej.

Projekt pracy magisterskiej (Gabriel Figur, Mikołaj Kusiński).

## Stack

| Warstwa | Technologia | Port |
|---|---|---|
| Frontend | React 19 + Vite + TypeScript, Recharts | 5173 |
| Backend | .NET 8 ASP.NET Core, EF Core + Npgsql | 5120 |
| ML | Python 3.11, Flask; scikit-learn / XGBoost / LightGBM / CatBoost / TensorFlow | 5001 |
| Baza | PostgreSQL 16 | 5432 |

Modele: 5 klasyfikatorów trenowanych na oknie W3 zbioru UCI „default of credit card
clients" (30 000 klientów), **kalibrowanych izotonicznie**, z progami alertu
optymalnymi kosztowo (FN=5×FP) i wyjaśnieniami SHAP (modele drzewiaste).
Szczegóły: [docs/MODEL_CARD.md](docs/MODEL_CARD.md).

## Uruchomienie end-to-end

```bash
# 1. Baza + backend (auto-migracje) + serwis ML — jedną komendą:
docker compose up

# 2. Frontend (poza compose, dev-server z hot-reload):
cd frontend/WebApp && npm install && npm run dev
# → http://localhost:5173  (zakładki: Prediction / Monitoring)

# 3. (opcjonalnie) dane demo — 3 klientów z różnymi trajektoriami:
python ml-learing-center/seed_demo_clients.py
```

Health check ML: `GET http://localhost:5001/health` · Swagger: `http://localhost:5120/swagger`

> **Uwaga (dane demo sprzed 2026-07-07):** snapshoty zapisane starym wolumenem
> zawierają predykcje sprzed naprawy train/serve skew — wyczyść wolumen
> (`docker compose down -v`) i zseeduj ponownie. Szczegóły:
> `docs/api-contracts/monitoring.md` (Data note).

## Development

```bash
# Testy
cd backend && dotnet test                 # 25 testów (PersistenceTests wymagają Dockera)
cd ml-service && pytest                   # 17 testów (w tym parytet trening/serving)
cd frontend/WebApp && npm run test        # 34 testy Vitest
cd ml-learing-center && pytest sliding_window_test.py

# Retrain + pełna ewaluacja (venv: ml-learing-center/.venv)
cd ml-learing-center
.venv/bin/python main.py                  # artefakty *_w3 + alert_thresholds.json
.venv/bin/python evaluation.py            # metryki + wykresy
.venv/bin/python fairness_audit.py        # DPD/EOD wrt SEX (fairlearn)
.venv/bin/python static_vs_dynamic.py     # dowód tezy: statyka vs monitoring
.venv/bin/python final_report.py          # reports/FINAL_REPORT.md
```

CI (GitHub Actions): 4 joby — backend (xUnit), ml-service (pytest), ml-training
(pytest), frontend (Vitest); czerwony PR blokuje merge.

## Struktura repo

```
backend/            .NET 8 API + EF Core + testy (xUnit, Testcontainers)
frontend/WebApp/    React 19 + TS + Vitest
ml-service/         Flask: inferencja 5 modeli, trajektorie, SHAP + testy parytetu
ml-learing-center/  trening, ewaluacja, audyty; reports/ = kanoniczne wyniki
docs/               api-contracts/monitoring.md (kontrakt 4 endpointów), MODEL_CARD.md
TASKS.md            definicje zadań CREDIT-XXX + graf zależności
CHECKLIST.md        statusy zadań per sprint
```

## Kluczowe wyniki (po naprawach metodologicznych 2026-07-07)

- CatBoost najlepszy pojedynczy model: **AUC 0.779**, Brier 0.136 (test 6 000 klientów).
- Monitoring vs statyka @FA=10%: statyka wygrywa na catch rate dla 4 modeli, ale
  **LSTM (+2.6 pp) wygrywa monitoringiem**; monitoring daje średnio **~2 okna lead time**
  i 39–74 unikalnych wykryć/model. Pełny raport: `ml-learing-center/reports/FINAL_REPORT.md`.
- Fairness (fairlearn, SEX): wszystkie modele |DPD|, |EOD| ≤ 0.04 przy limicie 0.10.
