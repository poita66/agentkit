import { useState, useEffect, useCallback } from 'react';
import { getRuns } from '../api/client';

interface RunSummary {
  run_id: string;
  goal: string;
  status: string;
  reason: string | null;
  total_cost: number;
  started_at: string | null;
  finished_at: string | null;
}

interface UseRunsResult {
  runs: RunSummary[];
  total: number;
  loading: boolean;
  error: string | null;
  limit: number;
  offset: number;
  loadMore: () => Promise<void>;
  refetch: () => Promise<void>;
}

export function useRuns(limit = 20): UseRunsResult {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  const fetchRuns = useCallback(async (offsetVal = 0, append = false) => {
    try {
      const data = await getRuns(limit, offsetVal);
      if (append) {
        setRuns(prev => [...prev, ...data.runs]);
      } else {
        setRuns(data.runs);
      }
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch runs.');
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    setOffset(0);
    fetchRuns(0, false);
  }, [fetchRuns]);

  const loadMore = useCallback(async () => {
    const nextOffset = offset + limit;
    if (nextOffset >= total) return;
    setOffset(nextOffset);
    await fetchRuns(nextOffset, true);
  }, [offset, limit, total, fetchRuns]);

  const refetch = useCallback(async () => {
    setLoading(true);
    setOffset(0);
    await fetchRuns(0, false);
  }, [fetchRuns]);

  return { runs, total, loading, error, limit, offset, loadMore, refetch };
}
