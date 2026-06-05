import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import TrendAlerts from '../TrendAlerts';
import { Trends } from '../../types/monitoring';

const trends: Trends = {
  randomForest: { slope: 0.4, alert: 'INCREASING_RISK' },
  xgboost: { slope: -0.15, alert: 'DECREASING_RISK' },
  lightgbm: { slope: 0.3, alert: 'INCREASING_RISK' },
  catboost: { slope: -0.2, alert: 'DECREASING_RISK' },
  lstm: { slope: 0.05, alert: 'STABLE' },
};

describe('TrendAlerts', () => {
  it('renders a card per model with its name', () => {
    render(<TrendAlerts trends={trends} />);

    expect(screen.getByRole('heading', { name: /random forest/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /xgboost/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /lightgbm/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /catboost/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /lstm/i })).toBeInTheDocument();
  });

  it('shows the alert label for each trend state', () => {
    render(<TrendAlerts trends={trends} />);

    // 5 models, mix of alerts: 2× INCREASING_RISK (RF + LightGBM), 2× DECREASING_RISK
    // (XGB + CatBoost), 1× STABLE (LSTM).
    expect(screen.getAllByText(/increasing risk/i)).toHaveLength(2);
    expect(screen.getAllByText(/decreasing risk/i)).toHaveLength(2);
    expect(screen.getAllByText(/stable/i)).toHaveLength(1);
  });

  it('formats the slope with a sign', () => {
    render(<TrendAlerts trends={trends} />);

    expect(screen.getByText('+0.40')).toBeInTheDocument();
    expect(screen.getByText('-0.15')).toBeInTheDocument();
    expect(screen.getByText('+0.30')).toBeInTheDocument();
    expect(screen.getByText('-0.20')).toBeInTheDocument();
    expect(screen.getByText('+0.05')).toBeInTheDocument();
  });
});
