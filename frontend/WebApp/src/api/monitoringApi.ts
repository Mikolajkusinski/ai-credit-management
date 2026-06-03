import axios from 'axios';
import { TimeseriesRequest, TimeseriesResponse } from '../types/monitoring';

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
      predictions: { randomForest: 0.18, xgboost: 0.2, lstm: 0.15 },
    },
    {
      window: 'W1',
      label: 'Feb-Apr 2026',
      predictions: { randomForest: 0.27, xgboost: 0.29, lstm: 0.24 },
    },
    {
      window: 'W2',
      label: 'Mar-May 2026',
      predictions: { randomForest: 0.41, xgboost: 0.44, lstm: 0.39 },
    },
    {
      window: 'W3',
      label: 'Apr-Jun 2026',
      predictions: { randomForest: 0.58, xgboost: 0.61, lstm: 0.55 },
    },
  ],
  trends: {
    randomForest: { slope: 0.4, alert: 'INCREASING_RISK' },
    xgboost: { slope: 0.41, alert: 'INCREASING_RISK' },
    lstm: { slope: 0.4, alert: 'INCREASING_RISK' },
  },
};
