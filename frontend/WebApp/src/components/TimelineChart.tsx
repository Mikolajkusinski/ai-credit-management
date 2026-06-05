import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { ModelKey, TrajectoryPoint } from '../types/monitoring';

interface TimelineChartProps {
  trajectory: TrajectoryPoint[];
  title?: string;
  subtitle?: string;
}

interface ChartRow {
  window: string;
  label: string;
  randomForest: number;
  xgboost: number;
  lightgbm: number;
  catboost: number;
  lstm: number;
}

// CREDIT-109 + CREDIT-115: 5-model family. Distinct hues so all 5 lines are readable.
const MODELS: { key: ModelKey; name: string; color: string }[] = [
  { key: 'randomForest', name: 'Random Forest', color: '#34d399' },
  { key: 'xgboost', name: 'XGBoost', color: '#60a5fa' },
  { key: 'lightgbm', name: 'LightGBM', color: '#fbbf24' },
  { key: 'catboost', name: 'CatBoost', color: '#a78bfa' },
  { key: 'lstm', name: 'LSTM', color: '#f472b6' },
];

// Flatten the contract trajectory into Recharts-friendly rows (one row per window,
// model PDs hoisted to top-level keys). Exported so tests can assert "4 points/model"
// deterministically without depending on SVG rendering in jsdom.
export const buildChartData = (trajectory: TrajectoryPoint[]): ChartRow[] =>
  trajectory.map((point) => ({
    window: point.window,
    label: point.label ?? point.window,
    randomForest: point.predictions.randomForest,
    xgboost: point.predictions.xgboost,
    lightgbm: point.predictions.lightgbm,
    catboost: point.predictions.catboost,
    lstm: point.predictions.lstm,
  }));

const TimelineChart = ({
  trajectory,
  title = 'PD Trajectory',
  subtitle = 'Probability of default across the four 3-month windows (W0 → W3)',
}: TimelineChartProps) => {
  const data = buildChartData(trajectory);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
    }}>
      <h3 style={{ margin: '0 0 4px 0', fontSize: '18px', fontWeight: 600, color: '#e2e8f0' }}>
        {title}
      </h3>
      <p style={{ margin: '0 0 20px 0', fontSize: '14px', color: '#94a3b8' }}>
        {subtitle}
      </p>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.25)" />
          <XAxis dataKey="label" tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} tickLine={false} />
          <YAxis type="number" domain={[0, 1]} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} tickLine={false} />
          <Tooltip
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: '#e2e8f0' }}
            labelStyle={{ color: '#e2e8f0', fontWeight: 600 }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Legend wrapperStyle={{ color: '#e2e8f0' }} />
          {MODELS.map((model) => (
            <Line
              key={model.key}
              type="monotone"
              dataKey={model.key}
              name={model.name}
              stroke={model.color}
              strokeWidth={2}
              dot={{ r: 4, fill: model.color }}
              activeDot={{ r: 6 }}
              isAnimationActive={!prefersReducedMotion}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TimelineChart;
