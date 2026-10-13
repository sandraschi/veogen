# 🔍 Docker MCP Diagnostic Script
# Diagnoses Docker configuration issues for MCP integration

Write-Host "🔍 VeoGen Docker MCP Diagnostic Tool" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=====================================" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "`n📊 1. DOCKER BASIC STATUS" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow

# Check if Docker is running
try {
    $dockerVersion = docker version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
        docker version --format "{{.Client.Version}}" | ForEach-Object { Write-Host "📦 Client Version: $_" -ForegroundColor Cyan }
        docker version --format "{{.Server.Version}}" | ForEach-Object { Write-Host "🖥️  Server Version: $_" -ForegroundColor Cyan }
    } else {
        Write-Host "❌ Docker is not running or not accessible" -ForegroundColor Red
        Write-Host "💡 Please start Docker Desktop" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Docker command failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 2. DOCKER CONTEXT ANALYSIS" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow

# Check Docker contexts
try {
    Write-Host "Available contexts:" -ForegroundColor Cyan
    docker context ls
    
    Write-Host "`nCurrent context details:" -ForegroundColor Cyan
    docker context inspect | Out-String | Write-Host -ForegroundColor Gray
} catch {
    Write-Host "⚠️ Could not retrieve context information: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n🐳 3. CONTAINER MODE DETECTION" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# Test with a simple container to determine mode
try {
    Write-Host "Testing Linux container capability..." -ForegroundColor Cyan
    $linuxTest = docker run --rm alpine echo "Linux containers work" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Linux containers: WORKING" -ForegroundColor Green
        Write-Host "🎯 Mode: Linux Container Mode" -ForegroundColor Green
    } else {
        Write-Host "❌ Linux containers: NOT WORKING" -ForegroundColor Red
        
        Write-Host "`nTesting Windows container capability..." -ForegroundColor Cyan
        $windowsTest = docker run --rm mcr.microsoft.com/windows/nanoserver:ltsc2022 cmd /c echo "Windows containers work" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Windows containers: WORKING" -ForegroundColor Green
            Write-Host "🎯 Mode: Windows Container Mode" -ForegroundColor Green
            Write-Host "⚠️ MCP Docker server expects Linux containers!" -ForegroundColor Yellow
        } else {
            Write-Host "❌ Windows containers: NOT WORKING" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "⚠️ Container testing failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n🔧 4. DOCKER ENGINE ENDPOINTS" -ForegroundColor Yellow
Write-Host "------------------------------" -ForegroundColor Yellow

# Check which named pipes exist
Write-Host "Checking Docker named pipes:" -ForegroundColor Cyan

$pipes = @(
    "\\.\pipe\docker_engine",
    "\\.\pipe\docker_engine_linux", 
    "\\.\pipe\docker_engine_windows",
    "\\.\pipe\dockerDesktopLinuxEngine"
)

foreach ($pipe in $pipes) {
    if (Test-Path $pipe) {
        Write-Host "✅ $pipe - EXISTS" -ForegroundColor Green
    } else {
        Write-Host "❌ $pipe - NOT FOUND" -ForegroundColor Red
    }
}

Write-Host "`n🌐 5. DOCKER ENVIRONMENT VARIABLES" -ForegroundColor Yellow
Write-Host "----------------------------------" -ForegroundColor Yellow

$dockerEnvVars = @("DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH", "DOCKER_CONTEXT")
foreach ($var in $dockerEnvVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "✅ $var = $value" -ForegroundColor Green
    } else {
        Write-Host "➖ $var = (not set)" -ForegroundColor Gray
    }
}

Write-Host "`n📋 6. VeoGen SERVICES STATUS" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow

# Check VeoGen containers specifically
try {
    Write-Host "Checking VeoGen containers:" -ForegroundColor Cyan
    $veogenContainers = docker ps --filter "name=veogen" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    if ($veogenContainers) {
        Write-Host $veogenContainers -ForegroundColor Green
    } else {
        Write-Host "⚠️ No VeoGen containers found running" -ForegroundColor Yellow
        Write-Host "💡 Try: docker-compose ps" -ForegroundColor Cyan
        
        # Try docker-compose
        if (Test-Path "docker-compose.yml") {
            docker-compose ps
        }
    }
} catch {
    Write-Host "⚠️ Could not check containers: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n💡 7. RECOMMENDED SOLUTIONS" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow

Write-Host "Based on the diagnosis above, try these solutions:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔄 If Linux containers are not working:" -ForegroundColor White
Write-Host "   1. Right-click Docker Desktop tray icon" -ForegroundColor Gray
Write-Host "   2. Select 'Switch to Linux containers...'" -ForegroundColor Gray
Write-Host "   3. Or run: .\DockerCli.exe -SwitchLinuxEngine" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 If context issues detected:" -ForegroundColor White
Write-Host "   docker context use default" -ForegroundColor Gray
Write-Host "   # or" -ForegroundColor Gray  
Write-Host "   docker context use desktop-linux" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 If VeoGen containers not running:" -ForegroundColor White
Write-Host "   cd `"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen`"" -ForegroundColor Gray
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Alternative MCP configuration:" -ForegroundColor White
Write-Host "   Add to Docker MCP config:" -ForegroundColor Gray
Write-Host "   `"env`": { `"DOCKER_HOST`": `"unix:///var/run/docker.sock`" }" -ForegroundColor Gray

Write-Host "`n✅ Diagnostic complete! Use the solutions above to fix Docker MCP." -ForegroundColor Green
