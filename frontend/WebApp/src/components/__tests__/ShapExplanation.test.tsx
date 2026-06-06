import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ShapExplanation, {
  RAISE_COLOR,
  LOWER_COLOR,
  barColor,
  barWidthPct,
  formatSignedValue,
} from '../ShapExplanation';
import { ShapExplanation as ShapExplanationType } from '../../types/monitoring';

// 4 tree models, 5 features each, with a mix of +/− values. No LSTM (TreeExplainer only).
const shap: ShapExplanationType = {
  window: 'W3',
  randomForest: {
    topFeatures: [
      { feature: 'PAY_mean', value: 0.031 },
      { feature: 'PAY_max', value: 0.03 },
      { feature: 'PAY_AMT_mean', value: -0.025 },
      { feature: 'late_count', value: 0.024 },
      { feature: 'utilization_rate', value: -0.018 },
    ],
  },
  xgboost: {
    topFeatures: [
      { feature: 'PAY_max', value: 0.041 },
      { feature: 'PAY_mean', value: 0.033 },
      { feature: 'severe_late', value: 0.027 },
      { feature: 'PAY_AMT_mean', value: -0.022 },
      { feature: 'BILL_trend', value: 0.015 },
    ],
  },
  lightgbm: {
    topFeatures: [
      { feature: 'PAY_mean', value: 0.036 },
      { feature: 'late_count', value: 0.028 },
      { feature: 'PAY_AMT_mean', value: -0.024 },
      { feature: 'PAY_max', value: 0.021 },
      { feature: 'utilization_rate', value: -0.016 },
    ],
  },
  catboost: {
    topFeatures: [
      { feature: 'PAY_max', value: 0.038 },
      { feature: 'PAY_mean', value: 0.032 },
      { feature: 'payment_ratio', value: -0.026 },
      { feature: 'late_count', value: 0.02 },
      { feature: 'BILL_mean', value: -0.014 },
    ],
  },
};

describe('ShapExplanation helpers', () => {
  it('colors positive SHAP red (raises PD) and negative green (lowers PD)', () => {
    expect(barColor(0.03)).toBe(RAISE_COLOR);
    expect(barColor(0)).toBe(RAISE_COLOR);
    expect(barColor(-0.02)).toBe(LOWER_COLOR);
  });

  it('formats the value signed to 3 dp', () => {
    expect(formatSignedValue(0.031)).toBe('+0.031');
    expect(formatSignedValue(-0.03)).toBe('-0.030');
  });

  it('scales bar width to the strongest feature in the model', () => {
    expect(barWidthPct(0.04, 0.04)).toBe(100);
    expect(barWidthPct(0.02, 0.04)).toBe(50);
    expect(barWidthPct(0.04, 0)).toBe(0); // guards divide-by-zero
  });
});

describe('ShapExplanation', () => {
  it('renders a heading for each of the 4 tree models', () => {
    render(<ShapExplanation shap={shap} />);

    expect(screen.getByRole('heading', { name: 'Random Forest' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'XGBoost' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'LightGBM' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'CatBoost' })).toBeInTheDocument();
  });

  it('renders 5 bars per model (20 total)', () => {
    render(<ShapExplanation shap={shap} />);
    expect(screen.getAllByTestId('shap-bar')).toHaveLength(20);
  });

  it('uses red bars for positive SHAP and green for negative', () => {
    render(<ShapExplanation shap={shap} />);
    const raisers = screen.getAllByTitle('raises PD');
    const lowerers = screen.getAllByTitle('lowers PD');

    expect(raisers.length).toBeGreaterThan(0);
    expect(lowerers.length).toBeGreaterThan(0);
    raisers.forEach((bar) => expect(bar).toHaveStyle({ backgroundColor: RAISE_COLOR }));
    lowerers.forEach((bar) => expect(bar).toHaveStyle({ backgroundColor: LOWER_COLOR }));
  });

  it('renders nothing when no model blocks are present', () => {
    const { container } = render(<ShapExplanation shap={{ window: 'W3' }} />);
    expect(container).toBeEmptyDOMElement();
  });
});
