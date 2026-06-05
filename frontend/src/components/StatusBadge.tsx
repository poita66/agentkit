interface StatusBadgeProps {
  reason: string | null;
  status: string;
}

const BADGE_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  succeeded: { bg: 'var(--color-success-bg)', color: 'var(--color-success)', label: 'Succeeded' },
  step_cap: { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)', label: 'Step limit reached' },
  cost_cap: { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)', label: 'Budget limit reached' },
  stuck: { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)', label: 'Agent stuck' },
  timeout: { bg: 'var(--color-error-bg)', color: 'var(--color-error)', label: 'Timed out' },
  error: { bg: 'var(--color-error-bg)', color: 'var(--color-error)', label: 'Error' },
  running: { bg: 'var(--color-info-bg)', color: 'var(--color-info)', label: 'Running' },
};

export default function StatusBadge({ reason, status }: StatusBadgeProps) {
  const key = status === 'running' ? 'running' : (reason ?? 'unknown');
  const style = BADGE_STYLES[key] ?? { bg: 'var(--color-card-bg)', color: 'var(--color-text-muted)', label: key };

  return (
    <span
      className="status-badge"
      style={{ backgroundColor: style.bg, color: style.color }}
      role="status"
      aria-label={style.label}
    >
      {style.label}
    </span>
  );
}
