# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A **credit card default risk prediction system** that accepts 22 input fields (demographics, 6-month payment history, bills, and payment amounts) and returns default probability predictions from an ensemble of 3 ML models (Random Forest, XGBoost, LSTM).

## Services & Ports

| Service | Port | Tech |
|---|---|---|
| Frontend | 5173 | React 19 + Vite + TypeScript |
| Backend API | 5120 | .NET 8 ASP.NET Core |
| ML Service | 5001 | Python Flask |

## Development Commands

### Frontend (`frontend/WebApp/`)
```bash
npm install
npm run dev        # http://localhost:5173
npm run build
npm run lint
```

### Backend (`backend/WebApi/`)
```bash
dotnet build
dotnet run         # http://localhost:5120; Swagger at /swagger
```

### ML Service (`ml-service/`)
```bash
pip install -r requirements.txt
python app.py      # http://localhost:5001
```

### Model Training (`ml-learing-center/`)
```bash
python main.py     # Trains and saves RF, XGBoost, and LSTM models
```

### Docker (ML Service only)
```bash
docker build -t ml-service ./ml-service
docker run -p 5001:5001 ml-service
```

## Architecture

```
React Frontend (5173)
    → POST /api/predict
.NET Backend (5120)         ← validates & transforms input
    → POST /predict
Flask ML Service (5001)     ← feature engineering + 3-model ensemble
    → JSON response with probabilities
```

The backend acts as an orchestrator/gateway: it validates the request, transforms field names from camelCase (`PredictRequest.cs`) to snake_case (`FlaskPredictRequest.cs`), calls the Flask service, and returns a typed `PredictResponse`.

CORS is configured to allow `http://localhost:5173` only.

The Flask ML URL is configured in `backend/WebApi/appsettings.json` under `FlaskServiceUrl`.

## Key Data Flow

1. **Frontend** posts a `PredictRequest` (22 fields) to `/api/predict`
2. **Backend** validates inputs (e.g., age 18–100, limit 10K–1M, education 1–4), maps to `FlaskPredictRequest` (snake_case JSON properties), and forwards to Flask
3. **Flask** runs `engineer_features()` to derive 13+ features (payment stats, bill trends, utilization rate, late counts, etc.), prepares LSTM input as a `(1, 6, 3)` tensor using pre-saved scalers, then returns predictions from all 3 models
4. **Response** is `PredictResponse` with `ModelPrediction` entries (each has `defaultProbability` and `prediction`: `"DEFAULT"` or `"NO DEFAULT"`)

## ML Service Details

- Models loaded at Flask startup from `.pkl`/`.keras` files
- LSTM uses pre-saved scalers (not fit at inference time) — saved alongside the model in `ml-service/`
- `prepare_lstm_input()` shapes 6-month sequences into `(1, 6, 3)` tensors for the LSTM
- Health check endpoint: `GET http://localhost:5001/health`

## Frontend Components

- `InputForm.tsx`: 22-field form (Client Info, Payment Status, Bills, Payments sections)
- `ResultsDashboard.tsx`: Renders prediction results
- `ModelCard.tsx`: Per-model result display
- `ProbabilityGauge.tsx`: Circular progress bar (react-circular-progressbar)
- `ComparisonChart.tsx`: Cross-model visualization (Recharts)
- `predictApi.ts`: Axios client targeting `http://localhost:5120/api`
