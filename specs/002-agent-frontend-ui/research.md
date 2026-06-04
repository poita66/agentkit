# Research: Agent Frontend UI

## Decision: Real-time updates via polling

**Rationale**: The backend API (FastAPI) does not expose Server-Sent Events or WebSocket endpoints. Adding SSE would require backend changes, which is out of scope for this feature. Polling `GET /runs/{run_id}` at 1-2 second intervals during active runs is the simplest approach that meets the 2-second update requirement (SC-004).

**Alternatives considered**:
- SSE: Would require backend modification; ruled out
- WebSocket: Same as SSE; ruled out
- Long polling: More complex than simple polling for this scale; ruled out

**Implementation**: Custom `useRun` hook that polls every 1.5s while `status === "running"`, stops polling when status is terminal. Includes a 10-second timeout on individual fetch requests to prevent hung connections.

---

## Decision: CSS approach — plain CSS with custom properties

**Rationale**: The project is a small single-page app (~5-8 components). A CSS framework like Tailwind adds build complexity and bundle size for minimal benefit at this scale. Plain CSS with custom properties (CSS variables) for theming provides adequate structure while keeping the build simple.

**Alternatives considered**:
- Tailwind CSS: Overkill for this scope; adds PostCSS dependency
- CSS Modules: Adds complexity without benefit for this component count
- Styled-components: Runtime overhead; not needed for this scope

**Implementation**: Single `global.css` file with CSS custom properties for colors, spacing, and typography. Component-scoped styles using BEM-like class names.

---

## Decision: Backend URL via Vite environment variable

**Rationale**: The spec states "the backend URL [is] configurable". Vite's `import.meta.env.VITE_API_URL` provides a clean build-time configuration. Falls back to `http://localhost:8000` for local development.

**Alternatives considered**:
- Hardcoded URL: Violates the configurable requirement
- Runtime config file: Adds complexity; build-time env is sufficient for single-tenant

**Implementation**: `.env.development` with `VITE_API_URL=http://localhost:8000`. The `api/client.ts` module reads `import.meta.env.VITE_API_URL` and prepends it to all fetch calls.

---

## Decision: Step friendly descriptions via tool name mapping

**Rationale**: The spec requires "a friendly, human-readable description of the action being taken" (FR-004). Tool calls contain `tool_name` and `args`. A mapping from known tool names to template strings (with arg substitution) produces readable descriptions. Unknown tools fall back to a generic "Using {tool_name}" message.

**Alternatives considered**:
- LLM-generated descriptions: Too slow and expensive for real-time display
- Static descriptions per tool: Same as mapping approach; chosen for simplicity

**Implementation**: `formatStep.ts` exports a `describeStep(step): string` function with a `TOOL_DESCRIPTIONS` map. Examples:
- `search_documents` → `Searching documents for "{query}"`
- `read_file` → `Reading file "{path}"`
- `write_file` → `Writing file "{path}"`
- Unknown → `Using {tool_name}`

---

## Decision: Termination reason messages

**Rationale**: FR-007 requires translating each termination reason code into a human-readable, actionable message. The backend returns one of: `step_cap`, `cost_cap`, `stuck`, `timeout`, `error`, `succeeded`.

**Implementation**: `formatOutcome.ts` exports a `describeOutcome(reason, totalCost, maxCostUsd): string` function:
- `succeeded` → "Goal completed successfully"
- `step_cap` → "Reached the step limit (20 steps). Try a more specific goal."
- `cost_cap` → `Reached the budget limit ($0.50)`
- `stuck` → "The agent kept repeating the same action. Try rephrasing the goal."
- `timeout` → "The run exceeded the time limit (60 seconds). Try a simpler goal."
- `error` → "An error occurred during the run."

---

## Decision: Routing — React Router with two routes

**Rationale**: The spec requires a main screen (goal input + run list) and a detail view for individual runs. React Router DOM provides declarative routing with URL state.

**Alternatives considered**:
- Single-page with state-only navigation: Loses URL state; can't bookmark a run
- Hash routing: React Router's default is browser history; preferred for SPA

**Implementation**:
- `/` → Home page with `GoalInput` + `RunList`
- `/runs/:runId` → `RunDetail` with steps, final answer, and outcome

---

## Decision: TypeScript strict mode

**Rationale**: Constitution Principle I requires code to be "properly typed" and `tsc --noEmit` must pass. TypeScript strict mode ensures null safety, proper typing of API responses, and catches common bugs at compile time.

**Alternatives considered**:
- JavaScript: Violates constitution
- Relaxed TypeScript: Would allow `any` types; violates constitution

**Implementation**: `tsconfig.json` with `"strict": true`, `"noUncheckedIndexedAccess": true`. API response types in `api/types.ts` mirror backend Pydantic schemas exactly.
