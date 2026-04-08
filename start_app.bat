@echo off
REM Medical AI Application - Complete Setup and Start Script
REM This script installs all dependencies and starts both backend and frontend

setlocal enabledelayedexpansion

echo.
echo ====================================
echo    Medical AI - Setup & Start
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Get current directory
cd /d "%~dp0"

echo [1/6] Checking Python virtual environment...
if not exist ".venv" (
    echo [2/6] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment already exists, skipping creation...
)

echo [3/6] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [4/6] Installing backend dependencies...
pip install -q -r backend/requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo [5/6] Installing frontend dependencies...
cd frontend\medi-ai
call npm install --silent
if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo [6/6] Starting services...
echo.
echo ====================================
echo    Services Starting...
echo ====================================
echo.
echo Backend will start on http://localhost:8000
echo Frontend will start on http://localhost:3000
echo.
echo Press any key in backend terminal to stop the server
echo.

REM Start backend in new terminal
start cmd /k "cd /d "%cd%\backend" && call ..\\.venv\Scripts\activate.bat && echo. && echo Starting FastAPI Backend... && echo. && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak

REM Start frontend in new terminal
start cmd /k "cd /d "%cd%\frontend\medi-ai" && echo. && echo Starting React Frontend... && echo. && npm start"

echo.
echo ====================================
echo    ✓ Setup Complete
echo ====================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Two new terminal windows have been opened for backend and frontend.
echo Close either terminal to stop that service.
echo.
pause
