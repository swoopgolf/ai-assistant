@echo off
REM Agent Creation Script Wrapper for Windows
REM This script provides an easy way to create new agents

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\"

echo 🤖 Multi-Agent Framework - Agent Creator
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not found
    exit /b 1
)

REM Check if we're in the right directory
if not exist "%PROJECT_ROOT%agent_template\pyproject.toml" (
    echo ❌ Agent template not found. Make sure you're running this from the project root.
    exit /b 1
)

REM Run the Python script
if "%~1"=="" (
    echo 🔧 Running in interactive mode...
    python "%SCRIPT_DIR%create_new_agent.py"
) else (
    echo 🔧 Running with provided arguments...
    python "%SCRIPT_DIR%create_new_agent.py" %*
) 