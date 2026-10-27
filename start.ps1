# PolicyDiff - Windows PowerShell Startup Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PolicyDiff — Semantic Policy Change Detector" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in separate window
Write-Host "[1/2] Starting PolicyDiff FastAPI Backend (Port 8000)..." -ForegroundColor Green
$BackendCmd = "cd '$CurrentDir'; `$env:PYTHONPATH='backend'; .\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd

# 2. Start Frontend in separate window
Write-Host "[2/2] Starting PolicyDiff React Frontend (Port 5173)..." -ForegroundColor Green
$FrontendCmd = "cd '$CurrentDir\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd

Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
Write-Host "PolicyDiff services launched successfully!" -ForegroundColor Green
Write-Host "Backend API:  http://127.0.0.1:8000 (Swagger docs: http://127.0.0.1:8000/docs)" -ForegroundColor White
Write-Host "Frontend App: http://localhost:5173" -ForegroundColor White
Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
