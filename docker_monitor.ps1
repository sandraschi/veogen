# 🚀 VeoGen Docker Auto-Restart Monitor
# Monitors Docker Desktop and VeoGen services, auto-restarts when needed
# Run this as a Windows Task Scheduler job every 2 minutes

param(
    [string]$LogPath = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\monitor.log",
    [string]$VeogenPath = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen",
    [int]$MaxRestartAttempts = 3,
    [bool]$EnableNotifications = $true
)

# Initialize logging
function Write-MonitorLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Output $logMessage
    Add-Content -Path $LogPath -Value $logMessage
}

# Check if Docker Desktop is running
function Test-DockerDesktop {
    try {
        $dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
        if ($dockerProcess) {
            return $true
        }
        
        # Also check if Docker daemon is responding
        $dockerInfo = & docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        
        return $false
    }
    catch {
        return $false
    }
}

# Start Docker Desktop
function Start-DockerDesktop {
    Write-MonitorLog "🐋 Starting Docker Desktop..."
    
    try {
        # Find Docker Desktop executable
        $dockerDesktopPaths = @(
            "$env:LOCALAPPDATA\Docker\Docker Desktop Installer\Docker Desktop.exe",
            "$env:PROGRAMFILES\Docker\Docker\Docker Desktop.exe",
            "${env:PROGRAMFILES(X86)}\Docker\Docker\Docker Desktop.exe"
        )
        
        $dockerExe = $null
        foreach ($path in $dockerDesktopPaths) {
            if (Test-Path $path) {
                $dockerExe = $path
                break
            }
        }
        
        if (-not $dockerExe) {
            Write-MonitorLog "❌ Docker Desktop executable not found" "ERROR"
            return $false
        }
        
        # Start Docker Desktop
        Start-Process $dockerExe -WindowStyle Hidden
        Write-MonitorLog "🚀 Docker Desktop startup initiated"
        
        # Wait up to 60 seconds for Docker to start
        $timeout = 60
        $elapsed = 0
        while ($elapsed -lt $timeout) {
            Start-Sleep 5
            $elapsed += 5
            
            if (Test-DockerDesktop) {
                Write-MonitorLog "✅ Docker Desktop started successfully"
                return $true
            }
            
            Write-MonitorLog "⏳ Waiting for Docker Desktop... ($elapsed/$timeout seconds)"
        }
        
        Write-MonitorLog "❌ Docker Desktop failed to start within timeout" "ERROR"
        return $false
    }
    catch {
        Write-MonitorLog "❌ Error starting Docker Desktop: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Check VeoGen services health
function Test-VeogenServices {
    try {
        Set-Location $VeogenPath
        
        # Check if services are running
        $containerStatus = & docker-compose ps --format json 2>$null | ConvertFrom-Json
        
        if (-not $containerStatus) {
            return $false
        }
        
        # Check critical services
        $criticalServices = @("backend", "frontend", "postgres", "redis")
        $healthyServices = 0
        
        foreach ($service in $criticalServices) {
            $serviceContainer = $containerStatus | Where-Object { $_.Service -eq $service }
            if ($serviceContainer -and $serviceContainer.State -eq "running") {
                $healthyServices++
            }
        }
        
        # Consider healthy if most critical services are running
        return ($healthyServices -ge ($criticalServices.Count * 0.75))
    }
    catch {
        Write-MonitorLog "❌ Error checking VeoGen services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Start VeoGen services
function Start-VeogenServices {
    Write-MonitorLog "🎬 Starting VeoGen services..."
    
    try {
        Set-Location $VeogenPath
        
        # Start services
        $result = & docker-compose up -d 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-MonitorLog "✅ VeoGen services started successfully"
            
            # Wait for services to be healthy
            Start-Sleep 30
            
            # Verify startup
            if (Test-VeogenServices) {
                Write-MonitorLog "✅ VeoGen services are healthy"
                return $true
            } else {
                Write-MonitorLog "⚠️ VeoGen services started but not all healthy" "WARN"
                return $false
            }
        } else {
            Write-MonitorLog "❌ Failed to start VeoGen services: $result" "ERROR"
            return $false
        }
    }
    catch {
        Write-MonitorLog "❌ Error starting VeoGen services: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Test VeoGen web interface
function Test-VeogenWebInterface {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:4710" -TimeoutSec 10 -UseBasicParsing
        return ($response.StatusCode -eq 200)
    }
    catch {
        return $false
    }
}

# Send notification (if configured)
function Send-Notification {
    param([string]$Title, [string]$Message, [string]$Type = "Info")
    
    if (-not $EnableNotifications) {
        return
    }
    
    try {
        # Windows 10/11 Toast Notification
        $template = @"
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

`$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
`$xml.LoadXml(@"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$Title</text>
            <text>$Message</text>
        </binding>
    </visual>
</toast>
"@)

`$toast = New-Object Windows.UI.Notifications.ToastNotification `$xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("VeoGen Monitor").Show(`$toast)
"@
        
        Invoke-Expression $template
    }
    catch {
        # Fallback to simple popup
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show($Message, $Title, "OK", $Type)
    }
}

# Main monitoring logic
function Start-Monitoring {
    Write-MonitorLog "🔍 Starting VeoGen monitoring cycle..."
    
    $restartAttempts = 0
    $dockerHealthy = Test-DockerDesktop
    $veogenHealthy = $false
    
    # Check Docker Desktop
    if (-not $dockerHealthy) {
        Write-MonitorLog "❌ Docker Desktop is not running" "WARN"
        
        if ($restartAttempts -lt $MaxRestartAttempts) {
            $restartAttempts++
            Write-MonitorLog "🔄 Attempting to restart Docker Desktop (attempt $restartAttempts/$MaxRestartAttempts)"
            
            if (Start-DockerDesktop) {
                $dockerHealthy = $true
                Send-Notification "VeoGen Monitor" "Docker Desktop restarted successfully" "Information"
            } else {
                Write-MonitorLog "❌ Failed to restart Docker Desktop" "ERROR"
                Send-Notification "VeoGen Monitor" "Failed to restart Docker Desktop" "Error"
            }
        } else {
            Write-MonitorLog "❌ Max restart attempts reached for Docker Desktop" "ERROR"
            Send-Notification "VeoGen Monitor" "Docker Desktop restart failed after $MaxRestartAttempts attempts" "Error"
        }
    } else {
        Write-MonitorLog "✅ Docker Desktop is running"
    }
    
    # Check VeoGen services if Docker is healthy
    if ($dockerHealthy) {
        $veogenHealthy = Test-VeogenServices
        
        if (-not $veogenHealthy) {
            Write-MonitorLog "❌ VeoGen services are not healthy" "WARN"
            
            if ($restartAttempts -lt $MaxRestartAttempts) {
                $restartAttempts++
                Write-MonitorLog "🔄 Attempting to restart VeoGen services (attempt $restartAttempts/$MaxRestartAttempts)"
                
                if (Start-VeogenServices) {
                    $veogenHealthy = $true
                    Send-Notification "VeoGen Monitor" "VeoGen services restarted successfully" "Information"
                } else {
                    Write-MonitorLog "❌ Failed to restart VeoGen services" "ERROR"
                    Send-Notification "VeoGen Monitor" "Failed to restart VeoGen services" "Error"
                }
            }
        } else {
            Write-MonitorLog "✅ VeoGen services are healthy"
        }
        
        # Test web interface
        $webHealthy = Test-VeogenWebInterface
        if ($webHealthy) {
            Write-MonitorLog "✅ VeoGen web interface is accessible"
        } else {
            Write-MonitorLog "⚠️ VeoGen web interface is not accessible" "WARN"
        }
    }
    
    # Summary
    if ($dockerHealthy -and $veogenHealthy) {
        Write-MonitorLog "🎉 All systems healthy - VeoGen is fully operational"
    } else {
        Write-MonitorLog "⚠️ System issues detected - manual intervention may be required" "WARN"
    }
    
    Write-MonitorLog "✅ Monitoring cycle completed"
}

# Cleanup old logs (keep last 100 entries)
function Cleanup-Logs {
    try {
        if (Test-Path $LogPath) {
            $lines = Get-Content $LogPath
            if ($lines.Count -gt 100) {
                $lines[-100..-1] | Set-Content $LogPath
                Write-MonitorLog "🧹 Log file cleaned up"
            }
        }
    }
    catch {
        Write-MonitorLog "⚠️ Failed to cleanup logs: $($_.Exception.Message)" "WARN"
    }
}

# Script entry point
try {
    # Create log directory if needed
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Write-MonitorLog "=" * 80
    Write-MonitorLog "🚀 VeoGen Docker Monitor v1.0 - Starting monitoring session"
    Write-MonitorLog "📍 VeoGen Path: $VeogenPath"
    Write-MonitorLog "📝 Log Path: $LogPath"
    Write-MonitorLog "🔄 Max Restart Attempts: $MaxRestartAttempts"
    Write-MonitorLog "🔔 Notifications: $EnableNotifications"
    Write-MonitorLog "=" * 80
    
    # Run monitoring
    Start-Monitoring
    
    # Cleanup
    Cleanup-Logs
    
    Write-MonitorLog "🏁 Monitoring session completed successfully"
}
catch {
    Write-MonitorLog "💥 Critical error in monitoring script: $($_.Exception.Message)" "ERROR"
    Write-MonitorLog "📍 Stack trace: $($_.Exception.StackTrace)" "ERROR"
    
    if ($EnableNotifications) {
        Send-Notification "VeoGen Monitor Error" "Critical error in monitoring script: $($_.Exception.Message)" "Error"
    }
    
    exit 1
}

exit 0