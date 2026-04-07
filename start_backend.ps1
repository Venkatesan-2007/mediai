#!/usr/bin/env pwsh
# Start Medical AI Backend with optimizations

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Medical AI Backend - Startup Script" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Disable Paddle OCR model source check
$env:PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK = "True"

# Navigate to backend folder
Push-Location "$PSScriptRoot\backend"

Write-Host ""
Write-Host "Starting backend on port 8000..." -ForegroundColor Green
Write-Host "API URL: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

python main.py

Pop-Location
