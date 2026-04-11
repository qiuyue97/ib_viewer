@echo off
cd /d "%~dp0"

echo Starting IB Viewer backend...
start "IB Viewer Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

timeout /t 2 /nobreak >nul

echo Opening browser...
start http://localhost:8000

echo.
echo IB Viewer is running at http://localhost:8000
echo Close the backend window to stop.
