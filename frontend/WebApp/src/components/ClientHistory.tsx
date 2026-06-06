import { useCallback, useEffect, useState } from 'react';
import { HistoryPoint, HistoryResponse, TrajectoryPoint } from '../types/monitoring';
import { PredictRequest } from '../types/prediction';
import { getClientHistory } from '../api/monitoringApi';
import TimelineChart from './TimelineChart';
import TrendAlerts from './TrendAlerts';
import SnapshotForm from './SnapshotForm';

interface ClientHistoryProps {
  clientRef: string;
  onBack: () => void;
}

// "2026-05-24" → "May 24" for the chart X axis (UTC-safe, no date library).
export const formatSnapshotLabel = (iso: string): string => {
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  if (!y || !m || !d) return iso;
  const month = new Date(Date.UTC(y, m - 1, d)).toLocaleString('en-US', {
    month: 'short',
    timeZone: 'UTC',
  });
  return `${month} ${d}`;
};

// Adapt the persisted snapshot timeline (calendar dates) onto the TimelineChart's trajectory shape.
// Each snapshot becomes one X point; the window id is the (unique, stable) snapshotId. Exported so
// tests can assert the mapping without rendering SVG.
export const historyToTrajectory = (history: HistoryPoint[]): TrajectoryPoint[] =>
  history.map((p) => ({
    window: String(p.snapshotId),
    label: formatSnapshotLabel(p.snapshotDate),
    predictions: p.predictions,
  }));

const card: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  borderRadius: '16px',
  padding: '24px',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
};

const ClientHistory = ({ clientRef, onBack }: ClientHistoryProps) => {
  const [data, setData] = useState<HistoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  // Session memory for SnapshotForm's "copy from previous" — the last features entered for this
  // client. (The history endpoint returns only PD values, not raw features, so we remember them here.)
  const [lastFeatures, setLastFeatures] = useState<PredictRequest | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getClientHistory(clientRef));
    } catch {
      setError('Could not load history. Please ensure the backend service is running.');
    } finally {
      setLoading(false);
    }
  }, [clientRef]);

  useEffect(() => {
    load();
  }, [load]);

  // Reset form visibility + copy-from-previous memory when switching clients.
  useEffect(() => {
    setShowForm(false);
    setLastFeatures(null);
  }, [clientRef]);

  const points = data ? historyToTrajectory(data.history) : [];

  return (
    <div style={{ display: 'grid', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
        <div style={{ minWidth: 0 }}>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '22px', fontWeight: 700, color: '#f1f5f9' }}>
            {clientRef}
          </h2>
          <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8' }}>
            {loading
              ? 'Loading…'
              : data
                ? `${data.history.length} snapshot${data.history.length === 1 ? '' : 's'} on record`
                : 'Client history'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexShrink: 0 }}>
          <button
            type="button"
            onClick={() => setShowForm((s) => !s)}
            style={{
              padding: '8px 20px',
              borderRadius: '9999px',
              border: `1px solid ${showForm ? '#7c3aed' : 'rgba(167, 139, 250, 0.4)'}`,
              backgroundColor: showForm ? 'rgba(124, 58, 237, 0.25)' : '#7c3aed',
              color: '#f1f5f9',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {showForm ? 'Close form' : '+ Add snapshot'}
          </button>
          <button
            type="button"
            onClick={onBack}
            style={{
              padding: '8px 20px',
              borderRadius: '9999px',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: '#e2e8f0',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ← Back to clients
          </button>
        </div>
      </div>

      {showForm && (
        <SnapshotForm
          clientRef={clientRef}
          previousFeatures={lastFeatures}
          onClose={() => setShowForm(false)}
          onSubmitted={(features) => {
            setLastFeatures(features);
            load();
          }}
        />
      )}

      {error && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          color: '#fca5a5',
          padding: '16px',
          borderRadius: '12px',
          textAlign: 'center',
        }}>
          {error}
        </div>
      )}

      {!loading && !error && data && data.history.length === 0 && (
        <div style={{ ...card, textAlign: 'center', color: '#94a3b8' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#e2e8f0', fontWeight: 600 }}>
            No snapshots for this client yet
          </p>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Submit a snapshot to start building the PD timeline.
          </p>
        </div>
      )}

      {!error && data && data.history.length > 0 && (
        <>
          <TimelineChart
            trajectory={points}
            title="PD History"
            subtitle="Probability of default across recorded snapshots (oldest → newest)"
          />
          <TrendAlerts trends={data.trends} />
        </>
      )}
    </div>
  );
};

export default ClientHistory;
