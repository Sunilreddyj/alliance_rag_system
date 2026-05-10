#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"
[ -f "$PYTHON" ] || PYTHON="python"

echo "Starting Alliance RAG backend on http://localhost:8000 ..."
cd "$SCRIPT_DIR/backend"
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
