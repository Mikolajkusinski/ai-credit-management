import { useCallback, useEffect, useState } from 'react';
import { AlertType, ClientSummary } from '../types/monitoring';
import { listClients } from '../api/monitoringApi';

interface ClientListProps {
  onSelect: (clientRef: string) => void;
}

const ALERT_BADGE: Record<AlertType, { color: string; label: string; icon: string }> = {
  INCREASING_RISK: { color: '#ef4444', label: 'Increasing risk', icon: '↑' },
  DECREASING_RISK: { color: '#10b981', label: 'Decreasing risk', icon: '↓' },
  STABLE: { color: '#94a3b8', label: 'Stable', icon: '→' },
};

const card: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(12px)',
  WebkitBackdropFilter: 'blur(12px)',
  borderRadius: '16px',
  padding: '24px',
  border: '1px solid rgba(255, 255, 255, 0.08)',
  boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
};

// "2026-05-24" → "May 24, 2026" without pulling in a date library or risking a TZ shift.
const formatDate = (iso?: string | null): string => {
  if (!iso) return '—';
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  if (!y || !m || !d) return iso;
  const month = new Date(Date.UTC(y, m - 1, d)).toLocaleString('en-US', {
    month: 'short',
    timeZone: 'UTC',
  });
  return `${month} ${d}, ${y}`;
};

const ClientList = ({ onSelect }: ClientListProps) => {
  const [clients, setClients] = useState<ClientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listClients();
      setClients(data.clients);
    } catch {
      setError('Could not load clients. Please ensure the backend service is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div style={{ display: 'grid', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '22px', fontWeight: 700, color: '#f1f5f9' }}>
            Monitored clients
          </h2>
          <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8' }}>
            {loading ? 'Loading…' : `${clients.length} client${clients.length === 1 ? '' : 's'} with persisted history`}
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={loading}
          style={{
            padding: '8px 20px',
            borderRadius: '9999px',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            color: '#e2e8f0',
            fontSize: '14px',
            fontWeight: 600,
            cursor: loading ? 'default' : 'pointer',
            opacity: loading ? 0.6 : 1,
          }}
        >
          Refresh
        </button>
      </div>

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

      {!loading && !error && clients.length === 0 && (
        <div style={{ ...card, textAlign: 'center', color: '#94a3b8' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#e2e8f0', fontWeight: 600 }}>
            No clients yet
          </p>
          <p style={{ margin: 0, fontSize: '14px' }}>
            Submit a snapshot via <code>POST /api/v1/monitoring/clients/&#123;ref&#125;/snapshots</code> and it
            will appear here.
          </p>
        </div>
      )}

      {!error && clients.length > 0 && (
        <div style={{ display: 'grid', gap: '12px' }}>
          {clients.map((c) => {
            const badge = ALERT_BADGE[c.latestAlert] ?? ALERT_BADGE.STABLE;
            return (
              <button
                key={c.clientRef}
                type="button"
                onClick={() => onSelect(c.clientRef)}
                style={{
                  ...card,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '16px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  width: '100%',
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: '17px', fontWeight: 600, color: '#f1f5f9', marginBottom: '4px' }}>
                    {c.clientRef}
                  </div>
                  <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                    {c.snapshotCount} snapshot{c.snapshotCount === 1 ? '' : 's'} · latest {formatDate(c.latestSnapshotDate)}
                  </div>
                </div>
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  backgroundColor: `${badge.color}26`,
                  color: badge.color,
                  padding: '6px 14px',
                  borderRadius: '9999px',
                  fontWeight: 600,
                  fontSize: '13px',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                }}>
                  <span aria-hidden="true">{badge.icon}</span>
                  {badge.label}
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ClientList;
