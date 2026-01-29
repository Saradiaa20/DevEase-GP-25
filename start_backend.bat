@echo off
echo Starting DevEase Backend API...
cd backend
if errorlevel 1 (
    echo Error: Could not change to backend directory
    pause
    exit /b 1
)
python -m app.main
if errorlevel 1 (
    echo.
    echo Error starting backend. Make sure you have installed dependencies:
    echo   pip install -r requirements.txt
    echo   pip install -r backend/requirements.txt
    pause
    exit /b 1
)
pause
