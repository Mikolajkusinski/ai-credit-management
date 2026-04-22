import { useEffect, useState, useRef } from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

interface ProbabilityGaugeProps {
  probability: number;
}

const DURATION_MS = 2000;

const ProbabilityGauge = ({ probability }: ProbabilityGaugeProps) => {
  const targetPercentage = probability * 100;
  const [displayed, setDisplayed] = useState(0);
  const rafRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);

  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (prefersReducedMotion) {
      setDisplayed(targetPercentage);
      return;
    }

    setDisplayed(0);
    startTimeRef.current = null;

    const animate = (timestamp: number) => {
      if (startTimeRef.current === null) startTimeRef.current = timestamp;
      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / DURATION_MS, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(eased * targetPercentage);
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [targetPercentage]);

  const getColor = () => {
    if (probability < 0.3) return '#10b981';
    if (probability < 0.6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div style={{ width: 180, height: 180 }}>
      <CircularProgressbar
        value={displayed}
        text={`${displayed.toFixed(1)}%`}
        styles={buildStyles({
          textColor: getColor(),
          pathColor: getColor(),
          trailColor: 'rgba(255,255,255,0.1)',
          textSize: '20px',
          pathTransitionDuration: 0,
        })}
      />
    </div>
  );
};

export default ProbabilityGauge;