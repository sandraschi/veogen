# 🚀 Install QuantGeekDev Docker MCP Server
# This script installs the docker-mcp server for enhanced Docker management in Claude

Write-Host "🚀 Installing QuantGeekDev Docker MCP Server..." -ForegroundColor Green

# Method 1: Try uvx installation first (recommended)
Write-Host "📦 Attempting uvx installation..." -ForegroundColor Yellow

try {
    # Check if uvx is available
    $uvxCheck = uvx --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ uvx found, installing docker-mcp..." -ForegroundColor Green
        uvx install docker-mcp
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ docker-mcp installed successfully via uvx!" -ForegroundColor Green
            Write-Host "📋 Configuration for Claude:" -ForegroundColor Cyan
            Write-Host @"
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uvx",
      "args": ["docker-mcp"]
    }
  }
}
"@ -ForegroundColor White
            exit 0
        }
    }
} catch {
    Write-Host "⚠️ uvx not available, trying alternative method..." -ForegroundColor Yellow
}

# Method 2: Clone and local installation
Write-Host "📂 Cloning repository for local installation..." -ForegroundColor Yellow

$targetDir = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\mcp-servers\docker-mcp"

if (Test-Path $targetDir) {
    Write-Host "🗂️ Directory exists, updating..." -ForegroundColor Yellow
    cd $targetDir
    git pull
} else {
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\mcp-servers"
    git clone https://github.com/QuantGeekDev/docker-mcp.git
    cd docker-mcp
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ docker-mcp installed successfully!" -ForegroundColor Green
    Write-Host "📋 Configuration for Claude:" -ForegroundColor Cyan
    Write-Host @"
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "$targetDir",
        "run",
        "docker-mcp"
      ]
    }
  }
}
"@ -ForegroundColor White
} else {
    Write-Host "❌ Installation failed. Please check dependencies." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host "1. Add the configuration above to your Claude desktop config" -ForegroundColor White
Write-Host "2. Restart Claude" -ForegroundColor White
Write-Host "3. Test with: 'List all Docker containers'" -ForegroundColor White
Write-Host ""
Write-Host "📍 Config file location: %APPDATA%\Claude\claude_desktop_config.json" -ForegroundColor Cyan
