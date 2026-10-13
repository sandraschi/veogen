# VeoGen Development Server Startup Script
# Starts backend and frontend in dev mode with proper environment setup

param(
    [switch]$Background,
    [string]$BackendPort = "8000",
    [string]$FrontendPort = "3000"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "🚀 Starting VeoGen Development Servers..." -ForegroundColor Cyan
Write-Host ""

# Check if feature flags are loaded
if (-not $env:FLOW_ENABLED) {
    Write-Host "⚠️  Feature flags not loaded. Run: . .\scripts\feature_flags.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check backend port
if (Test-Port -Port $BackendPort) {
    Write-Host "⚠️  Backend port $BackendPort is already in use!" -ForegroundColor Yellow
    Write-Host "   Stop the existing server or change the port." -ForegroundColor Yellow
    exit 1
}

# Check frontend port
if (Test-Port -Port $FrontendPort) {
    Write-Host "⚠️  Frontend port $FrontendPort is already in use!" -ForegroundColor Yellow
    Write-Host "   Stop the existing server or change the port." -ForegroundColor Yellow
    exit 1
}

# Start backend
Write-Host "📦 Starting Backend (port $BackendPort)..." -ForegroundColor Green
$backendDir = Join-Path $repoRoot "backend"
Push-Location $backendDir

# Check for virtual environment
$venvPath = Join-Path $backendDir ".venv"
if (Test-Path $venvPath) {
    Write-Host "   Activating virtual environment..." -ForegroundColor Gray
    & "$venvPath\Scripts\Activate.ps1"
}

# Check for uv
$hasUv = Get-Command uv -ErrorAction SilentlyContinue
if ($hasUv) {
    Write-Host "   Using uv to run backend..." -ForegroundColor Gray
    if ($Background) {
        Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $BackendPort, "--reload" -WindowStyle Minimized
        Write-Host "   OK Backend started in background" -ForegroundColor Green
    } else {
        Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $BackendPort, "--reload" -NoNewWindow
    }
} else {
    # Fallback to python
    Write-Host "   Using python to run backend..." -ForegroundColor Gray
    if ($Background) {
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $BackendPort, "--reload" -WindowStyle Minimized
        Write-Host "   OK Backend started in background" -ForegroundColor Green
    } else {
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $BackendPort, "--reload" -NoNewWindow
    }
}

Pop-Location

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🎨 Starting Frontend (port $FrontendPort)..." -ForegroundColor Green
$frontendDir = Join-Path $repoRoot "frontend"
Push-Location $frontendDir

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing dependencies..." -ForegroundColor Yellow
    npm install
}

if ($Background) {
    $env:HOST = "127.0.0.1"
    $env:DANGEROUSLY_DISABLE_HOST_CHECK = "true"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm start" -WindowStyle Minimized
    Write-Host "   OK Frontend started in background" -ForegroundColor Green
} else {
    $env:HOST = "127.0.0.1"
    $env:DANGEROUSLY_DISABLE_HOST_CHECK = "true"
    npm start
}

Pop-Location

Write-Host ""
Write-Host "✅ Development servers starting!" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Backend:  http://localhost:$BackendPort" -ForegroundColor White
Write-Host "   Frontend: http://localhost:$FrontendPort" -ForegroundColor White
Write-Host "   API Docs: http://localhost:$BackendPort/docs" -ForegroundColor White
Write-Host ""
if ($Background) {
    Write-Host "   Servers running in background. Check task manager to stop them." -ForegroundColor Gray
} else {
    Write-Host "   Press Ctrl+C to stop servers" -ForegroundColor Gray
}

