# Session: Mock LLM canned response for unselected scenarios

**Session ID:** ses_169f0e4ddffe9lI44aahvv3X0o

**Agent:** build

**Model:** llama/default

**Messages:** 45

---

## User (1)

When no scenario is selected, we need a canned response from the mock llm - maybe lorem ipsum?

---

## Assistant (2)

I'll create a default scenario with lorem ipsum and update the API to use it when no scenario is selected but mock is enabled.

---

## Assistant (3)

Now update `runs.py` to fall back to `default` when mock is enabled but no scenario is selected:

---

## Assistant (4)

Now add the default scenario to the descriptions so it appears in the UI:

---

## Assistant (5)

Done. Two changes:

1. **`backend/tests/scenarios/default.json`** — new scenario with a lorem ipsum final answer
2. **`backend/src/api/runs.py:71-74`** — falls back to `default.json` when `AGENT_MOCK_ENABLED` is set but no scenario is selected

The default scenario also appears in the `/runs/scenarios` list with description "Default canned response (no specific scenario)".

---

## User (6)

I just tried with the message "hello" and got an infinite spinner

---

## User (7)

agent mock is indeed set, but I didn't select a scenario

---

## Assistant (8)

File exists. The backend server likely needs a restart to pick up the code changes. But let me also check the request schema to make sure `req.scenario` resolves correctly:

---

## User (9)

nevermind i had to restart the server. make sure the default scenario is hidden - it should just happen when the user enters text

---

## Assistant (10)

Now filter it out of the scenarios list:

---

## Assistant (11)

Done. The `default.json` scenario is hidden from the UI but used automatically when no scenario is selected.

---

## User (12)

also, scenario matching should just use the input text, not a specific scenario id

---

## Assistant (13)

I'll add `triggers` (keywords) to each scenario and match them against the goal text.

---

## Assistant (14)

Now update `runs.py` to match goal text against triggers:

---

## Assistant (15)

Remove unused imports and the old `_SCENARIO_DESCRIPTIONS`:

---

## Assistant (16)

Now remove the scenario field from the frontend. Let me read the relevant files:

---

## User (17)

No, the scenario selection in the frontend needs to remain

---

## Assistant (18)

Got it — keep the UI, but match on the goal text server-side instead of sending a scenario ID. Let me revert the API changes:

---

## Assistant (19)

Now update the scenario descriptions to include trigger keywords, so clicking a scenario button fills the input with text that matches:

---

## Assistant (20)

Now update the frontend to stop sending `scenario` — the buttons just set the goal text:

---

## Assistant (21)

Clean up the `scenario` field from the frontend types and client:

---

## Assistant (22)

Done. The flow is now:

- **Backend** (`runs.py:46-55`): `_match_scenario()` scans all scenario files for `triggers` that appear as substrings in the goal text (case-insensitive). Falls back to `default.json` (lorem ipsum) if nothing matches.
- **Frontend**: Scenario buttons still exist — clicking one fills the input with the scenario description (which contains trigger keywords). Submitting sends only the goal text, no scenario ID.
- **Scenario files**: Each has a `triggers` array with keywords that will match against the goal text.

---

## User (23)

nice! commit

---

## Assistant (24)

Done. `0667798` on `main`.

---

## User (25)

ensure tests succeed

---

## Assistant (26)

Two test failures. The integration test expects `scenario: null` in the request — let me fix that. The `formatStep` failure is pre-existing.

---

## Assistant (27)

Pre-existing test — the implementation reads `result.answer` but the test provides `result.data`. Let me fix both:

---

## Assistant (28)

Frontend: all 42 tests pass. Backend has pre-existing failures. Let me check if they're related to my changes:

---

## Assistant (29)

Pre-existing — same 6 failures on the previous commit. All frontend tests pass (42/42). Let me commit the test fixes:

---

## Assistant (30)

Done. `a6e8b86` — frontend: 42/42 pass. Backend: 6 pre-existing failures in `test_tool_retrieval.py` (Tool constructor signature mismatch), unrelated to these changes.

---

## User (31)

now fix the other issues in the tests and commit when done

---

## Assistant (32)

All the `Tool` constructors in the tests are missing `parallel_safe` and `idempotent`. Let me fix both test files:

---

## User (33)

use subagents as necessary

---

## Assistant (34)

Down to 2 failures. Let me read the relevant source code and dispatch subagents:

---

## Assistant (35)

Two issues to fix:

1. **`_retry` in tool_runtime.py:93-100** — `RETRIES_EXHAUSTED` always returns `recoverable: False`, but should preserve the original error's recoverability
2. **`test_concurrent_runs`** — 100 concurrent runs with 0.5s tool invocations need more time to settle

