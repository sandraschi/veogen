const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Create a log file
const logFile = path.join(__dirname, 'playwright_debug.log');

function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}\n`;
    console.log(logMessage);
    fs.appendFileSync(logFile, logMessage);
}

async function main() {
    log('Starting Playwright debug script');
    
    try {
        log('Attempting to launch browser...');
        const browser = await chromium.launch({ 
            headless: true,
            timeout: 30000 // 30 second timeout
        });
        log('Browser launched successfully');
        
        try {
            log('Creating new context and page');
            const context = await browser.newContext();
            const page = await context.newPage();
            
            const url = 'http://localhost:5000/';
            log(`Navigating to ${url}`);
            
            await page.goto(url, { 
                waitUntil: 'networkidle',
                timeout: 30000
            });
            
            log('Page loaded successfully');
            
            // Create screenshots directory
            const screenshotsDir = path.join(__dirname, 'screenshots');
            if (!fs.existsSync(screenshotsDir)) {
                fs.mkdirSync(screenshotsDir);
                log(`Created directory: ${screenshotsDir}`);
            }
            
            // Take screenshot
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshotPath = path.join(screenshotsDir, `dashboard-${timestamp}.png`);
            
            log(`Taking screenshot and saving to: ${screenshotPath}`);
            await page.screenshot({ 
                path: screenshotPath, 
                fullPage: true 
            });
            
            log('Screenshot captured successfully');
            
        } catch (error) {
            log(`Error during page interaction: ${error.message}\n${error.stack}`);
            throw error;
        } finally {
            log('Closing browser');
            await browser.close();
        }
        
    } catch (error) {
        log(`Fatal error: ${error.message}\n${error.stack}`);
        process.exit(1);
    }
}

main().catch(err => {
    console.error('Unhandled error:', err);
    process.exit(1);
});
