import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useRun } from '@/hooks/useRun';

const mockGetRun = vi.hoisted(() => vi.fn());
vi.mock('@/api/client', () => ({
  getRun: mockGetRun,
}));

const runningRun = {
  run_id: 'test-123',
  goal: 'Test goal',
  status: 'running',
  reason: null,
  total_cost: 0.1,
  max_steps: 20,
  max_cost_usd: 0.5,
  started_at: '2024-01-01T00:00:00Z',
  finished_at: null,
  steps: [],
};

const completedRun = {
  ...runningRun,
  status: 'completed',
  reason: 'succeeded',
  finished_at: '2024-01-01T00:01:00Z',
  steps: [{
    step_number: 1,
    tool_name: 'search_documents',
    args: { query: 'test' },
    result: { ok: true, data: 'found' },
    cost: 0.05,
    created_at: '2024-01-01T00:00:30Z',
  }],
};

describe('useRun', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('fetches run data on mount', async () => {
    mockGetRun.mockResolvedValueOnce(runningRun);

    const { result } = renderHook(() => useRun('test-123'));

    expect(result.current.loading).toBe(true);

    await act(async () => {
      await Promise.resolve();
    });

    expect(mockGetRun).toHaveBeenCalledWith('test-123');
    expect(result.current.run).toEqual(runningRun);
    expect(result.current.loading).toBe(false);
  });

  it('polls while status is running', async () => {
    mockGetRun
      .mockResolvedValueOnce({ ...runningRun, steps: [] })
      .mockResolvedValueOnce({ ...runningRun, steps: [{ step_number: 1, tool_name: 'search_documents', args: { query: 'test' }, result: { ok: true }, cost: 0.05, created_at: '2024-01-01T00:00:30Z' }] });

    const { result } = renderHook(() => useRun('test-123'));

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.run?.steps.length).toBe(0);

    await act(async () => {
      vi.advanceTimersByTime(1500);
      await Promise.resolve();
    });

    expect(result.current.run?.steps.length).toBe(1);
    expect(mockGetRun).toHaveBeenCalledTimes(2);
  });

  it('stops polling when status is completed', async () => {
    mockGetRun
      .mockResolvedValueOnce(runningRun)
      .mockResolvedValueOnce(completedRun);

    const { result } = renderHook(() => useRun('test-123'));

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.run?.status).toBe('running');

    await act(async () => {
      vi.advanceTimersByTime(1500);
      await Promise.resolve();
    });

    expect(result.current.run?.status).toBe('completed');
    expect(result.current.run?.reason).toBe('succeeded');
    expect(mockGetRun).toHaveBeenCalledTimes(2);

    await act(async () => {
      vi.advanceTimersByTime(2000);
      await Promise.resolve();
    });

    expect(mockGetRun).toHaveBeenCalledTimes(2);
  });

  it('handles fetch errors', async () => {
    mockGetRun.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useRun('test-123'));

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.loading).toBe(false);
  });

  it('refetches data on demand', async () => {
    mockGetRun
      .mockResolvedValueOnce(runningRun)
      .mockResolvedValueOnce(completedRun);

    const { result } = renderHook(() => useRun('test-123'));

    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.run?.status).toBe('running');

    await act(async () => {
      await result.current.refetch();
    });

    expect(result.current.run?.status).toBe('completed');
    expect(mockGetRun).toHaveBeenCalledTimes(2);
  });
});
