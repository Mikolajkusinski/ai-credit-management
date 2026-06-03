import { PredictRequest } from './prediction';

// Types mirroring the CREDIT-210 monitoring API contract
// (docs/api-contracts/monitoring.md + backend/WebApi/Models/TimeseriesResponse.cs).
// JSON is camelCase; model keys are randomForest / xgboost / lstm; alert enum is
// SCREAMING_SNAKE_CASE. Keep these in lockstep with the contract.

export type ModelKey = 'randomForest' | 'xgboost' | 'lstm';

export type AlertType = 'INCREASING_RISK' | 'DECREASING_RISK' | 'STABLE';

export interface WindowPredictions {
  randomForest: number;
  xgboost: number;
  lstm: number;
}

export interface TrajectoryPoint {
  window: string; // "W0" | "W1" | "W2" | "W3"
  label?: string; // backend-computed month range, e.g. "Jan-Mar 2026"
  predictions: WindowPredictions;
}

export interface TrendInfo {
  slope: number; // PD_W3 - PD_W0
  alert: AlertType;
}

export interface Trends {
  randomForest: TrendInfo;
  xgboost: TrendInfo;
  lstm: TrendInfo;
}

export interface TimeseriesResponse {
  clientRef?: string;
  snapshotDate?: string; // ISO date, e.g. "2026-06-03"
  trajectory: TrajectoryPoint[];
  trends: Trends;
}

// The 22-feature snapshot has the same shape as PredictRequest.
export type Snapshot22Features = PredictRequest;

export interface TimeseriesRequest {
  clientRef?: string;
  snapshotDate?: string;
  features: Snapshot22Features;
}

// --- Persisted client history (contract 4.4: GET clients/{ref}/history) ---
// A point on the real calendar-time timeline: one persisted snapshot with its W3 predictions.
export interface HistoryPoint {
  snapshotId: number;
  snapshotDate: string; // ISO date, e.g. "2026-05-10"
  predictions: WindowPredictions;
}

export interface HistoryResponse {
  clientRef: string;
  createdAt: string; // ISO datetime
  history: HistoryPoint[]; // ascending by date (oldest → newest)
  trends: Trends;
}

// --- Client list (contract 4.5: GET clients) ---
export interface ClientSummary {
  clientRef: string;
  createdAt: string; // ISO datetime
  snapshotCount: number;
  latestSnapshotDate?: string | null; // ISO date; null when no snapshots yet
  latestAlert: AlertType; // roll-up badge across the per-model trends
}

export interface ClientListResponse {
  clients: ClientSummary[];
}

export interface HistoryQuery {
  from?: string;
  to?: string;
  limit?: number;
}
