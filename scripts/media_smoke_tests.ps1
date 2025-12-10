# Basic media/API smoke tests for new integrations
param(
    [string]$ApiBase = "http://localhost:8000/api/v1"
)

function Show-Result($title, $expr) {
    Write-Host "`n[$title]"
    try {
        $r = Invoke-RestMethod -Method GET -Uri $expr -TimeoutSec 15
        $r | ConvertTo-Json -Depth 5
    } catch {
        Write-Host "Request failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "=== VeoGen Media Smoke Tests ==="

# 0) Auth reminder
Write-Host "Ensure you are logged in (cookies) if endpoints require auth."

# 1) Flow projects list (requires FLOW_ENABLED)
Show-Result "Flow: List Projects" "$ApiBase/flow/projects"

# 2) Prompt Coach availability (requires PROMPT_COACH_ENABLED)
Write-Host "`n[Prompt Coach: Start Session]"
try {
    $session = Invoke-RestMethod -Method POST -Uri "$ApiBase/prompt-coach/session" -TimeoutSec 15
    $session | ConvertTo-Json -Depth 5
    $sid = $session.session_id
    if ($sid) {
        Write-Host "`n[Prompt Coach: Critique]"
        $body = @{ session_id = $sid; prompt = "Rainy neon alley, tracking shot, reflective puddles." } | ConvertTo-Json
        $crit = Invoke-RestMethod -Method POST -Uri "$ApiBase/prompt-coach/critique" -ContentType "application/json" -Body $body -TimeoutSec 30
        $crit | ConvertTo-Json -Depth 5
    }
} catch {
    Write-Host "Prompt Coach unavailable or disabled: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3) Sound Design (requires AUDIOFX_ENABLED)
Write-Host "`n[Sound Design: Generate]"
try {
    $sd = @{
        prompt = "Soft sci-fi engine hum with subtle modulation"
        duration_seconds = 10
        category = "ambience"
        loop = $true
        bpm = 100
        intensity = "low"
    } | ConvertTo-Json
    $res = Invoke-RestMethod -Method POST -Uri "$ApiBase/sound-design/generate" -ContentType "application/json" -Body $sd -TimeoutSec 60
    $res | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Sound Design unavailable or disabled: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4) Compliance audit (requires SYNTHID_DASHBOARD_ENABLED)
Write-Host "`n[Compliance: SynthID Audit]"
try {
    $audit = Invoke-RestMethod -Method POST -Uri "$ApiBase/compliance/synthid/audit" -TimeoutSec 20
    $audit | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Compliance audit unavailable or disabled: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nSmoke tests completed."