---

## Assistant (36)

## Goal
- Make the mock LLM return a canned lorem ipsum response when no scenario is selected, and match scenarios by goal-text triggers instead of a scenario ID

## Constraints & Preferences
- Scenario selection UI must remain in the frontend (buttons fill the input with trigger-containing text)
- Default scenario must be hidden from the `/runs/scenarios` list
- Scenario matching uses keyword triggers in goal text (case-insensitive substring match)
- `AGENT_MOCK_SCENARIO` env var still overrides as a manual fallback

## Progress
### Done
- Created `backend/tests/scenarios/default.json` with lorem ipsum final answer
- Added `triggers` arrays to all 7 scenario files (`success`, `step_cap`, `cost_cap`, `stuck`, `tool_error_recoverable`, `tool_error_nonrecoverable`, `tool_error_exhausted`)
- Implemented `_match_scenario()` in `backend/src/api/runs.py` to scan triggers against goal text
- Updated `_SCENARIO_DESCRIPTIONS` to include trigger keywords so UI buttons populate matching text
- Removed `scenario` field from frontend `RunCreateRequest` type, `createRun` client, and `useRunMutation` hook
- Fixed `frontend/src/utils/formatStep.ts` to also check `result.data` (not just `result.answer`)
- Fixed `frontend/tests/integration/goal-submission.test.tsx` to remove `scenario: null` expectation
- Fixed `backend/tests/unit/test_tool_retrieval.py` and `backend/tests/unit/test_tool_runtime.py` to pass `parallel_safe` and `idempotent` to `Tool` constructors
- Frontend tests: 42/42 passing; Backend unit tests: 24/24 passing

### In Progress
- (none)

### Blocked
- Backend integration tests (`test_full_run.py`, `test_concurrent_runs.py`) have pre-existing `pytest` errors unrelated to these changes

## Key Decisions
- Scenario matching uses simple substring matching on `triggers` arrays in each scenario JSON
- Default scenario is hidden from the UI but used as fallback when no triggers match
- Frontend scenario buttons still exist and set the goal text to the scenario description (which contains trigger keywords)
- `scenario` field removed from frontend request types to keep things clean; backend ignores it anyway

## Next Steps
- (none)

## Critical Context
- Backend integration tests fail with `pytest` errors (not related to these changes)
- `AGENT_MOCK_ENABLED` env var must be set for mock scenarios to activate
- `_SCENARIOS_DIR` resolves to `backend/tests/scenarios/`

## Relevant Files
- `backend/src/api/runs.py`: `_match_scenario()` function, `/runs` POST endpoint, `/runs/scenarios` GET endpoint
- `backend/tests/scenarios/default.json`: Lorem ipsum fallback scenario
- `backend/tests/scenarios/*.json`: All 7 scenarios updated with `triggers` arrays
- `frontend/src/api/types.ts`: `RunCreateRequest` type (removed `scenario`)
- `frontend/src/api/client.ts`: `createRun` function (removed `scenario`)
- `frontend/src/hooks/useRunMutation.ts`: `createRunFn` type and call (removed `scenario`)
- `frontend/src/components/GoalInput.tsx`: Removed `scenario` from submission options
- `frontend/src/utils/formatStep.ts`: Fixed to check `result.data` fallback
- `frontend/tests/integration/goal-submission.test.tsx`: Removed `scenario: null` from expectation
- `backend/tests/unit/test_tool_retrieval.py`: Added `parallel_safe`/`idempotent` to all `Tool` constructors
- `backend/tests/unit/test_tool_runtime.py`: Added `parallel_safe`/`idempotent` to fixture `Tool` constructors

---

## User (37)

Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed.

---

## Assistant (38)

SQLite concurrency issue — some step writes get lost with 100 concurrent runs. I need to add retry logic around the DB operations.

---

## Assistant (39)

I'll add a retry wrapper for DB operations to handle SQLite locking under concurrency:

---

## Assistant (40)

The issue is that SQLite can't handle 100 concurrent writers reliably. Let me make the test poll for completion instead of relying on a fixed sleep:

---

## Assistant (41)

The issue is that with `:memory:` SQLite, each connection in the pool gets its own database. I need to use a file-based temp DB for the test.

---

## Assistant (42)

All 38 backend tests pass. Let me verify frontend tests still pass:

---

## Assistant (43)

All tests pass:
- **Backend**: 38/38 passing
- **Frontend**: 42/42 passing

---

## User (44)

commit

---

## Assistant (45)

Done. Commit `b1975c5` with 6 files changed, 191 insertions, 35 deletions.

---

