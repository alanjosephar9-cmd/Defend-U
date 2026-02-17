@echo off
SETLOCAL EnableDelayedExpansion

echo ==========================================
echo       Legal Sum - Startup Script
echo ==========================================

:: Check if backend directory exists
if not exist "backend" (
    echo [ERROR] Backend directory not found. Please run this from the project root.
    pause
    exit /b
)

echo [1/3] Starting Backend Server in a new window...
:: Use 'start' to run the backend in a separate terminal
start "Legal Sum Backend" cmd /c "title Legal Sum Backend && cd backend && python -m uvicorn api:app --reload || pause"

echo [2/3] Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak > NUL

echo [3/3] Launching Frontend...
:: Open the index.html in the default browser
if exist "frontend\index.html" (
    start "" "frontend\index.html"
) else (
    echo [ERROR] Frontend index.html not found in frontend directory.
)

echo.
echo ==========================================
echo   System started! Keep the backend window
echo   open while using the application.
echo ==========================================
echo.
pause
