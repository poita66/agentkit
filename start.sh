#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_PORT=8000
export VITE_API_URL="http://localhost:$BACKEND_PORT"

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
