import { useEffect, useRef, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { PredictResponse } from '../types/prediction';

interface ComparisonChartProps {
  results: PredictResponse;
}

const DURATION_MS = 2000;

const ComparisonChart = ({ results }: ComparisonChartProps) => {
  const targetData = [
    { name: 'Random Forest', probability: results.randomForest.defaultProbability },
    { name: 'XGBoost',       probability: results.xgboost.defaultProbability },
    { name: 'LSTM',          probability: results.lstm.defaultProbability }
  ].sort((a, b) => a.probability - b.probability);

  const [progress, setProgress] = useState(0);
  const rafRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (prefersReducedMotion) {
      setProgress(1);
      return;
    }

    setProgress(0);
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      if (startTimeRef.current === null) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const t = Math.min(elapsed / DURATION_MS, 1);
      // ease-out cubic — matches ProbabilityGauge
      setProgress(1 - Math.pow(1 - t, 3));
      if (t < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [results]);

  const animatedData = targetData.map(d => ({
    ...d,
    probability: d.probability * progress
  }));

  const getColor = (value: number) => {
    if (value < 0.3) return '#10b981';
    if (value < 0.6) return '#f59e0b';
    return '#ef4444';
  };

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
      <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#e2e8f0' }}>
        Model Comparison
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={animatedData} cursor={{ fill: 'rgba(255,255,255,0.05)' }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.25)" />
          <XAxis dataKey="name" tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} tickLine={false} />
          <YAxis type="number" domain={[0, 1]} tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`} tick={{ fill: '#e2e8f0', fontSize: 13 }} axisLine={{ stroke: 'rgba(255,255,255,0.3)' }} tickLine={false} />
          <Tooltip
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '8px', color: '#e2e8f0' }}
            labelStyle={{ color: '#e2e8f0', fontWeight: 600 }}
            itemStyle={{ color: '#e2e8f0' }}
          />
          <Bar dataKey="probability" isAnimationActive={false}>
            {animatedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(targetData[index].probability)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ComparisonChart;