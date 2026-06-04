# API Contract: Runs

## Endpoints

### POST /runs

Create a new agent run. The agent loop executes in the background.

**Request**:
```
Content-Type: application/json
```

```json
{
  "goal": "Find the Q3 revenue report and summarize it",
  "max_steps": 20,
  "max_cost_usd": 0.5
}
```

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `goal` | string | Yes | — | Non-empty, max 4096 chars |
| `max_steps` | integer | No | 20 | Positive integer |
| `max_cost_usd` | number | No | 0.5 | Positive float |

**Response 202 Accepted**:
```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Response 422 Unprocessable Entity**:
```json
{
  "detail": "Goal must not be empty or whitespace-only"
}
```

---

### GET /runs

List recent runs, ordered by most recent first.

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 20 | Number of runs to return (1-100) |
| `offset` | integer | No | 0 | Number of runs to skip |

**Response 200 OK**:
```json
{
  "runs": [
    {
      "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "goal": "Find the Q3 revenue report and summarize it",
      "status": "succeeded",
      "reason": "succeeded",
      "total_cost": 0.12,
      "started_at": "2026-06-04T12:00:00Z",
      "finished_at": "2026-06-04T12:00:15Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

---

### GET /runs/{run_id}

Get the full state of a specific run, including all steps.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `run_id` | string (UUID) | Yes | The run identifier |

**Response 200 OK**:
```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "goal": "Find the Q3 revenue report and summarize it",
  "status": "succeeded",
  "reason": "succeeded",
  "total_cost": 0.12,
  "max_steps": 20,
  "max_cost_usd": 0.5,
  "started_at": "2026-06-04T12:00:00Z",
  "finished_at": "2026-06-04T12:00:15Z",
  "steps": [
    {
      "step_number": 1,
      "tool_name": "search_docs",
      "args": {"query": "Q3 revenue report"},
      "result": {"ok": true, "data": {"documents": ["doc-123"]}, "error": null},
      "cost": 0.04,
      "created_at": "2026-06-04T12:00:02Z"
    },
    {
      "step_number": 2,
      "tool_name": null,
      "args": null,
      "result": {"answer": "The Q3 revenue was $2.4M, up 15% from Q2."},
      "cost": 0.02,
      "created_at": "2026-06-04T12:00:14Z"
    }
  ]
}
```

**Response 404 Not Found**:
```json
{
  "detail": "Run 'invalid-id' not found"
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message"
}
```

## Termination Reasons

| Reason | Status | Description |
|--------|--------|-------------|
| `succeeded` | `succeeded` | Agent reached a final answer |
| `step_cap` | `failed` | Step count exceeded `max_steps` |
| `cost_cap` | `failed` | Total cost exceeded `max_cost_usd` |
| `stuck` | `failed` | Same tool call repeated 3 times |
| `timeout` | `failed` | 60-second wall-clock limit reached |
| `error` | `failed` | Unrecoverable tool error or system error |
