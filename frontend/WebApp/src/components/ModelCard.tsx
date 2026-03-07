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
      backgroundColor: 'white',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '16px'
    }}>
      <div style={{ fontSize: '32px' }}>{icon}</div>
      <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
        {modelName}
      </h3>
      <ProbabilityGauge probability={prediction.defaultProbability} />
      <div style={{
        backgroundColor: isDefault ? '#fee2e2' : '#d1fae5',
        color: isDefault ? '#991b1b' : '#065f46',
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
