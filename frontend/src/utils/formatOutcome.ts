type TerminationReason = 'succeeded' | 'step_cap' | 'cost_cap' | 'stuck' | 'timeout' | 'error' | 'tool_errors';

export function describeOutcome(
  reason: TerminationReason | null,
  _totalCost: number,
  maxCostUsd: number,
): string {
  if (!reason) return 'Run in progress...';

  switch (reason) {
    case 'succeeded':
      return 'Goal completed successfully.';
    case 'step_cap':
      return `Reached the step limit. Try a more specific goal.`;
    case 'cost_cap':
      return `Reached the budget limit ($${maxCostUsd.toFixed(2)}). Try a simpler goal.`;
    case 'stuck':
      return 'The agent kept repeating the same action. Try rephrasing the goal.';
    case 'timeout':
      return 'The run exceeded the time limit. Try a simpler goal.';
    case 'error':
      return 'An error occurred during the run.';
    case 'tool_errors':
      return 'The agent hit too many consecutive tool errors. Try a different goal.';
    default:
      return 'Run ended with an unknown status.';
  }
}
