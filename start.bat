@echo off
title PolicyDiff Launcher
echo ==========================================================
echo   Starting PolicyDiff - Semantic Policy Change Detector
echo ==========================================================
cd /d "%~dp0"

echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "PolicyDiff Backend" powershell -NoExit -Command "cd '%~dp0'; $env:PYTHONPATH='backend'; .\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching Vite Frontend on http://localhost:5173 ...
start "PolicyDiff Frontend" powershell -NoExit -Command "cd '%~dp0frontend'; npm run dev"

echo ----------------------------------------------------------
echo PolicyDiff started! Opening browser in 3 seconds...
echo ----------------------------------------------------------
timeout /t 3 /nobreak >nul
start http://localhost:5173
