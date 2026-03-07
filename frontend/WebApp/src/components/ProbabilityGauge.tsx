import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface ProbabilityGaugeProps {
  probability: number;
}

const ProbabilityGauge = ({ probability }: ProbabilityGaugeProps) => {
  const percentage = probability * 100;

  const getColor = () => {
    if (probability < 0.3) return '#10b981'; // green
    if (probability < 0.6) return '#f59e0b'; // amber
    return '#ef4444'; // red
  };

  return (
    <div style={{ width: 120, height: 120 }}>
      <CircularProgressbar
        value={percentage}
        text={`${percentage.toFixed(1)}%`}
        styles={buildStyles({
          textColor: getColor(),
          pathColor: getColor(),
          trailColor: '#e5e7eb',
          textSize: '16px',
        })}
      />
    </div>
  );
};

export default ProbabilityGauge;
