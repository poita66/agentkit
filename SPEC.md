# Specification - AgentKit (ElevateIQ Technical Assessment)

## Overview

This repository contains my (Peter Stewart) implementation of the ElevateIQ technical task to implement a basic LLM agent framework called AgentKit.
The system has two components: a backend agent framework and a frontend web UI for agent interaction.

## Backend Requirements

- Python 3.12 with FastAPI, async SQLAlchemy and pytest
- SQLite for agent state persistence
- Mock LLM API for deterministic testing

## Frontend Requirements

- React
- Vite
- TypeScript
- Accessibility in mind

## Personal Choices Beyond Requirements

- Biome for linting and formatting
- Shadcn UI component library
- Tailwind CSS for styling
- Vitest for testing

## Features

| Feature             | Description                                   |
| ------------------- | --------------------------------------------- |
| Backend API         | Python REST API for agent management          |
| Agent framework     | Core agent logic and orchestration            |
| Agent state storage | SQLite persistence                            |
| Frontend UI         | React/TypeScript web UI for agent interaction |
| Mock LLM API        | Deterministic LLM responses for testing       |

## Backend Spec

### API surface

```
POST  /runs             -> create a run, return { run_id }
GET   /runs             -> list recent runs (paginated, newest first)
GET   /runs/{run_id}    -> return run state and steps
POST  /runs/{run_id}/resume   (optional)
```

The request body for POST /runs looks like this:

```json
{
  "goal": "Free-text goal the agent should pursue",
  "max_steps": 20,
  "max_cost_usd": 0.5
}
```

### Agent loop

1. Load the full tool registry, which should contain around ten tools that you define.
1. Run a tool-retrieval step to pick the top-K most relevant tools (something like five) for the goal before calling the LLM. A keyword match, a BM25 implementation or a simple embedding-based approach are all fine. The point is that you can articulate why we should not be dumping thirty tools into every LLM call.
1. Call the mock LLM with { goal, past_steps, candidate_tools }. It should return either a tool call or a final answer.
1. If the LLM returns a tool call, dispatch it through a tool runtime that enforces the error contract below, persist the step and continue the loop.
1. If the LLM returns a final answer, persist it and mark the run as succeeded.

### Safety guards

The runtime needs to enforce four guards, each of which should terminate the run with a clear reason.

1. The step cap uses max_steps from the request, defaulting to twenty.
1. The cost cap sums the (mock) token cost reported by each step and stops the run once it crosses max_cost_usd.
1. The stuck detector watches for the same (tool_name, args_hash) repeating three times and terminates the run with reason stuck.
1. The wall-clock guard enforces a sixty-second hard ceiling on a single run.

A terminated run must record a clear reason chosen from step_cap, cost_cap, stuck, timeout, error or succeeded.
Tool error contract

Tools should return a structured result rather than raising raw exceptions back into the loop:

```
{
  "ok": bool,
  "data": ... | None,
  "error": { "code": str, "message": str, "recoverable": bool } | None
}
```

The runtime should decide whether to retry transparently when the error is transient or surface the error to the model when it is semantic (for example, an invalid argument). Retries should be bounded.

### Persistence

Each step should persist to SQLite. Two tables cover the requirement:

1. The `runs` table stores id, goal, status, reason, total_cost, started_at and finished_at.
1. The `steps` table stores run_id, step_number, tool_name, args_json, result_json, cost and created_at.

Once a run finishes, it must be readable through `GET /runs/{run_id}`.

## Frontend Spec

One main screen, chat-style, plus a simple list of past runs. Think of it as the experience a non-technical user would have, not a debug console.

What the UI needs to do

1. Ask for a goal in plain language. A single text input is enough. The technical knobs (max_steps, max_cost_usd) should not be in the user's face. Either hide them behind a small "Advanced" toggle or just send sensible defaults from the frontend and skip the UI entirely.
1. Show the agent's progress in plain language while it runs. As steps come in, render a friendly line per step (for example, "Searching documents for 'Q3 report'" rather than tool_call: search_docs {"q":"Q3 report"}). Power users can still expand a step to see the raw arguments and result if they want to, but that should not be the default view.
1. Show the final answer prominently. When the run finishes successfully, the agent's final response should be the most visible thing on the screen, not buried at the end of the timeline.
1. Translate terminal reasons into something a person can act on. A run that ended with cost_cap should read as something like "Reached the $0.50 budget for this run." A stuck run should explain that the agent kept repeating itself. The raw code can still appear as a small label, but the message is what the user sees first.
1. List past runs. A sidebar or simple list showing each run's goal, an outcome glyph (success, capped, stuck, errored) and a relative timestamp. Clicking a row reopens that run.
1. Live updates while a run is in flight. Polling GET /runs/{id} every one to two seconds is fine. If you did the streaming stretch on the backend, wire the SSE or WebSocket feed in instead.
