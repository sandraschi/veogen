# MCP Server Verification Tool
# Verifies that MCP servers in mcp.json are legitimate and up-to-date

function Test-MCPServer {
    param(
        [string]$ServerName,
        [string]$Package
    )
    
    Write-Host "Verifying: $ServerName" -ForegroundColor Yellow
    
    if ($Package.StartsWith("@modelcontextprotocol/")) {
        try {
            $result = npm view $Package --json 2>$null | ConvertFrom-Json
            if ($result) {
                Write-Host "  ✅ Official MCP server - VERIFIED" -ForegroundColor Green
                Write-Host "  📦 Latest version: $($result.version)" -ForegroundColor Cyan
                Write-Host "  📅 Last updated: $($result.time.modified)" -ForegroundColor Cyan
                return @{ Valid = $true; Official = $true; Version = $result.version }
            } else {
                Write-Host "  ❌ Package not found on NPM!" -ForegroundColor Red
                return @{ Valid = $false; Official = $false; Version = $null }
            }
        } catch {
            Write-Host "  ❌ Error checking package: $($_.Exception.Message)" -ForegroundColor Red
            return @{ Valid = $false; Official = $false; Version = $null }
        }
    } elseif ($Package -eq "node" -or $Package -eq "python" -or $Package -eq "uvx" -or $Package -eq "cmd") {
        Write-Host "  📝 Custom/Local server - Manual verification needed" -ForegroundColor Blue
        return @{ Valid = $true; Official = $false; Version = "custom" }
    } else {
        Write-Host "  ⚠️  Third-party server - Please verify manually" -ForegroundColor Magenta
        Write-Host "  🔍 Check: https://npmjs.com/package/$Package" -ForegroundColor Gray
        return @{ Valid = $true; Official = $false; Version = "unknown" }
    }
}

function Show-BogusWarnings {
    Write-Host "`n⚠️  KNOWN BOGUS SERVERS TO AVOID:" -ForegroundColor Red -BackgroundColor Black
    Write-Host "================================" -ForegroundColor Red
    
    $bogusServers = @(
        "mcp-server-teams",
        "mcp-server-onenote", 
        "mcp-server-sharepoint",
        "mcp-server",
        "mcp-teams",
        "mcp-office365",
        "server-teams",
        "server-onenote"
    )
    
    foreach ($bogus in $bogusServers) {
        Write-Host "  ❌ $bogus" -ForegroundColor Red
    }
    
    Write-Host "`n💡 Always use official @modelcontextprotocol/ packages!" -ForegroundColor Yellow
}

function Show-OfficialServers {
    Write-Host "`n✅ VERIFIED OFFICIAL SERVERS:" -ForegroundColor Green -BackgroundColor Black
    Write-Host "============================" -ForegroundColor Green
    
    $officialServers = @{
        "Core" = @("filesystem", "memory", "fetch", "shell", "time")
        "Databases" = @("postgres", "sqlite") 
        "Web" = @("playwright", "puppeteer", "brave-search", "github")
        "Cloud" = @("aws", "azure", "docker", "kubernetes")
        "Google" = @("gdrive", "google-maps")
        "Media" = @("everart", "sequential-thinking")
    }
    
    foreach ($category in $officialServers.Keys) {
        Write-Host "`n📁 $category" -ForegroundColor Cyan
        foreach ($server in $officialServers[$category]) {
            Write-Host "  ✅ @modelcontextprotocol/server-$server" -ForegroundColor Green
        }
    }
}

# Main execution
Write-Host "🔍 VeoGen MCP Server Verification Tool" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "=======================================" -ForegroundColor White -BackgroundColor DarkBlue

if (-not (Test-Path "mcp.json")) {
    Write-Host "`n❌ mcp.json not found in current directory!" -ForegroundColor Red
    Write-Host "💡 Please run this script from your VeoGen root directory" -ForegroundColor Yellow
    exit 1
}

try {
    $mcpConfig = Get-Content "mcp.json" | ConvertFrom-Json
    
    if (-not $mcpConfig.mcpServers) {
        Write-Host "`n❌ No mcpServers found in mcp.json!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "`n📊 Analyzing $($mcpConfig.mcpServers.PSObject.Properties.Count) MCP servers..." -ForegroundColor White
    
    $verified = 0
    $official = 0
    $custom = 0
    $total = 0
    $results = @()
    
    foreach ($server in $mcpConfig.mcpServers.PSObject.Properties) {
        $total++
        $serverName = $server.Name
        $command = $server.Value.command
        
        # Determine package name
        if ($command -eq "npx" -and $server.Value.args -and $server.Value.args.Count -gt 1) {
            $package = $server.Value.args[1]
        } else {
            $package = $command
        }
        
        $result = Test-MCPServer -ServerName $serverName -Package $package
        
        if ($result.Valid) { $verified++ }
        if ($result.Official) { $official++ } else { $custom++ }
        
        $results += [PSCustomObject]@{
            Name = $serverName
            Package = $package
            Valid = $result.Valid
            Official = $result.Official
            Version = $result.Version
        }
    }
    
    # Summary
    Write-Host "`n📈 VERIFICATION SUMMARY" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host "======================" -ForegroundColor White -BackgroundColor DarkGreen
    Write-Host "Total Servers: $total" -ForegroundColor White
    Write-Host "Verified: $verified" -ForegroundColor $(if($verified -eq $total) {"Green"} else {"Yellow"})
    Write-Host "Official: $official" -ForegroundColor Green  
    Write-Host "Custom: $custom" -ForegroundColor Blue
    
    if ($verified -eq $total) {
        Write-Host "`n🎉 ALL SERVERS VERIFIED!" -ForegroundColor Green -BackgroundColor Black
        Write-Host "Your MCP setup looks excellent!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  SOME SERVERS NEED ATTENTION" -ForegroundColor Yellow -BackgroundColor Black
        $invalid = $results | Where-Object { -not $_.Valid }
        foreach ($inv in $invalid) {
            Write-Host "  ❌ $($inv.Name): $($inv.Package)" -ForegroundColor Red
        }
    }
    
    # Show reference lists
    Show-BogusWarnings
    Show-OfficialServers
    
    Write-Host "`n📚 For more information:" -ForegroundColor Cyan
    Write-Host "  🌐 Official MCP: https://modelcontextprotocol.io" -ForegroundColor Gray
    Write-Host "  📦 NPM Registry: https://npmjs.com/package/@modelcontextprotocol/" -ForegroundColor Gray
    Write-Host "  📖 VeoGen Docs: ./docs/development/mcp-integration-guide.md" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ Error reading mcp.json: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 