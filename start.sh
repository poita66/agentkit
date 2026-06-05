#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_PORT=8000
export VITE_API_URL="http://localhost:$BACKEND_PORT"
export AGENT_MOCK_ENABLED="true"

# Setup backend venv and dependencies
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

source "$SCRIPT_DIR/.venv/bin/activate"

if ! pip list --format=freeze | grep -q "fastapi"; then
    echo "Installing backend dependencies..."
    pip install -r "$BACKEND_DIR/requirements.txt"
fi

# Setup frontend dependencies
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$FRONTEND_DIR" && npm install
fi

cleanup() {
    echo "Shutting down..."
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    exit
}

trap cleanup EXIT INT TERM

echo "Starting backend on port $BACKEND_PORT..."
cd "$SCRIPT_DIR"
uvicorn backend.src.main:app --host 127.0.0.1 --port $BACKEND_PORT &
BACKEND_PID=$!

sleep 1

echo "Starting frontend (VITE_API_URL=$VITE_API_URL)..."
cd "$FRONTEND_DIR"
npm run dev
