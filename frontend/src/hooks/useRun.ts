import { useCallback, useEffect, useRef, useState } from 'react';
import { getRun } from '../api/client';

interface UseRunResult {
  run: {
    run_id: string;
    goal: string;
    status: string;
    reason: string | null;
    total_cost: number;
    max_steps: number;
    max_cost_usd: number;
    started_at: string | null;
    finished_at: string | null;
    steps: Array<{
      step_number: number;
      tool_name: string | null;
      args: Record<string, unknown> | null;
      result: Record<string, unknown>;
      cost: number;
      created_at: string | null;
    }>;
  } | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

const POLL_INTERVAL = 1500;

export function useRun(runId: string): UseRunResult {
  const [run, setRun] = useState<UseRunResult['run']>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchRun = useCallback(async () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }

    abortRef.current = new AbortController();

    try {
      const data = await getRun(runId);
      setRun(data);
      setError(null);
      setLoading(false);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch run.';
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setError(message);
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => {
    let mounted = true;

    const poll = async () => {
      if (!mounted) return;
      const data = await fetchRun();
      if (data?.status === 'running') {
        const timer = setTimeout(() => {
          if (mounted) poll();
        }, POLL_INTERVAL);
        return () => clearTimeout(timer);
      }
    };

    poll();

    return () => {
      mounted = false;
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
  }, [fetchRun]);

  const refetch = useCallback(async () => {
    setLoading(true);
    await fetchRun();
  }, [fetchRun]);

  return { run, loading, error, refetch };
}
