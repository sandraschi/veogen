# 🔍 MCP Configuration Reader Script
# Purpose: Read and analyze Sandra's Claude MCP configuration without manual grunt work

param(
    [switch]$Backup,
    [switch]$Analyze,
    [switch]$ListServers,
    [switch]$ShowProblems,
    [switch]$All
)

# 📍 MCP Configuration Paths
$mcpConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$backupDir = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\config-backups"

Write-Host "🔍 MCP Configuration Analysis Tool" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# 📂 Check if config exists
if (-not (Test-Path $mcpConfigPath)) {
    Write-Host "❌ ERROR: MCP config not found at: $mcpConfigPath" -ForegroundColor Red
    exit 1
}

# 📖 Read and parse configuration
try {
    $configContent = Get-Content $mcpConfigPath -Raw
    $config = $configContent | ConvertFrom-Json
    Write-Host "✅ Configuration loaded successfully" -ForegroundColor Green
    Write-Host "📍 Location: $mcpConfigPath" -ForegroundColor Gray
} catch {
    Write-Host "❌ ERROR: Failed to parse JSON configuration" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 💾 Backup if requested
if ($Backup -or $All) {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupFile = "$backupDir\claude_desktop_config_$timestamp.json"
    
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    
    Copy-Item $mcpConfigPath $backupFile
    Write-Host "💾 Backup created: $backupFile" -ForegroundColor Green
}

# 📊 Show raw configuration
Write-Host "`n📄 RAW CONFIGURATION:" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow
Write-Host $configContent

# 🔍 Analyze MCP servers
if ($config.mcpServers) {
    $serverCount = ($config.mcpServers | Get-Member -MemberType NoteProperty).Count
    Write-Host "`n🚀 MCP SERVERS ANALYSIS:" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan
    Write-Host "📊 Total servers configured: $serverCount" -ForegroundColor White
    
    if ($ListServers -or $All) {
        Write-Host "`n📋 SERVER LIST:" -ForegroundColor Yellow
        $config.mcpServers | Get-Member -MemberType NoteProperty | ForEach-Object {
            $serverName = $_.Name
            $serverConfig = $config.mcpServers.$serverName
            
            Write-Host "`n🔧 $serverName" -ForegroundColor Cyan
            Write-Host "   Command: $($serverConfig.command)" -ForegroundColor Gray
            if ($serverConfig.args) {
                Write-Host "   Args: $($serverConfig.args -join ' ')" -ForegroundColor Gray
            }
            if ($serverConfig.env) {
                Write-Host "   Environment vars: $($serverConfig.env.PSObject.Properties.Name -join ', ')" -ForegroundColor Gray
            }
        }
    }
    
    if ($Analyze -or $All) {
        Write-Host "`n🔍 DETAILED ANALYSIS:" -ForegroundColor Yellow
        
        # 📊 Command types breakdown
        $commandTypes = @{}
        $config.mcpServers | Get-Member -MemberType NoteProperty | ForEach-Object {
            $serverName = $_.Name
            $command = $config.mcpServers.$serverName.command
            if ($commandTypes.ContainsKey($command)) {
                $commandTypes[$command]++
            } else {
                $commandTypes[$command] = 1
            }
        }
        
        Write-Host "`n📊 Commands used:" -ForegroundColor Cyan
        $commandTypes.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
            Write-Host "   $($_.Key): $($_.Value) server(s)" -ForegroundColor Gray
        }
        
        # 🚨 Identify potentially problematic servers
        if ($ShowProblems -or $All) {
            Write-Host "`n🚨 POTENTIAL ISSUES:" -ForegroundColor Red
            
            $problematicServers = @()
            $config.mcpServers | Get-Member -MemberType NoteProperty | ForEach-Object {
                $serverName = $_.Name
                $serverConfig = $config.mcpServers.$serverName
                
                # Check for known problematic patterns
                if ($serverName -eq "desktop-commander") {
                    $problematicServers += "❌ $serverName - KNOWN FILE CORRUPTION BUG (truncates large files)"
                }
                if ($serverName -eq "docker-mcp") {
                    $problematicServers += "❌ $serverName - Poor Windows support, limited functionality"
                }
                if ($serverConfig.command -eq "uvx" -and $serverConfig.args -contains "docker-mcp") {
                    $problematicServers += "⚠️  $serverName - QuantGeekDev docker-mcp (Linux-centric)"
                }
                if ($serverConfig.args -and ($serverConfig.args -join " ") -match "blender.*mcp.*server") {
                    $problematicServers += "⚠️  $serverName - Potentially fake blender MCP package"
                }
            }
            
            if ($problematicServers.Count -gt 0) {
                $problematicServers | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
            } else {
                Write-Host "   ✅ No obvious problems detected" -ForegroundColor Green
            }
        }
    }
} else {
    Write-Host "❌ No mcpServers configuration found" -ForegroundColor Red
}

# 🎯 Show recommendations
if ($All) {
    Write-Host "`n🎯 RECOMMENDATIONS:" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host "1. 💾 Always backup before changes: .\mcp-config-reader.ps1 -Backup" -ForegroundColor Gray
    Write-Host "2. 🔍 Regular analysis: .\mcp-config-reader.ps1 -All" -ForegroundColor Gray
    Write-Host "3. 🚨 Check for problems: .\mcp-config-reader.ps1 -ShowProblems" -ForegroundColor Gray
    Write-Host "4. 📋 List servers: .\mcp-config-reader.ps1 -ListServers" -ForegroundColor Gray
}

Write-Host "`n✅ Analysis complete!" -ForegroundColor Green
Write-Host "📍 Config location: $mcpConfigPath" -ForegroundColor Gray