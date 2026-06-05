# Tasks: Agent Frontend UI

**Input**: Design documents from `/specs/002-agent-frontend-ui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution Principle II and plan.md testing requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [X] T001 Create frontend project structure: src/, src/api/, src/components/, src/hooks/, src/utils/, src/styles/, tests/unit/, tests/integration/
- [X] T002 Initialize package.json with React 18, Vite 5, React Router DOM, Vitest, React Testing Library, @testing-library/react, @testing-library/jest-dom, @testing-library/user-event, @types/react, @types/react-dom, TypeScript 5.x, eslint, @vitejs/plugin-react
- [X] T003 Create vite.config.ts with React plugin and alias configuration
- [X] T004 Create tsconfig.json with strict mode, noUncheckedIndexedAccess, and path aliases
- [X] T005 Create .env.development with VITE_API_URL=http://localhost:8000
- [X] T006 Create index.html with root div and proper meta tags

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### API Layer

- [X] T007 Create API types in frontend/src/api/types.ts with RunDetail, StepDetail, RunSummary, RunListResponse, RunCreateRequest, RunCreateResponse interfaces
- [X] T008 Implement API client in frontend/src/api/client.ts with fetch wrapper, VITE_API_URL base URL, and 10s timeout

### Utilities

- [X] T009 [P] Implement formatOutcome in frontend/src/utils/formatOutcome.ts with describeOutcome(reason, totalCost, maxCostUsd) mapping all six termination reasons to human-readable messages
- [X] T010 [P] Implement formatStep in frontend/src/utils/formatStep.ts with describeStep(step) using TOOL_DESCRIPTIONS map for known tools and generic fallback
- [X] T011 [P] Implement timeAgo in frontend/src/utils/timeAgo.ts for relative timestamp formatting from ISO 8601 strings

### Global Styles

- [X] T012 Create global.css in frontend/src/styles/global.css with CSS custom properties for color palette, spacing, typography, focus rings, and WCAG AA contrast

### Custom Hooks

- [X] T013 Implement useRunMutation in frontend/src/hooks/useRunMutation.ts with createRun(goal, options) function, loading/error/success state, and input validation
- [X] T014 Implement useRun in frontend/src/hooks/useRun.ts with fetch + poll pattern: polls GET /runs/{runId} every 1.5s while status is running, stops on completion, 10s fetch timeout
- [X] T015 Implement useRuns in frontend/src/hooks/useRuns.ts with GET /runs fetch, pagination support (limit/offset), and loading/error state

### Entry Point & Router

- [X] T016 Create main.tsx entry point with React strict mode and ReactDOM.createRoot
- [X] T017 Create App.tsx with React Router DOM: / route for home (GoalInput + RunList), /runs/:runId route for RunDetail

### Foundational Tests

- [X] T018 [P] Unit test for formatOutcome in frontend/tests/unit/formatOutcome.test.ts covering all six termination reasons
- [X] T019 [P] Unit test for formatStep in frontend/tests/unit/formatStep.test.ts covering known tool descriptions and unknown tool fallback

**Checkpoint**: Foundation ready - API layer, utilities, hooks, router, and styles are complete. User story implementation can now begin.

---

## Phase 3: User Story 1 - Submit a Goal and See the Agent Work (Priority: P1) MVP

**Goal**: User types a goal, submits it, and sees step-by-step progress with friendly descriptions. Final answer appears prominently on completion.

**Independent Test**: Enter a goal, submit it, observe step-by-step progress updates, and confirm the final answer displays prominently upon completion.

### Tests for User Story 1

- [X] T020 [US1] Unit test for useRun polling logic in frontend/tests/unit/useRun.test.ts verifying poll interval, stop on completion, and error handling

### Implementation for User Story 1

- [X] T021 [P] [US1] Create GoalInput component in frontend/src/components/GoalInput.tsx with text input, submit button, disabled state during submission, and advanced toggle for max_steps/max_cost_usd
- [X] T022 [P] [US1] Create StepCard component in frontend/src/components/StepCard.tsx with default friendly summary (using formatStep), expandable raw details (tool name, args JSON, result, cost, timestamp), and distinct styling for final answer steps
- [X] T023 [US1] Create RunDetail component in frontend/src/components/RunDetail.tsx with useRun hook for fetch+poll, prominent final answer display, outcome message from formatOutcome, steps rendered as StepCard list, and back navigation

**Checkpoint**: User Story 1 should be fully functional - user can submit a goal, see live progress, and view the final answer.

---

## Phase 4: User Story 2 - Understand Why a Run Ended (Priority: P1)

**Goal**: When a run ends for any reason, the user sees a clear, human-readable explanation with the raw reason code as a small label.

**Independent Test**: Trigger each termination reason (via backend runs) and verify the frontend displays the appropriate human-readable message with distinct visual indicators.

### Implementation for User Story 2

- [X] T024 [P] [US2] Create StatusBadge component in frontend/src/components/StatusBadge.tsx with color-coded badges: green (succeeded), amber (step_cap, cost_cap, stuck), red (error, timeout), blue (running), and ARIA labels for accessibility
- [X] T025 [US2] Integrate outcome display into RunDetail in frontend/src/components/RunDetail.tsx with human-readable message from formatOutcome and StatusBadge with raw reason code as small label

**Checkpoint**: User Story 2 should be fully functional - all termination reasons display with distinct visual indicators and human-readable messages.

---

## Phase 5: User Story 3 - Browse and Reopen Past Runs (Priority: P2)

**Goal**: User views a list of past runs with goal, outcome indicator, and relative timestamp. Clicking a run reopens its full detail view.

**Independent Test**: Create multiple runs with different outcomes and verify the list displays them correctly with accurate outcome indicators and timestamps.

### Implementation for User Story 3

- [X] T026 [US3] Create RunList component in frontend/src/components/RunList.tsx with useRuns hook, each item showing truncated goal, StatusBadge, and relative timestamp from timeAgo, empty state with guidance, and pagination support

**Checkpoint**: User Story 3 should be fully functional - user can browse past runs and click to view details.

---

## Phase 6: User Story 4 - Live Updates During a Run (Priority: P2)

**Goal**: While a run is in progress, the UI updates automatically to show new steps and status changes without user action.

**Independent Test**: Start a run with multiple steps and verify the UI updates automatically as each step completes.

### Implementation for User Story 4

- [X] T027 [US4] Verify RunDetail polling in frontend/src/components/RunDetail.tsx auto-updates steps and status via useRun hook (polling implemented in T014, wired in T023)
- [X] T028 [US4] Add auto-scroll behavior to RunDetail in frontend/src/components/RunDetail.tsx to keep latest step visible as new steps arrive

**Checkpoint**: User Story 4 should be fully functional - UI updates within 2s of new steps completing on server.

---

## Phase 7: User Story 5 - Handle Loading, Empty, and Error States (Priority: P3)

**Goal**: The UI gracefully handles situations where no runs exist, when loading data, and when something goes wrong connecting to the backend.

**Independent Test**: Visit the app with no runs, disconnect the backend, and observe appropriate messaging in each case.

### Implementation for User Story 5

- [X] T029 [P] [US5] Create LoadingIndicator component in frontend/src/components/LoadingIndicator.tsx with animated indicator, message prop, and 10s timeout that switches to error state with retry option
- [X] T030 [P] [US5] Create ErrorMessage component in frontend/src/components/ErrorMessage.tsx with title, message, and optional retry button
- [X] T031 [US5] Add error handling to RunDetail in frontend/src/components/RunDetail.tsx for 404 (run not found) and network errors using ErrorMessage
- [X] T032 [US5] Add error handling to RunList in frontend/src/components/RunList.tsx for network errors and empty state with guidance
- [X] T033 [US5] Add error handling to GoalInput in frontend/src/components/GoalInput.tsx for 422 validation errors and backend unavailable states

**Checkpoint**: User Story 5 should be fully functional - all loading, empty, and error states are handled gracefully.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

### Integration Testing

- [X] T034 Integration test for full goal submission flow in frontend/tests/integration/goal-submission.test.tsx covering submit, progress display, and completion

### Accessibility & UX Polish

- [X] T035 [P] Audit keyboard navigation across all components ensuring Tab order: input -> submit -> run list items -> run detail steps, with visible focus rings
- [X] T036 [P] Verify WCAG AA color contrast for all text and UI elements in frontend/src/styles/global.css
- [X] T037 Handle edge cases: empty/whitespace-only goal validation in GoalInput, navigation away and back to running run in RunDetail, and large step lists with virtualization or pagination

### Build Validation

- [X] T038 Run npm run typecheck and npm run lint to ensure clean output per Constitution Principle I
- [X] T039 Run npm test to verify all unit and integration tests pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Foundational
  - US3 (P2) depends on US2 (needs StatusBadge)
  - US4 (P2) depends on US1 (extends RunDetail polling)
  - US5 (P3) depends on US1 and US3 (adds error states to existing components)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P1)**: Can start after Foundational - Independent of US1 (adds to RunDetail but US1 already creates it)
- **US3 (P2)**: Depends on US2 (needs StatusBadge component)
- **US4 (P2)**: Depends on US1 (extends RunDetail polling behavior)
- **US5 (P3)**: Depends on US1 and US3 (adds error states to GoalInput, RunList, RunDetail)

### Parallel Opportunities

- T009, T010, T011: Utility functions can be written in parallel
- T013, T014, T015: Custom hooks can be written in parallel
- T018, T019: Foundational tests can be written in parallel
- T021, T022: US1 components can be written in parallel
- T020: US1 test can be written in parallel with US1 components
- T029, T030: US5 components can be written in parallel
- T035, T036: Polish tasks can be written in parallel
- US1 and US2 can be worked on in parallel by different developers

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test goal submission, progress display, and final answer independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Deploy/Demo (MVP!)
3. Add User Story 2 -> Test independently -> Deploy/Demo
4. Add User Story 3 -> Test independently -> Deploy/Demo
5. Add User Story 4 -> Test independently -> Deploy/Demo
6. Add User Story 5 -> Test independently -> Deploy/Demo
7. Complete Polish -> Final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (GoalInput, StepCard, RunDetail)
   - Developer B: User Story 2 (StatusBadge, outcome integration)
3. After US1 and US2:
   - Developer A: User Story 3 (RunList)
   - Developer B: User Story 4 (polling verification, auto-scroll)
4. Developer A or B: User Story 5 (LoadingIndicator, ErrorMessage, error handling)
5. Team: Polish & integration testing
