@echo off
echo Starting Docsify Auto-Rebuild Watcher...
echo This will watch for changes in windsurf-docs and automatically rebuild the sidebar
echo Press Ctrl+C to stop
echo.
node auto-rebuild-watcher.js --verbose
pause
