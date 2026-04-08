# Medical AI Application - Complete Setup and Start Script
# This script installs all dependencies and starts both backend and frontend

Clear-Host

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "   Medical AI - Setup & Start" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ [ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ [ERROR] Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Get current directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Create Python virtual environment if needed
Write-Host "[1/6] Checking Python virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $projectRoot ".venv"

if (-not (Test-Path $venvPath)) {
    Write-Host "[2/6] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ [ERROR] Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[2/6] Virtual environment already exists, skipping creation..." -ForegroundColor Yellow
}

# Step 2: Activate virtual environment
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ [ERROR] Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Install backend dependencies
Write-Host "[4/6] Installing backend dependencies..." -ForegroundColor Yellow
$requirementsPath = Join-Path $projectRoot "backend\requirements.txt"
pip install -q -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ [ERROR] Failed to install backend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Backend dependencies installed" -ForegroundColor Green

# Step 4: Install frontend dependencies
Write-Host "[5/6] Installing frontend dependencies..." -ForegroundColor Yellow
$frontendPath = Join-Path $projectRoot "frontend\medi-ai"
Push-Location $frontendPath
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ [ERROR] Failed to install frontend dependencies" -ForegroundColor Red
    Pop-Location
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
Pop-Location

# Step 5: Start services
Write-Host "[6/6] Starting services..." -ForegroundColor Yellow
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "   Services Starting..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Magenta
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Magenta
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host ""

# Start backend in new PowerShell window
$backendCmd = "cd '$projectRoot'; .\.venv\Scripts\Activate.ps1; Write-Host 'Starting FastAPI Backend...' -ForegroundColor Green; uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit -Command $backendCmd"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend in new PowerShell window
$frontendCmd = "cd '$frontendPath'; Write-Host 'Starting React Frontend...' -ForegroundColor Green; npm start"
Start-Process powershell -ArgumentList "-NoExit -Command $frontendCmd"

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "   ✓ Setup Complete" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Two new PowerShell windows have been opened:"
Write-Host "  • Backend terminal (FastAPI on port 8000)"
Write-Host "  • Frontend terminal (React on port 3000)"
Write-Host ""
Write-Host "Close either terminal to stop that service." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this window"
