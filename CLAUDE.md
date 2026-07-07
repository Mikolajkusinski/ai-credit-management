# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A **credit default risk monitoring system** (thesis project, "Wariant B"): the same
client is scored repeatedly over a sliding window of payment history, producing a
**PD trajectory** used for early warning. Five calibrated ML models (Random Forest,
XGBoost, LightGBM, CatBoost, LSTM) are trained on a 3-month window (W3) of the UCI
"default of credit card clients" dataset and applied to 4 overlapping windows
(W0..W3) to yield a 4-point trajectory per model, with cost-optimal alert
thresholds, per-model trends and SHAP explanations.

## Services & Ports

| Service | Port | Tech |
|---|---|---|
| Frontend | 5173 | React 19 + Vite + TypeScript (outside docker-compose) |
| Backend API | 5120 | .NET 8 ASP.NET Core + EF Core |
| ML Service | 5001 | Python Flask |
| PostgreSQL | 5432 | postgres:16 (docker-compose, named volume `pg_data`) |

## Development Commands

### Everything backend-side at once
```bash
docker compose up    # db (healthcheck) + backend (auto-migrations) + ml-service
```

### Frontend (`frontend/WebApp/`)
```bash
npm install
npm run dev        # http://localhost:5173
npm run build
npm run lint
npm run test       # Vitest (34 tests)
```

### Backend (`backend/WebApi/`)
```bash
dotnet build
dotnet run         # http://localhost:5120; Swagger at /swagger
dotnet test        # xUnit, 25 tests; PersistenceTests need Docker (Testcontainers)
```

### ML Service (`ml-service/`)
```bash
pip install -r requirements.txt
python app.py      # http://localhost:5001
pytest             # 17 tests incl. train/serve parity suite
```

### Model Training (`ml-learing-center/`)
```bash
# venv with the full stack lives at ml-learing-center/.venv (python3.11)
.venv/bin/python main.py            # retrains legacy + W3 models, writes artifacts + thresholds
.venv/bin/python evaluation.py      # metrics_w3.csv + ROC/PR/calibration/KS/confusion plots
.venv/bin/python fairness_audit.py  # DPD/EOD wrt SEX (fairlearn)
.venv/bin/python timeseries_eval.py # lead time / slope metrics
.venv/bin/python static_vs_dynamic.py  # thesis proof: static W3 vs monitoring W0..W3
.venv/bin/python final_report.py    # aggregates everything into reports/FINAL_REPORT.md
```

## Architecture

```
React Frontend (5173)
    → POST/GET /api/v1/monitoring/*         (Monitoring tab: trajectory, history, snapshots)
    → POST /api/predict                     (legacy Prediction tab)
.NET Backend (5120)      ← validation (DataAnnotations), camelCase→SNAKE_CASE mapping,
    |                      window labels, error envelope, EF Core persistence
    → POST /predict/timeseries              (main path — 5 models × 4 windows)
    → POST /predict                         (legacy 6-month, 3 uncalibrated models)
Flask ML Service (5001)  ← engineer_features(df, window) + (1,3,3) LSTM tensor,
    |                      isotonic-calibrated PD, trends, cost thresholds, SHAP top-5
PostgreSQL 16 (5432)     ← Client / Snapshot (22 raw features) / Prediction / Trend
```

Backend endpoints (contract: `docs/api-contracts/monitoring.md`, 4 endpoints):
`POST /api/v1/monitoring/predict-timeseries` (stateless scoring),
`POST /api/v1/monitoring/clients/{ref}/snapshots` (score + persist, **atomic transaction**,
409 on duplicate date), `GET /api/v1/monitoring/clients` (roster with roll-up alert),
`GET /api/v1/monitoring/clients/{ref}/history` (persisted PD trajectory).

CORS is configured to allow `http://localhost:5173` only. The Flask ML URL is
configured in `backend/WebApi/appsettings.json` under `FlaskServiceUrl`.

## Key ML Details

- **Sliding window** (`sliding_window.py`, identical copy in both `ml-learing-center/`
  and `ml-service/` — keep them in sync, same for `features.py`): one UCI row → 4
  overlapping 3-month windows W0..W3; training on W3 (aligned with the October label),
  inference on all four.
- **Calibration:** `CalibratedClassifierCV(FrozenEstimator, isotonic)` for the 4 tree
  models; external `IsotonicRegression` (`lstm_calibrator_w3.pkl`) applied to raw LSTM
  output. 3-way split 60/20/20 (train/calib/test, `random_state=42`, stratified).
- **Scalers are fitted on the TRAIN split only** and applied with `transform` at
  inference — never refit (leakage fix 2026-07-07, `reports/scaler_leakage_fix.md`).
- **Alert thresholds** (`ml-service/alert_thresholds.json`): per-model, cost model
  FN=5×FP, optimized on the calibration split (`reports/threshold_leakage_fix.md`).
- **One-hot encoding uses fixed category domains** (`features.UCI_CATEGORIES`) —
  never call `get_dummies(drop_first=True)` on raw columns of a single-row frame
  (it silently drops all dummies; regression pinned by
  `ml-service/tests/test_train_serve_parity.py`).
- **SHAP** (CREDIT-107): TreeExplainer on the unwrapped base estimators, top-5
  features per prediction for the 4 tree models; LSTM skipped by design.
- Canonical evaluation numbers live in `ml-learing-center/reports/` (`metrics_w3.csv`,
  `fairness_metrics_w3.csv`, `FINAL_REPORT.md`); do not quote numbers from sprint
  summaries — several carry ERRATA banners.

## Frontend Components

- Prediction tab (legacy): `InputForm.tsx` (22 fields, dynamic month labels),
  `ResultsDashboard.tsx`, `ModelCard.tsx`, `ProbabilityGauge.tsx`, `ComparisonChart.tsx`
- Monitoring tab: `ClientList.tsx` ⇄ `ClientHistory.tsx` (master-detail),
  `TimelineChart.tsx` (5 PD lines), `TrendAlerts.tsx` (5 semaphore cards),
  `SnapshotForm.tsx` (dated snapshot entry), `ShapExplanation.tsx` (diverging bars)
- API clients: `api/predictApi.ts` (legacy), `api/monitoringApi.ts` (monitoring, typed
  by `types/monitoring.ts` — `ModelKey` covers all 5 models)

## Known Constraints / Gotchas

- UCI has **no `PAY_1`** — September maps to `PAY_0` + `BILL_AMT1` + `PAY_AMT1`.
- The legacy `/predict` endpoint serves 3 **uncalibrated** 6-month models at a 0.5
  threshold — kept as a historical baseline; do not mix its outputs with W3 numbers.
- `ml-learing-center` vs `ml-service`: training vs inference. Shared logic is
  duplicated by file copy; any edit to `features.py`/`sliding_window.py` must land
  in both (parity guarded by tests).
- Project audit reports with findings, defense Q&A and executable fix prompts:
  `Fable5_Task1.md` (thesis vs code), `Fable5_Task2.md` (fairness), `Fable5_Task3.md`
  (ML correctness), `Fable5_Task4.md` (sprint execution audit).
- Task tracking: `TASKS.md` + `CHECKLIST.md` (statuses, dependency graph, update
  workflow at the bottom of CHECKLIST).
