# Implementation Plan: Agent Loop RESTful API with Persistence

**Branch**: `001-agent-loop-api` | **Date**: 2026-06-04 | **Spec**: `/specs/001-agent-loop-api/spec.md`

**Input**: Feature specification from `/specs/001-agent-loop-api/spec.md`

## Summary

Build a RESTful API backend (Python/FastAPI) that implements an LLM agent loop with tool dispatch, safety guards (step cap, cost cap, stuck detection, timeout), and SQLite persistence. The frontend (React/Vite/TypeScript) provides a chat-style UI for goal submission, live progress, and run history. This plan covers the backend API and agent framework; the frontend is a separate concern.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)

**Primary Dependencies**: FastAPI, async SQLAlchemy, SQLite, pytest (backend); React, Vite, Tailwind CSS, Shadcn UI, Vitest (frontend)

**Storage**: SQLite with async SQLAlchemy ORM

**Testing**: pytest (backend), Vitest (frontend)

**Target Platform**: Linux server

**Project Type**: web-service (backend API + frontend UI)

**Performance Goals**: Run creation <2s, run retrieval <1s, run list <2s for 1000 runs, 100 concurrent runs without data corruption

**Constraints**: 60s wall-clock hard ceiling per run, 20 step default cap, cost cap configurable per run, atomic step persistence

**Scale/Scope**: Single-tenant, ~10 tools in registry, ~5 candidate tools per LLM call, up to 1000 runs in history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | Python with ruff + mypy; TypeScript with biome + tsc --noEmit. Clear module boundaries planned. |
| II. Testing Standards | PASS | Unit tests for tool-retrieval ranking, stuck detection, caps, retry logic. Integration test for full run end-to-end with mock LLM. |
| III. User Experience Consistency | N/A | Frontend is a separate feature; this plan covers backend API only. |
| IV. Performance Requirements | PASS | Four safety guards (step_cap, cost_cap, stuck, timeout) with structured error contract. Bounded retries. |

## Project Structure

### Documentation (this feature)

```text
specs/001-agent-loop-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── run.py            # Run ORM model
│   │   └── step.py           # Step ORM model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_loop.py     # Core agent loop orchestration
│   │   ├── tool_registry.py  # Tool registry and retrieval
│   │   ├── tool_runtime.py   # Tool dispatch, error handling, retries
│   │   ├── guards.py         # Safety guards (step, cost, stuck, timeout)
│   │   └── llm.py            # LLM interface (mock + real)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── runs.py           # POST /runs, GET /runs, GET /runs/{id}
│   │   └── schemas.py        # Pydantic request/response models
│   └── db/
│       ├── __init__.py
│       └── session.py        # Async database session management
└── tests/
    ├── unit/
    │   ├── test_guards.py
    │   ├── test_tool_runtime.py
    │   ├── test_tool_retrieval.py
    │   └── test_stuck_detection.py
    ├── integration/
    │   └── test_full_run.py
    └── conftest.py

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Backend/frontend split as defined in SPEC.md. Backend uses FastAPI with async SQLAlchemy for SQLite persistence. Frontend is React/Vite/TypeScript (separate feature). The backend is the focus of this implementation plan.

## Research Decisions

### Mock LLM Design
- **Decision**: Deterministic mock LLM that reads from a scenario file to produce predictable tool calls and final answers
- **Rationale**: Required for deterministic testing; must exercise every guard scenario
- **Alternatives considered**: Random LLM (non-deterministic), real LLM API (cost, latency, non-deterministic)

### Tool Retrieval Approach
- **Decision**: Simple keyword/scoring-based relevance matching between goal text and tool descriptions
- **Rationale**: Assessment states keyword match, BM25, or embedding-based are all acceptable; keyword is simplest and sufficient for ~10 tools
- **Alternatives considered**: BM25 (more complex, marginal benefit at 10 tools), embeddings (requires embedding model, overkill)

### Persistence Strategy
- **Decision**: async SQLAlchemy with SQLite, one transaction per step write
- **Rationale**: Atomic step persistence required (SC-007); async avoids blocking the event loop during I/O
- **Alternatives considered**: Synchronous SQLAlchemy (blocks event loop), raw SQLite (loses ORM benefits)

### Error Classification
- **Decision**: Tool errors return structured `{ok, data, error: {code, message, recoverable}}` per spec
- **Rationale**: Required by constitution Principle IV and SPEC.md tool error contract
- **Alternatives considered**: Raw exceptions (loses structured error info), HTTP status codes only (insufficient for retry logic)

## Complexity Tracking

No violations to report. The design follows the constitution principles directly.
