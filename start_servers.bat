@echo off
echo Starting EAIS Backend and Frontend...

start cmd /k "cd /d C:\Users\Machenike\PycharmProjects\EAIS && .venv\Scripts\Activate.ps1 && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
start cmd /k "cd /d C:\Users\Machenike\PycharmProjects\EAIS\frontend && python -m http.server 3000"

echo Servers started in new windows. Press Ctrl+C in each window to stop.
pause