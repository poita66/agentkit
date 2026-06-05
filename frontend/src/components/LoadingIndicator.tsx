import { useEffect, useState } from 'react';

interface LoadingIndicatorProps {
  message: string;
}

export default function LoadingIndicator({ message }: LoadingIndicatorProps) {
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setTimedOut(true), 10000);
    return () => clearTimeout(timer);
  }, []);

  if (timedOut) {
    return (
      <div className="loading-indicator loading-indicator--timeout" role="alert">
        <p>The operation is taking longer than expected.</p>
        <button className="loading-indicator-retry" onClick={() => window.location.reload()}>
          Retry
        </button>
        <style>{`
          .loading-indicator--timeout {
            padding: var(--spacing-xl);
            text-align: center;
            color: var(--color-warning);
          }
          .loading-indicator-retry {
            margin-top: var(--spacing-md);
            padding: var(--spacing-sm) var(--spacing-md);
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="loading-indicator" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true"></div>
      <p>{message}</p>
      <style>{`
        .loading-indicator {
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
