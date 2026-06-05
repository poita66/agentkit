# Session: Validate backend against 001-agent-loop-api spec

**Session ID:** ses_16ab58f30ffeQInLJwyX7SO34A

**Agent:** build

**Model:** llama/default

**Messages:** 9

---

## User (1)

Validate that the backend implementation matches the spec in @specs/001-agent-loop-api/
Called the Read tool with the following input: {"filePath":"/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/specs/001-agent-loop-api/"}
<path>/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/specs/001-agent-loop-api/</path>
<type>directory</type>
<entries>
checklists/
contracts/
data-model.md
plan.md
quickstart.md
research.md
spec.md
tasks.md

(8 entries)
</entries>

---

## Assistant (2)

I'll start by reading the spec and examining the backend implementation.

---

## Assistant (3)

Let me read the contracts, checklists, and explore the backend implementation.

---

## Assistant (4)

Now let me read all the backend source files to compare against the spec.

---

## Assistant (5)

Let me now read the key implementation files in detail to do a thorough validation.

---

## Assistant (6)

Now let me read the test files for completeness.

---

## Assistant (7)

Here is the validation report comparing the backend implementation against the spec:

---

## Validation Report: Backend vs Spec `001-agent-loop-api`

### Functional Requirements: All 15 Covered

| ID | Requirement | Status | Notes |
|----|-----------|--------|-------|
| FR-001 | Goal submission with optional params | ✅ | POST /runs, validates goal, defaults match |
| FR-002 | Tool registry | ✅ | 10 tools, in-memory |
| FR-003 | Tool subset selection | ✅ | Keyword scoring, top-K=5 |
| FR-004 | Agent loop orchestration | ✅ | LLM call + dispatch + persist |
| FR-005 | Step cap (default 20) | ✅ | `check_step_cap` |
| FR-006 | Cost cap | ✅ | `check_cost_cap`, `>` comparison |
| FR-007 | Stuck detection (3 repeats) | ✅ | `check_stuck` with args hash |
| FR-008 | 60s timeout | ✅ | `asyncio.timeout(60)` |
| FR-009 | Step recording | ✅ | All fields persisted |
| FR-010 | Run state persistence | ✅ | All fields, retrievable |
| FR-011 | Run details by ID | ✅ | GET /runs/{id} with steps |
| FR-012 | Paginated run list | ✅ | GET /runs, limit/offset |
| FR-013 | Error classification | ✅ | recoverable/non-recoverable |
| FR-014 | Bounded retries | ✅ | Max 3, exponential backoff |
| FR-015 | Fixed termination reasons | ✅ | All 6 reasons implemented |

### Data Model: Matches

Run and Step ORM models match `data-model.md` fields, types, constraints, and state transitions. The `UNIQUE(run_id, step_number)` constraint is present.

### API Contracts: Match

All three endpoints (POST /runs, GET /runs/{id}, GET /runs) match the contracts in `runs-api.md` for request/response formats, status codes, and error handling.

Tool error contract matches `tool-error.md` with `{ok, data, error: {code, message, recoverable}}` structure.

---

### Issues Found

**1. RETRIES_EXHAUSTED does not terminate the run (US4, scenario 3)** — `agent_loop.py:109`

When all 3 retries fail, `tool_runtime.py` returns `RETRIES_EXHAUSTED` with `recoverable: false`. The agent loop treats this as a non-recoverable error (logs a warning, surfaces to LLM) and continues. The spec says: *"When the retry limit is reached, the run terminates with an error reason."* The agent loop should check for `RETRIES_EXHAUSTED` and call `_finalize_run(run_id, "error")`.

**2. No SQLite WAL mode** — `session.py:20`

The plan specifies WAL mode for concurrent run safety (SC-004), but the engine is created without it. Add `connect_args` PRAGMA or use `?mode=wal` URI.

**3. Test scaffolding in production endpoint** — `runs.py:110-116`

`_select_scenario()` is test-only logic embedded in the POST /runs endpoint. In production, the LLM shouldn't be selected by goal keywords.

**4. Missing integration tests**

- No test for **timeout** termination (FR-008)
- No test for **error** termination (unhandled exceptions)
- No test for **100 concurrent runs** (SC-004)
- No test for **tool_error_nonrecoverable** and **tool_error_exhausted** scenarios (US4)

**5. Stuck detection cost inconsistency** — `agent_loop.py:80`

When stuck is detected, `total_cost` is incremented (line 80) but the step is never persisted (termination happens at line 87). The run's `total_cost` will include the LLM call cost for the undetected step.

**6. Missing explicit `idx_steps_run_id` index** — `step.py:12`

The data model specifies `CREATE INDEX idx_steps_run_id ON steps(run_id)`. The ORM only has the composite `UNIQUE(run_id, step_number)` constraint. The composite index can serve run_id lookups, but the spec calls for a dedicated index.

---

### Test Coverage Summary

| Test file | Spec coverage |
|-----------|--------------|
| `test_guards.py` | step_cap, cost_cap ✅ |
| `test_stuck_detection.py` | stuck detection ✅ |
| `test_tool_retrieval.py` | tool selection ✅ |
| `test_tool_runtime.py` | dispatch, retry, error ✅ |
| `test_full_run.py` | success, step_cap, cost_cap, stuck ✅ |
| Missing | timeout, error termination, concurrent runs, US4 scenarios |

### Verdict

The implementation covers all 15 functional requirements and matches the data model and API contracts. The **critical gap** is that exhausted retries don't terminate the run as specified. The other issues are missing tests, WAL mode not enabled, and test scaffolding in production code.

---

## User (8)

put a plan together to fix the issues and write it to file for recall in a fresh session

---

## Assistant (9)

Written to `specs/001-agent-loop-api/fix-plan.md`.

**9 fixes across 3 priority levels:**

| ID | Priority | What |
|----|----------|------|
| FIX-001 | Critical | RETRIES_EXHAUSTED must terminate run (US4 scenario 3) |
| FIX-002 | High | Enable SQLite WAL mode (SC-004) |
| FIX-003 | High | Remove test scaffolding from production endpoint |
| FIX-004 | High | Fix stuck detection cost/run.total_cost mismatch |
| FIX-005 | High | Add `idx_steps_run_id` index to Step model |
| FIX-006 | Medium | Add timeout integration test |
| FIX-007 | Medium | Add error termination integration test |
| FIX-008 | Medium | Add US4 tool error integration tests |
| FIX-009 | Medium | Add 100-concurrent-runs safety test |

Execution order: 005 → 002 → 001 → 004 → 003 → 006-009 (parallel).

---

