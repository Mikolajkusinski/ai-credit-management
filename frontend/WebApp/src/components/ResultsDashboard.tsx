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

  return (
    <div style={{
      animation: 'fadeIn 0.5s ease-in',
      maxWidth: '1200px',
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
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        <ModelCard
          modelName="Random Forest"
          prediction={results.randomForest}
          icon="🌲"
        />
        <ModelCard
          modelName="XGBoost"
          prediction={results.xgboost}
          icon="🚀"
        />
        <ModelCard
          modelName="LSTM"
          prediction={results.lstm}
          icon="🧠"
        />
      </div>

      <ComparisonChart results={results} />

      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        marginTop: '24px',
        textAlign: 'center'
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          Risk Summary
        </h3>
        <p style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#6b7280' }}>
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
