# ElevateIQ AgentKit

An LLM agent framework with a FastAPI backend and React frontend. Submit a goal in plain language and watch the agent work through it step by step.

## What It Does

- **Backend** — Python/FastAPI agent loop with tool selection, safety guards (step cap, cost cap, stuck detection, timeout), and SQLite persistence
- **Frontend** — React/TypeScript single-page app with goal submission, live progress tracking, run history, and human-readable outcomes

## Prerequisites

- Python 3.12+
- Node.js 18+
- A `.venv` with backend dependencies installed (see below)

## Quick Start

```bash
# First time setup — create the virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend && npm install && cd ..

# Start both backend and frontend
bash start.sh
```

`start.sh` launches the backend on port 8000 and the frontend dev server, then polls for progress updates. Open the URL shown by Vite (usually `http://localhost:5173`) in your browser.

## Project Structure

```
backend/          # FastAPI backend (agent loop, tool runtime, SQLite)
frontend/         # React/Vite/TypeScript frontend
start.sh          # Convenience script to run both servers
```

## API

| Method | Path                      | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/runs`                   | Create a new agent run             |
| GET    | `/runs`                   | List recent runs (paginated)       |
| GET    | `/runs/{run_id}`          | Get run state and steps            |

## Testing

```bash
# Backend
cd backend && python -m pytest

# Frontend
cd frontend && npm run test
```

## Assessment Notes

### Stretch Targets

No stretch targets were implemented because I wanted to focus on the core system and believe I reached the 4 hour time limit (hard to be precise when I was doing it while handling sick kids).

### Decisions

Frontend was done in React/Vite/TypeScript because it was familiar to me already and I could get it working quickly.

Backend was done in FastAPI because the doc specified that's what you use in production already, and I wanted to prove I could build a backend with it.

Persistence was done with SQLite because it's simple and works well for this demo. However Postgres is my preferred DBMS.

### Process and Tooling Used

#### AI Agent

OpenCode + Qwen3.6 27B (Lorbus/Qwen3.6-27B-int4-AutoRound hosted on my local vLLM inference server).

I began by reading the doc and writing a SPEC.md from it.
Then used SpecKit to create a formal specification and then implemented it.
I did this separately for the backend and frontend.

Beyond this I let the LLM use Google Chrome to interact with the UI for initial testing and debugging.

Then I took over almost entirely to test and debug the implementation, with a few small conversations with the agent to address issues.

MCP servers provided to the agent (however they weren't used much by the agent):
- Context7
- Tavily Search

OpenCode also provides LSP (Language Server Protocol) integrations automatically so the LLM immediately gets feedback about files it writes.

#### Other

- VS Code
- Lazygit
- eslint
- biome
- ruff
- pyright
- mypy

### Mitigating Factors

1. I had trouble selecting a stack to use at first. This took some of the time away from the implementation.
Historically I've had someone to bounce these ideas off of, but this time I had to do it alone (which is fine, but took a bit longer).

2. LLM strength - I currently don't have access to any LLM coding subscriptions, so I was limited to what Qwen3.6 27B could do.
It required some more manual intervention than e.g. Claude Opus 4.7, but was still quite capable.
However the small context window and low concurrency slowed me down a bit (these are hardware limitations, not model limitations).

### Known Gaps

Accessibility isn't as well tested as I would like. I did, however, use biome to lint the frontend code for accessibility issues.
