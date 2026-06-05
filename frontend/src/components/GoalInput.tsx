import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getScenarios } from "../api/client";
import { ScenarioInfo } from "../api/types";
import { useRunMutation } from "../hooks/useRunMutation";

interface GoalInputProps {
  onSubmit?: (
    goal: string,
    options?: { max_steps?: number; max_cost_usd?: number },
  ) => void;
  disabled?: boolean;
}

export default function GoalInput({
  onSubmit,
  disabled: externalDisabled,
}: GoalInputProps) {
  const [goal, setGoal] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxSteps, setMaxSteps] = useState("");
  const [maxCost, setMaxCost] = useState("");
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioInfo[]>([]);
  const { loading, error, success, runId, createRunFn } = useRunMutation();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getScenarios()
      .then((data) => setScenarios(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (success && runId) {
      if (onSubmit) {
        const options: {
          max_steps?: number;
          max_cost_usd?: number;
          scenario?: string | null;
        } = {};
        if (maxSteps) options.max_steps = parseInt(maxSteps, 10);
        if (maxCost) options.max_cost_usd = parseFloat(maxCost);
        if (selectedScenario) options.scenario = selectedScenario;
        onSubmit(
          goal.trim(),
          Object.keys(options).length > 0 ? options : undefined,
        );
      }
      navigate(`/runs/${runId}`);
      setGoal("");
      setMaxSteps("");
      setMaxCost("");
      setSelectedScenario(null);
    }
  }, [
    success,
    runId,
    onSubmit,
    navigate,
    goal,
    maxSteps,
    maxCost,
    selectedScenario,
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const options: {
      max_steps?: number;
      max_cost_usd?: number;
      scenario?: string | null;
    } = {};
    if (maxSteps) options.max_steps = parseInt(maxSteps, 10);
    if (maxCost) options.max_cost_usd = parseFloat(maxCost);
    if (selectedScenario) options.scenario = selectedScenario;
    await createRunFn(
      goal,
      Object.keys(options).length > 0 ? options : undefined,
    );
  };

  const isDisabled = externalDisabled || loading;

  return (
    <form
      className="goal-input"
      onSubmit={handleSubmit}
      aria-label="Submit a goal"
    >
      <div className="goal-input-row">
        <input
          ref={inputRef}
          type="text"
          className="goal-input-field"
          placeholder="What would you like the agent to do?"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          disabled={isDisabled}
          aria-label="Goal"
        />
        <button
          type="submit"
          className="goal-input-submit"
          disabled={isDisabled || !goal.trim()}
          aria-label={loading ? "Submitting goal..." : "Submit goal"}
        >
          {loading ? "Submitting..." : "Submit"}
        </button>
      </div>

      <div className="goal-input-advanced">
        <button
          type="button"
          className="goal-input-toggle"
          onClick={() => setShowAdvanced(!showAdvanced)}
          aria-expanded={showAdvanced}
        >
          {showAdvanced ? "Hide" : "Advanced"}
        </button>

        {showAdvanced && (
          <div className="goal-input-options">
            <label className="goal-input-label">
              <span>Max steps</span>
              <input
                type="number"
                className="goal-input-option"
                value={maxSteps}
                onChange={(e) => setMaxSteps(e.target.value)}
                min="1"
                max="100"
                placeholder="20"
                aria-label="Maximum number of steps"
              />
            </label>
            <label className="goal-input-label">
              <span>Max cost ($)</span>
              <input
                type="number"
                className="goal-input-option"
                value={maxCost}
                onChange={(e) => setMaxCost(e.target.value)}
                min="0.01"
                step="0.01"
                placeholder="0.50"
                aria-label="Maximum cost in USD"
              />
            </label>
          </div>
        )}
      </div>

      {scenarios.length > 0 && (
        <div className="goal-input-scenarios">
          <span className="goal-input-scenarios-label">Test scenarios:</span>
          <div className="goal-input-scenario-buttons">
            {scenarios.map((s) => (
              <button
                key={s.name}
                type="button"
                className={`goal-input-scenario-btn${selectedScenario === s.name ? " goal-input-scenario-btn--active" : ""}`}
                onClick={() => {
                  scenarioOnClick(s);
                }}
                title={s.description}
              >
                {s.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="goal-input-error" role="alert">
          {error}
        </div>
      )}

      <style>{`
        .goal-input {
          margin-bottom: var(--spacing-lg);
        }
        .goal-input-row {
          display: flex;
          gap: var(--spacing-sm);
        }
        .goal-input-field {
          flex: 1;
          padding: var(--spacing-md);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-input-bg);
          font-size: 1rem;
        }
        .goal-input-field:focus {
          box-shadow: var(--focus-ring);
        }
        .goal-input-submit {
          padding: var(--spacing-md) var(--spacing-lg);
          background: var(--color-primary);
          color: white;
          border: none;
          border-radius: var(--radius-md);
          font-weight: 600;
          white-space: nowrap;
        }
        .goal-input-submit:hover:not(:disabled) {
          background: var(--color-primary-hover);
        }
        .goal-input-advanced {
          margin-top: var(--spacing-sm);
        }
        .goal-input-toggle {
          background: none;
          border: none;
          color: var(--color-text-muted);
          font-size: 0.875rem;
          padding: var(--spacing-xs) var(--spacing-sm);
        }
        .goal-input-toggle:hover {
          color: var(--color-text);
        }
        .goal-input-options {
          display: flex;
          gap: var(--spacing-md);
          margin-top: var(--spacing-sm);
        }
        .goal-input-label {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
          font-size: 0.875rem;
          color: var(--color-text-muted);
        }
        .goal-input-option {
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          background: var(--color-input-bg);
          width: 120px;
        }
        .goal-input-error {
          margin-top: var(--spacing-sm);
          padding: var(--spacing-sm) var(--spacing-md);
          background: var(--color-error-bg);
          color: var(--color-error);
          border-radius: var(--radius-sm);
          font-size: 0.875rem;
        }
        .goal-input-scenarios {
          margin-top: var(--spacing-md);
          padding-top: var(--spacing-sm);
          border-top: 1px solid var(--color-border);
        }
        .goal-input-scenarios-label {
          font-size: 0.75rem;
          color: var(--color-text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          display: block;
          margin-bottom: var(--spacing-xs);
        }
        .goal-input-scenario-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: var(--spacing-xs);
        }
        .goal-input-scenario-btn {
          padding: var(--spacing-xs) var(--spacing-sm);
          background: var(--color-card-bg);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          color: var(--color-text-muted);
          font-size: 0.8rem;
          cursor: pointer;
        }
        .goal-input-scenario-btn:hover {
          border-color: var(--color-primary);
          color: var(--color-text);
        }
        .goal-input-scenario-btn--active {
          background: var(--color-primary-bg);
          border-color: var(--color-primary);
          color: var(--color-primary);
        }
      `}</style>
    </form>
  );

  function scenarioOnClick(s: ScenarioInfo) {
    const previouslySelected = selectedScenario === s.name;
    setSelectedScenario(previouslySelected ? null : s.name);
    setGoal(previouslySelected ? "" : s.description);
  }
}
