# AI Chat Hub Startup Script for Windows (PowerShell)

Write-Host "Starting AI Chat Hub..." -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "backend")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "Starting backend service..." -ForegroundColor Yellow
Set-Location backend

# Check virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found, copying from example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit backend\.env to configure your API keys" -ForegroundColor Yellow
}

# Start backend service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & .\venv\Scripts\Activate.ps1; python run.py" -WindowTitle "AI Chat Hub Backend"

Set-Location ..

# Start Frontend
Write-Host "Starting frontend service..." -ForegroundColor Yellow
Set-Location frontend

# Check node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; npm run dev" -WindowTitle "AI Chat Hub Frontend"

Set-Location ..

Write-Host "`nAI Chat Hub started successfully!" -ForegroundColor Green
Write-Host "`nFrontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nClose the PowerShell windows to stop services" -ForegroundColor Yellow

Read-Host "`nPress Enter to continue"
