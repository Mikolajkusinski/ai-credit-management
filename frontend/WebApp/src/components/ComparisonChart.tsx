import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { PredictResponse } from '../types/prediction';

interface ComparisonChartProps {
  results: PredictResponse;
}

const ComparisonChart = ({ results }: ComparisonChartProps) => {
  const data = [
    { name: 'Random Forest', probability: results.randomForest.defaultProbability },
    { name: 'XGBoost', probability: results.xgboost.defaultProbability },
    { name: 'LSTM', probability: results.lstm.defaultProbability }
  ];

  const getColor = (value: number) => {
    if (value < 0.3) return '#10b981';
    if (value < 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
    }}>
      <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
        Model Comparison
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={[0, 1]} />
          <YAxis dataKey="name" type="category" width={120} />
          <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
          <Bar dataKey="probability">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.probability)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ComparisonChart;
