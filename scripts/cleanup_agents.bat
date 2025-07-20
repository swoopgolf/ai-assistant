@echo off
REM Agent Cleanup Script Wrapper for Windows
REM This script provides an easy way to clean up created agents

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\"

echo 🧹 Multi-Agent Framework - Agent Cleanup
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found
    exit /b 1
)

REM Run the Python cleanup script
echo 🔧 Running cleanup script...
python "%SCRIPT_DIR%cleanup_agents.py" %* 