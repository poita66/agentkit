# API Contract: Backend HTTP Endpoints

The frontend communicates with the FastAPI backend over HTTP. All endpoints are prefixed with `/runs`.

## POST /runs

Create a new agent run.

**Request**:
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "goal": "string (required, 1-4096 chars)",
    "max_steps": "number | null (optional, default 20)",
    "max_cost_usd": "number | null (optional, default 0.5)"
  }
  ```

**Responses**:
- `202 Accepted`: `{ "run_id": "string (UUID)" }` — run created and processing started
- `422 Unprocessable Entity`: `{ "detail": "string" }` — validation error (empty goal, too long, etc.)

---

## GET /runs/{run_id}

Get full details of a specific run, including all steps.

**Request**:
- Method: `GET`
- Path parameter: `run_id` (UUID string)

**Responses**:
- `200 OK`: `RunDetail` object with `run_id`, `goal`, `status`, `reason`, `total_cost`, `max_steps`, `max_cost_usd`, `started_at`, `finished_at`, `steps[]`
- `404 Not Found`: `{ "detail": "string" }` — run not found

---

## GET /runs

List recent runs with pagination.

**Request**:
- Method: `GET`
- Query parameters:
  - `limit`: `number` (default 20, max 100)
  - `offset`: `number` (default 0)

**Responses**:
- `200 OK`: `{ "runs": RunSummary[], "total": number, "limit": number, "offset": number }`

---

## Error Handling

The frontend must handle:
- Network errors (backend unavailable) → show error state with retry option
- 404 responses → show "run not found" message
- 422 responses → show validation error message inline
- Timeout responses (fetch > 10s) → show timeout message with retry option
