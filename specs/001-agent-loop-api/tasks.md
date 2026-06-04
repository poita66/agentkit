# Tasks: Agent Loop RESTful API with Persistence

**Input**: Design documents from `/specs/001-agent-loop-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution Principle II (mandatory for guards, tool retrieval, retry logic, and full-run integration)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure: `backend/src/` (with `models/`, `services/`, `api/`, `db/` subdirs), `backend/tests/` (with `unit/`, `integration/` subdirs), and `__init__.py` files
- [X] T002 Create `backend/requirements.txt` with FastAPI, uvicorn, SQLAlchemy, aiosqlite, pydantic, httpx, pytest, pytest-asyncio
- [X] T003 [P] Configure `backend/pyproject.toml` with ruff linter and mypy type checker settings per Constitution Principle I

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create async database session management in `backend/src/db/session.py` with SQLite WAL mode and `metadata.create_all()` initialization
- [X] T005 [P] Create Run ORM model in `backend/src/models/run.py` with fields: id (UUID), goal, status, reason, total_cost, max_steps, max_cost_usd, started_at, finished_at
- [X] T006 [P] Create Step ORM model in `backend/src/models/step.py` with fields: id (UUID), run_id (FK), step_number, tool_name, args_json, result_json, cost, created_at; with UNIQUE(run_id, step_number) constraint
- [X] T007 [P] Create tool registry in `backend/src/services/tool_registry.py` with keyword-based relevance scoring (top-K selection, default K=5) and sample tool definitions
- [X] T008 [P] Create LLM interface in `backend/src/services/llm.py` with deterministic mock LLM that reads from scenario JSON files and returns structured responses (tool call or final answer)
- [X] T009 Create safety guards in `backend/src/services/guards.py` with four check functions: step_cap (default 20), cost_cap (sum vs max_cost_usd), stuck detector (tool_name + args_hash repeating 3 times), and timeout (60s via asyncio.wait_for)
- [X] T010 Create tool runtime in `backend/src/services/tool_runtime.py` with tool dispatch, structured error returns `{ok, data, error: {code, message, recoverable}}`, and bounded retry logic (max 3 attempts for recoverable errors)
- [X] T011 Create agent loop orchestration in `backend/src/services/agent_loop.py` that: selects candidate tools via registry, calls LLM with goal + past steps + tools, dispatches tool calls via runtime, checks guards each iteration, and persists steps atomically
- [X] T012 Create FastAPI app entry point in `backend/src/main.py` with lifespan event for DB initialization and router registration
- [X] T013 [P] Create Pydantic schemas in `backend/src/api/schemas.py`: RunCreate (goal, max_steps, max_cost_usd), RunResponse (run_id), RunDetail (full state + steps), RunSummary (list item), RunListResponse (paginated)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Start an Agent Run (Priority: P1) 🎯 MVP

**Goal**: User submits a goal and receives a run ID; the agent loop executes in the background with all four safety guards enforced.

**Independent Test**: Submit a goal via POST /runs, verify run ID returned, verify run reaches a terminal state with correct reason.

### Tests for User Story 1 ⚠️

- [X] T014 [P] [US1] Create unit tests for safety guards in `backend/tests/unit/test_guards.py`: test step_cap termination, cost_cap termination, and guard check functions
- [X] T015 [P] [US1] Create unit tests for tool retrieval in `backend/tests/unit/test_tool_retrieval.py`: test keyword scoring, top-K selection, and edge cases
- [X] T016 [P] [US1] Create unit tests for stuck detection in `backend/tests/unit/test_stuck_detection.py`: test 3-repeat detection with args hashing and non-stuck sequences
- [X] T017 [P] [US1] Create unit tests for tool runtime in `backend/tests/unit/test_tool_runtime.py`: test dispatch, error classification, and retry logic
- [X] T018 [US1] Create pytest fixtures in `backend/tests/conftest.py`: async DB session fixture, mock LLM fixture with scenario loading, sample tool registry fixture

### Implementation for User Story 1

- [X] T019 [US1] Implement POST /runs endpoint in `backend/src/api/runs.py`: validate goal (non-empty, max 4096 chars), create Run record with status=running, spawn agent loop as asyncio background task, return 202 with run_id
- [X] T020 [US1] Create mock LLM scenario files in `backend/tests/scenarios/`: success scenario (2-3 tool calls then final answer), step_cap scenario, cost_cap scenario, stuck scenario, tool_error_recoverable scenario

**Checkpoint**: User Story 1 fully functional — goal submission, agent loop execution, guard enforcement, and atomic step persistence

---

## Phase 4: User Story 2 - View Run Status and Details (Priority: P1)

**Goal**: User queries a run by ID and receives full state including all steps, results, and termination reason.

**Independent Test**: Start a run, wait for completion, query by ID and verify all fields (goal, status, reason, total_cost, steps with tool_name, args, result, cost).

### Implementation for User Story 2

- [X] T021 [US2] Implement GET /runs/{run_id} endpoint in `backend/src/api/runs.py`: query Run by UUID, eagerly load Steps ordered by step_number, serialize to RunDetail schema; return 404 if not found
- [X] T022 [US2] Add in-progress run response handling in `backend/src/api/runs.py`: return partial steps and status=running when run is still executing

**Checkpoint**: User Stories 1 and 2 both functional — runs can be started and their full state retrieved

---

## Phase 5: User Story 3 - Browse Recent Runs (Priority: P2)

**Goal**: User views a paginated list of recent runs ordered by most recent first.

**Independent Test**: Create multiple runs, query GET /runs with limit/offset, verify correct ordering and pagination metadata.

### Implementation for User Story 3

- [X] T023 [US3] Implement GET /runs endpoint in `backend/src/api/runs.py`: query runs ordered by started_at DESC, with limit (default 20, max 100) and offset pagination, return RunListResponse with total count
- [X] T024 [US3] Add performance optimization for run listing: ensure `idx_steps_run_id` index exists and query uses efficient LIMIT/OFFSET

**Checkpoint**: All P1 and P2 stories functional

---

## Phase 6: User Story 4 - Handle Tool Errors Gracefully (Priority: P2)

**Goal**: Tool failures are classified as recoverable or non-recoverable; recoverable errors are retried up to 3 times; non-recoverable errors are surfaced to the agent.

**Independent Test**: Simulate tool failures (both types) and verify retry behavior, error surfacing, and run termination when retries exhausted.

### Implementation for User Story 4

- [X] T025 [US4] Enhance tool runtime in `backend/src/services/tool_runtime.py`: implement retry loop with bounded attempts (max 3), exponential backoff, and termination with reason=error when all retries fail
- [X] T026 [US4] Add non-recoverable error surfacing in `backend/src/services/agent_loop.py`: when tool returns non-recoverable error, include error in step context passed to LLM for alternative decision-making
- [X] T027 [US4] Create additional test scenarios in `backend/tests/scenarios/`: tool_error_nonrecoverable scenario (agent switches tool), tool_error_exhausted scenario (run terminates with error reason)

**Checkpoint**: All user stories functional with robust error handling

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T028 [P] Run all quickstart.md validation scenarios (8 curl-based tests) to verify end-to-end correctness
- [X] T029 Run ruff and mypy across `backend/src/` to ensure Constitution Principle I compliance
- [X] T030 [P] Add `backend/src/api/__init__.py` router registration and lifespan events for background task cleanup
- [X] T031 Verify concurrent run safety: test 100 concurrent POST /runs calls with SQLite WAL mode, confirm no data corruption
- [X] T032 Add `backend/src/db/init.py` module for standalone database initialization (`python -m backend.src.db.init`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 and US2 (P1) can proceed in parallel after Phase 2
  - US3 (P2) depends on US2 (shares runs.py endpoint file)
  - US4 (P2) depends on US1 (extends agent_loop.py and tool_runtime.py)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P1)**: Can start after Foundational - Reads from same DB as US1 but no code dependency
- **US3 (P2)**: Depends on US2 (same `runs.py` file) - should be implemented after US2
- **US4 (P2)**: Depends on US1 (extends `tool_runtime.py` and `agent_loop.py`) - should be implemented after US1

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration

### Parallel Opportunities

- T003, T005, T006 can run in parallel within Phase 2
- T007, T008 can run in parallel within Phase 2
- T014, T015, T016, T017 can run in parallel within Phase 3
- T021, T022 can run in parallel within Phase 4
- T025, T026 can run in parallel within Phase 6
- T028, T029, T030 can run in parallel within Phase 7

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for US1 together:
Task: "Unit tests for safety guards in backend/tests/unit/test_guards.py"
Task: "Unit tests for tool retrieval in backend/tests/unit/test_tool_retrieval.py"
Task: "Unit tests for stuck detection in backend/tests/unit/test_stuck_detection.py"
Task: "Unit tests for tool runtime in backend/tests/unit/test_tool_runtime.py"

# Launch scenario files together:
Task: "Mock LLM scenario files in backend/tests/scenarios/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test US1 independently with quickstart scenarios 1, 5, 6, 7
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP!
3. Add User Story 2 → Test independently → Run details available
4. Add User Story 3 → Test independently → Run history available
5. Add User Story 4 → Test independently → Robust error handling
6. Polish → Lint, type-check, concurrent safety, quickstart validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (POST /runs, agent loop, tests)
   - Developer B: User Story 2 (GET /runs/{id})
3. After P1 stories done:
   - Developer A: User Story 4 (error handling)
   - Developer B: User Story 3 (run listing)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution Principle II requires: unit tests for guards, tool retrieval, stuck detection, retry logic; one integration test for full run
