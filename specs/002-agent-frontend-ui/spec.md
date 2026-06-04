# Feature Specification: Agent Frontend UI

**Feature Branch**: `002-agent-frontend-ui`

**Created**: 2026-06-04

**Status**: Draft

**Input**: User description: "Add a frontend for the agent backend API as defined in @SPEC.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit a Goal and See the Agent Work (Priority: P1)

A user types a goal in plain language into a text input and submits it. The system starts an agent run and immediately shows progress as the agent works through steps. Each step appears as a friendly, human-readable description of what the agent is doing. When the run completes, the final answer appears prominently at the top of the screen.

**Why this priority**: This is the core user journey — without it, the frontend provides no value. It covers the primary reason a user visits the application.

**Independent Test**: Can be fully tested by entering a goal, submitting it, observing step-by-step progress updates, and confirming the final answer displays prominently upon completion.

**Acceptance Scenarios**:

1. **Given** the user is on the main screen, **When** the user types a goal and submits it, **Then** the system starts a new run and begins showing progress
2. **Given** a run is in progress, **When** new steps complete, **Then** each step appears as a friendly description (e.g., "Searching documents for 'Q3 report'") rather than raw tool call data
3. **Given** a run completes successfully, **When** the final answer is available, **Then** it is displayed prominently as the most visible element on screen
4. **Given** a run is in progress, **When** the user views a step, **Then** the step shows a friendly summary by default with an option to expand and see raw tool arguments and results

---

### User Story 2 - Understand Why a Run Ended (Priority: P1)

When a run ends for any reason — success, budget exceeded, step limit reached, stuck in a loop, timeout, or error — the user sees a clear, human-readable explanation of what happened. The message tells the user what occurred and, where relevant, what they can do about it.

**Why this priority**: Users need to understand outcomes to trust the system and take corrective action. A run ending with an opaque error code erodes confidence.

**Independent Test**: Can be fully tested by triggering each termination reason (via backend runs) and verifying the frontend displays the appropriate human-readable message.

**Acceptance Scenarios**:

1. **Given** a run ended due to the cost cap, **When** the user views the run result, **Then** the system displays a message like "Reached the budget limit for this run" with the raw reason code available as a small label
2. **Given** a run ended because the agent was stuck, **When** the user views the run result, **Then** the system displays a message explaining the agent kept repeating the same action
3. **Given** a run ended due to the step cap, **When** the user views the run result, **Then** the system displays a message explaining the step limit was reached
4. **Given** a run timed out, **When** the user views the run result, **Then** the system displays a message explaining the time limit was exceeded
5. **Given** a run ended with an error, **When** the user views the run result, **Then** the system displays a message explaining what went wrong

---

### User Story 3 - Browse and Reopen Past Runs (Priority: P2)

A user views a list of past runs showing each run's goal, an outcome indicator (success, capped, stuck, errored), and a relative timestamp. Clicking a run reopens its full detail view with steps and results.

**Why this priority**: Enables users to review history, compare outcomes, and revisit previous work without re-entering goals.

**Independent Test**: Can be fully tested by creating multiple runs with different outcomes and verifying the list displays them correctly with accurate outcome indicators and timestamps.

**Acceptance Scenarios**:

1. **Given** multiple runs exist, **When** the user views the run list, **Then** each run shows its goal, an outcome indicator, and a relative timestamp
2. **Given** the user is viewing the run list, **When** the user clicks a past run, **Then** the system opens that run's detail view with steps and results
3. **Given** runs have different outcomes, **When** the user views the run list, **Then** each outcome type is visually distinct (not just different words)

---

### User Story 4 - Live Updates During a Run (Priority: P2)

While a run is in progress, the UI updates automatically to show new steps and status changes without the user needing to refresh or take any action.

**Why this priority**: Real-time feedback builds trust and keeps the user engaged. A static screen during a run feels broken.

**Independent Test**: Can be fully tested by starting a run with multiple steps and verifying the UI updates automatically as each step completes.

**Acceptance Scenarios**:

1. **Given** a run is in progress, **When** new steps complete on the server, **Then** the UI updates within 2 seconds to show the new steps
2. **Given** a run transitions from in-progress to completed, **When** the status changes, **Then** the UI reflects the new status and shows the final result

