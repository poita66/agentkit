import { useEffect, useRef } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useRun } from '../hooks/useRun';
import { useTools } from '../hooks/useTools';
import { describeOutcome } from '../utils/formatOutcome';
import ErrorMessage from './ErrorMessage';
import StatusBadge from './StatusBadge';
import StepCard from './StepCard';

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const { run, loading, error, refetch } = useRun(runId!);
  const { tools } = useTools();
  const stepsEndRef = useRef<HTMLDivElement>(null);
  const prevStepCount = useRef(0);

  useEffect(() => {
    if (run && run.steps.length > prevStepCount.current) {
      const newSteps = run.steps.slice(prevStepCount.current);
      const hasNewFinalAnswer = newSteps.some((s) => s.tool_name === null);
      prevStepCount.current = run.steps.length;
      if (!hasNewFinalAnswer && stepsEndRef.current && typeof stepsEndRef.current.scrollIntoView === 'function') {
        stepsEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    }
    if (!run) {
      prevStepCount.current = 0;
    }
  }, [run]);

  if (loading) {
    return (
      <div className="run-detail run-detail--loading">
        <Link to="/" className="run-detail-back">
          ← Back to runs
        </Link>
        <div className="run-detail-loading" role="status">
          <div className="spinner" aria-hidden="true"></div>
          <p>Loading run...</p>
        </div>
        <style>{`
          .run-detail--loading {
            padding: var(--spacing-xl);
            max-width: 800px;
            margin: 0 auto;
          }
          .run-detail-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--spacing-md);
            padding: var(--spacing-xl) 0;
          }
          .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid var(--color-border);
            border-top-color: var(--color-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="run-detail">
        <Link to="/" className="run-detail-back">
          ← Back to runs
        </Link>
        <ErrorMessage
          title="Error loading run"
          message={error}
          onRetry={() => {
            if (error.includes('404') || error.includes('not found')) {
              navigate('/');
            } else {
              refetch();
            }
          }}
        />
      </div>
    );
  }

  if (!run) {
    return (
      <div className="run-detail">
        <Link to="/" className="run-detail-back">
          ← Back to runs
        </Link>
        <ErrorMessage
          title="Run not found"
          message="This run may have been deleted or the ID is invalid."
          onRetry={() => navigate('/')}
        />
      </div>
    );
  }

  const isRunning = run.status === 'running';
  const outcomeMessage = describeOutcome(
    run.reason as 'succeeded' | 'step_cap' | 'cost_cap' | 'stuck' | 'timeout' | 'error' | 'tool_errors' | null,
    run.total_cost,
    run.max_cost_usd,
  );

  // Extract the final answer from the last step where tool_name is null
  const finalStep = run.steps.find((s) => s.tool_name === null);
  const finalAnswer = finalStep?.result?.answer as string | undefined;
  const hasFinalAnswer = !isRunning && run.reason === 'succeeded' && finalAnswer;

  return (
    <div className="run-detail">
      <Link to="/" className="run-detail-back">
        ← Back to runs
      </Link>

      <header className="run-detail-header">
        <h1 className="run-detail-goal">{run.goal}</h1>
        <div className="run-detail-status">
          <StatusBadge reason={run.reason} status={run.status} />
          <span className="run-detail-cost">${run.total_cost.toFixed(4)}</span>
        </div>
      </header>

      {hasFinalAnswer && (
        <div className="run-detail-final-answer" role="region" aria-label="Final answer">
          <h2 className="run-detail-final-answer-label">Answer</h2>
          <p className="run-detail-final-answer-text">{finalAnswer}</p>
        </div>
      )}

      {!isRunning && run.reason && (
        <div className="run-detail-outcome" role="status">
          <p>{outcomeMessage}</p>
          <span className="run-detail-reason-code">{run.reason}</span>
        </div>
      )}

      {run.steps.length > 0 && (
        <div className="run-detail-steps">
          {run.steps.map((step) => (
            <StepCard key={step.step_number} step={step} stepNumber={step.step_number} tools={tools} />
          ))}
          <div ref={stepsEndRef} />
        </div>
      )}

      {isRunning && (
        <div className="run-detail-polling" role="status" aria-live="polite">
          <div className="spinner-small" aria-hidden="true"></div>
          <span>
            Processing... ({run.steps.length} step{run.steps.length !== 1 ? 's' : ''} so far)
          </span>
        </div>
      )}

      <style>{`
        .run-detail {
          padding: var(--spacing-xl);
          max-width: 800px;
          margin: 0 auto;
        }
        .run-detail-back {
          display: inline-block;
          margin-bottom: var(--spacing-md);
          font-size: 0.875rem;
          color: var(--color-text-muted);
        }
        .run-detail-back:hover {
          color: var(--color-primary);
        }
        .run-detail-header {
          margin-bottom: var(--spacing-lg);
        }
        .run-detail-goal {
          font-size: 1.5rem;
          margin-bottom: var(--spacing-sm);
        }
        .run-detail-status {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
        }
        .run-detail-cost {
          font-size: 0.875rem;
          color: var(--color-text-muted);
        }
        .run-detail-outcome {
          padding: var(--spacing-md);
          background: var(--color-card-bg);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-lg);
          border-left: 3px solid var(--color-primary);
        }
        .run-detail-final-answer {
          padding: var(--spacing-xl);
          background: var(--color-success-bg);
          border-radius: var(--radius-lg);
          margin-bottom: var(--spacing-lg);
          border: 2px solid var(--color-success);
          box-shadow: var(--shadow-md);
        }
        .run-detail-final-answer-label {
          font-size: 0.875rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--color-success);
          margin-bottom: var(--spacing-sm);
        }
        .run-detail-final-answer-text {
          font-size: 1.25rem;
          line-height: 1.6;
          color: var(--color-text);
        }
        .run-detail-reason-code {
          display: inline-block;
          margin-top: var(--spacing-xs);
          font-size: 0.75rem;
          color: var(--color-text-muted);
          font-family: var(--font-mono);
        }
        .run-detail-steps {
          margin-top: var(--spacing-md);
        }
        .run-detail-polling {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: var(--spacing-md);
          color: var(--color-text-muted);
          font-size: 0.875rem;
        }
        .spinner-small {
          width: 16px;
          height: 16px;
          border: 2px solid var(--color-border);
          border-top-color: var(--color-primary);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
