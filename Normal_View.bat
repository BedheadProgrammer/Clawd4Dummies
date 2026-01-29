@echo off
REM ClawdForDummies GUI Launcher for Windows
REM This script launches the graphical user interface (Friendly View) with real scanning

title ClawdForDummies GUI

echo ==========================================
echo    CLAWD FOR DUMMIES - GUI Application
echo ==========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%
set GUI_DIR=%SCRIPT_DIR%\clawd-for-dummies-gui

REM Check if GUI directory exists
if not exist "%GUI_DIR%" (
    echo ERROR: GUI directory not found at %GUI_DIR%
    echo.
    echo Please ensure the GUI application is installed.
    pause
    exit /b 1
)

REM Check for Node.js
where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js/npm is not installed or not in PATH
    echo.
    echo Please install Node.js from https://nodejs.org/
    echo ^(Version 20 or higher required^)
    pause
    exit /b 1
)

REM Get Node version
for /f "tokens=*" %%a in ('node --version') do set NODE_VERSION=%%a
echo Found Node.js %NODE_VERSION%

cd /d "%GUI_DIR%"

REM Check if dependencies are installed
if not exist "%GUI_DIR%\node_modules" (
    echo.
    echo Installing GUI dependencies ^(first time setup^)...
    echo This may take a minute...
    echo.
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

REM Always build to ensure we have the latest version
echo.
echo Building GUI application...
echo.
call npm run build
if errorlevel 1 (
    echo ERROR: Failed to build GUI application
    echo.
    echo Please check for TypeScript errors and try again.
    pause
    exit /b 1
)
echo.
echo Build completed successfully!
echo.

echo Starting GUI application...
echo ^(Console output will be shown below for debugging^)
echo.
echo TIP: Use the View Mode toggle in the header to switch between:
echo   - Dev View ^(CLI-like terminal style^)
echo   - Friendly View ^(card-based, user-friendly^)
echo.

REM Launch Electron app with production build - show all output for debugging
call npx cross-env NODE_ENV=production electron .

echo.
echo ==========================================
echo Application has exited.
echo.
echo If the window closed immediately, check the console output above for errors.
echo ==========================================
echo.

pause
