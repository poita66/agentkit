# Feature Specification: Agent Loop RESTful API with Persistence

**Feature Branch**: `001-agent-loop-api`

**Created**: 2026-06-04

**Status**: Draft

**Input**: User description: "Agent loop RESTful API with persistence"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start an Agent Run (Priority: P1)

A user submits a goal in plain language and receives a unique run identifier. The system begins processing the goal through the agent loop, executing tool calls as needed until the goal is achieved or a safety guard terminates the run.

**Why this priority**: This is the core value proposition — without the ability to start and execute agent runs, the system provides no value.

**Independent Test**: Can be fully tested by submitting a goal via the API endpoint and verifying that a run ID is returned and the run eventually reaches a terminal state.

**Acceptance Scenarios**:

1. **Given** the system is running, **When** a user submits a goal with valid parameters, **Then** the system returns a unique run identifier and begins processing
2. **Given** a run is processing, **When** the agent completes the goal successfully, **Then** the run status changes to succeeded with a final answer
3. **Given** a run is processing, **When** the step limit is reached, **Then** the run terminates with a step_cap reason
4. **Given** a run is processing, **When** the cost limit is exceeded, **Then** the run terminates with a cost_cap reason
5. **Given** a run is processing, **When** the same tool call repeats three times, **Then** the run terminates with a stuck reason
6. **Given** a run is processing, **When** sixty seconds elapse, **Then** the run terminates with a timeout reason

---

### User Story 2 - View Run Status and Details (Priority: P1)

A user queries the status of a specific run and receives the current state, including all executed steps, tool calls, results, and the final outcome if completed.

**Why this priority**: Users need visibility into what the agent is doing to trust the system and understand outcomes.

**Independent Test**: Can be fully tested by starting a run, waiting for completion, and querying the run details to verify all steps and the final state are returned accurately.

**Acceptance Scenarios**:

1. **Given** a run has completed, **When** a user queries the run by ID, **Then** the system returns the full run state including goal, status, reason, all steps with tool names, arguments, results, and costs
2. **Given** a run is still in progress, **When** a user queries the run by ID, **Then** the system returns the current status and steps executed so far
3. **Given** a run ID does not exist, **When** a user queries the run, **Then** the system returns an appropriate error

---

### User Story 3 - Browse Recent Runs (Priority: P2)

A user views a list of recent runs, ordered by most recent first, with summary information including goal, outcome, and timing.

**Why this priority**: Enables users to review history and identify runs of interest without needing to know specific run IDs.

**Independent Test**: Can be fully tested by creating multiple runs and verifying the list endpoint returns them in the correct order with accurate summary data.

**Acceptance Scenarios**:

1. **Given** multiple runs exist, **When** a user requests the run list, **Then** the system returns runs ordered by most recent first with goal, status, and timing information
2. **Given** many runs exist, **When** a user requests the run list, **Then** the system returns a paginated result set

---

### User Story 4 - Handle Tool Errors Gracefully (Priority: P2)

When a tool call fails, the system determines whether the error is recoverable and either retries the call or surfaces the error to the agent for alternative decision-making.

**Why this priority**: Tool failures are expected in real-world usage; the system must handle them without crashing or losing state.

**Independent Test**: Can be fully tested by simulating tool failures (both recoverable and non-recoverable) and verifying appropriate retry behavior or error surfacing.

**Acceptance Scenarios**:

1. **Given** a tool call returns a recoverable error, **When** the runtime processes the result, **Then** the system retries the tool call up to a bounded number of attempts
2. **Given** a tool call returns a non-recoverable error, **When** the runtime processes the result, **Then** the system surfaces the error to the agent for alternative decision-making
3. **Given** a tool call fails on all retry attempts, **When** the retry limit is reached, **Then** the run terminates with an error reason

---

### Edge Cases

- What happens when a goal is empty or contains only whitespace?
- What happens when a tool call returns malformed or incomplete results?
- How does the system handle concurrent runs for the same user?
- What happens if the persistence layer is unavailable during a run?
- How does the system handle goals that require more tools than available in the registry?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a goal submission with optional step limit and cost limit parameters, returning a unique run identifier
- **FR-002**: System MUST maintain a tool registry containing the available tools the agent can use
- **FR-003**: System MUST select a subset of the most relevant tools for each goal before invoking the language model
- **FR-004**: System MUST execute the agent loop: calling the language model with goal context, past steps, and candidate tools, then dispatching tool calls or recording final answers
- **FR-005**: System MUST enforce a step cap (defaulting to 20 steps) that terminates the run when exceeded
- **FR-006**: System MUST enforce a cost cap that sums the cost of each step and terminates the run when the budget is exceeded
- **FR-007**: System MUST detect when the same tool call (by tool name and arguments) repeats three times and terminate the run as stuck
- **FR-008**: System MUST enforce a wall-clock timeout of 60 seconds per run
- **FR-009**: System MUST record each step with tool name, arguments, result, cost, and timestamp
- **FR-010**: System MUST persist run state (goal, status, termination reason, total cost, start and end times) so that completed runs are retrievable
- **FR-011**: System MUST return run details including all steps when queried by run ID
- **FR-012**: System MUST return a paginated list of recent runs ordered by most recent first
- **FR-013**: System MUST classify tool errors as recoverable or non-recoverable and handle each appropriately
- **FR-014**: System MUST bound the number of retry attempts for recoverable tool errors
- **FR-015**: System MUST assign a termination reason from a fixed set: step_cap, cost_cap, stuck, timeout, error, or succeeded

### Key Entities

- **Run**: Represents a single agent execution. Contains the goal, current status, termination reason, total cost, and timing information. A run progresses through states from initiation to a terminal state.
- **Step**: Represents a single iteration within a run. Contains the step number, tool name (or final answer indicator), arguments, result, cost, and creation timestamp. Steps are ordered sequentially within a run.
- **Tool**: Represents a capability the agent can invoke. Contains a name, description, and parameters. Tools return structured results indicating success or failure with error classification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can submit a goal and receive a run identifier within 2 seconds
- **SC-002**: Runs terminated by safety guards report the correct termination reason 100% of the time
- **SC-003**: Completed runs are retrievable by ID with full step history within 1 second
- **SC-004**: The system can handle 100 concurrent runs without data corruption or lost state
- **SC-005**: Tool retry logic successfully recovers from transient errors in at least 90% of retryable failure scenarios
- **SC-006**: Run list queries return results within 2 seconds for histories of up to 1,000 runs
- **SC-007**: Each step is persisted atomically — a run interruption does not result in partial or corrupted step records

## Assumptions

- The system operates in a single-tenant environment where all runs belong to one user or organization
- A language model interface (mock or real) is available and returns structured responses indicating either a tool call or a final answer
- The tool registry contains approximately ten tools sufficient for common agent tasks
- Tool execution time is bounded and does not individually exceed the wall-clock timeout
- Persistence layer provides transactional guarantees for step and run records
- The system processes runs sequentially or with sufficient isolation to prevent cross-run interference
- Users access the system through API calls; a user interface is a separate concern
