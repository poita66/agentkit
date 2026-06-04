# Implementation Plan: Agent Frontend UI

**Branch**: `002-agent-frontend-ui` | **Date**: 2026-06-04 | **Spec**: specs/002-agent-frontend-ui/spec.md

**Input**: Feature specification from `/specs/002-agent-frontend-ui/spec.md`

## Summary

Build a single-page React frontend for the Agent Loop API (FastAPI backend). The frontend provides a text input for goal submission, real-time step-by-step progress display via polling, human-readable outcome messages, a browsable run history, and proper loading/empty/error states. All technical parameters are hidden behind an advanced toggle.

## Technical Context

**Language/Version**: TypeScript 5.x

**Primary Dependencies**: React 18, Vite 5, React Router DOM

**Storage**: N/A (stateless frontend; all data from backend API)

**Testing**: Vitest with React Testing Library

**Target Platform**: Modern web browser (Chrome, Firefox, Safari, Edge)

**Project Type**: web-app (single-page application)

**Performance Goals**: First progress update within 3s of submission; new steps appear within 2s of server completion

**Constraints**: Polling-based updates (no SSE on backend); single-tenant; no authentication; WCAG AA contrast; keyboard navigable

**Scale/Scope**: Single-page app with ~5-8 components; handles up to 100 runs in history view

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Code Quality | PASS | TypeScript with strict mode; eslint configured; clear component boundaries; no premature abstractions |
| II. Testing Standards | PASS | Unit tests for state management, polling logic, and step rendering; integration test for full goal submission flow |
| III. UX Consistency | PASS | Visual hierarchy (goal loudest, then activity, then answer); distinct outcome states; human-readable termination messages; loading/empty/error states handled; technical knobs hidden; semantic HTML; keyboard nav; focus rings; WCAG AA contrast |
| IV. Performance Requirements | PASS | Polling interval 1-2s bounded; no infinite spinners (10s timeout on loading states); run list paginated |

## Project Structure

### Documentation (this feature)

```text
specs/002-agent-frontend-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── src/
│   ├── main.tsx                 # Entry point
│   ├── App.tsx                  # Router + layout
│   ├── api/
│   │   ├── client.ts            # Fetch wrapper with base URL config
│   │   └── types.ts             # TypeScript interfaces matching backend schemas
│   ├── components/
│   │   ├── GoalInput.tsx        # Text input + submit button (+ advanced toggle)
│   │   ├── RunList.tsx          # List of past runs with outcome indicators
│   │   ├── RunDetail.tsx        # Full run view with steps and final answer
│   │   ├── StepCard.tsx         # Individual step with friendly summary + expand
│   │   ├── StatusBadge.tsx      # Visual outcome indicator (color-coded)
│   │   ├── LoadingIndicator.tsx # Bounded loading state
│   │   └── ErrorMessage.tsx     # Backend unavailable / error states
│   ├── hooks/
│   │   ├── useRun.ts            # Fetch + poll a single run
│   │   ├── useRuns.ts           # Fetch run list
│   │   └── useRunMutation.ts    # Create run mutation
│   ├── utils/
│   │   ├── formatOutcome.ts     # Termination reason → human-readable message
│   │   ├── formatStep.ts        # Tool call → friendly description
│   │   └── timeAgo.ts           # Relative timestamps
│   └── styles/
│       └── global.css           # Base styles, focus rings, color palette
└── tests/
    ├── unit/
    │   ├── formatOutcome.test.ts
    │   ├── formatStep.test.ts
    │   └── useRun.test.ts
    └── integration/
        └── goal-submission.test.tsx
```

**Structure Decision**: Single-page React application under `frontend/` directory. The backend (`backend/`) remains unchanged. Communication is HTTP-only with polling for real-time updates. TypeScript interfaces in `api/types.ts` mirror the backend Pydantic schemas to ensure type safety.

## Complexity Tracking

N/A — no constitution violations.
