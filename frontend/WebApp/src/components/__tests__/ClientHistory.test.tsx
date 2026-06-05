import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ClientHistory, { historyToTrajectory, formatSnapshotLabel } from '../ClientHistory';
import { getClientHistory } from '../../api/monitoringApi';
import type { HistoryResponse } from '../../types/monitoring';

vi.mock('../../api/monitoringApi', () => ({
  getClientHistory: vi.fn(),
}));

const mockedGet = vi.mocked(getClientHistory);

const history: HistoryResponse = {
  clientRef: 'alpha',
  createdAt: '2026-05-01T00:00:00Z',
  history: [
    { snapshotId: 11, snapshotDate: '2026-05-10', predictions: { randomForest: 0.18, xgboost: 0.2, lightgbm: 0.19, catboost: 0.17, lstm: 0.15 } },
    { snapshotId: 12, snapshotDate: '2026-05-24', predictions: { randomForest: 0.58, xgboost: 0.61, lightgbm: 0.6, catboost: 0.57, lstm: 0.55 } },
  ],
  trends: {
    randomForest: { slope: 0.4, alert: 'INCREASING_RISK' },
    xgboost: { slope: 0.41, alert: 'INCREASING_RISK' },
    lightgbm: { slope: 0.41, alert: 'INCREASING_RISK' },
    catboost: { slope: 0.4, alert: 'INCREASING_RISK' },
    lstm: { slope: 0.4, alert: 'INCREASING_RISK' },
  },
};

describe('historyToTrajectory', () => {
  it('maps each snapshot to a trajectory point with a formatted, date-based label', () => {
    const points = historyToTrajectory(history.history);

    expect(points).toHaveLength(2);
    expect(points[0]).toMatchObject({ window: '11', label: 'May 10' });
    expect(points[1].label).toBe('May 24');
    expect(points[1].predictions.randomForest).toBe(0.58);
  });

  it('formatSnapshotLabel renders a UTC-safe short month + day', () => {
    expect(formatSnapshotLabel('2026-01-05')).toBe('Jan 5');
  });
});

describe('ClientHistory', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetches and renders the PD history chart and trend alerts', async () => {
    mockedGet.mockResolvedValue(history);
    render(<ClientHistory clientRef="alpha" onBack={() => {}} />);

    expect(await screen.findByRole('heading', { name: /pd history/i })).toBeInTheDocument();
    // TrendAlerts renders one card per model, all increasing here.
    expect(screen.getAllByText(/increasing risk/i).length).toBeGreaterThan(0);
    expect(mockedGet).toHaveBeenCalledWith('alpha');
  });

  it('calls onBack when the back button is clicked', async () => {
    mockedGet.mockResolvedValue(history);
    const onBack = vi.fn();
    render(<ClientHistory clientRef="alpha" onBack={onBack} />);

    fireEvent.click(await screen.findByRole('button', { name: /back to clients/i }));
    expect(onBack).toHaveBeenCalled();
  });

  it('shows an empty state when the client has no snapshots', async () => {
    mockedGet.mockResolvedValue({ ...history, history: [] });
    render(<ClientHistory clientRef="alpha" onBack={() => {}} />);

    expect(await screen.findByText(/no snapshots for this client yet/i)).toBeInTheDocument();
  });
});
