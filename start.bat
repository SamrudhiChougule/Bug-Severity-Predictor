@echo off
echo Starting Bug Severity Predictor...

REM Start backend API in background
start "Bug Severity Predictor API" cmd /k "cd backend && python app.py"

REM Wait for backend to initialize
timeout /t 3 /nobreak > nul

REM Open frontend in default browser
start frontend/index.html

echo Backend started and frontend opened!
echo Close this window when done.
pause
