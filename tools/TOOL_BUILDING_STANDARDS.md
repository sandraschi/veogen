# 📐 VeoGen Tool Building Standards - Complete Developer Guide

## 🎯 **Purpose**
This document establishes comprehensive standards for building professional tools in the VeoGen ecosystem. Every tool must meet these standards to ensure consistency, quality, and maintainability.

## 🏗️ **Architecture Standards**

### **File Structure Template**
Every VeoGen tool MUST follow this exact structure:
```
tool-name/
├── README.md              # Complete documentation
├── tool-name.html         # Artifact window interface
├── tool-name.ps1          # PowerShell script
├── start.ps1              # PowerShell launcher
├── start.bat              # Batch launcher
└── assets/                # Optional: images, styles
    └── screenshots/       # Tool demonstration images
```

### **Naming Conventions**
- **Tool directories**: `kebab-case` (e.g., `mcp-config-analyzer`)
- **File names**: Match directory name (e.g., `mcp-config-analyzer.html`)
- **Functions**: `PascalCase` for PowerShell (e.g., `Test-Configuration`)
- **Variables**: `camelCase` for JavaScript (e.g., `configData`)

## 🎨 **UI/UX Standards**

### **Artifact Window Design Requirements**
```css
/* MANDATORY: VeoGen brand identity */
:root {
    --vg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --vg-secondary: rgba(255, 255, 255, 0.95);
    --vg-accent: #3498db;
    --vg-success: #27ae60;
    --vg-warning: #f39c12;
    --vg-danger: #e74c3c;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--vg-primary);
    min-height: 100vh;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: var(--vg-secondary);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}
```

### **Responsive Design Requirements**
- **Mobile-first**: Design for 320px+ width
- **Artifact window**: Optimize for 800-1200px artifact display
- **Grid systems**: Use CSS Grid or Flexbox, never floats
- **Typography**: Minimum 14px font size, 1.6 line height

### **Interaction Standards**
- **Loading states**: Show spinners for operations > 1 second
- **Error handling**: User-friendly messages, never raw errors
- **Success feedback**: Clear confirmation of completed actions
- **Micro-animations**: Smooth transitions (300ms max)

## ⚡ **PowerShell Standards**

