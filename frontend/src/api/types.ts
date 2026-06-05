export interface StepDetail {
  step_number: number;
  tool_name: string | null;
  args: Record<string, unknown> | null;
  result: Record<string, unknown>;
  cost: number;
  created_at: string | null;
}

export interface RunDetail {
  run_id: string;
  goal: string;
  status: 'running' | 'completed';
  reason: 'succeeded' | 'step_cap' | 'cost_cap' | 'stuck' | 'timeout' | 'error' | null;
  total_cost: number;
  max_steps: number;
  max_cost_usd: number;
  started_at: string | null;
  finished_at: string | null;
  steps: StepDetail[];
}

export interface RunSummary {
  run_id: string;
  goal: string;
  status: string;
  reason: string | null;
  total_cost: number;
  started_at: string | null;
  finished_at: string | null;
}

export interface RunListResponse {
  runs: RunSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface RunCreateRequest {
  goal: string;
  max_steps?: number | null;
  max_cost_usd?: number | null;
}

export interface RunCreateResponse {
  run_id: string;
}
