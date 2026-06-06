import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import InputForm, { deriveMonthLabels, DEFAULT_FEATURES } from '../InputForm';

describe('deriveMonthLabels', () => {
  it('returns the 6 most recent calendar months, newest → oldest', () => {
    // Reference: 15 June 2026 → June back to January.
    expect(deriveMonthLabels(new Date(2026, 5, 15))).toEqual([
      'June',
      'May',
      'April',
      'March',
      'February',
      'January',
    ]);
  });

  it('crosses the year boundary without rollover bugs', () => {
    // Reference: 31 January 2026 → Jan back to August (day-1 construction avoids skipping Feb).
    expect(deriveMonthLabels(new Date(2026, 0, 31))).toEqual([
      'January',
      'December',
      'November',
      'October',
      'September',
      'August',
    ]);
  });
});

describe('InputForm', () => {
  it('renders the default submit label, overridable via props', () => {
    const { rerender } = render(<InputForm onSubmit={() => {}} loading={false} />);
    expect(screen.getByRole('button', { name: 'Predict Default Risk' })).toBeInTheDocument();

    rerender(<InputForm onSubmit={() => {}} loading={false} submitLabel="Add snapshot" />);
    expect(screen.getByRole('button', { name: 'Add snapshot' })).toBeInTheDocument();
  });

  it('submits the current feature values', () => {
    const onSubmit = vi.fn();
    render(<InputForm onSubmit={onSubmit} loading={false} />);

    fireEvent.click(screen.getByRole('button', { name: 'Predict Default Risk' }));
    expect(onSubmit).toHaveBeenCalledWith(DEFAULT_FEATURES);
  });

  it('labels the month fields from the reference date', () => {
    render(<InputForm onSubmit={() => {}} loading={false} referenceDate={new Date(2026, 5, 15)} />);
    // Each of the 3 monthly sections renders a "June" label → 3 occurrences.
    expect(screen.getAllByText('June')).toHaveLength(3);
  });
});
