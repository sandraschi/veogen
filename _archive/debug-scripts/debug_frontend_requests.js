const { chromium } = require('playwright');

/**
 * Debug what's actually being sent from frontend
 */

async function debugFrontendRequests() {
    console.log('🔍 Debugging Frontend Login Requests...');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 1000
    });
    
    const page = await browser.newPage();
    
    // Capture all network requests
    const requests = [];
    const responses = [];
    
    page.on('request', request => {
        if (request.url().includes('/login')) {
            requests.push({
                url: request.url(),
                method: request.method(),
                headers: request.headers(),
                postData: request.postData()
            });
            console.log(`📤 LOGIN REQUEST:`, {
                url: request.url(),
                method: request.method(),
                postData: request.postData()
            });
        }
    });
    
    page.on('response', response => {
        if (response.url().includes('/login')) {
            responses.push({
                url: response.url(),
                status: response.status(),
                statusText: response.statusText()
            });
            console.log(`📥 LOGIN RESPONSE:`, {
                url: response.url(),
                status: response.status(),
                statusText: response.statusText()
            });
        }
    });
    
    try {
        console.log('\n=== STEP 1: Navigate to app ===');
        await page.goto('http://localhost:4710');
        await page.waitForTimeout(2000);
        
        console.log('\n=== STEP 2: Fill form EXACTLY as user would ===');
        
        // Clear and type exactly like a user would
        const emailField = page.locator('input[type="email"]');
        const passwordField = page.locator('input[type="password"]');
        
        await emailField.click();
        await emailField.clear();
        await emailField.type('valid@test.com');
        
        await passwordField.click();
        await passwordField.clear(); 
        await passwordField.type('Test123!');
        
        console.log('✅ Filled form');
        
        // Check what values are actually in the fields
        const emailValue = await emailField.inputValue();
        const passwordValue = await passwordField.inputValue();
        
        console.log(`📧 Email field contains: "${emailValue}"`);
        console.log(`🔐 Password field contains: "${passwordValue}"`);
        
        await page.waitForTimeout(1000);
        
        console.log('\n=== STEP 3: Submit login ===');
        await page.click('button:has-text("SIGN IN")');
        
        // Wait for request/response
        await page.waitForTimeout(5000);
        
        console.log('\n=== NETWORK ANALYSIS ===');
        console.log(`Total login requests captured: ${requests.length}`);
        console.log(`Total login responses captured: ${responses.length}`);
        
        if (requests.length > 0) {
            const lastRequest = requests[requests.length - 1];
            console.log('\nLast Request Details:');
            console.log(`URL: ${lastRequest.url}`);
            console.log(`Method: ${lastRequest.method}`);
            console.log(`Post Data: ${lastRequest.postData}`);
            
            if (lastRequest.postData) {
                try {
                    const parsedData = JSON.parse(lastRequest.postData);
                    console.log('Parsed Request Data:');
                    console.log(`  Email: "${parsedData.email}"`);
                    console.log(`  Password: "${parsedData.password}"`);
                    console.log(`  Email Length: ${parsedData.email ? parsedData.email.length : 'N/A'}`);
                    console.log(`  Password Length: ${parsedData.password ? parsedData.password.length : 'N/A'}`);
                } catch (e) {
                    console.log('Could not parse post data as JSON');
                }
            }
        }
        
        if (responses.length > 0) {
            const lastResponse = responses[responses.length - 1];
            console.log('\nLast Response Details:');
            console.log(`Status: ${lastResponse.status}`);
            console.log(`Status Text: ${lastResponse.statusText}`);
        }
        
        // Check for error messages on page
        const errorMessages = await page.locator('.error, .alert-danger, [role="alert"]').allTextContents();
        if (errorMessages.length > 0) {
            console.log('\nError Messages on Page:');
            errorMessages.forEach((msg, i) => console.log(`  ${i + 1}: "${msg}"`));
        }
        
        console.log('\n🎭 Browser staying open for 15 seconds...');
        await page.waitForTimeout(15000);
        
    } catch (error) {
        console.error(`❌ Debug failed: ${error.message}`);
        await page.waitForTimeout(5000);
    } finally {
        await browser.close();
        console.log('🎬 Debug complete!');
    }
}

debugFrontendRequests().catch(console.error);