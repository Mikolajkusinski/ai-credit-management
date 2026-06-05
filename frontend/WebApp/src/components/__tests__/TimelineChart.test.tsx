import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import TimelineChart, { buildChartData } from '../TimelineChart';
import { MOCK_TIMESERIES_RESPONSE } from '../../api/monitoringApi';

describe('TimelineChart', () => {
  it('buildChartData returns 4 rows with a PD for each of the 5 models', () => {
    const rows = buildChartData(MOCK_TIMESERIES_RESPONSE.trajectory);

    expect(rows).toHaveLength(4);
    rows.forEach((row) => {
      expect(typeof row.randomForest).toBe('number');
      expect(typeof row.xgboost).toBe('number');
      expect(typeof row.lightgbm).toBe('number');
      expect(typeof row.catboost).toBe('number');
      expect(typeof row.lstm).toBe('number');
    });
    // X-axis values come from the window labels
    expect(rows.map((r) => r.label)).toEqual([
      'Jan-Mar 2026',
      'Feb-Apr 2026',
      'Mar-May 2026',
      'Apr-Jun 2026',
    ]);
  });

  it('falls back to the window id when a label is missing', () => {
    const rows = buildChartData([
      { window: 'W0', predictions: { randomForest: 0.1, xgboost: 0.1, lightgbm: 0.1, catboost: 0.1, lstm: 0.1 } },
    ]);

    expect(rows[0].label).toBe('W0');
  });

  it('renders the chart heading without crashing', () => {
    render(<TimelineChart trajectory={MOCK_TIMESERIES_RESPONSE.trajectory} />);

    expect(screen.getByRole('heading', { name: /pd trajectory/i })).toBeInTheDocument();
  });
});
