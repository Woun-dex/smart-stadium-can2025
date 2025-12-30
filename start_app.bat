@echo off
echo ========================================
echo AFCON 2025 Morocco Stadium Simulator
echo ========================================
echo.

:: Start API server in background
echo Starting API server...
start "API Server" cmd /c "cd /d %~dp0 && python api\server.py"

:: Wait for API to start
timeout /t 3 /nobreak > nul

:: Start React frontend
echo Starting React dashboard...
cd /d %~dp0frontend
npm start

pause
