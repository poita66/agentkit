import { Link } from 'react-router-dom';
import { useRuns } from '../hooks/useRuns';
import StatusBadge from './StatusBadge';
import { timeAgo } from '../utils/timeAgo';

export default function RunList() {
  const { runs, total, loading, error, loadMore } = useRuns(20);

  if (loading) {
    return (
      <div className="run-list run-list--loading">
        <div className="spinner" aria-hidden="true"></div>
        <p>Loading runs...</p>
        <style>{`
          .run-list--loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: var(--spacing-md);
            padding: var(--spacing-xl) 0;
          }
          .spinner {
            width: 32px;
            height: 32px;
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
      <div className="run-list run-list--error">
        <div className="run-list-error" role="alert">
          <p>Failed to load runs: {error}</p>
        </div>
        <style>{`
          .run-list-error {
            padding: var(--spacing-md);
            background: var(--color-error-bg);
            color: var(--color-error);
            border-radius: var(--radius-md);
            text-align: center;
          }
        `}</style>
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className="run-list run-list--empty">
        <div className="run-list-empty">
          <h3>No runs yet</h3>
          <p>Submit a goal above to get started.</p>
        </div>
        <style>{`
          .run-list-empty {
            padding: var(--spacing-xl);
            text-align: center;
            color: var(--color-text-muted);
          }
          .run-list-empty h3 {
            margin-bottom: var(--spacing-sm);
            color: var(--color-text);
          }
        `}</style>
      </div>
    );
  }

  return (
    <section className="run-list" aria-label="Run history">
      <h2 className="run-list-title">Recent Runs</h2>
      <ul className="run-list-items" role="list">
        {runs.map((run) => (
          <li key={run.run_id} className="run-list-item">
            <Link to={`/runs/${run.run_id}`} className="run-list-link" aria-label={`View run: ${run.goal}`}>
              <span className="run-list-goal">{truncate(run.goal, 80)}</span>
              <div className="run-list-meta">
                <StatusBadge reason={run.reason} status={run.status} />
                <span className="run-list-time">
                  {run.started_at ? timeAgo(run.started_at) : ''}
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>

      {runs.length < total && (
        <button className="run-list-load-more" onClick={() => loadMore()}>
          Load more ({total - runs.length} remaining)
        </button>
      )}

      <style>{`
        .run-list {
          margin-top: var(--spacing-lg);
        }
        .run-list-title {
          font-size: 1.125rem;
          margin-bottom: var(--spacing-md);
          color: var(--color-text-muted);
        }
        .run-list-items {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        .run-list-item {
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-sm);
          background: var(--color-card-bg);
        }
        .run-list-item:hover {
          background: var(--color-card-hover);
        }
        .run-list-link {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          padding: var(--spacing-md);
          color: inherit;
          text-decoration: none;
        }
        .run-list-link:hover {
          text-decoration: none;
        }
        .run-list-goal {
          font-size: 0.9375rem;
          font-weight: 500;
        }
        .run-list-meta {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }
        .run-list-time {
          font-size: 0.75rem;
          color: var(--color-text-muted);
        }
        .status-badge {
          display: inline-block;
          padding: 2px var(--spacing-sm);
          border-radius: var(--radius-sm);
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: capitalize;
        }
        .run-list-load-more {
          display: block;
          margin: var(--spacing-md) auto;
          padding: var(--spacing-sm) var(--spacing-lg);
          background: none;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          color: var(--color-text-muted);
          font-size: 0.875rem;
        }
        .run-list-load-more:hover {
          border-color: var(--color-primary);
          color: var(--color-primary);
        }
      `}</style>
    </section>
  );
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}
