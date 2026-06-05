interface ErrorMessageProps {
  title: string;
  message: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ title, message, onRetry }: ErrorMessageProps) {
  return (
    <div className="error-message" role="alert">
      <h2 className="error-message-title">{title}</h2>
      <p className="error-message-text">{message}</p>
      {onRetry && (
        <button className="error-message-retry" onClick={onRetry}>
          Retry
        </button>
      )}
      <style>{`
        .error-message {
          padding: var(--spacing-xl);
          background: var(--color-error-bg);
          border-radius: var(--radius-md);
          text-align: center;
        }
        .error-message-title {
          color: var(--color-error);
          margin-bottom: var(--spacing-sm);
        }
        .error-message-text {
          color: var(--color-text);
          margin-bottom: var(--spacing-md);
        }
        .error-message-retry {
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-primary);
          color: white;
          border: none;
          border-radius: var(--radius-sm);
        }
        .error-message-retry:hover {
          background: var(--color-primary-hover);
        }
      `}</style>
    </div>
  );
}
