#!/bin/bash

# Agent Cleanup Script Wrapper for Unix-like systems
# This script provides an easy way to clean up created agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧹 Multi-Agent Framework - Agent Cleanup"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Run the Python cleanup script
echo "🔧 Running cleanup script..."
python3 "$SCRIPT_DIR/cleanup_agents.py" "$@" 