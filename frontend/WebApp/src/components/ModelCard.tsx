import { ModelPrediction } from '../types/prediction';
import ProbabilityGauge from './ProbabilityGauge';

interface ModelCardProps {
  modelName: string;
  prediction: ModelPrediction;
  icon: string;
}

const ModelCard = ({ modelName, prediction, icon }: ModelCardProps) => {
  const isDefault = prediction.prediction === 'DEFAULT';

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'space-between',
      minHeight: '280px'
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
        <div style={{ fontSize: '32px' }}>{icon}</div>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9' }}>
          {modelName}
        </h3>
      </div>
      <ProbabilityGauge probability={prediction.defaultProbability} />
      <div style={{
        backgroundColor: isDefault ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)',
        color: isDefault ? '#fca5a5' : '#6ee7b7',
        border: `1px solid ${isDefault ? 'rgba(239,68,68,0.35)' : 'rgba(16,185,129,0.35)'}`,
        padding: '8px 16px',
        borderRadius: '9999px',
        fontWeight: 600,
        fontSize: '14px'
      }}>
        {prediction.prediction}
      </div>
    </div>
  );
};

export default ModelCard;
