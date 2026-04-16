# Fix Docker Desktop Daemon 500 Error
# This script restarts Docker Desktop to fix API errors

Write-Host "Docker Desktop API is returning 500 errors - restarting Docker Desktop..." -ForegroundColor Red

# Try to restart Docker Desktop via WSL if available
Write-Host "`nAttempting to restart Docker Desktop..." -ForegroundColor Yellow

# Method 1: Restart Docker Desktop service
Write-Host "Method 1: Restarting Docker Desktop service..." -ForegroundColor Cyan
$dockerService = Get-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
if ($dockerService) {
    Stop-Service -Name "com.docker.service" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    Start-Service -Name "com.docker.service" -ErrorAction SilentlyContinue
    Write-Host "  Docker service restarted" -ForegroundColor Green
} else {
    Write-Host "  Docker service not found (may be running as Desktop app)" -ForegroundColor Yellow
}

# Method 2: Kill Docker Desktop processes
Write-Host "`nMethod 2: Killing Docker Desktop processes..." -ForegroundColor Cyan
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "`nPlease manually restart Docker Desktop:" -ForegroundColor Yellow
Write-Host "  1. Right-click Docker Desktop icon in system tray" -ForegroundColor White
Write-Host "  2. Select 'Quit Docker Desktop'" -ForegroundColor White
Write-Host "  3. Wait 10 seconds" -ForegroundColor White
Write-Host "  4. Start Docker Desktop from Start Menu" -ForegroundColor White
Write-Host "  5. Wait for Docker to fully start (whale icon stops animating)" -ForegroundColor White
Write-Host "`nThen verify Docker is working:" -ForegroundColor Cyan
Write-Host "  docker version" -ForegroundColor Yellow
Write-Host "  docker ps" -ForegroundColor Yellow

