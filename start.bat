@echo off
chcp 65001 >nul
REM AI Chat Hub Startup Script for Windows

echo Starting AI Chat Hub...

REM Check if in project root
if not exist "backend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Start Backend
echo Starting backend service...
cd backend

REM Check virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

REM Check .env file
if not exist ".env" (
    echo Warning: .env file not found, copying from example...
    copy .env.example .env
    echo Please edit backend\.env to configure your API keys
)

REM Start backend service
start "AI Chat Hub Backend" python run.py

cd ..

REM Start Frontend
echo Starting frontend service...
cd frontend

REM Check node_modules
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

REM Start frontend dev server
start "AI Chat Hub Frontend" npm run dev

cd ..

echo.
echo AI Chat Hub started successfully!
echo.
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the command windows to stop services

pause
