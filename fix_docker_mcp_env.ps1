# 🔧 Docker MCP Environment Fix Script
# Attempts to fix Docker MCP with environment variables instead of switching container modes

Write-Host "🔧 Docker MCP Environment Configuration Fix" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=============================================" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "`n🎯 This fix avoids switching Docker container modes" -ForegroundColor Green
Write-Host "We'll configure the MCP to use the correct Docker endpoint instead" -ForegroundColor Green

Write-Host "`n📋 Step 1: Detecting Docker configuration..." -ForegroundColor Yellow

# Check current Docker context and setup
try {
    $dockerInfo = docker info --format "{{.ServerVersion}}" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker Server Version: $dockerInfo" -ForegroundColor Green
        
        # Check which engine is active
        $context = docker context inspect --format "{{.Endpoints.docker.Host}}" 2>$null
        Write-Host "✅ Current Docker Context: $context" -ForegroundColor Green
        
        # Check available contexts
        Write-Host "`n📋 Available Docker contexts:" -ForegroundColor Cyan
        docker context ls
        
    } else {
        Write-Host "❌ Docker not accessible" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to get Docker info: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔍 Step 2: Testing pipe connections..." -ForegroundColor Yellow

# Test which Docker pipes are available
$pipes = @{
    "default" = "//./pipe/docker_engine"
    "linux" = "//./pipe/dockerDesktopLinuxEngine" 
    "windows" = "//./pipe/docker_engine_windows"
}

$workingPipe = $null
foreach ($pipeName in $pipes.Keys) {
    $pipeUrl = $pipes[$pipeName]
    Write-Host "Testing $pipeName ($pipeUrl)..." -ForegroundColor Cyan
    
    # Test if we can connect using DOCKER_HOST environment variable
    $env:DOCKER_HOST = "npipe://$pipeUrl"
    try {
        $test = docker version --format "{{.Server.Version}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $pipeName pipe WORKS!" -ForegroundColor Green
            $workingPipe = "npipe://$pipeUrl"
            break
        } else {
            Write-Host "❌ $pipeName pipe failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $pipeName pipe error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Reset environment
Remove-Item Env:DOCKER_HOST -ErrorAction SilentlyContinue

if ($workingPipe) {
    Write-Host "`n🎉 Found working Docker pipe: $workingPipe" -ForegroundColor Green
    
    Write-Host "`n📝 Step 3: MCP Configuration Recommendations" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Yellow
    
    Write-Host "`nAdd this to your claude_desktop_config.json Docker MCP entry:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host '"docker": {' -ForegroundColor White
    Write-Host '  "command": "npx",' -ForegroundColor White
    Write-Host '  "args": ["-y", "@modelcontextprotocol/server-docker"],' -ForegroundColor White
    Write-Host "  `"env`": {" -ForegroundColor Green
    Write-Host "    `"DOCKER_HOST`": `"$workingPipe`"" -ForegroundColor Green
    Write-Host "  }" -ForegroundColor Green
    Write-Host '}' -ForegroundColor White
    
    Write-Host "`n💡 Alternative configurations to try:" -ForegroundColor Yellow
    Write-Host "1. Default context:" -ForegroundColor Cyan
    Write-Host '   "DOCKER_HOST": "unix:///var/run/docker.sock"' -ForegroundColor Gray
    Write-Host "2. TCP connection:" -ForegroundColor Cyan  
    Write-Host '   "DOCKER_HOST": "tcp://localhost:2375"' -ForegroundColor Gray
    Write-Host "3. Working pipe:" -ForegroundColor Cyan
    Write-Host "   `"DOCKER_HOST`": `"$workingPipe`"" -ForegroundColor Gray
    
} else {
    Write-Host "`n❌ No working Docker pipes found" -ForegroundColor Red
    Write-Host "This suggests a deeper Docker configuration issue" -ForegroundColor Yellow
    
    Write-Host "`n🔧 Try these troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Restart Docker Desktop" -ForegroundColor Gray
    Write-Host "2. Check Docker Desktop settings > General > 'Expose daemon on tcp://localhost:2375'" -ForegroundColor Gray
    Write-Host "3. Switch Docker context: docker context use default" -ForegroundColor Gray
    Write-Host "4. If needed, switch container mode (as last resort)" -ForegroundColor Gray
}

Write-Host "`n✅ Environment fix analysis complete!" -ForegroundColor Green
Write-Host "Try the MCP configuration changes above before switching container modes." -ForegroundColor White
