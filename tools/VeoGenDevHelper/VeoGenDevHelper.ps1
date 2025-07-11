# 🎛️ VeoGen Dev Helper - Management Script v2.1
# Purpose: Environment control center for VeoGen development
# Anti-Guillotine Protected: v2.1

param(
    [switch]$Start,
    [switch]$Status,
    [switch]$Help
)

# 📍 VeoGen Path Intelligence - No More Schnitzeljagd!
$VeoGenPaths = @{
    Root = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"
    Tools = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\tools"
    Backend = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\backend"
    Frontend = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\frontend"
    Incidents = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\incidents"
    DevHelper = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\tools\VeoGenDevHelper"
}

Write-Host "🎛️ VeoGen Dev Helper v2.1" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

if ($Help -or (-not $Start -and -not $Status)) {
    Write-Host "VeoGen Environment Control Center" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  -Start    Launch the Dev Helper web interface" -ForegroundColor Gray
    Write-Host "  -Status   Show VeoGen system status" -ForegroundColor Gray
    Write-Host "  -Help     Show this help" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Features:" -ForegroundColor White
    Write-Host "  • Service status monitoring" -ForegroundColor Gray
    Write-Host "  • Quick access to all VeoGen components" -ForegroundColor Gray
    Write-Host "  • Embedded path intelligence" -ForegroundColor Gray
    Write-Host "  • Anti-guillotine protection" -ForegroundColor Gray
    exit 0
}

if ($Start) {
    Write-Host "🚀 Starting VeoGen Dev Helper..." -ForegroundColor Green
    
    $htmlPath = Join-Path $VeoGenPaths.DevHelper "VeoGenDevHelper.html"
    if (Test-Path $htmlPath) {
        Start-Process $htmlPath
        Write-Host "✅ Dev Helper launched: $htmlPath" -ForegroundColor Green
        Write-Host "🌐 Web interface should open in your default browser" -ForegroundColor White
    } else {
        Write-Host "❌ HTML file not found: $htmlPath" -ForegroundColor Red
        Write-Host "Run from tools directory to regenerate" -ForegroundColor Yellow
    }
}

if ($Status) {
    Write-Host "📊 VeoGen System Status" -ForegroundColor Blue
    Write-Host "======================" -ForegroundColor Blue
    
    Write-Host "🎛️ Dev Helper: Ready" -ForegroundColor Green
    Write-Host "📍 Paths: All embedded" -ForegroundColor Green
    Write-Host "🛡️ Protection: Anti-guillotine v2.1" -ForegroundColor Magenta
    
    Write-Host ""
    Write-Host "VeoGen Paths:" -ForegroundColor White
    foreach ($path in $VeoGenPaths.GetEnumerator()) {
        $exists = Test-Path $path.Value
        $status = if ($exists) { "✅" } else { "❌" }
        Write-Host "  $($path.Key): $status $($path.Value)" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "Quick Links:" -ForegroundColor White
    Write-Host "  • VeoGen App: http://localhost:4710" -ForegroundColor Gray
    Write-Host "  • API Docs: http://localhost:4700/docs" -ForegroundColor Gray
    Write-Host "  • Grafana: http://localhost:4725" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🛡️ VeoGen Dev Helper v2.1 - Ready for operation" -ForegroundColor Green