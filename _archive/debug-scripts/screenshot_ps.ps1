# Create screenshots directory if it doesn't exist
$screenshotsDir = Join-Path -Path $PSScriptRoot -ChildPath 'screenshots'
if (-not (Test-Path -Path $screenshotsDir)) {
    New-Item -ItemType Directory -Path $screenshotsDir | Out-Null
}

# Generate timestamp for filename
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$screenshotPath = Join-Path -Path $screenshotsDir -ChildPath "dashboard-$timestamp.png"

# Try to capture the screenshot using different methods
$success = $false

# Method 1: Using WebClient
if (-not $success) {
    try {
        $url = "http://localhost:5000/"
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($url, $screenshotPath)
        $success = $true
        Write-Host "Screenshot saved using WebClient: $screenshotPath" -ForegroundColor Green
    } catch {
        Write-Host "WebClient method failed: $_" -ForegroundColor Yellow
    }
}

# Method 2: Using Invoke-WebRequest
if (-not $success) {
    try {
        $url = "http://localhost:5000/"
        Invoke-WebRequest -Uri $url -OutFile $screenshotPath
        $success = $true
        Write-Host "Screenshot saved using Invoke-WebRequest: $screenshotPath" -ForegroundColor Green
    } catch {
        Write-Host "Invoke-WebRequest method failed: $_" -ForegroundColor Yellow
    }
}

if (-not $success) {
    Write-Host "Failed to capture screenshot. Please try one of these options:" -ForegroundColor Red
    Write-Host "1. Check if the server is running on http://localhost:5000/"
    Write-Host "2. Try accessing the URL in your web browser"
    Write-Host "3. Install Playwright manually: 'npm install playwright'"
}
