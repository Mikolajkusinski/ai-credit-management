import { ShapExplanation as ShapExplanationType, ShapModel, ShapModelKey } from '../types/monitoring';

interface ShapExplanationProps {
  shap: ShapExplanationType;
  title?: string;
  subtitle?: string;
}

// CREDIT-107/211: SHAP covers the 4 tree-based models only (LSTM excluded — TreeExplainer N/A).
const MODELS: { key: ShapModelKey; name: string }[] = [
  { key: 'randomForest', name: 'Random Forest' },
  { key: 'xgboost', name: 'XGBoost' },
  { key: 'lightgbm', name: 'LightGBM' },
  { key: 'catboost', name: 'CatBoost' },
];

// Diverging-bar colors: red = pushes PD up (toward DEFAULT), green = pushes PD down.
export const RAISE_COLOR = '#ef4444';
export const LOWER_COLOR = '#10b981';

export const barColor = (value: number): string => (value >= 0 ? RAISE_COLOR : LOWER_COLOR);

// e.g. 0.031 → "+0.031", -0.03 → "-0.030" (3 dp, signed). Mirrors TrendAlerts.formatSlope.
export const formatSignedValue = (value: number): string =>
  `${value >= 0 ? '+' : ''}${value.toFixed(3)}`;

// Bar length as a % of the half-axis, relative to the strongest feature in the model.
export const barWidthPct = (value: number, maxAbs: number): number =>
  maxAbs > 0 ? (Math.abs(value) / maxAbs) * 100 : 0;

const card: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  borderRadius: '16px',
  padding: '24px',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
};

const ModelSection = ({ name, model }: { name: string; model: ShapModel }) => {
  const maxAbs = Math.max(...model.topFeatures.map((f) => Math.abs(f.value)), 0);

  return (
    <div style={{ display: 'grid', gap: '10px' }}>
      <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#f1f5f9' }}>{name}</h4>
      {model.topFeatures.map((f) => {
        const pct = barWidthPct(f.value, maxAbs);
        const color = barColor(f.value);
        const raises = f.value >= 0;
        return (
          <div key={f.feature} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span
              style={{
                width: '128px',
                flexShrink: 0,
                textAlign: 'right',
                fontSize: '13px',
                color: '#cbd5e1',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
              title={f.feature}
            >
              {f.feature}
            </span>

            {/* Diverging track: negatives grow left (green), positives grow right (red). */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', minWidth: 0 }}>
              <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
                {!raises && (
                  <div
                    data-testid="shap-bar"
                    title="lowers PD"
                    style={{ width: `${pct}%`, height: '14px', backgroundColor: color, borderRadius: '4px 0 0 4px' }}
                  />
                )}
              </div>
              <div style={{ width: '1px', height: '20px', backgroundColor: 'rgba(255,255,255,0.25)', flexShrink: 0 }} />
              <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-start' }}>
                {raises && (
                  <div
                    data-testid="shap-bar"
                    title="raises PD"
                    style={{ width: `${pct}%`, height: '14px', backgroundColor: color, borderRadius: '0 4px 4px 0' }}
                  />
                )}
              </div>
            </div>

            <span
              style={{
                width: '56px',
                flexShrink: 0,
                textAlign: 'right',
                fontSize: '13px',
                fontWeight: 600,
                color,
              }}
            >
              {formatSignedValue(f.value)}
            </span>
          </div>
        );
      })}
    </div>
  );
};

const ShapExplanation = ({
  shap,
  title = 'Why this score?',
  subtitle = 'Top-5 SHAP features per model for the latest window (W3)',
}: ShapExplanationProps) => {
  const sections = MODELS.map(({ key, name }) => ({ name, model: shap[key] }))
    .filter((s): s is { name: string; model: ShapModel } => !!s.model && s.model.topFeatures.length > 0);

  if (sections.length === 0) return null;

  return (
    <div style={card}>
      <h3 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 600, color: '#e2e8f0' }}>{title}</h3>
      <p style={{ margin: '0 0 4px 0', fontSize: '14px', color: '#94a3b8' }}>{subtitle}</p>
      <p style={{ margin: '0 0 20px 0', fontSize: '13px', color: '#64748b' }}>
        <span style={{ color: LOWER_COLOR }}>←&nbsp;reduces&nbsp;PD</span>
        {'   ·   '}
        <span style={{ color: RAISE_COLOR }}>raises&nbsp;PD&nbsp;→</span>
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '28px' }}>
        {sections.map((s) => (
          <ModelSection key={s.name} name={s.name} model={s.model} />
        ))}
      </div>
    </div>
  );
};

export default ShapExplanation;
