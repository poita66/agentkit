# UI Contract: Component Interface

## GoalInput

**Purpose**: Text input for entering a goal and submitting it.

**Props**:
- `onSubmit(goal: string, options?: { max_steps?: number; max_cost_usd?: number }): void` — called when user submits
- `disabled: boolean` — whether the input is disabled (e.g., during submission)

**Behavior**:
- Shows a single text input with placeholder text
- Hides technical parameters (`max_steps`, `max_cost_usd`) behind an "Advanced" toggle
- Validates input is non-empty before enabling submit
- Disables input and button while submission is in progress

---

## RunList

**Purpose**: Displays a list of past runs for browsing.

**Props**:
- `onSelectRun(runId: string): void` — called when user clicks a run

**Behavior**:
- Fetches runs via `GET /runs?limit=20`
- Each item shows: goal (truncated), outcome indicator (color-coded badge), relative timestamp
- Outcome indicators are visually distinct: green for success, amber for capped/stuck, red for error/timeout, blue for running
- Shows empty state with guidance when no runs exist
- Supports pagination (load more / next page)

---

## RunDetail

**Purpose**: Full view of a single run with steps and outcome.

**Props**:
- `runId: string` — the run to display
- `onBack(): void` — called to return to the list

**Behavior**:
- Fetches run details via `GET /runs/{runId}`
- While running: polls every 1.5s, shows live step updates
- When complete: shows final answer prominently at top
- Shows outcome message (human-readable) with reason code as small label
- Steps displayed as expandable cards (friendly summary default, raw details on expand)
- Shows loading state on initial load (bounded to 10s)
- Shows error state if run not found or fetch fails

---

## StepCard

**Purpose**: Displays a single step with expandable details.

**Props**:
- `step: StepDetail` — step data
- `stepNumber: number` — for ordering

**Behavior**:
- Default view: friendly description (e.g., "Searching documents for 'Q3 report'")
- Expanded view: raw tool name, arguments (formatted JSON), result, cost, timestamp
- Final answer steps (where `tool_name` is null) displayed with distinct styling

---

## StatusBadge

**Purpose**: Visual indicator for run outcome.

**Props**:
- `reason: string | null` — termination reason or null for running
- `status: string` — running or completed

**Behavior**:
- Color-coded: green (succeeded), amber (step_cap, cost_cap, stuck), red (error, timeout), blue (running)
- Accessible: uses ARIA labels, not just color

---

## LoadingIndicator

**Purpose**: Shows loading state with bounded timeout.

**Props**:
- `message: string` — text to display (e.g., "Starting your run...")

**Behavior**:
- Shows animated indicator with message
- After 10 seconds, switches to an error state with retry option

---

## ErrorMessage

**Purpose**: Displays error states with actionable guidance.

**Props**:
- `title: string` — error title
- `message: string` — explanation
- `onRetry?(): void` — optional retry button

**Behavior**:
- Shows title, message, and optional retry button
- Used for: backend unavailable, fetch timeout, run not found
