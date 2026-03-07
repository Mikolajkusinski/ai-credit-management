import { useState } from 'react';
import { PredictRequest } from '../types/prediction';

interface InputFormProps {
  onSubmit: (data: PredictRequest) => void;
  loading: boolean;
}

const InputForm = ({ onSubmit, loading }: InputFormProps) => {
  const [formData, setFormData] = useState<PredictRequest>({
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
  });

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
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'white'
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '6px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#374151'
  };

  const sectionStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '24px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          Client Information
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
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

      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          Payment Status (Last 6 Months)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
          {['September', 'August', 'July', 'June', 'May', 'April'].map((month, idx) => {
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

      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          Bill Amounts (Last 6 Months, NT$)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
          {['September', 'August', 'July', 'June', 'May', 'April'].map((month, idx) => {
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

      <div style={sectionStyle}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 600, color: '#1f2937' }}>
          Payment Amounts (Last 6 Months, NT$)
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
          {['September', 'August', 'July', 'June', 'May', 'April'].map((month, idx) => {
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

      <button
        type="submit"
        disabled={loading}
        style={{
          width: '100%',
          padding: '16px',
          backgroundColor: loading ? '#9ca3af' : '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          fontSize: '18px',
          fontWeight: 600,
          cursor: loading ? 'not-allowed' : 'pointer',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}
      >
        {loading ? 'Predicting...' : 'Predict Default Risk'}
      </button>
    </form>
  );
};

export default InputForm;
