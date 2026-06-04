# Research: Agent Loop API

**Date**: 2026-06-04
**Status**: Complete

## 1. Mock LLM Design

**Decision**: Deterministic mock LLM driven by scenario files

**Rationale**: The constitution (Principle II) requires deterministic testing. The mock LLM must be able to exercise every guard: goals that trigger 2-5 tool calls, goals that fire the stuck detector, goals that exceed the cost cap, and tool calls that fail then succeed on retry. Scenario files (JSON/YAML) define sequences of LLM responses, each specifying either a tool call (tool_name, arguments, mock cost) or a final answer.

**Alternatives considered**:
- Random LLM: Non-deterministic, fails the testing requirement
- Real LLM API: Adds cost, latency, and non-determinism; unsuitable for unit tests
- Hard-coded responses in test code: Less flexible than scenario files; harder to share scenarios across tests

**Implementation approach**: Each scenario is a JSON file with an array of response objects. The mock LLM maintains a pointer into the array and returns the next response on each call. The `conftest.py` fixture loads scenarios and injects the mock LLM into the agent loop.

## 2. Tool Retrieval (Top-K Selection)

**Decision**: Keyword/scoring-based relevance matching

**Rationale**: The assessment states "a keyword match, a BM25 implementation or a simple embedding-based approach are all fine." With ~10 tools, keyword matching between the goal text and each tool's name + description is sufficient and avoids the complexity of BM25 or embedding models.

**Alternatives considered**:
- BM25: More sophisticated but adds a dependency (rank_bm25) and complexity for marginal gain at 10 tools
- Embeddings: Requires an embedding model (sentence-transformers or API call); overkill for 10 tools and adds latency

**Implementation approach**: Score each tool by counting keyword overlaps between the goal text (tokenized, lowercased) and the tool's name + description. Return the top-K (default 5) tools sorted by score. This is a pure function with no I/O, making it easy to test.

## 3. Persistence Layer

**Decision**: async SQLAlchemy 2.0 with SQLite

**Rationale**: The SPEC.md specifies async SQLAlchemy and SQLite. The constitution (SC-007) requires atomic step persistence. async SQLAlchemy provides transactional guarantees with SQLite while not blocking the asyncio event loop.

**Alternatives considered**:
- Synchronous SQLAlchemy: Would block the event loop during I/O, causing latency issues under concurrent runs
- Raw aiosqlite: Loses ORM benefits (model definitions, migrations, type safety)
- PostgreSQL: Overkill for single-tenant assessment; SQLite is specified

**Implementation approach**: Use SQLAlchemy 2.0 async ORM with `AsyncSession`. Each step write is wrapped in a transaction. The `runs` and `steps` tables are defined as ORM models. Database initialization uses `metadata.create_all()` for simplicity (no Alembic needed for this scope).

## 4. Tool Error Contract & Retry Logic

**Decision**: Structured error returns with bounded retries for recoverable errors

**Rationale**: The constitution (Principle IV) and SPEC.md define the error contract: `{ok, data, error: {code, message, recoverable}}`. The runtime checks `error.recoverable` to decide whether to retry (up to a bounded number of attempts, default 3) or surface the error to the agent for alternative decision-making.

**Alternatives considered**:
- Raw exceptions: Loses structured error classification; harder to test retry logic
- Fixed retry count for all errors: Doesn't distinguish between transient and semantic failures

**Implementation approach**: The `tool_runtime.py` module wraps tool execution in a try/except, converts exceptions to the structured format, and handles retries for recoverable errors. After max retries, the error is surfaced to the agent. If the agent cannot proceed, the run terminates with reason `error`.

## 5. Safety Guards Implementation

**Decision**: Four independent guard checks evaluated each loop iteration

**Rationale**: The constitution (Principle IV) requires four guards: step cap, cost cap, stuck detector, wall-clock timeout. Each guard is a pure check function that returns (should_terminate, reason). The agent loop checks all guards before each step.

**Alternatives considered**:
- Guards as middleware: More complex; inline checks are simpler and more testable
- Async timeout with signal: Linux signals don't work well in asyncio; use `asyncio.wait_for` with 60s timeout

**Implementation approach**:
- Step cap: Compare step count against `max_steps` (default 20)
- Cost cap: Sum step costs against `max_cost_usd`; terminate when exceeded
- Stuck detector: Track (tool_name, args_hash) pairs; terminate if any pair repeats 3 times
- Timeout: Wrap the entire agent loop in `asyncio.wait_for(..., timeout=60)`; catch `asyncio.TimeoutError` and terminate with reason `timeout`

## 6. FastAPI Concurrent Run Handling

**Decision**: Each POST /runs spawns an asyncio task for the agent loop

**Rationale**: The SPEC.md requires 100 concurrent runs without data corruption. FastAPI is async-native; each request handler runs as a coroutine. The agent loop runs in the background via `asyncio.create_task()`, and the response returns immediately with the run_id.

**Alternatives considered**:
- Celery/RQ worker queue: Overkill for single-tenant; adds infrastructure complexity
- Sequential processing: Cannot meet the 100 concurrent runs requirement

**Implementation approach**: The POST /runs handler creates the run record, then spawns the agent loop as a background task. The GET /runs/{id} handler polls the run state from the database. SQLite's WAL mode is enabled for concurrent read/write safety.
