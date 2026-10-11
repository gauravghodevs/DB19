#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$REPO_ROOT/applications/payment-api"

echo "======================================"
echo " SecureOps Payment API Quality Gate"
echo "======================================"

if [[ ! -x "$API_DIR/.venv/bin/python" ]]; then
    echo "ERROR: Payment API virtual environment not found."
    echo "Activate or create the project's existing .venv first."
    exit 1
fi

PYTHON="$API_DIR/.venv/bin/python"

echo
echo "[1/2] Running Ruff..."
cd "$API_DIR"
"$PYTHON" -m ruff check app tests

echo
echo "[2/2] Running API tests..."
"$PYTHON" -m pytest -q

echo
echo "QUALITY GATE PASSED"
