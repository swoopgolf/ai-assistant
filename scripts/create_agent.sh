#!/bin/bash

# Agent Creation Script Wrapper
# This script provides an easy way to create new agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🤖 Multi-Agent Framework - Agent Creator"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/agent_template/pyproject.toml" ]; then
    echo "❌ Agent template not found. Make sure you're running this from the project root."
    exit 1
fi

# Run the Python script
if [ "$#" -eq 0 ]; then
    echo "🔧 Running in interactive mode..."
    python3 "$SCRIPT_DIR/create_new_agent.py"
else
    echo "🔧 Running with provided arguments..."
    python3 "$SCRIPT_DIR/create_new_agent.py" "$@"
fi 