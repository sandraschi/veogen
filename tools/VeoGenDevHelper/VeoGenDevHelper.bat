@echo off
:: 🎛️ VeoGen Dev Helper Quick Launcher v2.1
:: Purpose: Environment control center for VeoGen development
:: Anti-Guillotine Protected: v2.1

echo 🎛️ VeoGen Dev Helper v2.1
echo ===========================
echo Environment Control Center
echo No More Schnitzeljagd!
echo.

:: Check if PowerShell script exists
if not exist "%~dp0VeoGenDevHelper.ps1" (
    echo ❌ ERROR: PowerShell script not found!
    echo Location: %~dp0VeoGenDevHelper.ps1
    pause
    exit /b 1
)

:: Launch Dev Helper
echo 🚀 Launching VeoGen Dev Helper...
powershell -ExecutionPolicy Bypass -File "%~dp0VeoGenDevHelper.ps1" -Start

echo.
echo ✅ VeoGen Dev Helper launched successfully!
echo 🌐 Web interface should be open in your browser
echo.
echo Quick access to VeoGen development environment:
echo   • Service monitoring
echo   • Path intelligence  
echo   • Quick actions
echo   • Anti-guillotine protection
echo.
pause