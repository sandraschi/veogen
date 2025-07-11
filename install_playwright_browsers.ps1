# Install Playwright browsers
cd "C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen"

Write-Host "Installing Playwright browsers..."

# Try different installation methods
Write-Host "Method 1: Basic playwright install"
npm install playwright

Write-Host "Method 2: Install all browsers"
npx playwright install

Write-Host "Method 3: Install specific browsers"
npx playwright install chromium
npx playwright install firefox  
npx playwright install webkit

Write-Host "Method 4: Install Chrome specifically"
npx playwright install chrome

Write-Host "Method 5: Install Edge"
npx playwright install msedge

Write-Host "Checking installation..."
npx playwright --version

Write-Host "Done!"
