@echo off
echo === Docsify Sidebar Rebuilder ===
echo.
echo Options:
echo 1. Rebuild sidebar once
echo 2. Rebuild and watch for changes
echo 3. Rebuild with verbose output
echo.
choice /c 123 /m "Choose option"

if %errorlevel%==1 (
    echo Building sidebar...
    powershell -ExecutionPolicy Bypass -File "rebuild-sidebar.ps1"
)
if %errorlevel%==2 (
    echo Building sidebar and watching for changes...
    echo Press Ctrl+C to stop watching
    powershell -ExecutionPolicy Bypass -File "rebuild-sidebar.ps1" -Watch
)
if %errorlevel%==3 (
    echo Building sidebar with verbose output...
    powershell -ExecutionPolicy Bypass -File "rebuild-sidebar.ps1" -Verbose
)

pause
