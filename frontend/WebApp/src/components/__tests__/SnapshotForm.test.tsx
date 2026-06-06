import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SnapshotForm from '../SnapshotForm';
import { DEFAULT_FEATURES } from '../InputForm';
import { createSnapshot } from '../../api/monitoringApi';
import type { CreateSnapshotResponse } from '../../types/monitoring';

vi.mock('../../api/monitoringApi', () => ({
  createSnapshot: vi.fn(),
}));

const mockedCreate = vi.mocked(createSnapshot);

const okResponse: CreateSnapshotResponse = {
  snapshotId: 42,
  clientRef: 'alpha',
  snapshotDate: '2026-06-03',
  trajectory: [],
  trends: {
    randomForest: { slope: 0.1, alert: 'STABLE' },
    xgboost: { slope: 0.1, alert: 'STABLE' },
    lightgbm: { slope: 0.1, alert: 'STABLE' },
    catboost: { slope: 0.1, alert: 'STABLE' },
    lstm: { slope: 0.1, alert: 'STABLE' },
  },
  persisted: { clientCreated: false, predictionIds: [1, 2, 3, 4, 5], trendIds: [6, 7, 8, 9, 10] },
};

describe('SnapshotForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders the date input and disables "Copy from previous" with no prior snapshot', () => {
    render(
      <SnapshotForm
        clientRef="alpha"
        previousFeatures={null}
        onSubmitted={() => {}}
        onClose={() => {}}
      />,
    );

    expect(screen.getByLabelText(/snapshot date/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /copy from previous/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Add snapshot' })).toBeInTheDocument();
  });

  it('enables "Copy from previous" when prior features exist', () => {
    render(
      <SnapshotForm
        clientRef="alpha"
        previousFeatures={DEFAULT_FEATURES}
        onSubmitted={() => {}}
        onClose={() => {}}
      />,
    );

    expect(screen.getByRole('button', { name: /copy from previous/i })).toBeEnabled();
  });

  it('posts the snapshot and reports success', async () => {
    mockedCreate.mockResolvedValue(okResponse);
    const onSubmitted = vi.fn();
    render(
      <SnapshotForm
        clientRef="alpha"
        previousFeatures={null}
        onSubmitted={onSubmitted}
        onClose={() => {}}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Add snapshot' }));

    await waitFor(() => expect(onSubmitted).toHaveBeenCalledWith(DEFAULT_FEATURES));
    expect(mockedCreate).toHaveBeenCalledWith(
      'alpha',
      expect.objectContaining({
        features: DEFAULT_FEATURES,
        snapshotDate: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      }),
    );
  });

  it('shows a conflict message on 409', async () => {
    const conflict = Object.assign(new Error('conflict'), {
      isAxiosError: true,
      response: { status: 409, data: { error: { code: 'CONFLICT', message: 'dup' } } },
    });
    mockedCreate.mockRejectedValue(conflict);
    const onSubmitted = vi.fn();
    render(
      <SnapshotForm
        clientRef="alpha"
        previousFeatures={null}
        onSubmitted={onSubmitted}
        onClose={() => {}}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: 'Add snapshot' }));

    expect(await screen.findByText(/already exists for this date/i)).toBeInTheDocument();
    expect(onSubmitted).not.toHaveBeenCalled();
  });

  it('calls onClose from the Cancel button', () => {
    const onClose = vi.fn();
    render(
      <SnapshotForm
        clientRef="alpha"
        previousFeatures={null}
        onSubmitted={() => {}}
        onClose={onClose}
      />,
    );

    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalled();
  });
});
