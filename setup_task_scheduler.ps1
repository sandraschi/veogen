# 📅 Windows Task Scheduler Setup for VeoGen Monitoring
# Run this script as Administrator to set up automatic monitoring

# Configuration
$TaskName = "VeoGen-Docker-Monitor"
$TaskDescription = "Monitors Docker Desktop and VeoGen services, auto-restarts when needed"
$ScriptPath = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\docker_monitor.ps1"
$LogPath = "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\task_scheduler.log"
$IntervalMinutes = 2

function Write-TaskLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Output $logMessage
    Add-Content -Path $LogPath -Value $logMessage -ErrorAction SilentlyContinue
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-VeogenMonitorTask {
    Write-TaskLog "🚀 Setting up VeoGen Docker Monitor task..."
    
    try {
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-TaskLog "⚠️ Task already exists. Removing old task..."
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }
        
        # Create task action
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$ScriptPath`""
        
        # Create task trigger (every X minutes)
        $trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration (New-TimeSpan -Days 365) -Once -At (Get-Date)
        
        # Create task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false -DontStopOnIdleEnd
        
        # Create task principal (run as current user)
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType ServiceAccount
        
        # Register the task
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $TaskDescription
        
        Write-TaskLog "✅ VeoGen Monitor task created successfully"
        Write-TaskLog "📊 Task will run every $IntervalMinutes minutes"
        Write-TaskLog "👤 Running as user: $env:USERNAME"
        
        # Start the task immediately
        Start-ScheduledTask -TaskName $TaskName
        Write-TaskLog "🏁 Task started immediately for testing"
        
        return $true
    }
    catch {
        Write-TaskLog "❌ Error creating task: $($_.Exception.Message)"
        return $false
    }
}

function Show-TaskStatus {
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            
            Write-TaskLog "📋 Task Status Information:"
            Write-TaskLog "   Task Name: $($task.TaskName)"
            Write-TaskLog "   State: $($task.State)"
            Write-TaskLog "   Last Run: $($taskInfo.LastRunTime)"
            Write-TaskLog "   Next Run: $($taskInfo.NextRunTime)"
            Write-TaskLog "   Last Result: $($taskInfo.LastTaskResult)"
            
            if ($taskInfo.LastTaskResult -eq 0) {
                Write-TaskLog "✅ Task is running successfully"
            } else {
                Write-TaskLog "⚠️ Task last run had issues (code: $($taskInfo.LastTaskResult))"
            }
        } else {
            Write-TaskLog "❌ Task not found"
        }
    }
    catch {
        Write-TaskLog "❌ Error getting task status: $($_.Exception.Message)"
    }
}

function Remove-VeogenMonitorTask {
    try {
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-TaskLog "🗑️ VeoGen Monitor task removed successfully"
        } else {
            Write-TaskLog "ℹ️ Task was not installed"
        }
    }
    catch {
        Write-TaskLog "❌ Error removing task: $($_.Exception.Message)"
    }
}

function Test-MonitoringScript {
    Write-TaskLog "🧪 Testing monitoring script..."
    
    if (-not (Test-Path $ScriptPath)) {
        Write-TaskLog "❌ Monitoring script not found at: $ScriptPath"
        return $false
    }
    
    try {
        # Test script execution
        $result = & PowerShell.exe -ExecutionPolicy Bypass -File $ScriptPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TaskLog "✅ Monitoring script test successful"
            return $true
        } else {
            Write-TaskLog "❌ Monitoring script test failed with exit code: $LASTEXITCODE"
            Write-TaskLog "❌ Output: $result"
            return $false
        }
    }
    catch {
        Write-TaskLog "❌ Error testing script: $($_.Exception.Message)"
        return $false
    }
}

function Show-Menu {
    Write-Host "`n🎭 VeoGen Docker Monitor - Task Scheduler Setup" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "1. Install monitoring task (run every $IntervalMinutes minutes)" -ForegroundColor Green
    Write-Host "2. Remove monitoring task" -ForegroundColor Red
    Write-Host "3. Show task status" -ForegroundColor Yellow
    Write-Host "4. Test monitoring script" -ForegroundColor Blue
    Write-Host "5. View recent logs" -ForegroundColor Magenta
    Write-Host "6. Exit" -ForegroundColor Gray
    Write-Host "=" * 60 -ForegroundColor Gray
}

function Show-RecentLogs {
    Write-Host "`n📝 Recent Monitor Logs:" -ForegroundColor Cyan
    if (Test-Path $LogPath) {
        Get-Content $LogPath -Tail 20 | ForEach-Object {
            if ($_ -match "\[ERROR\]") {
                Write-Host $_ -ForegroundColor Red
            } elseif ($_ -match "\[WARN\]") {
                Write-Host $_ -ForegroundColor Yellow
            } elseif ($_ -match "✅") {
                Write-Host $_ -ForegroundColor Green
            } else {
                Write-Host $_
            }
        }
    } else {
        Write-Host "No logs found yet." -ForegroundColor Gray
    }
}

# Main script execution
try {
    Write-TaskLog "🚀 VeoGen Task Scheduler Setup v1.0"
    
    # Check administrator privileges
    if (-not (Test-Administrator)) {
        Write-Host "❌ This script requires Administrator privileges" -ForegroundColor Red
        Write-Host "Please right-click and 'Run as Administrator'" -ForegroundColor Yellow
        pause
        exit 1
    }
    
    Write-TaskLog "✅ Running with Administrator privileges"
    
    # Interactive menu
    do {
        Show-Menu
        $choice = Read-Host "`nSelect option (1-6)"
        
        switch ($choice) {
            "1" {
                Write-Host "`n🔧 Installing VeoGen monitoring task..." -ForegroundColor Yellow
                if (Test-MonitoringScript) {
                    if (Install-VeogenMonitorTask) {
                        Write-Host "✅ Task installed successfully!" -ForegroundColor Green
                        Write-Host "📊 Monitoring will run every $IntervalMinutes minutes" -ForegroundColor Cyan
                        Write-Host "📝 Check logs at: $LogPath" -ForegroundColor Gray
                    } else {
                        Write-Host "❌ Task installation failed" -ForegroundColor Red
                    }
                } else {
                    Write-Host "❌ Monitoring script test failed - please check the script" -ForegroundColor Red
                }
                pause
            }
            "2" {
                Write-Host "`n🗑️ Removing VeoGen monitoring task..." -ForegroundColor Yellow
                Remove-VeogenMonitorTask
                pause
            }
            "3" {
                Write-Host "`n📊 Checking task status..." -ForegroundColor Yellow
                Show-TaskStatus
                pause
            }
            "4" {
                Write-Host "`n🧪 Testing monitoring script..." -ForegroundColor Yellow
                Test-MonitoringScript
                pause
            }
            "5" {
                Show-RecentLogs
                pause
            }
            "6" {
                Write-Host "`n👋 Goodbye!" -ForegroundColor Green
                break
            }
            default {
                Write-Host "`n❌ Invalid option. Please select 1-6." -ForegroundColor Red
                pause
            }
        }
    } while ($choice -ne "6")
    
    Write-TaskLog "🏁 Task Scheduler setup session completed"
}
catch {
    Write-TaskLog "💥 Critical error: $($_.Exception.Message)"
    Write-Host "💥 Critical error: $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

exit 0