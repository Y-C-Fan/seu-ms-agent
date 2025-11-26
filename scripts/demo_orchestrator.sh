#!/bin/bash

# Demo Orchestrator Run Script
# Usage: ./scripts/demo_orchestrator.sh [query]

set -e

QUERY="${1:-Help me build a snake game with Python}"
echo "=================================================="
echo "🚀 Starting Orchestrator Demo"
echo "Query: $QUERY"
echo "=================================================="

# Ensure PYTHONPATH is set
export PYTHONPATH=$(pwd)

# Check if dependencies are installed (simple check)
if ! python3 -c "import dotenv" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements/framework.txt
fi

# Run Orchestrator
# We use 'yes' to automatically confirm the Human Review step for demo purposes
# In real usage, remove 'yes |' to interact manually
echo "C" | python3 orchestrator/main.py "$QUERY"

echo "=================================================="
echo "✅ Demo Completed!"
echo "=================================================="
