# Session: Apply backend spec validation fixes

**Session ID:** ses_16aa91e42ffeVZD1NOVoCwGkLl

**Agent:** build

**Model:** llama/default

**Messages:** 12

---

## User (1)

Use speckit-worker subagents to apply the fixes in @specs/001-agent-loop-api/fix-plan.md
Called the Read tool with the following input: {"filePath":"/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/specs/001-agent-loop-api/fix-plan.md"}
<path>/var/home/peter/Repos/Personal/ElevateIQ-AgentKit/specs/001-agent-loop-api/fix-plan.md</path>
<type>file</type>
<content>
1: # Fix Plan: Backend Spec Validation Issues
2: 
3: **Date**: 2026-06-05
4: **Source**: Validation of backend implementation against `specs/001-agent-loop-api/`
5: **Status**: Pending
6: 
7: ---
8: 
9: ## Critical
10: 
11: ### FIX-001: RETRIES_EXHAUSTED should terminate the run (US4, scenario 3)
12: 
13: **Spec**: "When the retry limit is reached, the run terminates with an error reason."
14: 
15: **Current behavior**: `agent_loop.py:109` treats `RETRIES_EXHAUSTED` (recoverable=false) as a non-recoverable error, logs a warning, and continues the loop for the LLM to decide.
16: 
17: **Fix**:
18: - In `backend/src/services/agent_loop.py`, after `runtime.execute()` (line 91), check if `result["error"]["code"] == "RETRIES_EXHAUSTED"`
19: - If so, persist the step, then call `_finalize_run(run_id, "error")` and return
20: - File: `backend/src/services/agent_loop.py`
21: 
22: ---
23: 
24: ## High
25: 
26: ### FIX-002: Enable SQLite WAL mode for concurrent safety (SC-004)
27: 
28: **Spec**: Plan calls for WAL mode; SC-004 requires 100 concurrent runs without data corruption.
29: 
30: **Current behavior**: `session.py:20` creates engine without WAL mode.
31: 
32: **Fix**:
33: - In `backend/src/db/session.py`, add a `connect_args` or event listener to set `PRAGMA journal_mode=WAL`
34: - File: `backend/src/db/session.py`
35: 
36: ### FIX-003: Remove test scaffolding from production endpoint
37: 
38: **Current behavior**: `runs.py:110-116` has `_select_scenario()` that picks mock LLM scenarios based on request params. This is test-only logic in the production API.
39: 
40: **Fix**:
41: - Remove `_select_scenario()` and the `SCENARIOS_DIR` / `MockLLM` instantiation from `backend/src/api/runs.py`
42: - POST /runs should accept or inject the LLM implementation differently (e.g., via dependency injection or configuration)
43: - File: `backend/src/api/runs.py`
44: 
45: ### FIX-004: Fix stuck detection cost inconsistency
46: 
47: **Current behavior**: `agent_loop.py:80` adds LLM call cost to `total_cost` before stuck check at line 85. If stuck triggers, the cost is counted but no step is persisted, creating a mismatch between `run.total_cost` and sum of step costs.
48: 
49: **Fix**:
50: - In `backend/src/services/agent_loop.py`, move cost accumulation (`total_cost += cost`) to after the stuck check, or subtract the cost if stuck terminates
51: - File: `backend/src/services/agent_loop.py`
52: 
53: ### FIX-005: Add explicit `idx_steps_run_id` index
54: 
55: **Spec**: `data-model.md` specifies `CREATE INDEX idx_steps_run_id ON steps(run_id)`.
56: 
57: **Current behavior**: Only the composite `UNIQUE(run_id, step_number)` constraint exists.
58: 
59: **Fix**:
60: - In `backend/src/models/step.py`, add `Index("idx_steps_run_id", "run_id")` to `__table_args__`
61: - File: `backend/src/models/step.py`
62: 
63: ---
64: 
65: ## Medium (Test Gaps)
66: 
67: ### FIX-006: Add timeout integration test
68: 
69: **Spec**: FR-008 — 60s wall-clock timeout.
70: 
71: **Fix**:
72: - Add test in `backend/tests/integration/test_full_run.py` that creates a scenario with enough tool calls to exceed 60s (or mock `asyncio.timeout` to fire sooner)
73: - Verify run terminates with reason `timeout`
74: - File: `backend/tests/integration/test_full_run.py`
75: 
76: ### FIX-007: Add error termination integration test
77: 
78: **Spec**: FR-015 — `error` termination reason for unhandled exceptions.
79: 
80: **Fix**:
81: - Add test that simulates an unexpected exception in the agent loop (e.g., mock LLM raises)
82: - Verify run terminates with reason `error` and status `failed`
83: - File: `backend/tests/integration/test_full_run.py`
84: 
85: ### FIX-008: Add US4 tool error integration tests
86: 
87: **Spec**: US4 scenarios — non-recoverable error surfacing, retry exhaustion termination.
88: 
89: **Fix**:
90: - Add test for `tool_error_nonrecoverable` scenario: tool returns non-recoverable error, agent loop surfaces to LLM, LLM switches tool or gives final answer
91: - Add test for `tool_error_exhausted` scenario: tool returns recoverable error 3 times, retries exhausted, run terminates with `error` reason (validates FIX-001)
92: - File: `backend/tests/integration/test_full_run.py`
93: 
94: ### FIX-009: Add concurrent run safety test
95: 
96: **Spec**: SC-004 — 100 concurrent runs without data corruption.
97: 
98: **Fix**:
99: - Add test in `backend/tests/integration/` that spawns 100 concurrent POST /runs calls
100: - Verify all 100 runs complete with valid terminal states, no duplicate step numbers, no corrupted data
101: - File: `backend/tests/integration/test_concurrent_runs.py`
102: 
103: ---
104: 
105: ## Execution Order
106: 
107: 1. FIX-005 (model change, no dependencies)
108: 2. FIX-002 (DB session change, no dependencies)
109: 3. FIX-001 (agent loop change, core fix)
110: 4. FIX-004 (agent loop change, depends on FIX-001 reading)
111: 5. FIX-003 (API endpoint cleanup)
112: 6. FIX-006 through FIX-009 (tests, can run in parallel after fixes 1-5)

