# VeoGen User Manager - Smart Startup Script
# This script checks dependencies and starts the User Manager

Write-Host "🎭 VeoGen User Manager - Smart Startup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# Change to VeoGen directory
Set-Location "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

# Check if Docker is running
Write-Host "🐳 Checking Docker..." -ForegroundColor Yellow
try {
    $dockerCheck = docker ps 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        throw "Docker not running"
    }
} catch {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check VeoGen services
Write-Host "🔍 Checking VeoGen services..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:4700/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ VeoGen services are running" -ForegroundColor Green
} catch {
    Write-Host "❌ VeoGen services not running - starting them..." -ForegroundColor Yellow
    
    Write-Host "🚀 Starting VeoGen services..." -ForegroundColor Cyan
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started - waiting for readiness..." -ForegroundColor Green
        Start-Sleep -Seconds 20
        
        # Recheck
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:4700/health" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✅ Services are ready!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Services still not ready" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "✅ All dependencies ready!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host "🎭 Starting User Manager..." -ForegroundColor Cyan
Write-Host "   Dashboard: http://localhost:8083" -ForegroundColor Yellow
Write-Host "   API Docs: http://localhost:8083/docs" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start User Manager
python user_manager_server.py