### **Script Structure Template**
```powershell
#Requires -Version 5.1

<#
.SYNOPSIS
    [Tool Name] - VeoGen Professional Tool

.DESCRIPTION
    [Detailed description of what the tool does]

.PARAMETER All
    Runs complete analysis

.PARAMETER Quick
    Runs quick health check

.PARAMETER Help
    Shows detailed help information

.EXAMPLE
    .\tool-name.ps1 -All
    Runs complete analysis

.NOTES
    Part of VeoGen Tools Ecosystem
    Created: [Date]
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [switch]$All,
    [switch]$Quick,
    [switch]$Help,
    [string]$LogLevel = "Info"
)

# Tool header
Write-Host "🔧 [Tool Name] - VeoGen Professional Tool" -ForegroundColor Cyan
Write-Host "Purpose: [Clear description]" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan

# Parameter validation
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# Main logic
try {
    if ($All) {
        Write-Host "`n🔍 Starting complete analysis..." -ForegroundColor Yellow
        # Implementation here
    }
    
    if ($Quick) {
        Write-Host "`n⚡ Running quick check..." -ForegroundColor Yellow
        # Implementation here
    }
}
catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    Write-Host "`n✅ Analysis complete!" -ForegroundColor Green
}
```

### **Error Handling Standards**
```powershell
# MANDATORY: Try-catch blocks for all operations
try {
    $result = Invoke-SomeOperation
    Write-Host "✅ Operation successful" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Suggestion: Check configuration and try again" -ForegroundColor Yellow
    exit 1
}
```

### **Output Formatting Standards**
```powershell
# Use consistent color coding
Write-Host "🚀 Starting..." -ForegroundColor Cyan      # Info
Write-Host "✅ Success!" -ForegroundColor Green        # Success
Write-Host "⚠️ Warning" -ForegroundColor Yellow        # Warning
Write-Host "❌ Error" -ForegroundColor Red             # Error
Write-Host "💡 Tip" -ForegroundColor Magenta           # Tips
Write-Host "📊 Results" -ForegroundColor Blue          # Data
```

## 🔗 **Integration Standards**

### **Basic Memory Integration**
Every tool should support session logging:
```powershell
function Save-ToolContext {
    param(
        [string]$ToolName,
        [string]$Operation,
        [string]$Status
    )
    
    $context = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Tool = $ToolName
        Operation = $Operation
        Status = $Status
        User = $env:USERNAME
        Machine = $env:COMPUTERNAME
    }
    
    # Log to basic memory via Claude API if available
    # Implementation depends on available APIs
}
```

### **VeoGen Ecosystem Integration**
- **Port allocation**: Use ports 8100-8199 for tool servers
- **Configuration**: Store in `tools/config/` directory
- **Logs**: Write to `tools/logs/tool-name.log`
- **Backups**: Create in `tools/backups/` with timestamps

## 📊 **Testing Standards**

### **Quality Gates Checklist**
Before any tool is considered complete:

#### **Functional Testing**
- [ ] HTML interface loads without errors
- [ ] All buttons and controls work
- [ ] PowerShell script runs with all parameters
- [ ] Error handling works correctly
- [ ] Help documentation is accurate

#### **Integration Testing**
- [ ] Tool integrates with VeoGen ecosystem
- [ ] File paths work on Sandra's system
- [ ] No conflicts with other tools
- [ ] Performance is acceptable (< 5 second startup)

#### **User Experience Testing**
- [ ] Interface is intuitive without training
- [ ] Error messages are helpful
- [ ] Success feedback is clear
- [ ] Documentation matches functionality

### **Test Automation Template**
```powershell
# tools/test/Test-ToolName.ps1
function Test-ToolName {
    Write-Host "🧪 Testing [Tool Name]..." -ForegroundColor Cyan
    
    # Test 1: PowerShell script
    try {
        & ".\tool-name.ps1" -Help
        Write-Host "✅ PowerShell script help works" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ PowerShell script failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Test 2: HTML file exists and valid
    if (Test-Path ".\tool-name.html") {
        Write-Host "✅ HTML interface exists" -ForegroundColor Green
    }
    else {
        Write-Host "❌ HTML interface missing" -ForegroundColor Red
        return $false
    }
    
    # Test 3: Documentation
    if (Test-Path ".\README.md") {
        $readme = Get-Content ".\README.md" -Raw
        if ($readme.Length -gt 500) {
            Write-Host "✅ Documentation is comprehensive" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️ Documentation may be incomplete" -ForegroundColor Yellow
        }
    }
    
    Write-Host "🎉 [Tool Name] passes all tests!" -ForegroundColor Green
    return $true
}
```

## 🛡️ **Security Standards**

### **Input Validation**
```powershell
# MANDATORY: Validate all user inputs
function Test-UserInput {
    param([string]$Input)
    
    # Check for dangerous characters
    $dangerousChars = @('&', '|', ';', '$', '`', '\', '"', "'", '<', '>')
    foreach ($char in $dangerousChars) {
        if ($Input.Contains($char)) {
            throw "Invalid character detected: $char"
        }
    }
    
    # Check length
    if ($Input.Length -gt 1000) {
        throw "Input too long (max 1000 characters)"
    }
}
```

### **File System Safety**
```powershell
# MANDATORY: Validate paths before file operations
function Test-SafePath {
    param([string]$Path)
    
    # Must be within allowed directories
    $allowedPaths = @(
        "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen",
        "C:\Users\sandr\AppData\Roaming\Claude"
    )
    
    $resolvedPath = Resolve-Path $Path -ErrorAction SilentlyContinue
    if (-not $resolvedPath) {
        throw "Path does not exist: $Path"
    }
    
    $isAllowed = $false
    foreach ($allowed in $allowedPaths) {
        if ($resolvedPath.Path.StartsWith($allowed)) {
            $isAllowed = $true
            break
        }
    }
    
    if (-not $isAllowed) {
        throw "Path outside allowed directories: $Path"
    }
}
```

## 📚 **Documentation Standards**

### **README.md Template**
```markdown
# 🔧 [Tool Name] - VeoGen Professional Tool

## 🎯 Purpose
[1-2 sentences describing what problem this tool solves]

## 🚀 Quick Start
```powershell
# 30-second setup
.\start.ps1 web      # Open web interface
.\start.ps1 analyze  # Run analysis
```

## 📋 Features
- ✅ [Feature 1] - [Brief description]
- ✅ [Feature 2] - [Brief description]
- ✅ [Feature 3] - [Brief description]

## 🎨 Interfaces

### **Web Interface** 🌐
- **File**: [tool-name].html
- **Usage**: Open in artifact window for beautiful interface

### **PowerShell Script** ⚡
- **File**: [tool-name].ps1
- **Usage**: `.\[tool-name].ps1 -All` for complete analysis

## 📊 Screenshots
[Include at least one screenshot of the tool in action]

## 🔧 Configuration
[Any configuration requirements or environment setup]

## 🧪 Testing
[How to verify the tool works correctly]

## 📈 Troubleshooting
[Common issues and solutions]

## 📍 Integration
Part of VeoGen Professional Tool Suite

**Category**: [analysis/monitoring/management]  
**Created**: [Date]  
**Version**: 1.0.0  
**Status**: Production Ready ✅
```

### **Code Documentation Standards**
- **Functions**: JSDoc comments for JavaScript, comment-based help for PowerShell
- **Variables**: Descriptive names, no single letters except loop counters
- **Comments**: Explain WHY, not WHAT (code should be self-documenting)
- **TODOs**: Include author and date: `# TODO (Sandra, 2025-07-10): Add error logging`

## 🎯 **Performance Standards**

### **Response Time Requirements**
- **Web interface load**: < 2 seconds
- **PowerShell script startup**: < 3 seconds
- **Analysis operations**: Progress indicators for > 5 seconds
- **File operations**: Async for > 1 second operations

### **Resource Usage Guidelines**
- **Memory**: < 100MB for typical operations
- **CPU**: Don't monopolize (use Start-Sleep for long loops)
- **Disk space**: Clean up temporary files automatically
- **Network**: Timeout after 30 seconds for web requests

## 🔄 **Maintenance Standards**

### **Version Control**
- **Semantic versioning**: Major.Minor.Patch (e.g., 1.2.3)
- **Change logs**: Document all changes in README
- **Backward compatibility**: Don't break existing interfaces
- **Deprecation**: 30-day notice before removing features

### **Update Process**
1. **Backup**: Create backup before updates
2. **Test**: Run quality gates on updated version
3. **Document**: Update README and version numbers
4. **Deploy**: Replace files atomically
5. **Verify**: Confirm tool still works correctly

## 📧 **Support Standards**

### **Error Reporting**
When tools fail, they should provide:
```
❌ Error: [Clear description of what went wrong]
💡 Suggestion: [Actionable steps to fix the issue]
📍 Location: [File/line where error occurred]
🕐 Time: [Timestamp of error]
📋 Context: [What the user was trying to do]
```

### **User Feedback**
- **Success messages**: Clear confirmation of completed actions
- **Progress indicators**: Show what's happening during long operations
- **Help text**: Available via -Help parameter or ? button
- **Examples**: Include working examples in documentation

---

## 🎯 **Compliance Checklist**

Before marking any tool as "complete":

### **File Structure**
- [ ] All required files present and named correctly
- [ ] Directory structure matches template
- [ ] No extraneous files or temporary data

### **Functionality**
- [ ] Web interface loads and functions correctly
- [ ] PowerShell script runs with all parameters
- [ ] All launchers work (start.ps1, start.bat)
- [ ] Error handling works properly

### **Quality**
- [ ] Code follows style guidelines
- [ ] Documentation is complete and accurate
- [ ] Testing passes all quality gates
- [ ] Performance meets requirements

### **Integration**
- [ ] Fits properly in VeoGen ecosystem
- [ ] Uses correct ports and paths
- [ ] No conflicts with other tools
- [ ] Session logging implemented

---

**This document ensures every VeoGen tool meets professional standards and provides excellent user experience.**

**Created**: July 10, 2025  
**Version**: 1.0.0  
**Status**: Active Standard ✅