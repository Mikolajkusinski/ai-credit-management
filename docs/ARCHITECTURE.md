# Architecture

## Przepływ główny (Wariant B — monitoring trajektorii PD)

```
React Frontend (5173)
  │  Monitoring tab: ClientList ⇄ ClientHistory, TimelineChart (5 linii PD),
  │  TrendAlerts, SnapshotForm, ShapExplanation
  │
  ├─ POST /api/v1/monitoring/predict-timeseries      (scoring bez zapisu)
  ├─ POST /api/v1/monitoring/clients/{ref}/snapshots (scoring + zapis, transakcja atomowa, 409 na duplikat)
  ├─ GET  /api/v1/monitoring/clients                 (roster + roll-up alert)
  └─ GET  /api/v1/monitoring/clients/{ref}/history   (zapisana trajektoria)
                    │
.NET 8 Backend (5120) — MonitoringController → MonitoringService
  │  walidacja 22 cech (DataAnnotations), mapowanie camelCase→SCREAMING_SNAKE,
  │  labelki okien z snapshotDate, ErrorEnvelope (VALIDATION_FAILED / CONFLICT /
  │  CLIENT_NOT_FOUND / ML_SERVICE_ERROR / ML_SERVICE_UNAVAILABLE / INTERNAL_ERROR)
  │
  ├─ PythonModelClient ──► Flask POST /predict/timeseries (5001)
  │                          │  map_to_w3_columns → engineer_features(df, W3) na 4 oknach
  │                          │  + prepare_lstm_input_w3 (1,3,3); 5 modeli skalibrowanych;
  │                          │  trendy (slope W3−W0), progi kosztowe, SHAP top-5 (drzewa)
  │                          └─ legacy POST /predict (6-mies., 3 modele, baseline)
  │
  └─ SnapshotRepository / PredictionRepository / TrendRepository (wspólny scoped AppDbContext)
                    │
PostgreSQL 16 (5432) — EF Core, auto-migracje przy starcie
  Client(ExternalRef unique) 1─N Snapshot(22 cechy, timestamptz) 1─N Prediction(per model)
  Client 1─N Trend(upsert po (ClientId, ModelName))
```

Kontrakt API (typy, przykłady, kody błędów): `api-contracts/monitoring.md`.

## Warstwa ML — trening vs inferencja

- `ml-learing-center/` — trening (`main.py`), ewaluacja (`evaluation.py`,
  `timeseries_eval.py`, `static_vs_dynamic.py`, `fairness_audit.py`,
  `final_report.py`), kanoniczne wyniki w `reports/`.
- `ml-service/` — inferencja Flask; współdzielone moduły `features.py`
  i `sliding_window.py` są kopiami bajt-w-bajt (zmiany zawsze w obu; parytet
  trening/serving przypięty testami `tests/test_train_serve_parity.py`).
- Okna: W0=[kwi,maj,cze] … W3=[lip,sie,wrz]; trening na W3, inferencja na W0..W3.
- Artefakty ładowane raz przy starcie Flaska; skalery wyłącznie `transform`.

## Decyzje projektowe (skrót)

| Decyzja | Uzasadnienie |
|---|---|
| Kalibracja izotoniczna (P0) | trajektoria PD ma sens tylko przy skalibrowanych wartościach bezwzględnych |
| Progi kosztowe FN=5×FP na splicie kalibracyjnym | asymetria kosztów banku; bez dotykania testu (`reports/threshold_leakage_fix.md`) |
| Frontend poza docker-compose | wygoda hot-reload w dev |
| Transakcja atomowa w zapisie migawki | snapshot+5 predykcji+5 trendów spójne albo wcale (test rollbacku na Testcontainers) |
| SHAP tylko modele drzewiaste | TreeExplainer < 2 s DoD; KernelExplainer dla LSTM poza budżetem |
| Stacking (CREDIT-113) descoped | nie wnosi do dowodu tezy; wymaga protokołu OOF |

## CI

GitHub Actions (`.github/workflows/ci.yml`), 4 joby blokujące PR: backend
(xUnit, 25 testów), ml-service (pytest, 17), ml-training (pytest), frontend
(Vitest, 34).
