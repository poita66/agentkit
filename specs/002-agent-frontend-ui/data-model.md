# Data Model: Agent Frontend UI

The frontend is stateless — all data is fetched from the backend API and held in React component state. The TypeScript interfaces below mirror the backend Pydantic schemas.

## RunDetail

Represents a single agent execution with full step history.

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `string` | UUID identifier |
| `goal` | `string` | User's goal in plain language (max 4096 chars) |
| `status` | `"running" \| "completed"` | Current execution state |
| `reason` | `"succeeded" \| "step_cap" \| "cost_cap" \| "stuck" \| "timeout" \| "error" \| null` | Termination reason (null while running) |
| `total_cost` | `number` | Cumulative cost in USD |
| `max_steps` | `number` | Step limit for this run |
| `max_cost_usd` | `number` | Budget limit in USD |
| `started_at` | `string \| null` | ISO 8601 timestamp |
| `finished_at` | `string \| null` | ISO 8601 timestamp (null while running) |
| `steps` | `StepDetail[]` | Ordered list of steps |

## StepDetail

A single iteration within a run.

| Field | Type | Description |
|-------|------|-------------|
| `step_number` | `number` | Sequential step index (1-based) |
| `tool_name` | `string \| null` | Name of tool called (null for final answer) |
| `args` | `Record<string, unknown> \| null` | Tool arguments as JSON object |
| `result` | `Record<string, unknown>` | Tool result (contains `ok`, `data`, `error` fields) |
| `cost` | `number` | Cost of this step in USD |
| `created_at` | `string \| null` | ISO 8601 timestamp |

## RunSummary

Lightweight representation for list views.

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `string` | UUID identifier |
| `goal` | `string` | User's goal (truncated for display) |
| `status` | `string` | Current state |
| `reason` | `string \| null` | Termination reason |
| `total_cost` | `number` | Cumulative cost in USD |
| `started_at` | `string \| null` | ISO 8601 timestamp |
| `finished_at` | `string \| null` | ISO 8601 timestamp |

## RunListResponse

Paginated collection of run summaries.

| Field | Type | Description |
|-------|------|-------------|
| `runs` | `RunSummary[]` | Array of run summaries |
| `total` | `number` | Total count across all pages |
| `limit` | `number` | Page size |
| `offset` | `number` | Current offset |

## RunCreateRequest

Payload for creating a new run.

| Field | Type | Description |
|-------|------|-------------|
| `goal` | `string` | Goal in plain language (1-4096 chars) |
| `max_steps` | `number \| null` | Optional step limit (default 20) |
| `max_cost_usd` | `number \| null` | Optional budget limit (default 0.5) |

## RunCreateResponse

Response after creating a run.

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `string` | UUID of the newly created run |

## State Transitions

```
[Initial] --submit goal--> [running]
    [running] --poll--> [running] (new steps added)
    [running] --poll--> [completed] + reason: "succeeded"
    [running] --poll--> [completed] + reason: "step_cap"
    [running] --poll--> [completed] + reason: "cost_cap"
    [running] --poll--> [completed] + reason: "stuck"
    [running] --poll--> [completed] + reason: "timeout"
    [running] --poll--> [completed] + reason: "error"
```

## Validation Rules

- `goal`: non-empty, 1-4096 characters, trimmed
- `max_steps`: positive integer (default 20)
- `max_cost_usd`: positive float (default 0.5)
- `run_id`: valid UUID format
- `status`: one of `running`, `completed`
- `reason`: one of the six termination reasons or null
