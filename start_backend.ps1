# PowerShell script to start DevEase Backend
Write-Host "Starting DevEase Backend API..." -ForegroundColor Green

# Change to backend directory
Set-Location backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Could not change to backend directory" -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    Set-Location ..
    exit 1
}

# Start the backend
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python -m app.main

# If we get here, there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error starting backend!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you have installed dependencies:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Set-Location ..
    exit 1
}
