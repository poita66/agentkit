import { useState } from 'react';
import { ToolDefinition } from '../api/types';
import { describeStep } from '../utils/formatStep';
import { timeAgo } from '../utils/timeAgo';

interface StepDetail {
  step_number: number;
  tool_name: string | null;
  args: Record<string, unknown> | null;
  result: Record<string, unknown>;
  cost: number;
  created_at: string | null;
}

interface StepCardProps {
  step: StepDetail;
  stepNumber: number;
  tools?: ToolDefinition[];
}

export default function StepCard({ step, stepNumber, tools = [] }: StepCardProps) {
  const [expanded, setExpanded] = useState(false);
  const isFinalAnswer = step.tool_name === null;
  const summary = describeStep(step, tools);

  return (
    <article
      className={`step-card ${isFinalAnswer ? 'step-card--final' : ''}`}
      aria-label={isFinalAnswer ? 'Final answer' : `Step ${stepNumber}`}
    >
      <button
        type="button"
        className="step-card-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <span className="step-card-number">Step {stepNumber}</span>
        <span className="step-card-summary">{summary}</span>
        <span className="step-card-toggle" aria-hidden="true">
          {expanded ? '▾' : '▸'}
        </span>
      </button>

      {expanded && (
        <div className="step-card-details">
          {step.tool_name && (
            <div className="step-card-field">
              <span className="step-card-field-label">Tool</span>
              <code className="step-card-field-value">{step.tool_name}</code>
            </div>
          )}
          {step.args && (
            <div className="step-card-field">
              <span className="step-card-field-label">Arguments</span>
              <pre className="step-card-field-value">{JSON.stringify(step.args, null, 2)}</pre>
            </div>
          )}
          <div className="step-card-field">
            <span className="step-card-field-label">Result</span>
            <pre className="step-card-field-value">{JSON.stringify(step.result, null, 2)}</pre>
          </div>
          <div className="step-card-meta">
            <span>Cost: ${step.cost.toFixed(4)}</span>
            {step.created_at && <span>{timeAgo(step.created_at)}</span>}
          </div>
        </div>
      )}

      <style>{`
        .step-card {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-sm);
          background: var(--color-card-bg);
        }
        .step-card--final {
          border-color: var(--color-success);
          background: var(--color-success-bg);
        }
        .step-card-header {
          width: 100%;
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          background: none;
          border: none;
          text-align: left;
          cursor: pointer;
          font-family: inherit;
        }
        .step-card-header:hover {
          background: var(--color-card-hover);
        }
        .step-card-number {
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-text-muted);
          min-width: 50px;
        }
        .step-card-summary {
          flex: 1;
          font-size: 0.9375rem;
        }
        .step-card-toggle {
          color: var(--color-text-muted);
          font-size: 0.75rem;
        }
        .step-card-details {
          padding: 0 var(--spacing-md) var(--spacing-md);
          border-top: 1px solid var(--color-border);
        }
        .step-card-field {
          margin-top: var(--spacing-sm);
        }
        .step-card-field-label {
          display: block;
          font-size: 0.75rem;
          font-weight: 600;
          color: var(--color-text-muted);
          margin-bottom: var(--spacing-xs);
        }
        .step-card-field-value {
          font-family: var(--font-mono);
          font-size: 0.8125rem;
          background: var(--color-bg);
          padding: var(--spacing-sm);
          border-radius: var(--radius-sm);
          overflow-x: auto;
          white-space: pre-wrap;
          word-break: break-word;
        }
        .step-card-meta {
          display: flex;
          gap: var(--spacing-md);
          margin-top: var(--spacing-sm);
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
      `}</style>
    </article>
  );
}
