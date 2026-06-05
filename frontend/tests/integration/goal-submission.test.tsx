import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import App from '@/App';

const mockCreateRun = vi.hoisted(() => vi.fn());
const mockGetRun = vi.hoisted(() => vi.fn());
const mockGetRuns = vi.hoisted(() => vi.fn());
const mockGetScenarios = vi.hoisted(() => vi.fn().mockResolvedValue([]));

vi.mock('@/api/client', () => ({
  createRun: mockCreateRun,
  getRun: mockGetRun,
  getRuns: mockGetRuns,
  getScenarios: mockGetScenarios,
}));

function renderApp(initialEntries?: string[]) {
  return render(
    <MemoryRouter initialEntries={initialEntries ?? ['/']}>
      <App />
    </MemoryRouter>
  );
}

describe('Goal submission flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows the home page with goal input and run list', () => {
    mockGetRuns.mockResolvedValue({ runs: [], total: 0, limit: 20, offset: 0 });

    renderApp();

    expect(screen.getByText('ElevateIQ Agent')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('What would you like the agent to do?')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit goal/i })).toBeInTheDocument();
  });

  it('disables submit button when input is empty', () => {
    mockGetRuns.mockResolvedValue({ runs: [], total: 0, limit: 20, offset: 0 });

    renderApp();

    expect(screen.getByRole('button', { name: /submit goal/i })).toBeDisabled();
  });

  it('submits a goal and navigates to run detail', async () => {
    const user = userEvent.setup();

    mockGetRuns.mockResolvedValue({ runs: [], total: 0, limit: 20, offset: 0 });
    mockCreateRun.mockResolvedValue({ run_id: 'test-run-123' });
    mockGetRun.mockResolvedValue({
      run_id: 'test-run-123',
      goal: 'Test goal',
      status: 'completed',
      reason: 'succeeded',
      total_cost: 0.1,
      max_steps: 20,
      max_cost_usd: 0.5,
      started_at: '2024-01-01T00:00:00Z',
      finished_at: '2024-01-01T00:01:00Z',
      steps: [
        {
          step_number: 1,
          tool_name: 'search_documents',
          args: { query: 'test' },
          result: { ok: true, data: 'found' },
          cost: 0.05,
          created_at: '2024-01-01T00:00:30Z',
        },
        {
          step_number: 2,
          tool_name: null,
          args: null,
          result: { ok: true, data: 'The answer is 42' },
          cost: 0.05,
          created_at: '2024-01-01T00:01:00Z',
        },
      ],
    });

    renderApp();

    const input = screen.getByPlaceholderText('What would you like the agent to do?');
    await user.type(input, 'Test goal');
    await user.click(screen.getByRole('button', { name: /submit goal/i }));

    await waitFor(() => {
      expect(mockCreateRun).toHaveBeenCalledWith({
        goal: 'Test goal',
        max_steps: null,
        max_cost_usd: null,
        scenario: null,
      });
    });

    await waitFor(() => {
      expect(screen.getByText('Test goal')).toBeInTheDocument();
    });
  });

  it('shows run detail with steps and final answer', async () => {
    mockGetRun.mockResolvedValue({
      run_id: 'test-run-123',
      goal: 'Find the Q3 report',
      status: 'completed',
      reason: 'succeeded',
      total_cost: 0.15,
      max_steps: 20,
      max_cost_usd: 0.5,
      started_at: '2024-01-01T00:00:00Z',
      finished_at: '2024-01-01T00:01:00Z',
      steps: [
        {
          step_number: 1,
          tool_name: 'search_documents',
          args: { query: 'Q3 report' },
          result: { ok: true, data: 'found' },
          cost: 0.05,
          created_at: '2024-01-01T00:00:30Z',
        },
        {
          step_number: 2,
          tool_name: null,
          args: null,
          result: { ok: true, data: 'The Q3 report shows revenue growth of 15%' },
          cost: 0.05,
          created_at: '2024-01-01T00:01:00Z',
        },
      ],
    });

    renderApp(['/runs/test-run-123']);

    await waitFor(() => {
      expect(screen.getByText('Find the Q3 report')).toBeInTheDocument();
    });

    expect(screen.getByText('Goal completed successfully.')).toBeInTheDocument();
  });

  it('shows error when run fetch fails', async () => {
    mockGetRun.mockRejectedValue(new Error('Network error'));

    renderApp(['/runs/invalid-id']);

    await waitFor(() => {
      expect(screen.getByText('Error loading run')).toBeInTheDocument();
    });
  });
});