---

### User Story 5 - Handle Loading, Empty, and Error States (Priority: P3)

The UI gracefully handles situations where no runs exist yet, when the system is loading data, and when something goes wrong connecting to the backend.

**Why this priority**: These states are encountered frequently during normal use and poor handling creates confusion or frustration.

**Independent Test**: Can be fully tested by visiting the app with no runs, disconnecting the backend, and observing appropriate messaging in each case.

**Acceptance Scenarios**:

1. **Given** no runs exist, **When** the user opens the app, **Then** the user sees a clear empty state with guidance on how to start
2. **Given** the backend is unavailable, **When** the user tries to submit a goal, **Then** the user sees a clear error message explaining the issue
3. **Given** data is loading, **When** the UI is fetching run details, **Then** the user sees a loading indicator that does not spin indefinitely

---

### Edge Cases

- What happens when the user submits an empty or whitespace-only goal?
- What happens when the user navigates away from a run mid-execution and returns?
- What happens when multiple runs are in progress simultaneously?
- What happens when the user loses network connectivity during a run?
- What happens when a run has an unusually large number of steps?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a single text input for the user to enter a goal in plain language
- **FR-002**: System MUST hide technical parameters (step limit, cost limit) from the default view, either omitting them entirely or placing them behind an advanced toggle
- **FR-003**: System MUST send sensible default values for technical parameters when creating a run
- **FR-004**: System MUST display each agent step as a friendly, human-readable description of the action being taken
- **FR-005**: System MUST allow expanding individual steps to reveal raw tool arguments and results for power users
- **FR-006**: System MUST display the final answer prominently when a run succeeds, making it the most visible element on screen
- **FR-007**: System MUST translate each termination reason code into a human-readable, actionable message
- **FR-008**: System MUST keep the raw termination reason code visible as a small label alongside the human-readable message
- **FR-009**: System MUST provide a list of past runs showing goal, outcome indicator, and relative timestamp
- **FR-010**: System MUST make each outcome type (success, capped, stuck, errored, timeout) visually distinct
- **FR-011**: System MUST allow clicking a past run to reopen its full detail view
- **FR-012**: System MUST update the UI automatically while a run is in progress, reflecting new steps and status changes
- **FR-013**: System MUST handle loading states with appropriate indicators and no infinite spinners
- **FR-014**: System MUST handle empty states with clear guidance on next steps
- **FR-015**: System MUST handle error states (e.g., backend unavailable) with clear, actionable messages
- **FR-016**: System MUST use semantic HTML elements for accessibility
- **FR-017**: System MUST be keyboard navigable with preserved focus indicators
- **FR-018**: System MUST maintain adequate color contrast for readability

### Key Entities

- **Run**: A single agent execution with a goal, status, termination reason, steps, and timing. The frontend displays runs in list and detail views.
- **Step**: A single iteration within a run, containing tool information, arguments, results, and cost. Steps are displayed with friendly summaries and expandable raw details.
- **Run List**: A collection of recent runs with summary information used for browsing and navigation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can submit a goal and see the first progress update within 3 seconds
- **SC-002**: Users can identify a run's outcome at a glance from the run list without reading text
- **SC-003**: The final answer is visible without scrolling when a run completes successfully
- **SC-004**: New steps appear in the UI within 2 seconds of completing on the server
- **SC-005**: 100% of termination reasons are displayed with human-readable messages
- **SC-006**: Users can navigate the entire interface using only a keyboard
- **SC-007**: All interactive elements have visible focus indicators
- **SC-008**: Color contrast meets WCAG AA standards for all text and UI elements
- **SC-009**: Loading states resolve or show an error within 10 seconds — no infinite spinners
- **SC-010**: Users can find and reopen a past run within 3 clicks from the main screen

## Assumptions

- The backend API described in the Agent Loop API specification (specs/001-agent-loop-api) is available and functional
- The frontend communicates with the backend over HTTP, with the backend URL configurable
- The user is a non-technical person who may not understand concepts like "tool calls" or "API endpoints"
- The application runs in a modern web browser with JavaScript enabled
- Users have a stable internet connection during normal use
- The frontend runs on a separate port or path from the backend during development
- Runs are single-tenant — there is no need for user authentication or multi-user isolation
