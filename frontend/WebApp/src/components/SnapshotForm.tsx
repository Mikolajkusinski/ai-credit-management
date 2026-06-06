import { useState } from 'react';
import axios from 'axios';
import { PredictRequest } from '../types/prediction';
import { createSnapshot } from '../api/monitoringApi';
import InputForm, { DEFAULT_FEATURES } from './InputForm';

interface SnapshotFormProps {
  clientRef: string;
  previousFeatures: PredictRequest | null; // session memory for "copy from previous"
  onSubmitted: (features: PredictRequest) => void; // parent updates memory + reloads history
  onClose: () => void;
}

// Today as ISO yyyy-mm-dd in local time (matches the native date input + backend default).
const todayISO = (): string => {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mm}-${dd}`;
};

// "yyyy-mm-dd" → local Date (day 1 of that month is enough for month-label anchoring).
const parseLocalDate = (iso: string): Date => {
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  if (!y || !m || !d) return new Date();
  return new Date(y, m - 1, d);
};

// Map an API failure to a user-facing message. Backend uses the ErrorEnvelope shape
// { error: { code, message } } (contract 3.6); we lead with HTTP status and fall back to it.
const messageForError = (err: unknown): string => {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    const apiMessage = (err.response?.data as { error?: { message?: string } } | undefined)?.error
      ?.message;
    if (status === 409) return 'A snapshot already exists for this date.';
    if (status === 400) return apiMessage ?? 'Some inputs are invalid. Please review the form.';
    if (status === 502) return 'The ML service returned an error. Please try again.';
    if (status === 503) return 'The ML service is unavailable. Please ensure it is running.';
  }
  return 'Could not save the snapshot. Please ensure the backend service is running.';
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

const pillButton: React.CSSProperties = {
  padding: '8px 20px',
  borderRadius: '9999px',
  border: '1px solid rgba(255, 255, 255, 0.12)',
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  color: '#e2e8f0',
  fontSize: '14px',
  fontWeight: 600,
  cursor: 'pointer',
  flexShrink: 0,
};

const SnapshotForm = ({ clientRef, previousFeatures, onSubmitted, onClose }: SnapshotFormProps) => {
  const [snapshotDate, setSnapshotDate] = useState<string>(todayISO());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // `seed` remounts InputForm so it re-initialises from `initialValues` (used by copy-from-previous).
  const [initialValues, setInitialValues] = useState<PredictRequest>(DEFAULT_FEATURES);
  const [seed, setSeed] = useState(0);

  const copyFromPrevious = () => {
    if (!previousFeatures) return;
    setInitialValues(previousFeatures);
    setSeed((s) => s + 1);
  };

  const handleAdd = async (features: PredictRequest) => {
    setSubmitting(true);
    setError(null);
    try {
      await createSnapshot(clientRef, { snapshotDate, features });
      onSubmitted(features);
    } catch (err) {
      setError(messageForError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'grid', gap: '16px' }}>
      <div style={{ ...card, display: 'grid', gap: '16px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '16px',
            flexWrap: 'wrap',
          }}
        >
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9' }}>
            Add snapshot
          </h3>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              type="button"
              onClick={copyFromPrevious}
              disabled={!previousFeatures}
              style={{
                ...pillButton,
                cursor: previousFeatures ? 'pointer' : 'not-allowed',
                opacity: previousFeatures ? 1 : 0.5,
              }}
            >
              Copy from previous
            </button>
            <button type="button" onClick={onClose} style={pillButton}>
              Cancel
            </button>
          </div>
        </div>

        <div style={{ maxWidth: '260px' }}>
          <label
            htmlFor="snapshotDate"
            style={{
              display: 'block',
              marginBottom: '6px',
              fontSize: '14px',
              fontWeight: 500,
              color: '#94a3b8',
            }}
          >
            Snapshot date
          </label>
          <input
            id="snapshotDate"
            type="date"
            value={snapshotDate}
            max={todayISO()}
            onChange={(e) => setSnapshotDate(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: '6px',
              fontSize: '14px',
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              color: '#f1f5f9',
              height: '38px',
              boxSizing: 'border-box',
              colorScheme: 'dark',
            }}
          />
        </div>

        {error && (
          <div
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#fca5a5',
              padding: '12px 16px',
              borderRadius: '12px',
            }}
          >
            {error}
          </div>
        )}
      </div>

      <InputForm
        key={seed}
        initialValues={initialValues}
        referenceDate={parseLocalDate(snapshotDate)}
        submitLabel="Add snapshot"
        submittingLabel="Saving…"
        loading={submitting}
        onSubmit={handleAdd}
      />
    </div>
  );
};

export default SnapshotForm;
