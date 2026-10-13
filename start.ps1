param([switch]$Headless, [switch]$BackendOnly)
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSCommandPath
$BackendPort = 11150
$FrontendPort = 11151

Write-Host "=== VeoGen Industrial launcher (Phase 2 salvage) ===" -ForegroundColor Cyan

# Clear zombie processes on both ports
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

# Backend: uv venv + uvicorn in a background job
$BackendJob = Start-Job -Name "veogen-backend" -ScriptBlock {
    param($Root)
    Set-Location (Join-Path $Root "backend")
    if (-not (Test-Path ".venv\Scripts\python.exe")) { uv venv }
    uv sync --quiet
    uv run uvicorn app.main:app --host 127.0.0.1 --port 11150
} -ArgumentList $Root

# Wait for backend health
$healthy = $false
for ($i = 0; $i -lt 90; $i++) {
    Start-Sleep 1
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $healthy = $true; break }
    } catch {}
}
if (-not $healthy) {
    Write-Host "Backend failed to become healthy on port $BackendPort" -ForegroundColor Red
    Receive-Job $BackendJob
    exit 1
}
Write-Host "Backend healthy on http://127.0.0.1:$BackendPort" -ForegroundColor Green

if (-not $BackendOnly) {
    Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $Root "frontend") -WindowStyle Hidden
    Start-Sleep 3
    Start-Process "http://127.0.0.1:$FrontendPort"
    Write-Host "Frontend on http://127.0.0.1:$FrontendPort" -ForegroundColor Green
}

# Keep console alive
try {
    while ($true) {
        if ($BackendJob.State -in @("Completed", "Failed")) {
            Receive-Job $BackendJob
            break
        }
        Start-Sleep 2
    }
} finally {
    Stop-Job $BackendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob -Force -ErrorAction SilentlyContinue
}
