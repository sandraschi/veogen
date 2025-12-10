# Requires: uv, Python environment with project deps, running backend on $ApiBase (or start it separately)
param(
    [string]$ApiBase = "http://localhost:8000"
)

Write-Host "=== VeoGen Dev Checks ==="

# 1) Ruff lint
Write-Host "`n[1/4] Lint (ruff check) ..."
uv run ruff check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ruff check reported issues." -ForegroundColor Yellow
}

# 2) Ruff format (non-destructive validation step can be added if needed)
Write-Host "`n[2/4] Format (ruff format) ..."
uv run ruff format .

# 3) Pytests
Write-Host "`n[3/4] Tests (pytest) ..."
uv run python -m pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Review failures above." -ForegroundColor Red
    exit 1
}

# 4) Health check (optional if backend is running)
Write-Host "`n[4/4] Backend health check ..."
try {
    $resp = Invoke-RestMethod -Method GET -Uri "$ApiBase/health" -TimeoutSec 10
    Write-Host "Backend health: $($resp.status) version=$($resp.version)"
} catch {
    Write-Host "Health check failed. Is the backend running at $ApiBase ?" -ForegroundColor Yellow
}

Write-Host "`nAll checks completed."

