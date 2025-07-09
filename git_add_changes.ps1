# Git Add All Changes Script
Set-Location "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

Write-Host "📦 Adding all changes to git..." -ForegroundColor Cyan
Write-Host "📍 Working directory: $(Get-Location)" -ForegroundColor Gray

try {
    # Run git add .
    git add .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully added all changes to git!" -ForegroundColor Green
        
        # Show git status
        Write-Host ""
        Write-Host "📊 Git status:" -ForegroundColor Yellow
        $status = git status --porcelain
        
        if ($status) {
            $fileCount = ($status | Measure-Object).Count
            Write-Host "   📁 $fileCount files staged for commit" -ForegroundColor Green
            
            # Show first 10 files
            $status | Select-Object -First 10 | ForEach-Object {
                Write-Host "   $_" -ForegroundColor Gray
            }
            
            if ($fileCount -gt 10) {
                $remaining = $fileCount - 10
                Write-Host "   ... and $remaining more files" -ForegroundColor Gray
            }
        } else {
            Write-Host "   📝 No changes to stage (working tree clean)" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "🚀 Next step: Run 'git commit -m `"Fix User Manager UUID support and rebuild frontend`"'" -ForegroundColor Cyan
        
    } else {
        Write-Host "❌ Git add failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Git add failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Keep window open
Read-Host "Press Enter to exit"