(End of file - total 112 lines)
</content>

---

## Assistant (2)

I'll read the relevant source files first, then dispatch the speckit-worker subagents for each fix.

---

## Assistant (3)

Let me read the existing tasks.md and test file, plus the spec data model for context.

---

## Assistant (4)

Now I have all the context. Let me update `tasks.md` with the fix tasks and dispatch the speckit-worker subagents.

---

## Assistant (5)

Now dispatching the speckit-worker subagents in waves based on execution order:

**Wave 1: FIX-005 + FIX-002 (parallel, no dependencies)**

---

## Assistant (6)

Wave 1 done. **Wave 2: FIX-001 + FIX-003 (parallel, different files)**

---

## Assistant (7)

Wave 2 done. **Wave 3: FIX-004 (depends on FIX-001 changes)**

---

## Assistant (8)

Wave 3 done. **Wave 4: FIX-006 through FIX-009 (tests, parallel)**

---

## Assistant (9)

All 9 fixes from the fix plan have been applied. Here's the summary:

| Fix | Task | File | Status |
|-----|------|------|--------|
| FIX-005 | T033 | `backend/src/models/step.py` | ✅ Index added |
| FIX-002 | T034 | `backend/src/db/session.py` | ✅ WAL mode enabled |
| FIX-001 | T035 | `backend/src/services/agent_loop.py` | ✅ RETRIES_EXHAUSTED terminates run |
| FIX-004 | T036 | `backend/src/services/agent_loop.py` | ✅ Cost moved after stuck check |
| FIX-003 | T037 | `backend/src/api/runs.py` | ✅ Test scaffolding removed |
| FIX-006 | T038 | `backend/tests/integration/test_full_run.py` | ✅ Timeout test added |
| FIX-007 | T039 | `backend/tests/integration/test_full_run.py` | ✅ Error termination test added |
| FIX-008 | T040 | `backend/tests/integration/test_full_run.py` | ✅ 2 US4 tool error tests added |
| FIX-009 | T041 | `backend/tests/integration/test_concurrent_runs.py` | ✅ 100-concurrent-run test added |

---

## User (10)

commit the fixes in several commits - group the changes by logical similarity

---

## Assistant (11)

I'll make 4 logical commits:

1. **Model & DB layer** (FIX-005, FIX-002)
2. **Core logic** (FIX-001, FIX-003, FIX-004)
3. **Tests** (FIX-006 through FIX-009)
4. **Spec docs** (tasks.md, fix-plan.md)

---

## Assistant (12)

Done — 4 commits:

| Commit | Message | Files |
|--------|---------|-------|
| `5b7ad34` | fix: add idx_steps_run_id index and enable SQLite WAL mode | `step.py`, `session.py` |
| `54e3989` | fix: terminate on RETRIES_EXHAUSTED, fix cost accounting, remove test scaffolding | `agent_loop.py`, `runs.py` |
| `b4d2712` | test: add timeout, error, tool error, and concurrent run integration tests | `test_full_run.py`, `test_concurrent_runs.py` |
| `ccd6510` | docs: add fix plan and Phase 8 tasks for spec validation fixes | `tasks.md`, `fix-plan.md` |

---

