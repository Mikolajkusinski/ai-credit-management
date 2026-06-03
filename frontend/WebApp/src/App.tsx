import { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsDashboard from './components/ResultsDashboard';
import TimelineChart from './components/TimelineChart';
import TrendAlerts from './components/TrendAlerts';
import { PredictRequest, PredictResponse } from './types/prediction';
import { predictDefault } from './api/predictApi';
import { MOCK_TIMESERIES_RESPONSE } from './api/monitoringApi';

type Tab = 'prediction' | 'timeline';

function App() {
  const [tab, setTab] = useState<Tab>('prediction');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePredict = async (data: PredictRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await predictDefault(data);
      setResults(response);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Failed to get prediction. Please ensure the backend service is running.');
      } else {
        setError('Failed to get prediction. Please ensure the backend service is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(ellipse at top left, #1e1040 0%, #0f172a 55%, #0d1117 100%)',
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <header style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{
            fontSize: '36px',
            fontWeight: 700,
            color: '#f1f5f9',
            margin: '0 0 12px 0'
          }}>
            Credit Default Prediction
          </h1>
          <p style={{
            fontSize: '18px',
            color: '#94a3b8',
            margin: 0
          }}>
            AI-powered risk assessment using ensemble ML models
          </p>
        </header>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '12px',
          marginBottom: '32px'
        }}>
          {([
            { id: 'prediction', label: 'Prediction' },
            { id: 'timeline', label: 'Monitoring' },
          ] as { id: Tab; label: string }[]).map(({ id, label }) => {
            const active = tab === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => setTab(id)}
                style={{
                  padding: '10px 28px',
                  borderRadius: '9999px',
                  border: `1px solid ${active ? '#7c3aed' : 'rgba(255, 255, 255, 0.12)'}`,
                  backgroundColor: active ? '#7c3aed' : 'rgba(255, 255, 255, 0.05)',
                  color: active ? '#f1f5f9' : '#94a3b8',
                  fontSize: '15px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {label}
              </button>
            );
          })}
        </div>

        {tab === 'prediction' && (
          <>
            <InputForm onSubmit={handlePredict} loading={loading} />

            {error && (
              <div style={{
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.4)',
                color: '#fca5a5',
                padding: '16px',
                borderRadius: '12px',
                marginTop: '24px',
                textAlign: 'center'
              }}>
                {error}
              </div>
            )}

            {results && !loading && (
              <div style={{ marginTop: '24px' }}>
                <ResultsDashboard results={results} />
              </div>
            )}
          </>
        )}

        {tab === 'timeline' && (
          <div style={{ display: 'grid', gap: '24px' }}>
            <TimelineChart trajectory={MOCK_TIMESERIES_RESPONSE.trajectory} />
            <TrendAlerts trends={MOCK_TIMESERIES_RESPONSE.trends} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
