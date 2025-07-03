@echo off
REM VeoGen Complete Monitoring Stack Startup Script for Windows
REM This script initializes and starts the complete VeoGen application with full monitoring

echo Starting VeoGen Complete Monitoring Stack...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not available. Please install Docker Desktop and try again.
    pause
    exit /b 1
)

echo [INFO] Creating necessary directories...
if not exist "backend\logs" mkdir backend\logs
if not exist "backend\uploads" mkdir backend\uploads
if not exist "backend\outputs" mkdir backend\outputs
if not exist "backend\temp" mkdir backend\temp
if not exist "nginx\ssl" mkdir nginx\ssl

REM Create environment file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating default environment file...
    copy backend\.env.example .env
    echo [WARNING] Please update the .env file with your actual API keys and settings
)

echo [INFO] Stopping existing containers...
docker-compose down --remove-orphans 2>nul

echo [INFO] Building and starting all services...
docker-compose up --build -d

echo [INFO] Waiting for services to initialize...
timeout /t 30 /nobreak >nul

echo [INFO] Checking service health...
timeout /t 15 /nobreak >nul

echo.
echo VeoGen Monitoring Stack is starting up!
echo.
echo Access URLs:
echo   - VeoGen Frontend:    http://localhost:3000
echo   - VeoGen API:         http://localhost:8000
echo   - API Documentation:  http://localhost:8000/docs
echo   - Grafana:           http://localhost:3001 (admin/veogen123)
echo   - Prometheus:        http://localhost:9090
echo   - Alertmanager:      http://localhost:9093
echo   - Loki:              http://localhost:3100
echo.
echo Grafana Dashboards:
echo   - System Overview:    http://localhost:3001/d/veogen-overview
echo   - Video Analytics:    http://localhost:3001/d/veogen-video
echo   - Infrastructure:     http://localhost:3001/d/veogen-infrastructure
echo   - Error Analysis:     http://localhost:3001/d/veogen-errors
echo.
echo Monitoring Features:
echo   ✓ Comprehensive metrics collection
echo   ✓ Structured logging with Loki
echo   ✓ Real-time dashboards
echo   ✓ Alerting rules configured
echo   ✓ Container and system monitoring
echo   ✓ Error tracking and analysis
echo.

echo [INFO] Final service status check...
docker-compose ps

echo.
echo [INFO] VeoGen is ready! Check the URLs above to access the application and monitoring tools.
echo.
echo [WARNING] Note: It may take a few more minutes for all services to be fully operational.
echo [WARNING] If you encounter issues, check logs with: docker-compose logs [service-name]
echo.
echo [INFO] To stop all services: docker-compose down
echo [INFO] To view logs: docker-compose logs -f
echo [INFO] To restart: setup.bat
echo.
pause
