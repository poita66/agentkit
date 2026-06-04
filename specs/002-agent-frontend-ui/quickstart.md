# Quickstart: Agent Frontend UI

## Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000` (see `backend/` README)

## Setup

```bash
# From the project root
cd frontend

# Install dependencies
npm install

# Set up environment (creates .env.development)
echo "VITE_API_URL=http://localhost:8000" > .env.development
```

## Development

```bash
# Start the dev server (default port 5173)
npm run dev

# Run type check
npm run typecheck

# Run linter
npm run lint

# Run tests
npm test
```

## Validation Scenarios

### Scenario 1: Submit a goal and see progress

1. Start backend: `cd ../backend && uvicorn backend.src.main:app --reload`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173` in browser
4. Type a goal like "Find the Q3 report" and press Enter
5. **Expected**: Run starts, progress updates appear within 3 seconds, steps show friendly descriptions

### Scenario 2: View run completion

1. Wait for the run from Scenario 1 to complete
2. **Expected**: Final answer appears prominently at the top of the screen
3. **Expected**: Outcome shows "Goal completed successfully" with a green indicator

### Scenario 3: Browse past runs

1. Submit 2-3 different goals
2. Wait for them to complete
3. **Expected**: Run list at the bottom shows all runs with goal, outcome badge, and relative timestamp
4. Click a past run
5. **Expected**: Run detail view opens with full step history

### Scenario 4: Error handling

1. Stop the backend server
2. Refresh the frontend or try to submit a goal
3. **Expected**: Clear error message about backend being unavailable

### Scenario 5: Keyboard navigation

1. Press `Tab` repeatedly from the page load
2. **Expected**: Focus moves through input → submit button → run list items, with visible focus rings on each element

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL |

## Project Structure Overview

See [plan.md](./plan.md) for the full project structure and [data-model.md](./data-model.md) for type definitions. API contracts are in [contracts/api.md](./contracts/api.md) and [contracts/ui.md](./contracts/ui.md).
