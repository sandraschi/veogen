# Fix Text Corruption in Markdown Files
# This script finds and fixes common AI-generated text corruption patterns

param(
    [string]$Path = ".",
    [switch]$DryRun = $false
)

$corruptionPatterns = @{
    # Missing spaces
    "Whato" = "What to"
    "404sometimes" = "404 sometimes"
    "bexpanded" = "be expanded"
    "academicitations" = "academic citations"
    "feelike" = "feel like"
    "physicalaws" = "physical laws"
    "inon-human" = "in non-human"
    "separatevolutionary" = "separate evolutionary"
    "thexplanatory" = "the explanatory"
    "Qualiand" = "Qualia and"
    "abouthe" = "about the"
    "onlinedition" = "online edition"
    "Reversengineering" = "Reverse engineering"
    "withex" = "with hex"
    "iOS android" = "iOS and Android"
    "imagen" = "image generation"
    "washown" = "was shown"
    "toptimize" = "to optimize"
    "roboto" = "robot to"
    "morestablished" = "more established"
    "naturalanguage" = "natural language"
    "integratedirectly" = "integrated directly"
    "itstate-of-the-art" = "its state-of-the-art"
    "topenly" = "to openly"
    "Abstracthis" = "Abstract"
    "Wexamine" = "We examine"
    "thethical" = "the ethical"
    "ineutron" = "in neutron"
    "thatranscends" = "that transcends"
    "Cambridge Declaration Consciousness" = "Cambridge Declaration on Consciousness"
    "othervolutionary" = "other evolutionary"
    
    # Missing words
    "this an error" = "this is an error"
    "the an error" = "the is an error"
    "is an error" = "is an error"
}

Write-Host "Scanning for text corruption patterns..." -ForegroundColor Yellow

$markdownFiles = Get-ChildItem -Path $Path -Filter "*.md" -Recurse
$totalFiles = $markdownFiles.Count
$processedFiles = 0
$totalReplacements = 0

foreach ($file in $markdownFiles) {
    $processedFiles++
    Write-Progress -Activity "Processing files" -Status "File $processedFiles of $totalFiles" -PercentComplete (($processedFiles / $totalFiles) * 100)
    
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $fileReplacements = 0
    
    foreach ($pattern in $corruptionPatterns.GetEnumerator()) {
        $oldText = $pattern.Key
        $newText = $pattern.Value
        
        if ($content -match [regex]::Escape($oldText)) {
            $count = ([regex]::Matches($content, [regex]::Escape($oldText))).Count
            $fileReplacements += $count
            $totalReplacements += $count
            
            if (-not $DryRun) {
                $content = $content -replace [regex]::Escape($oldText), $newText
            }
            
            Write-Host "Found '$oldText' -> '$newText' ($count times) in $($file.Name)" -ForegroundColor Red
        }
    }
    
    if ($fileReplacements -gt 0) {
        Write-Host "$($file.Name): $fileReplacements replacements" -ForegroundColor Cyan
        
        if (-not $DryRun) {
            Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
            Write-Host "Fixed" -ForegroundColor Green
        }
    }
}

Write-Progress -Activity "Processing files" -Completed

Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "Files processed: $processedFiles" -ForegroundColor White
Write-Host "Total replacements: $totalReplacements" -ForegroundColor White

if ($DryRun) {
    Write-Host "This was a dry run. Use -DryRun:`$false to apply fixes." -ForegroundColor Yellow
} else {
    Write-Host "All fixes applied successfully!" -ForegroundColor Green
}

Write-Host "`nTip: Run this script periodically to catch new corruption patterns." -ForegroundColor Cyan 