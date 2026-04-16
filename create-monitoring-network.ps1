# Create the unified-monitoring network if it doesn't exist
# This network is required for veogen to connect to the centralized monitoring stack

Write-Host "Creating unified-monitoring network..." -ForegroundColor Cyan

$networkName = "configs_unified-monitoring"

# Check if network exists
$networkExists = docker network ls --format "{{.Name}}" | Select-String -Pattern "^$networkName$"

if ($networkExists) {
    Write-Host "Network '$networkName' already exists." -ForegroundColor Green
} else {
    Write-Host "Creating network '$networkName'..." -ForegroundColor Yellow
    docker network create --driver bridge --subnet 172.20.0.0/16 $networkName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Network '$networkName' created successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create network. You may need to start the unified monitoring stack first:" -ForegroundColor Red
        Write-Host "  cd D:\Dev\repos\mcp-central-docs\monitoring\configs" -ForegroundColor Yellow
        Write-Host "  docker compose -f docker-compose.unified-monitoring.yml up -d" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`nNetwork is ready. You can now start veogen:" -ForegroundColor Cyan
Write-Host "  docker compose up -d" -ForegroundColor Yellow

