@echo off
setlocal enabledelayedexpansion
echo.
echo ============================================
echo    VeoGen User Manager - Quick Start
echo ============================================
echo.

:: Check if we're in the right directory
if not exist "server.py" (
    echo Error: server.py not found!
    echo Please run this script from the user-manager directory
    echo Expected location: tools\user-manager\
    echo.
    pause
    exit /b 1
)

:: Check PostgreSQL connection
echo Checking VeoGen services...
python -c "import psycopg2; psycopg2.connect(host='localhost', port=4715, database='veogen', user='veogen', password='veogen123').close(); print('PostgreSQL connection: OK')" 2>nul
if errorlevel 1 (
    echo PostgreSQL connection failed!
    echo.
    echo Make sure VeoGen services are running:
    echo   cd ../../
    echo   docker-compose up -d
    echo.
    pause
    exit /b 1
)

:: Check if port 8100 is in use
echo Checking port 8100...
netstat -ano | findstr ":8100 " >nul 2>&1
if not errorlevel 1 (
    echo Port 8100 is currently in use
    echo.
    
    :: Find and kill processes using port 8100
    echo Finding processes using port 8100...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8100 "') do (
        echo Killing process ID %%a...
        taskkill /pid %%a /f >nul 2>&1
    )
    
    :: Wait for ports to be released
    echo Waiting for port to be released...
    timeout /t 3 /nobreak >nul
    
    :: Verify port is now free
    netstat -ano | findstr ":8100 " >nul 2>&1
    if not errorlevel 1 (
        echo Failed to free port 8100. Please manually stop the process.
        pause
        exit /b 1
    )
)

echo Port 8100 is available
echo.
echo Starting VeoGen User Manager...
echo.
echo Frontend: http://localhost:8100
echo API Docs: http://localhost:8100/docs
echo Health:   http://localhost:8100/health
echo.
echo Press Ctrl+C to stop the server
echo Opening browser in 3 seconds...
echo.

:: Start the server and open browser
timeout /t 3 /nobreak >nul
start http://localhost:8100
python server.py

echo.
echo User Manager stopped
pause