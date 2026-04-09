@echo off
REM Medical AI - Setup with Error Recovery
REM This script is more robust and handles common errors

setlocal enabledelayedexpansion

echo.
echo =====================================
echo    Medical AI - Setup with Recovery
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
) else (
    echo     Virtual environment already exists
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate venv
    pause
    exit /b 1
)

echo [3/5] Upgrading pip, setuptools, and wheels...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [WARN] Pip upgrade had issues, continuing...
)

echo [4/5] Installing dependencies...
echo.
echo   Trying standard requirements first...
pip install -r backend/requirements.txt
if errorlevel 1 (
    echo.
    echo   [WARN] Standard installation failed!
    echo   Trying with minimal requirements...
    pip install -r backend/requirements-minimal.txt
    if errorlevel 1 (
        echo   [ERROR] Even minimal install failed
        echo.
        echo   Try Option 1 instead: docker-compose up --build
        pause
        exit /b 1
    ) else (
        echo.
        echo   [OK] Minimal installation successful
        echo   Note: Some features may be limited
        echo   You can install additional packages later
    )
) else (
    echo [OK] Full installation successful
)

echo.
echo [5/5] Starting services...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.

REM Start backend
echo Starting backend...
start cmd /k "cd /d "%cd%\backend" && call ..\\.venv\Scripts\activate.bat && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak

REM Start frontend (if dependencies exist)
if exist "frontend\medi-ai\node_modules" (
    echo Starting frontend...
    start cmd /k "cd /d "%cd%\frontend\medi-ai" && npm start"
) else (
    if exist "frontend\medi-ai\package.json" (
        echo Installing frontend dependencies...
        start cmd /k "cd /d "%cd%\frontend\medi-ai" && npm install && npm start"
    )
)

echo.
echo =========================================
echo    Setup Complete!
echo =========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo If you had issues, see SETUP_ALTERNATIVES.md
echo.
pause
