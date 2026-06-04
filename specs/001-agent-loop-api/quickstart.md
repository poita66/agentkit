# Quickstart: Agent Loop API

## Prerequisites

- Python 3.12+
- SQLite 3 (bundled with Python)
- Node.js 18+ (for frontend, if applicable)

## Setup

```bash
# Clone and enter the project
cd ElevateIQ-AgentKit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Initialize the database
python -m backend.src.db.init
```

## Running the Server

```bash
# Start the FastAPI development server
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`.

## Validation Scenarios

### 1. Submit a Goal and Verify Run Creation

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"goal": "Search for Python best practices"}'
```

**Expected**: `202 Accepted` with `{"run_id": "..."}`

### 2. Check Run Status (In Progress)

```bash
curl http://localhost:8000/runs/{run_id}
```

**Expected**: `200 OK` with status `"running"` and partial steps

### 3. Check Run Status (Completed)

Wait for the run to complete, then:

```bash
curl http://localhost:8000/runs/{run_id}
```

**Expected**: `200 OK` with status `"succeeded"` or `"failed"`, all steps present, and `reason` set

### 4. List Recent Runs

```bash
curl "http://localhost:8000/runs?limit=10&offset=0"
```

**Expected**: `200 OK` with paginated run list, ordered by most recent first

### 5. Trigger Step Cap Termination

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"goal": "Search for Python best practices", "max_steps": 2}'
```

Then check the run:

```bash
curl http://localhost:8000/runs/{run_id}
```

**Expected**: Run terminates with reason `"step_cap"` after 2 steps

### 6. Trigger Cost Cap Termination

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"goal": "Search for Python best practices", "max_cost_usd": 0.01}'
```

**Expected**: Run terminates with reason `"cost_cap"` once cumulative cost exceeds $0.01

### 7. Invalid Goal (Empty)

```bash
curl -X POST http://localhost:8000/runs \
  -H "Content-Type: application/json" \
  -d '{"goal": "   "}'
```

**Expected**: `422 Unprocessable Entity` with error message

### 8. Non-existent Run

```bash
curl http://localhost:8000/runs/non-existent-id
```

**Expected**: `404 Not Found`

## Running Tests

```bash
# Run all backend tests
cd backend
pytest

# Run specific test suite
pytest tests/unit/test_guards.py -v
pytest tests/integration/test_full_run.py -v
```

## API Documentation

FastAPI auto-generates interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
