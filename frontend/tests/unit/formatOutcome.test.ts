import { describe, it, expect } from 'vitest';
import { describeOutcome } from '@/utils/formatOutcome';

describe('describeOutcome', () => {
  it('returns in-progress message for null reason', () => {
    expect(describeOutcome(null, 0, 0.5)).toBe('Run in progress...');
  });

  it('returns success message for succeeded', () => {
    expect(describeOutcome('succeeded', 0.12, 0.5)).toBe('Goal completed successfully.');
  });

  it('returns step limit message for step_cap', () => {
    expect(describeOutcome('step_cap', 0.45, 0.5)).toBe('Reached the step limit. Try a more specific goal.');
  });

  it('returns budget limit message for cost_cap with formatted cost', () => {
    expect(describeOutcome('cost_cap', 0.5, 0.5)).toBe('Reached the budget limit ($0.50). Try a simpler goal.');
  });

  it('returns stuck message', () => {
    expect(describeOutcome('stuck', 0.3, 0.5)).toBe('The agent kept repeating the same action. Try rephrasing the goal.');
  });

  it('returns timeout message', () => {
    expect(describeOutcome('timeout', 0.2, 0.5)).toBe('The run exceeded the time limit. Try a simpler goal.');
  });

  it('returns error message', () => {
    expect(describeOutcome('error', 0.1, 0.5)).toBe('An error occurred during the run.');
  });
});
