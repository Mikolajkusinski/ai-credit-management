import { useState } from 'react';
import { PredictRequest } from '../types/prediction';

interface InputFormProps {
  onSubmit: (data: PredictRequest) => void;
  loading: boolean;
  initialValues?: PredictRequest; // seed the 22 fields (e.g. copy-from-previous in SnapshotForm)
  referenceDate?: Date; // anchors the month labels; defaults to today
  submitLabel?: string;
  submittingLabel?: string;
}

// Sensible defaults for a fresh form. Exported so SnapshotForm can start from the same baseline.
export const DEFAULT_FEATURES: PredictRequest = {
  limitBal: 50000,
  sex: 2,
  education: 2,
  marriage: 1,
  age: 35,
  pay0: 0,
  pay2: 0,
  pay3: -1,
  pay4: 0,
  pay5: -1,
  pay6: -1,
  billAmt1: 40000,
  billAmt2: 38000,
  billAmt3: 35000,
  billAmt4: 33000,
  billAmt5: 30000,
  billAmt6: 28000,
  payAmt1: 2000,
  payAmt2: 1500,
  payAmt3: 1800,
  payAmt4: 1200,
  payAmt5: 1000,
  payAmt6: 900
};

// The 6 most recent calendar month names (newest → oldest) relative to `reference`.
// Index 0 = newest, maps to pay0 / billAmt1 / payAmt1; index 5 = oldest, maps to pay6 / billAmt6 /
// payAmt6. Building each date on day 1 avoids month-rollover bugs (e.g. setMonth on the 31st).
export const deriveMonthLabels = (reference: Date): string[] =>
  Array.from({ length: 6 }, (_, i) =>
    new Date(reference.getFullYear(), reference.getMonth() - i, 1).toLocaleString('en-US', {
      month: 'long',
    }),
  );

const InputForm = ({
  onSubmit,
  loading,
  initialValues,
  referenceDate,
  submitLabel = 'Predict Default Risk',
  submittingLabel = 'Predicting...',
}: InputFormProps) => {
  const [formData, setFormData] = useState<PredictRequest>(initialValues ?? DEFAULT_FEATURES);
  const months = deriveMonthLabels(referenceDate ?? new Date());

  const handleChange = (field: keyof PredictRequest, value: number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid rgba(255, 255, 255, 0.12)',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    color: '#f1f5f9',
    height: '38px',
    boxSizing: 'border-box' as const
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '6px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#94a3b8'
  };

  const sectionStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    borderRadius: '16px',
    padding: '24px',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)'
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>

        {/* Client Information */}
        <div style={sectionStyle}>
          <div style={{ height: '64px', marginBottom: '20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', textAlign: 'center' }}>
              Client Information
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={labelStyle}>Credit Limit (NT$)</label>
              <input
                type="number"
                value={formData.limitBal}
                onChange={(e) => handleChange('limitBal', Number(e.target.value))}
                style={inputStyle}
                required
              />
            </div>
            <div>
              <label style={labelStyle}>Sex</label>
              <select
                value={formData.sex}
                onChange={(e) => handleChange('sex', Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value={1}>Male</option>
                <option value={2}>Female</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Education</label>
              <select
                value={formData.education}
                onChange={(e) => handleChange('education', Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value={1}>Graduate School</option>
                <option value={2}>University</option>
                <option value={3}>High School</option>
                <option value={4}>Other</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Marital Status</label>
              <select
                value={formData.marriage}
                onChange={(e) => handleChange('marriage', Number(e.target.value))}
                style={inputStyle}
                required
              >
                <option value={1}>Married</option>
                <option value={2}>Single</option>
                <option value={3}>Other</option>
              </select>
            </div>
            <div>
              <label style={labelStyle}>Age</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => handleChange('age', Number(e.target.value))}
                style={inputStyle}
                required
              />
            </div>
          </div>
        </div>

        {/* Payment Status */}
        <div style={sectionStyle}>
          <div style={{ height: '64px', marginBottom: '20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', textAlign: 'center' }}>
              Payment Status<br />(Last 6 Months)
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {months.map((month, idx) => {
              const field = `pay${idx === 0 ? '0' : idx === 1 ? '2' : idx + 1}` as keyof PredictRequest;
              return (
                <div key={month}>
                  <label style={labelStyle}>{month}</label>
                  <select
                    value={formData[field]}
                    onChange={(e) => handleChange(field, Number(e.target.value))}
                    style={inputStyle}
                    required
                  >
                    <option value={-2}>No consumption</option>
                    <option value={-1}>Paid on time</option>
                    <option value={0}>Revolving credit</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(n => (
                      <option key={n} value={n}>{n} month{n > 1 ? 's' : ''} delay</option>
                    ))}
                  </select>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bill Amounts */}
        <div style={sectionStyle}>
          <div style={{ height: '64px', marginBottom: '20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', textAlign: 'center' }}>
              Bill Amounts<br />(Last 6 Months, NT$)
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {months.map((month, idx) => {
              const field = `billAmt${idx + 1}` as keyof PredictRequest;
              return (
                <div key={month}>
                  <label style={labelStyle}>{month}</label>
                  <input
                    type="number"
                    value={formData[field]}
                    onChange={(e) => handleChange(field, Number(e.target.value))}
                    style={inputStyle}
                    required
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Payment Amounts */}
        <div style={sectionStyle}>
          <div style={{ height: '64px', marginBottom: '20px', display: 'flex', alignItems: 'flex-start', justifyContent: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f1f5f9', whiteSpace: 'nowrap', textAlign: 'center' }}>
              Payment Amounts<br />(Last 6 Months, NT$)
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {months.map((month, idx) => {
              const field = `payAmt${idx + 1}` as keyof PredictRequest;
              return (
                <div key={month}>
                  <label style={labelStyle}>{month}</label>
                  <input
                    type="number"
                    value={formData[field]}
                    onChange={(e) => handleChange(field, Number(e.target.value))}
                    style={inputStyle}
                    required
                  />
                </div>
              );
            })}
          </div>
        </div>

      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          width: '100%',
          padding: '16px',
          backgroundColor: loading ? 'rgba(255,255,255,0.1)' : '#7c3aed',
          color: loading ? '#94a3b8' : 'white',
          border: loading ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(167,139,250,0.4)',
          borderRadius: '12px',
          fontSize: '18px',
          fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer',
          boxShadow: loading ? 'none' : '0 4px 24px rgba(124, 58, 237, 0.4)'
        }}
      >
        {loading ? submittingLabel : submitLabel}
      </button>
    </form>
  );
};

export default InputForm;
