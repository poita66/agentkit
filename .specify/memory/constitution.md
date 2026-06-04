<!--
Sync Impact Report:
  Version: N/A → 1.0.0 (initial ratification)
  Added principles:
    - I. Code Quality
    - II. Testing Standards
    - III. User Experience Consistency
    - IV. Performance Requirements
  Added sections:
    - Governance
  Removed sections: none (template placeholders resolved)
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes needed (Constitution Check section is generic)
    - .specify/templates/spec-template.md ✅ no changes needed (aligns with principle-driven requirements)
    - .specify/templates/tasks-template.md ✅ no changes needed (test/quality task categories align)
    - .specify/templates/checklist-template.md ✅ no changes needed (generic structure)
  Follow-up TODOs: none
-->

# AgentKit Constitution

## Core Principles

### I. Code Quality

Code must be readable, properly typed, and free of accidental complexity. The linter (`ruff` for Python, `eslint` for TypeScript) and type checker (`mypy`/`pyright` or `tsc --noEmit`) must pass cleanly on every commit. Every feature starts with a clear module boundary; do not introduce abstractions for imagined future requirements. Errors must be surfaced explicitly — never swallowed silently. The README must include an honest "Known gaps" section documenting rough edges and deliberate trade-offs.

**Rationale**: ExpandIQ evaluates code quality by running `ruff` or `tsc --noEmit` against the repo and expects a clean run. Pragmatism — knowing when the core is working and stopping — is valued over over-engineering.

### II. Testing Standards

Tests must target what is genuinely at risk, not implementation details. Unit tests MUST cover: tool-retrieval ranking, stuck detection, cost and step caps, and retry-classification logic. At least one integration test MUST drive a full run end to end against the mock LLM and assert on the resulting database state. The mock LLM must be deterministic and rich enough to exercise every guard: goals that trigger 2-5 tool calls, goals that fire the stuck detector, goals that exceed the cost cap, and tool calls that fail then succeed on retry.

**Rationale**: Full coverage is not the goal. The assessment explicitly states: "We want to see that you can pick the small number of tests that actually reduce risk in this design."

### III. User Experience Consistency

The frontend must present information with clear visual hierarchy: the goal, current activity, and final answer are the loudest elements. Outcome states (running, succeeded, capped, stuck, errored) must be visually distinct — not just words in a sentence. Terminal reason codes must be translated into human-actionable messages (e.g., "Reached the $0.50 budget" instead of `cost_cap`). Loading, empty, and error states must all be handled with no infinite spinners. Accessibility basics are non-negotiable: semantic HTML, keyboard navigability, preserved focus rings, and adequate contrast. Technical knobs (`max_steps`, `max_cost_usd`) must be hidden from the default view.

**Rationale**: The assessment evaluates UI/UX craft as a first-class criterion. The frontend is the window into how the engineer thinks about visual hierarchy, state, and the small details that make a tool feel trustworthy.

### IV. Performance Requirements

Every run is bounded by four safety guards: a step cap (default 20), a cost cap (sum of mock token costs against `max_cost_usd`), a stuck detector (same `tool_name` + `args_hash` repeating 3 times), and a wall-clock hard ceiling of 60 seconds. Each guard must terminate the run with a clear reason from the set: `step_cap`, `cost_cap`, `stuck`, `timeout`, `error`, `succeeded`. Tool retries on recoverable errors must be bounded. The tool error contract requires structured results with `ok`, `data`, and `error` (containing `code`, `message`, `recoverable`) fields.

**Rationale**: Safety guards are the core of the agent runtime. The assessment states the guards "should terminate the run with a clear reason" and that the runtime "should decide whether to retry transparently when the error is transient."

## Governance

### Amendment Procedure

Amendments to this constitution require: (1) a documented rationale for the change, (2) a Sync Impact Report summarizing additions, removals, and affected templates, and (3) propagation of any principle changes to dependent templates and documentation.

### Versioning Policy

Versions follow semantic versioning:
- **MAJOR**: Backward-incompatible governance changes, principle removals, or redefinitions.
- **MINOR**: New principles added, sections expanded, or material guidance changes.
- **PATCH**: Clarifications, wording improvements, typo fixes, or non-semantic refinements.

### Compliance

All implementation work must be verifiable against these principles. The Constitution Check in implementation plans must reference the applicable principles. PR reviews should flag violations of any principle.

**Version**: 1.0.0 | **Ratified**: 2026-06-04 | **Last Amended**: 2026-06-04
