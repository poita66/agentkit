# Data Model: Agent Loop API

**Date**: 2026-06-04

## Entities

### Run

Represents a single agent execution from initiation to terminal state.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String` (UUID) | Primary key, auto-generated | Unique run identifier |
| `goal` | `String` | NOT NULL, max 4096 chars | The user's goal in plain language |
| `status` | `String` | NOT NULL, enum: `running`, `succeeded`, `failed` | Current run status |
| `reason` | `String` | NULL when running; enum: `step_cap`, `cost_cap`, `stuck`, `timeout`, `error`, `succeeded` | Termination reason |
| `total_cost` | `Float` | NOT NULL, default 0.0, >= 0 | Cumulative cost in USD across all steps |
| `max_steps` | `Integer` | NOT NULL, default 20, > 0 | Step limit for this run |
| `max_cost_usd` | `Float` | NOT NULL, default 0.5, > 0 | Cost budget for this run |
| `started_at` | `DateTime` | NOT NULL, auto-set on creation | Run start timestamp (UTC) |
| `finished_at` | `DateTime` | NULL while running | Run completion timestamp (UTC) |

**State transitions**:
- `running` → `succeeded` (reason: `succeeded`)
- `running` → `failed` (reason: `step_cap`, `cost_cap`, `stuck`, `timeout`, `error`)

**Validation rules**:
- `goal` must not be empty or whitespace-only
- `max_steps` must be positive (default 20)
- `max_cost_usd` must be positive (default 0.5)
- `reason` must be set when transitioning out of `running`
- `finished_at` must be set when transitioning out of `running`

### Step

Represents a single iteration within a run (tool call or final answer).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | `String` (UUID) | Primary key, auto-generated | Unique step identifier |
| `run_id` | `String` (UUID) | Foreign key → Run.id, NOT NULL | Parent run |
| `step_number` | `Integer` | NOT NULL, > 0, unique within run | Sequential step number (1-based) |
| `tool_name` | `String` | NULL for final answer; max 256 chars | Name of the tool invoked |
| `args_json` | `String` (JSON) | NULL for final answer | Tool arguments as JSON string |
| `result_json` | `String` (JSON) | NOT NULL | Tool result or final answer text as JSON |
| `cost` | `Float` | NOT NULL, >= 0 | Cost of this step in USD |
| `created_at` | `DateTime` | NOT NULL, auto-set | Step creation timestamp (UTC) |

**Relationships**:
- Each step belongs to exactly one run
- Steps are ordered by `step_number` within a run
- A run may have 1 to `max_steps` steps

**Validation rules**:
- `step_number` must be sequential (n+1) within a run
- `tool_name` is NULL only for the final answer step
- `args_json` is NULL only for the final answer step
- `result_json` must be valid JSON
- Each step is persisted atomically (single transaction)

### Tool

Represents a capability the agent can invoke. Stored in the tool registry (in-memory, not persisted).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | `String` | Unique, max 256 chars | Tool identifier |
| `description` | `String` | NOT NULL, max 1024 chars | Human-readable description for relevance matching |
| `parameters` | `Dict` | NOT NULL | JSON Schema describing expected arguments |

**Validation rules**:
- Tool names must be unique within the registry
- Description is used for keyword-based relevance scoring
- Parameters follow JSON Schema format for argument validation

## Database Schema

```sql
CREATE TABLE runs (
    id TEXT PRIMARY KEY,
    goal TEXT NOT NULL CHECK (LENGTH(goal) <= 4096),
    status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    reason TEXT CHECK (reason IN ('step_cap', 'cost_cap', 'stuck', 'timeout', 'error', 'succeeded')),
    total_cost REAL NOT NULL DEFAULT 0.0 CHECK (total_cost >= 0),
    max_steps INTEGER NOT NULL DEFAULT 20 CHECK (max_steps > 0),
    max_cost_usd REAL NOT NULL DEFAULT 0.5 CHECK (max_cost_usd > 0),
    started_at DATETIME NOT NULL,
    finished_at DATETIME
);

CREATE TABLE steps (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(id),
    step_number INTEGER NOT NULL CHECK (step_number > 0),
    tool_name TEXT CHECK (LENGTH(tool_name) <= 256),
    args_json TEXT,
    result_json TEXT NOT NULL,
    cost REAL NOT NULL CHECK (cost >= 0),
    created_at DATETIME NOT NULL,
    UNIQUE(run_id, step_number)
);

CREATE INDEX idx_steps_run_id ON steps(run_id);
```

**Indexes**:
- `runs.id` — primary key (implicit index)
- `steps.run_id` — for querying all steps of a run
- `steps.run_id, steps.step_number` — unique constraint (implicit index)
