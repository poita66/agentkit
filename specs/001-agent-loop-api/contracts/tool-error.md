# Tool Error Contract

All tools return a structured result. The agent loop uses this contract to determine retry behavior and error surfacing.

## Success Response

```json
{
  "ok": true,
  "data": { ... },
  "error": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `true` for successful execution |
| `data` | object | Tool-specific result data |
| `error` | null | Always null on success |

## Error Response

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "The requested document was not found",
    "recoverable": false
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `ok` | boolean | `false` for failed execution |
| `data` | null | Always null on error |
| `error.code` | string | Machine-readable error code |
| `error.message` | string | Human-readable error message |
| `error.recoverable` | boolean | `true` if the error is transient and retry may succeed |

## Runtime Behavior

| `recoverable` | Action |
|---------------|--------|
| `true` | Retry up to 3 attempts; if all fail, terminate run with `error` reason |
| `false` | Surface error to the agent; agent may choose alternative tool or give final answer |

## Example Error Codes

| Code | Recoverable | Description |
|------|-------------|-------------|
| `NETWORK_TIMEOUT` | true | Transient network failure |
| `RATE_LIMITED` | true | API rate limit hit; retry after backoff |
| `INVALID_ARGUMENT` | false | Semantic error; retry won't help |
| `TOOL_NOT_FOUND` | false | Tool does not exist |
| `AUTHENTICATION_FAILED` | false | Credentials invalid |
