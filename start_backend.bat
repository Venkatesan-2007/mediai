@echo off
REM Start Medical AI Backend with optimizations
setlocal enabledelayedexpansion

echo ========================================================
echo Medical AI Backend - Startup Script
echo ========================================================

REM Disable Paddle OCR model source check
set PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

REM Navigate to backend folder
cd /d "%~dp0backend"

echo.
echo Starting backend on port 8000...
echo API URL: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python main.py

pause
