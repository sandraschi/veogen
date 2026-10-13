const { chromium } = require('playwright');
const path = require('path');

(async () => {
    // Launch browser in headless mode
    const browser = await chromium.launch({ headless: true });
    
    try {
        // Create a new browser context and page
        const context = await browser.newContext();
        const page = await context.newPage();
        
        console.log('Navigating to http://localhost:5000/...');
        await page.goto('http://localhost:5000/', { waitUntil: 'networkidle' });
        
        // Create screenshots directory if it doesn't exist
        const fs = require('fs');
        const screenshotsDir = path.join(__dirname, 'screenshots');
        if (!fs.existsSync(screenshotsDir)) {
            fs.mkdirSync(screenshotsDir);
        }
        
        // Take screenshot with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const screenshotPath = path.join(screenshotsDir, `dashboard-${timestamp}.png`);
        
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Screenshot saved to: ${screenshotPath}`);
        
    } catch (error) {
        console.error('Error during screenshot capture:', error);
    } finally {
        // Close the browser
        await browser.close();
        console.log('Browser closed.');
    }
})();
