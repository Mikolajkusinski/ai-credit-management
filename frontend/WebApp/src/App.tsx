import { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsDashboard from './components/ResultsDashboard';
import { PredictRequest, PredictResponse } from './types/prediction';
import { predictDefault } from './api/predictApi';

function App() {
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
      backgroundColor: '#f3f4f6',
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
            color: '#1f2937',
            margin: '0 0 12px 0'
          }}>
            Credit Default Prediction
          </h1>
          <p style={{
            fontSize: '18px',
            color: '#6b7280',
            margin: 0
          }}>
            AI-powered risk assessment using ensemble ML models
          </p>
        </header>

        <InputForm onSubmit={handlePredict} loading={loading} />

        {error && (
          <div style={{
            backgroundColor: '#fee2e2',
            border: '1px solid #fca5a5',
            color: '#991b1b',
            padding: '16px',
            borderRadius: '12px',
            marginTop: '24px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        {results && !loading && (
          <div style={{ marginTop: '40px' }}>
            <ResultsDashboard results={results} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
