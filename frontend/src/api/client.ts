const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function createRun(request: {
  goal: string;
  max_steps?: number | null;
  max_cost_usd?: number | null;
}): Promise<{ run_id: string }> {
  return apiFetch('/runs', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function getRun(runId: string): Promise<{
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
}> {
  return apiFetch(`/runs/${runId}`);
}

export async function getRuns(
  limit = 20,
  offset = 0,
): Promise<{
  runs: Array<{
    run_id: string;
    goal: string;
    status: string;
    reason: string | null;
    total_cost: number;
    started_at: string | null;
    finished_at: string | null;
  }>;
  total: number;
  limit: number;
  offset: number;
}> {
  return apiFetch(`/runs?limit=${limit}&offset=${offset}`);
}

export async function getScenarios(): Promise<Array<{ name: string; description: string }>> {
  return apiFetch('/runs/scenarios');
}

export async function getTools(): Promise<Array<{
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}>> {
  return apiFetch('/runs/tools');
}
