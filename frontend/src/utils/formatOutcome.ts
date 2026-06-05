type TerminationReason = 'succeeded' | 'step_cap' | 'cost_cap' | 'stuck' | 'timeout' | 'error';

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
    default:
      return 'Run ended with an unknown status.';
  }
}
