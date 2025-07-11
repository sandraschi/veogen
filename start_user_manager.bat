@echo off
echo.
echo ===============================================
echo   VeoGen User Manager - One Click Startup
echo ===============================================
echo.

REM Change to VeoGen directory
cd /d "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

REM Check if VeoGen services are running first
echo [1/3] Checking VeoGen services status...
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo.
    echo ⚠️  WARNING: VeoGen services don't appear to be running!
    echo    The User Manager needs the PostgreSQL database to work.
    echo.
    echo    Would you like to start VeoGen services first? [Y/N]
    set /p choice="> "
    if /i "%choice%"=="Y" (
        echo.
        echo [Starting VeoGen services...]
        docker-compose up -d
        echo [Waiting for services to be ready...]
        timeout /t 15 /nobreak >nul
    )
)

echo.
echo [2/3] Checking port 8083 availability...

REM Check if port 8083 is in use
netstat -ano | findstr ":8083" >nul
if not errorlevel 1 (
    echo    ⚠️  Port 8083 is already in use - killing previous process...
    
    REM Get PID of process using port 8083
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8083"') do (
        echo    🔪 Killing process PID: %%i
        
        REM Try normal taskkill first
        taskkill /PID %%i /F >nul 2>&1
        if errorlevel 1 (
            echo    🛡️  Need elevated privileges - attempting with admin rights...
            
            REM Use PowerShell with elevated privileges to kill the process
            powershell -Command "Start-Process powershell -ArgumentList 'taskkill /PID %%i /F' -Verb RunAs -WindowStyle Hidden" >nul 2>&1
            
            REM Wait a moment for the kill command to complete
            timeout /t 2 /nobreak >nul
        )
    )
    
    REM Verify port is now free
    timeout /t 1 /nobreak >nul
    netstat -ano | findstr ":8083" >nul
    if not errorlevel 1 (
        echo    ❌ Could not free port 8083 - process may still be running
        echo    💡 Try running this batch file as Administrator
        echo.
        pause
        exit /b 1
    ) else (
        echo    ✅ Port 8083 is now available
    )
) else (
    echo    ✅ Port 8083 is available
)

echo.
echo [3/3] Starting User Manager server...
echo    📊 Backend API: http://localhost:8083/api/users
echo    🎭 Frontend UI: http://localhost:8083
echo    📚 API Docs: http://localhost:8083/docs
echo.

REM Start the user manager server
echo [4/4] Launching User Manager...
start "" "http://localhost:8083"
python user_manager_server.py

REM If we get here, the server stopped
echo.
echo ===============================================
echo   User Manager has stopped
echo ===============================================
echo.
pause
