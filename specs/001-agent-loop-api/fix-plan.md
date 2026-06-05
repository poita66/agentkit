# Fix Plan: Backend Spec Validation Issues

**Date**: 2026-06-05
**Source**: Validation of backend implementation against `specs/001-agent-loop-api/`
**Status**: Pending

---

## Critical

### FIX-001: RETRIES_EXHAUSTED should terminate the run (US4, scenario 3)

**Spec**: "When the retry limit is reached, the run terminates with an error reason."

**Current behavior**: `agent_loop.py:109` treats `RETRIES_EXHAUSTED` (recoverable=false) as a non-recoverable error, logs a warning, and continues the loop for the LLM to decide.

**Fix**:
- In `backend/src/services/agent_loop.py`, after `runtime.execute()` (line 91), check if `result["error"]["code"] == "RETRIES_EXHAUSTED"`
- If so, persist the step, then call `_finalize_run(run_id, "error")` and return
- File: `backend/src/services/agent_loop.py`

---

## High

### FIX-002: Enable SQLite WAL mode for concurrent safety (SC-004)

**Spec**: Plan calls for WAL mode; SC-004 requires 100 concurrent runs without data corruption.

**Current behavior**: `session.py:20` creates engine without WAL mode.

**Fix**:
- In `backend/src/db/session.py`, add a `connect_args` or event listener to set `PRAGMA journal_mode=WAL`
- File: `backend/src/db/session.py`

### FIX-003: Remove test scaffolding from production endpoint

**Current behavior**: `runs.py:110-116` has `_select_scenario()` that picks mock LLM scenarios based on request params. This is test-only logic in the production API.

**Fix**:
- Remove `_select_scenario()` and the `SCENARIOS_DIR` / `MockLLM` instantiation from `backend/src/api/runs.py`
- POST /runs should accept or inject the LLM implementation differently (e.g., via dependency injection or configuration)
- File: `backend/src/api/runs.py`

### FIX-004: Fix stuck detection cost inconsistency

**Current behavior**: `agent_loop.py:80` adds LLM call cost to `total_cost` before stuck check at line 85. If stuck triggers, the cost is counted but no step is persisted, creating a mismatch between `run.total_cost` and sum of step costs.

**Fix**:
- In `backend/src/services/agent_loop.py`, move cost accumulation (`total_cost += cost`) to after the stuck check, or subtract the cost if stuck terminates
- File: `backend/src/services/agent_loop.py`

### FIX-005: Add explicit `idx_steps_run_id` index

**Spec**: `data-model.md` specifies `CREATE INDEX idx_steps_run_id ON steps(run_id)`.

**Current behavior**: Only the composite `UNIQUE(run_id, step_number)` constraint exists.

**Fix**:
- In `backend/src/models/step.py`, add `Index("idx_steps_run_id", "run_id")` to `__table_args__`
- File: `backend/src/models/step.py`

---

## Medium (Test Gaps)

### FIX-006: Add timeout integration test

**Spec**: FR-008 — 60s wall-clock timeout.

**Fix**:
- Add test in `backend/tests/integration/test_full_run.py` that creates a scenario with enough tool calls to exceed 60s (or mock `asyncio.timeout` to fire sooner)
- Verify run terminates with reason `timeout`
- File: `backend/tests/integration/test_full_run.py`

### FIX-007: Add error termination integration test

**Spec**: FR-015 — `error` termination reason for unhandled exceptions.

**Fix**:
- Add test that simulates an unexpected exception in the agent loop (e.g., mock LLM raises)
- Verify run terminates with reason `error` and status `failed`
- File: `backend/tests/integration/test_full_run.py`

### FIX-008: Add US4 tool error integration tests

**Spec**: US4 scenarios — non-recoverable error surfacing, retry exhaustion termination.

**Fix**:
- Add test for `tool_error_nonrecoverable` scenario: tool returns non-recoverable error, agent loop surfaces to LLM, LLM switches tool or gives final answer
- Add test for `tool_error_exhausted` scenario: tool returns recoverable error 3 times, retries exhausted, run terminates with `error` reason (validates FIX-001)
- File: `backend/tests/integration/test_full_run.py`

### FIX-009: Add concurrent run safety test

**Spec**: SC-004 — 100 concurrent runs without data corruption.

**Fix**:
- Add test in `backend/tests/integration/` that spawns 100 concurrent POST /runs calls
- Verify all 100 runs complete with valid terminal states, no duplicate step numbers, no corrupted data
- File: `backend/tests/integration/test_concurrent_runs.py`

---

## Execution Order

1. FIX-005 (model change, no dependencies)
2. FIX-002 (DB session change, no dependencies)
3. FIX-001 (agent loop change, core fix)
4. FIX-004 (agent loop change, depends on FIX-001 reading)
5. FIX-003 (API endpoint cleanup)
6. FIX-006 through FIX-009 (tests, can run in parallel after fixes 1-5)
