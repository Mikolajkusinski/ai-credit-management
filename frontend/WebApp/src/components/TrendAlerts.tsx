import { AlertType, ModelKey, Trends } from '../types/monitoring';

interface TrendAlertsProps {
  trends: Trends;
}

const MODELS: { key: ModelKey; name: string }[] = [
  { key: 'randomForest', name: 'Random Forest' },
  { key: 'xgboost', name: 'XGBoost' },
  { key: 'lstm', name: 'LSTM' },
];

const ALERT_STYLES: Record<AlertType, { color: string; label: string; icon: string }> = {
  INCREASING_RISK: { color: '#ef4444', label: 'Increasing risk', icon: '↑' },
  DECREASING_RISK: { color: '#10b981', label: 'Decreasing risk', icon: '↓' },
  STABLE: { color: '#94a3b8', label: 'Stable', icon: '→' },
};

const formatSlope = (slope: number) => `${slope >= 0 ? '+' : ''}${slope.toFixed(2)}`;

const TrendAlerts = ({ trends }: TrendAlertsProps) => (
  <div style={{
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px'
  }}>
    {MODELS.map(({ key, name }) => {
      const trend = trends[key];
      const style = ALERT_STYLES[trend.alert];
      return (
        <div key={key} style={{
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderRadius: '16px',
          padding: '24px',
          border: `1px solid ${style.color}59`,
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#f1f5f9' }}>
              {name}
            </h4>
            <span style={{ fontSize: '24px', color: style.color, lineHeight: 1 }} aria-hidden="true">
              {style.icon}
            </span>
          </div>
          <div style={{
            display: 'inline-block',
            backgroundColor: `${style.color}26`,
            color: style.color,
            padding: '6px 16px',
            borderRadius: '9999px',
            fontWeight: 600,
            fontSize: '14px',
            marginBottom: '12px'
          }}>
            {style.label}
          </div>
          <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8' }}>
            Slope (W3 − W0): <span style={{ color: '#e2e8f0', fontWeight: 600 }}>{formatSlope(trend.slope)}</span>
          </p>
        </div>
      );
    })}
  </div>
);

export default TrendAlerts;
