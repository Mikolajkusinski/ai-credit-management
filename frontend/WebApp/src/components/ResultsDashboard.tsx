import { PredictResponse } from '../types/prediction';
import ModelCard from './ModelCard';
import ComparisonChart from './ComparisonChart';

interface ResultsDashboardProps {
  results: PredictResponse;
}

const ResultsDashboard = ({ results }: ResultsDashboardProps) => {
  
  const defaultCount = [
    results.randomForest.prediction === 'DEFAULT',
    results.xgboost.prediction === 'DEFAULT',
    results.lstm.prediction === 'DEFAULT'
  ].filter(Boolean).length;

  const getRiskLevel = () => {
    if (defaultCount === 0) return { text: 'LOW', color: '#10b981' };
    if (defaultCount === 1) return { text: 'MODERATE', color: '#f59e0b' };
    if (defaultCount === 2) return { text: 'HIGH', color: '#f97316' };
    return { text: 'CRITICAL', color: '#ef4444' };
  };

  const risk = getRiskLevel();

  const sortedModels = [
    { modelName: 'Random Forest', prediction: results.randomForest, icon: '🌲' },
    { modelName: 'XGBoost',       prediction: results.xgboost,       icon: '🚀' },
    { modelName: 'LSTM',          prediction: results.lstm,           icon: '🧠' },
  ].sort((a, b) => a.prediction.defaultProbability - b.prediction.defaultProbability);

  return (
    <div style={{
      animation: 'fadeIn 0.5s ease-in',
      maxWidth: '1400px',
      margin: '0 auto'
    }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr) 2fr',
        gap: '24px',
        marginBottom: '24px',
        alignItems: 'stretch'
      }}>
        {sortedModels.map(({ modelName, prediction, icon }) => (
          <ModelCard key={modelName} modelName={modelName} prediction={prediction} icon={icon} />
        ))}
        <ComparisonChart results={results} />
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
        marginTop: '24px',
        textAlign: 'center'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 600, color: '#f1f5f9' }}>
          Risk Summary
        </h3>
        <p style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#94a3b8' }}>
          {defaultCount} out of 3 models predict default
        </p>
        <div style={{
          display: 'inline-block',
          backgroundColor: `${risk.color}20`,
          color: risk.color,
          padding: '12px 32px',
          borderRadius: '9999px',
          fontWeight: 700,
          fontSize: '20px'
        }}>
          OVERALL RISK: {risk.text}
        </div>
      </div>
    </div>
  );
};

export default ResultsDashboard;
