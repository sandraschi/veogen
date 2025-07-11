@echo off
echo Installing Playwright browsers...
cd /d "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

echo Trying npm playwright install...
call npm install playwright
call npx playwright install

echo Trying direct chromium install...
call npx playwright install chromium

echo Trying to install chrome specifically...
call npx playwright install chrome

echo Done. Checking what browsers are available...
call npx playwright --version

pause
