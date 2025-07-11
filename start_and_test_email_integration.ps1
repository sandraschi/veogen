# Start VeoGen Services and Test Email Integration
Write-Host "=== VeoGen Email Integration Test Script ===" -ForegroundColor Cyan

# Change to VeoGen directory
Write-Host "Changing to VeoGen directory..." -ForegroundColor Yellow
Set-Location "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

# Start Docker Compose services
Write-Host "Starting VeoGen services..." -ForegroundColor Green
docker-compose up -d

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Test the API health endpoint
Write-Host "Testing API health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:4700/health" -Method Get
    Write-Host "✅ API Health Status: $($health.status)" -ForegroundColor Green
    $health | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ API not ready: $_" -ForegroundColor Red
    exit 1
}

# Test Email Endpoints Integration
Write-Host "`n=== Testing Email Integration ===" -ForegroundColor Cyan

# Test email demo endpoint
Write-Host "Testing email demo endpoint..." -ForegroundColor Yellow
try {
    $demoResult = Invoke-RestMethod -Uri "http://localhost:4700/api/email/test/demo" -Method Post -ContentType "application/json"
    Write-Host "✅ Email Demo Test: SUCCESS" -ForegroundColor Green
    Write-Host "Generated emails: $($demoResult.total_emails_sent)" -ForegroundColor Green
    Write-Host "Check folder: $($demoResult.check_files)" -ForegroundColor Green
} catch {
    Write-Host "❌ Email Demo Test Failed: $_" -ForegroundColor Red
}

# Test individual email endpoints
Write-Host "`nTesting individual email endpoints..." -ForegroundColor Yellow

# Test enhanced verification
try {
    $verificationData = @{
        email = "sandraschipal@hotmail.com"
        name = "Sandra Schipal"
    } | ConvertTo-Json
    
    $verificationResult = Invoke-RestMethod -Uri "http://localhost:4700/api/email/verification/enhanced" -Method Post -Body $verificationData -ContentType "application/json"
    Write-Host "✅ Enhanced Verification: SUCCESS" -ForegroundColor Green
} catch {
    Write-Host "❌ Enhanced Verification Failed: $_" -ForegroundColor Red
}

# Test security challenge (requires user ID)
try {
    $challengeData = @{
        user_id = "demo_user_123"
        action = "Delete Account Test"
    } | ConvertTo-Json
    
    $challengeResult = Invoke-RestMethod -Uri "http://localhost:4700/api/email/challenge/initiate" -Method Post -Body $challengeData -ContentType "application/json"
    Write-Host "✅ Security Challenge: SUCCESS" -ForegroundColor Green
} catch {
    Write-Host "❌ Security Challenge Failed: $_" -ForegroundColor Red
}

# Test password reset
try {
    $resetData = @{
        email = "sandraschipal@hotmail.com"
        name = "Sandra Schipal"
    } | ConvertTo-Json
    
    $resetResult = Invoke-RestMethod -Uri "http://localhost:4700/api/email/password-reset/advanced" -Method Post -Body $resetData -ContentType "application/json"
    Write-Host "✅ Advanced Password Reset: SUCCESS" -ForegroundColor Green
} catch {
    Write-Host "❌ Advanced Password Reset Failed: $_" -ForegroundColor Red
}

# Test workflow status
try {
    $statusResult = Invoke-RestMethod -Uri "http://localhost:4700/api/email/workflows/status" -Method Get
    Write-Host "✅ Workflow Status: SUCCESS" -ForegroundColor Green
    Write-Host "Total workflows: $($statusResult.total_workflows)" -ForegroundColor Green
} catch {
    Write-Host "❌ Workflow Status Failed: $_" -ForegroundColor Red
}

Write-Host "`n=== Integration Test Complete ===" -ForegroundColor Cyan
Write-Host "Check the dev_emails/ folder for generated email files" -ForegroundColor Yellow
Write-Host "Visit http://localhost:4700/docs to see all email endpoints" -ForegroundColor Yellow