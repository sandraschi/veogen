# Enhanced PowerShell script to generate _sidebar.md for Windsurf docs in Google Drive
# Usage: .\rebuild-sidebar.ps1 [-Watch] [-Verbose]

param(
    [switch]$Watch,
    [switch]$Verbose
)

# Configuration
$docsifyRoot = $PSScriptRoot
$windsurfDocsPath = Join-Path $docsifyRoot "windsurf-docs"
$sidebarPath = Join-Path $docsifyRoot "_sidebar.md"
$excludeDirs = @('node_modules', '.git', '.github', '_media', 'assets', 'css', 'js', 'plugins', 'flows', 'junk', '.windsurf')
$excludeFiles = @('_sidebar.md', 'index.html', 'README.md', '.gitignore', '.nojekyll')

function Write-LogMessage {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Format-Title {
    param([string]$Name)
    
    # Clean up the name: remove numbers, underscores, hyphens
    $cleaned = $Name -replace '^\d+[-_]?', '' -replace '[-_]', ' '
    
    # Convert to title case
    return (Get-Culture).TextInfo.ToTitleCase($cleaned.ToLower())
}

function Get-MarkdownStructure {
    param (
        [string]$Directory,
        [string]$RelativeBase = "",
        [int]$Level = 0,
        [int]$MaxDepth = 4
    )
    
    if ($Level -gt $MaxDepth) { return @() }
    
    $indent = '  ' * $Level
    $content = @()
    
    if (!(Test-Path $Directory)) {
        Write-LogMessage "Directory not found: $Directory" "WARNING"
        return @()
    }
    
    try {
        # Get directories first, then files
        $directories = Get-ChildItem -Path $Directory -Directory -ErrorAction SilentlyContinue | 
                      Where-Object { $excludeDirs -notcontains $_.Name -and !$_.Name.StartsWith('.') } |
                      Sort-Object Name
        
        $files = Get-ChildItem -Path $Directory -File -Filter "*.md" -ErrorAction SilentlyContinue |
                Where-Object { $excludeFiles -notcontains $_.Name -and !$_.Name.StartsWith('_') } |
                Sort-Object Name
        
        # Process directories
        foreach ($dir in $directories) {
            $dirTitle = Format-Title $dir.Name
            $relativePath = if ($RelativeBase) { "$RelativeBase/$($dir.Name)" } else { $dir.Name }
            
            # Check if directory has a README.md
            $readmePath = Join-Path $dir.FullName "README.md"
            if (Test-Path $readmePath) {
                $content += "$indent- [**$dirTitle**]($relativePath/)"
            } else {
                $content += "$indent- **$dirTitle**"
            }
            
            # Recursively process subdirectories
            $subContent = Get-MarkdownStructure -Directory $dir.FullName -RelativeBase $relativePath -Level ($Level + 1) -MaxDepth $MaxDepth
            if ($subContent) {
                $content += $subContent
            }
        }
        
        # Process markdown files
        foreach ($file in $files) {
            $fileTitle = Format-Title ([System.IO.Path]::GetFileNameWithoutExtension($file.Name))
            $relativePath = if ($RelativeBase) { "$RelativeBase/$($file.Name)" } else { $file.Name }
            $content += "$indent- [$fileTitle]($relativePath)"
        }
        
    } catch {
        Write-LogMessage "Error processing directory $Directory`: $($_.Exception.Message)" "ERROR"
    }
    
    return $content
}

function Build-Sidebar {
    Write-LogMessage "Starting sidebar generation..."
    
    # Check if windsurf-docs exists
    if (!(Test-Path $windsurfDocsPath)) {
        Write-LogMessage "Windsurf docs path not found: $windsurfDocsPath" "ERROR"
        Write-LogMessage "Make sure the symbolic link is created properly" "ERROR"
        return $false
    }
    
    # Start building sidebar content
    $sidebarContent = @()
    
    # Header
    $sidebarContent += "- [Home](/)"
    $sidebarContent += "- [**Features**](features/)"
    $sidebarContent += "  - [Image Generation](features/image-generation.md)"
    $sidebarContent += "  - [Music Generation](features/music-generation.md)"
    $sidebarContent += "  - [Video Generation](features/video-generation.md)"
    $sidebarContent += "  - [Book & Movie Maker](features/book-movie-maker-guide.md)"
    $sidebarContent += "- [**Architecture**](architecture/)"
    $sidebarContent += "  - [AI Communication Flows](architecture/ai-communication-flows.md)"
    $sidebarContent += "  - [Mermaid Diagrams Guide](architecture/mermaid-diagrams-guide.md)"
    $sidebarContent += "  - [System Architecture](architecture/system-architecture.md)"
    $sidebarContent += "  - [Technology Stack](architecture/technology-stack.md)"
    
    # Windsurf Docs Section
    $sidebarContent += "- [**Windsurf Docs**](windsurf-docs/)"
    
    # Generate dynamic content from windsurf-docs
    $windsurfContent = Get-MarkdownStructure -Directory $windsurfDocsPath -RelativeBase "windsurf-docs" -Level 1
    if ($windsurfContent) {
        $sidebarContent += $windsurfContent
    }
    
    # Footer sections
    $sidebarContent += "- [Getting Started](getting-started.md)"
    $sidebarContent += "- [Interface Guide](interface-guide.md)"
    $sidebarContent += "- [Movie Maker](movie-maker.md)"
    $sidebarContent += "- [Gallery](gallery.md)"
    $sidebarContent += "- [Plugins](plugins.md)"
    $sidebarContent += "- [Documentation](documentation.md)"
    $sidebarContent += "- [Docker Guide](README-Docker.md)"
    
    # Write to _sidebar.md
    try {
        $sidebarContent | Out-File -FilePath $sidebarPath -Encoding UTF8 -Force
        Write-LogMessage "Sidebar generated successfully at: $sidebarPath" "SUCCESS"
        
        if ($Verbose) {
            Write-LogMessage "Generated $($sidebarContent.Count) sidebar entries" "INFO"
            Write-LogMessage "Windsurf docs path: $windsurfDocsPath" "INFO"
        }
        
        return $true
    } catch {
        Write-LogMessage "Error writing sidebar file: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-FileWatcher {
    Write-LogMessage "Starting file watcher for automatic sidebar regeneration..." "INFO"
    Write-LogMessage "Watching: $windsurfDocsPath" "INFO"
    Write-LogMessage "Press Ctrl+C to stop watching" "INFO"
    
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $windsurfDocsPath
    $watcher.Filter = "*.*"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true
    
    $action = {
        $event = $Event.SourceEventArgs
        $changeType = $event.ChangeType
        $path = $event.FullPath
        
        # Only rebuild for .md files or directory changes
        if ($path.EndsWith('.md') -or $changeType -eq 'Created' -or $changeType -eq 'Deleted') {
            Write-LogMessage "File change detected: $path ($changeType)" "INFO"
            Start-Sleep -Milliseconds 500  # Debounce
            Build-Sidebar
        }
    }
    
    Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Renamed" -Action $action
    
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        $watcher.EnableRaisingEvents = $false
        $watcher.Dispose()
        Write-LogMessage "File watcher stopped." "INFO"
    }
}

# Main execution
Write-LogMessage "=== Docsify Sidebar Generator ===" "INFO"

if ($Watch) {
    # Build initial sidebar
    if (Build-Sidebar) {
        Start-FileWatcher
    } else {
        Write-LogMessage "Initial sidebar build failed. Not starting watcher." "ERROR"
        exit 1
    }
} else {
    # Single build
    if (Build-Sidebar) {
        Write-LogMessage "Sidebar generation completed successfully!" "SUCCESS"
        exit 0
    } else {
        Write-LogMessage "Sidebar generation failed!" "ERROR"
        exit 1
    }
}
