import axios from 'axios';
import {
  ClientListResponse,
  HistoryQuery,
  HistoryResponse,
  TimeseriesRequest,
  TimeseriesResponse,
} from '../types/monitoring';

const API_BASE_URL = 'http://localhost:5120/api/v1/monitoring';

// Stateless trajectory scoring (contract 4.2). Wired and typed for CREDIT-302/303;
// the CREDIT-301 Timeline view renders MOCK_TIMESERIES_RESPONSE below until then.
export const predictTimeseries = async (
  data: TimeseriesRequest,
): Promise<TimeseriesResponse> => {
  const response = await axios.post<TimeseriesResponse>(
    `${API_BASE_URL}/predict-timeseries`,
    data,
  );
  return response.data;
};

// List every monitored client with roll-up stats (contract 4.5). Drives the ClientList view.
export const listClients = async (): Promise<ClientListResponse> => {
  const response = await axios.get<ClientListResponse>(`${API_BASE_URL}/clients`);
  return response.data;
};

// Read a client's persisted snapshot timeline (contract 4.4). Drives the ClientHistory view.
export const getClientHistory = async (
  clientRef: string,
  query: HistoryQuery = {},
): Promise<HistoryResponse> => {
  const response = await axios.get<HistoryResponse>(
    `${API_BASE_URL}/clients/${encodeURIComponent(clientRef)}/history`,
    { params: query },
  );
  return response.data;
};

// Mock payload taken from the CREDIT-210 contract example — an intentionally rising
// trajectory so the Timeline view tells the early-warning story (PD climbs across
// W0→W3, slope ≈ 0.40 → INCREASING_RISK for every model).
export const MOCK_TIMESERIES_RESPONSE: TimeseriesResponse = {
  clientRef: 'client-001',
  snapshotDate: '2026-06-03',
  trajectory: [
    {
      window: 'W0',
      label: 'Jan-Mar 2026',
      predictions: { randomForest: 0.18, xgboost: 0.2, lightgbm: 0.19, catboost: 0.17, lstm: 0.15 },
    },
    {
      window: 'W1',
      label: 'Feb-Apr 2026',
      predictions: { randomForest: 0.27, xgboost: 0.29, lightgbm: 0.28, catboost: 0.26, lstm: 0.24 },
    },
    {
      window: 'W2',
      label: 'Mar-May 2026',
      predictions: { randomForest: 0.41, xgboost: 0.44, lightgbm: 0.42, catboost: 0.4, lstm: 0.39 },
    },
    {
      window: 'W3',
      label: 'Apr-Jun 2026',
      predictions: { randomForest: 0.58, xgboost: 0.61, lightgbm: 0.6, catboost: 0.57, lstm: 0.55 },
    },
  ],
  trends: {
    randomForest: { slope: 0.4, alert: 'INCREASING_RISK' },
    xgboost: { slope: 0.41, alert: 'INCREASING_RISK' },
    lightgbm: { slope: 0.41, alert: 'INCREASING_RISK' },
    catboost: { slope: 0.4, alert: 'INCREASING_RISK' },
    lstm: { slope: 0.4, alert: 'INCREASING_RISK' },
  },
};
