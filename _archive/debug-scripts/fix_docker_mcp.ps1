# 🚀 Docker MCP Quick Fix Script
# Attempts common solutions for Docker MCP connectivity issues

Write-Host "🚀 VeoGen Docker MCP Quick Fix Tool" -ForegroundColor White -BackgroundColor DarkGreen
Write-Host "====================================" -ForegroundColor White -BackgroundColor DarkGreen

Write-Host "`n🔍 Step 1: Checking current Docker status..." -ForegroundColor Yellow

# Basic Docker check
try {
    $dockerStatus = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is accessible" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not accessible - please start Docker Desktop" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker command failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 Step 2: Switching to Linux containers..." -ForegroundColor Yellow

# Try to switch to Linux containers
$dockerCliPath = "C:\Program Files\Docker\Docker\DockerCli.exe"
if (Test-Path $dockerCliPath) {
    Write-Host "Found DockerCli.exe, attempting to switch to Linux engine..." -ForegroundColor Cyan
    try {
        & $dockerCliPath -SwitchLinuxEngine
        Write-Host "✅ Attempted switch to Linux containers" -ForegroundColor Green
        Write-Host "⏳ Waiting for Docker to restart..." -ForegroundColor Yellow
        Start-Sleep 10
    } catch {
        Write-Host "⚠️ Could not switch engines: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ DockerCli.exe not found, skipping engine switch" -ForegroundColor Yellow
}

Write-Host "`n🔄 Step 3: Setting default Docker context..." -ForegroundColor Yellow

# Set context to default
try {
    docker context use default 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Set Docker context to 'default'" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Could not set default context, trying desktop-linux..." -ForegroundColor Yellow
        docker context use desktop-linux 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Set Docker context to 'desktop-linux'" -ForegroundColor Green
        } else {
            Write-Host "❌ Could not set any context" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "⚠️ Context switching failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n🧪 Step 4: Testing Docker functionality..." -ForegroundColor Yellow

# Test Linux containers
Write-Host "Testing Linux container capability..." -ForegroundColor Cyan
try {
    $testResult = docker run --rm alpine echo "Docker MCP test successful" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Linux containers are working!" -ForegroundColor Green
        Write-Host "🎉 Docker MCP should now be functional" -ForegroundColor Green
    } else {
        Write-Host "❌ Linux containers still not working" -ForegroundColor Red
        Write-Host "💡 Manual intervention required" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Container test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📊 Step 5: VeoGen stack status check..." -ForegroundColor Yellow

# Change to VeoGen directory and check containers
$veogenDir = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
if (Test-Path $veogenDir) {
    Push-Location $veogenDir
    try {
        Write-Host "Checking VeoGen containers..." -ForegroundColor Cyan
        docker-compose ps
        
        $runningContainers = docker ps --filter "name=veogen" --format "table {{.Names}}\t{{.Status}}"
        if ($runningContainers) {
            Write-Host "✅ VeoGen containers are running" -ForegroundColor Green
        } else {
            Write-Host "⚠️ VeoGen containers not detected" -ForegroundColor Yellow
            Write-Host "💡 Consider running: docker-compose up -d" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "⚠️ Could not check VeoGen status: $($_.Exception.Message)" -ForegroundColor Yellow
    } finally {
        Pop-Location
    }
} else {
    Write-Host "⚠️ VeoGen directory not found" -ForegroundColor Yellow
}

Write-Host "`n🎯 Step 6: Testing Docker MCP specifically..." -ForegroundColor Yellow

# Try to test Docker MCP directly if possible
Write-Host "The Docker MCP should now work with Claude." -ForegroundColor Cyan
Write-Host "To test, try these Docker MCP commands:" -ForegroundColor Cyan
Write-Host "  - docker-mcp:list-containers" -ForegroundColor Gray
Write-Host "  - docker-mcp:get-logs container_name" -ForegroundColor Gray

Write-Host "`n✅ Quick fix attempt completed!" -ForegroundColor Green -BackgroundColor Black
Write-Host "If Docker MCP still doesn't work, run the diagnostic script:" -ForegroundColor White
Write-Host "  .\diagnose_docker_mcp.ps1" -ForegroundColor Gray
