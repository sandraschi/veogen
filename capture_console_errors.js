const { chromium } = require('playwright');

/**
 * Capture JavaScript Console Errors During Login
 */

async function captureConsoleErrors() {
    console.log('🔍 Capturing JavaScript Console Errors...');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 1000
    });
    
    const page = await browser.newPage();
    
    // Capture ALL console messages
    const consoleMessages = [];
    
    page.on('console', msg => {
        const messageInfo = {
            type: msg.type(),
            text: msg.text(),
            location: msg.location()
        };
        consoleMessages.push(messageInfo);
        
        // Print immediately for real-time debugging
        console.log(`[BROWSER ${msg.type().toUpperCase()}]: ${msg.text()}`);
        if (msg.location()) {
            console.log(`  Location: ${msg.location().url}:${msg.location().lineNumber}`);
        }
    });
    
    // Capture page errors
    page.on('pageerror', error => {
        console.log(`[PAGE ERROR]: ${error.message}`);
        console.log(`Stack: ${error.stack}`);
    });
    
    // Capture request failures
    page.on('requestfailed', request => {
        console.log(`[REQUEST FAILED]: ${request.url()}`);
        console.log(`  Failure: ${request.failure().errorText}`);
    });
    
    try {
        console.log('\n=== STEP 1: Navigate ===');
        await page.goto('http://localhost:4710');
        await page.waitForTimeout(3000);
        
        console.log('\n=== STEP 2: Fill Login Form ===');
        await page.fill('input[type="email"]', 'valid@test.com');
        await page.fill('input[type="password"]', 'Test123!');
        await page.waitForTimeout(1000);
        
        console.log('\n=== STEP 3: Submit and Watch Console ===');
        await page.click('button:has-text("SIGN IN")');
        
        // Wait longer to capture all console messages
        console.log('Waiting 10 seconds to capture all console activity...');
        await page.waitForTimeout(10000);
        
        console.log('\n=== CONSOLE MESSAGE SUMMARY ===');
        console.log(`Total console messages: ${consoleMessages.length}`);
        
        const errorMessages = consoleMessages.filter(msg => msg.type === 'error');
        const warningMessages = consoleMessages.filter(msg => msg.type === 'warning');
        const logMessages = consoleMessages.filter(msg => msg.type === 'log');
        
        console.log(`Errors: ${errorMessages.length}`);
        console.log(`Warnings: ${warningMessages.length}`);
        console.log(`Logs: ${logMessages.length}`);
        
        if (errorMessages.length > 0) {
            console.log('\n🚨 JAVASCRIPT ERRORS FOUND:');
            errorMessages.forEach((error, i) => {
                console.log(`${i + 1}. ${error.text}`);
                if (error.location) {
                    console.log(`   Location: ${error.location.url}:${error.location.lineNumber}`);
                }
            });
        }
        
        // Check final page state
        const currentURL = page.url();
        const hasToken = await page.evaluate(() => !!localStorage.getItem('token'));
        const errorElements = await page.locator('.error, .alert-danger, [role="alert"]').count();
        
        console.log('\n=== FINAL STATE ===');
        console.log(`Current URL: ${currentURL}`);
        console.log(`Has Token: ${hasToken}`);
        console.log(`Error Elements on Page: ${errorElements}`);
        
        if (errorElements > 0) {
            const errorTexts = await page.locator('.error, .alert-danger, [role="alert"]').allTextContents();
            console.log('Error Messages:');
            errorTexts.forEach((text, i) => console.log(`  ${i + 1}: ${text}`));
        }
        
        console.log('\n🎭 Browser staying open for 15 seconds...');
        await page.waitForTimeout(15000);
        
    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        await page.waitForTimeout(5000);
    } finally {
        await browser.close();
        console.log('🎬 Console capture complete!');
    }
}

captureConsoleErrors().catch(console.error);