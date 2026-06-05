import { useState, useCallback } from 'react';
import { createRun } from '../api/client';

interface UseRunMutationResult {
  loading: boolean;
  error: string | null;
  success: boolean;
  runId: string | null;
  createRunFn: (goal: string, options?: { max_steps?: number; max_cost_usd?: number }) => Promise<void>;
  reset: () => void;
}

export function useRunMutation(): UseRunMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);

  const createRunFn = useCallback(async (goal: string, options?: { max_steps?: number; max_cost_usd?: number }) => {
    const trimmedGoal = goal.trim();
    if (!trimmedGoal) {
      setError('Goal cannot be empty.');
      return;
    }
    if (trimmedGoal.length > 4096) {
      setError('Goal must be 4096 characters or fewer.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);
    setRunId(null);

    try {
      const result = await createRun({
        goal: trimmedGoal,
        max_steps: options?.max_steps ?? null,
        max_cost_usd: options?.max_cost_usd ?? null,
      });
      setRunId(result.run_id);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create run.');
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setSuccess(false);
    setRunId(null);
  }, []);

  return { loading, error, success, runId, createRunFn, reset };
}
