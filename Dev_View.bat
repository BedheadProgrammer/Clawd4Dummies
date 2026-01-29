@echo off
REM ClawdForDummies Launcher for Windows
REM This script launches the security scanner with proper environment setup
REM
REM Usage:
REM   start.bat              - Run CLI scanner
REM   start.bat --gui        - Launch GUI application
REM   start.bat --help       - Show all options

title ClawdForDummies Security Scanner

echo ==========================================
echo    CLAWD FOR DUMMIES - Security Scanner
echo ==========================================
echo.

REM Get the directory where this script is located
REM Note: %~dp0 always ends with a backslash. We strip it to avoid issues
REM when quoting paths (trailing backslash before quote can cause parsing issues)
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set PROJECT_DIR=%SCRIPT_DIR%

REM Check if we're in a virtual environment first and it's working
if exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    "%PROJECT_DIR%\venv\Scripts\python.exe" --version >nul 2>&1
    if not errorlevel 1 (
        echo Using virtual environment...
        set PYTHON=%PROJECT_DIR%\venv\Scripts\python.exe
        goto :found_python
    )
)

REM Check for Python using various common executable names
REM Try 'py' first (Windows Python Launcher - recommended on Windows)
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :found_python
)

REM Try 'python' (common PATH entry)
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python
    goto :found_python
)

REM Try 'python3' (less common on Windows but possible)
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python3
    goto :found_python
)

REM No Python found
echo ERROR: Python is not installed or not in PATH
echo Please install Python 3.8 or higher from https://python.org
echo.
echo Checked for: py, python, python3
pause
exit /b 1

:found_python
REM Get Python version
for /f "tokens=2" %%a in ('%PYTHON% --version') do (
    set PYTHON_VERSION=%%a
)
echo Found Python %PYTHON_VERSION% using '%PYTHON%'

REM Install dependencies if needed
if not exist "%PROJECT_DIR%\clawd_for_dummies.egg-info" (
    echo Installing dependencies...
    %PYTHON% -m pip install -e "%PROJECT_DIR%" --quiet
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting security scan...
echo.

REM Run the scanner
%PYTHON% -m clawd_for_dummies %*

REM Pause to see results
echo.
echo Scan complete. Press any key to exit...
pause >nul
