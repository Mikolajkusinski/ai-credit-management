import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import TrendAlerts from '../TrendAlerts';
import { Trends } from '../../types/monitoring';

const trends: Trends = {
  randomForest: { slope: 0.4, alert: 'INCREASING_RISK' },
  xgboost: { slope: -0.15, alert: 'DECREASING_RISK' },
  lstm: { slope: 0.05, alert: 'STABLE' },
};

describe('TrendAlerts', () => {
  it('renders a card per model with its name', () => {
    render(<TrendAlerts trends={trends} />);

    expect(screen.getByRole('heading', { name: /random forest/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /xgboost/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /lstm/i })).toBeInTheDocument();
  });

  it('shows the alert label for each trend state', () => {
    render(<TrendAlerts trends={trends} />);

    expect(screen.getByText(/increasing risk/i)).toBeInTheDocument();
    expect(screen.getByText(/decreasing risk/i)).toBeInTheDocument();
    expect(screen.getByText(/stable/i)).toBeInTheDocument();
  });

  it('formats the slope with a sign', () => {
    render(<TrendAlerts trends={trends} />);

    expect(screen.getByText('+0.40')).toBeInTheDocument();
    expect(screen.getByText('-0.15')).toBeInTheDocument();
    expect(screen.getByText('+0.05')).toBeInTheDocument();
  });
});
