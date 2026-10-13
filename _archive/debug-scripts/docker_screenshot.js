const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    const browser = await chromium.launch({ 
        headless: true,
        // If running in Docker, you might need to add:
        // args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const context = await browser.newContext();
        const page = await context.newPage();
        
        console.log('Navigating to http://localhost:5000/...');
        await page.goto('http://localhost:5000/', { 
            waitUntil: 'networkidle',
            timeout: 30000
        });
        
        // Create screenshots directory if it doesn't exist
        const screenshotsDir = path.join(__dirname, 'screenshots');
        if (!fs.existsSync(screenshotsDir)) {
            fs.mkdirSync(screenshotsDir);
        }
        
        // Take screenshot with timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const screenshotPath = path.join(screenshotsDir, `docker-dashboard-${timestamp}.png`);
        
        await page.screenshot({ 
            path: screenshotPath, 
            fullPage: true 
        });
        
        console.log(`✅ Screenshot saved to: ${screenshotPath}`);
        
    } catch (error) {
        console.error('❌ Error during screenshot capture:', error);
    } finally {
        await browser.close();
    }
})();
