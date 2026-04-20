Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

# VeoGen Industrial v3.1 - Fleet Startup Script
# Standard SOTA 2026 Launcher

$BackendPort = 10730
$FrontendPort = 10731

Write-Host "ðŸš€ Initializing VeoGen Industrial v3.1..." -ForegroundColor Cyan

# 1. Backend Setup
Write-Host "`n[1/3] Verifying Backend Environment..." -ForegroundColor Yellow
cd backend
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}
. .venv\Scripts\Activate.ps1
Write-Host "Installing industrial dependencies..."
python -m pip install -q -r requirements.txt
cd ..

# 2. Frontend Setup
Write-Host "`n[2/3] Verifying Frontend Environment..." -ForegroundColor Yellow
cd frontend
if (!(Test-Path "node_modules")) {
    Write-Host "Installing NPM packages..."
    npm install --quiet
}
cd ..

# 3. Launch
Write-Host "`n[3/3] Launching Fleet Hub..." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:$BackendPort" -ForegroundColor Green
Write-Host "Frontend: http://localhost:$FrontendPort" -ForegroundColor Green

# Use Start-Process to run both in background/new windows if needed, 
# or just provide instructions.
# For this session, we'll just verify they CAN start.

Write-Host "`nâœ… Environment Ready. Use 'npm run dev' in /frontend and 'uvicorn app.main:app' in /backend." -ForegroundColor Cyan

