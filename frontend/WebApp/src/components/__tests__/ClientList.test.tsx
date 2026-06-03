import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ClientList from '../ClientList';
import { listClients } from '../../api/monitoringApi';
import type { ClientListResponse } from '../../types/monitoring';

vi.mock('../../api/monitoringApi', () => ({
  listClients: vi.fn(),
}));

const mockedListClients = vi.mocked(listClients);

const twoClients: ClientListResponse = {
  clients: [
    {
      clientRef: 'alpha',
      createdAt: '2026-05-01T00:00:00Z',
      snapshotCount: 3,
      latestSnapshotDate: '2026-05-24',
      latestAlert: 'INCREASING_RISK',
    },
    {
      clientRef: 'beta',
      createdAt: '2026-05-02T00:00:00Z',
      snapshotCount: 1,
      latestSnapshotDate: '2026-04-15',
      latestAlert: 'STABLE',
    },
  ],
};

describe('ClientList', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renders a row per client with stats and an alert badge', async () => {
    mockedListClients.mockResolvedValue(twoClients);
    render(<ClientList onSelect={() => {}} />);

    expect(await screen.findByText('alpha')).toBeInTheDocument();
    expect(screen.getByText('beta')).toBeInTheDocument();
    // Roll-up badges, one per client.
    expect(screen.getByText(/increasing risk/i)).toBeInTheDocument();
    expect(screen.getByText(/stable/i)).toBeInTheDocument();
    // Latest snapshot date + count are formatted for display.
    expect(screen.getByText(/3 snapshots · latest May 24, 2026/)).toBeInTheDocument();
  });

  it('calls onSelect with the client ref when a row is clicked', async () => {
    mockedListClients.mockResolvedValue(twoClients);
    const onSelect = vi.fn();
    render(<ClientList onSelect={onSelect} />);

    fireEvent.click(await screen.findByText('alpha'));
    expect(onSelect).toHaveBeenCalledWith('alpha');
  });

  it('shows an empty state when there are no clients', async () => {
    mockedListClients.mockResolvedValue({ clients: [] });
    render(<ClientList onSelect={() => {}} />);

    expect(await screen.findByText(/no clients yet/i)).toBeInTheDocument();
  });

  it('shows an error message when the request fails', async () => {
    mockedListClients.mockRejectedValue(new Error('network'));
    render(<ClientList onSelect={() => {}} />);

    expect(await screen.findByText(/could not load clients/i)).toBeInTheDocument();
  });
});
