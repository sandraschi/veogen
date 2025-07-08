const { chromium } = require('playwright');

/**
 * VeoGen Visible Browser Test
 * This will open a visible browser and show you exactly what's happening
 */

async function testLoginVisually() {
    console.log('🎬 Starting VISIBLE browser test...');
    console.log('You will see the browser window open and watch the automation!');
    
    const browser = await chromium.launch({ 
        headless: false,     // Make browser VISIBLE
        slowMo: 2000,       // Slow down actions so you can see them
        devtools: false     // Set to true if you want dev tools open
    });
    
    const page = await browser.newPage();
    
    // Make the browser window larger so it's easy to see
    await page.setViewportSize({ width: 1280, height: 720 });
    
    try {
        console.log('\n=== STEP 1: Going to VeoGen ===');
        await page.goto('http://localhost:4710', { waitUntil: 'networkidle' });
        
        console.log('Current URL:', page.url());
        
        // Take a moment to see the page
        await page.waitForTimeout(3000);
        
        console.log('\n=== STEP 2: Looking for login form ===');
        
        // Check if we can see the login elements
        const emailInput = page.locator('input[type="email"]');
        const passwordInput = page.locator('input[type="password"]');
        const loginButton = page.locator('button:has-text("Login"), button:has-text("Sign In"), button:has-text("SIGN IN")');
        
        const emailExists = await emailInput.count() > 0;
        const passwordExists = await passwordInput.count() > 0;
        const loginExists = await loginButton.count() > 0;
        
        console.log(`Email field found: ${emailExists}`);
        console.log(`Password field found: ${passwordExists}`);
        console.log(`Login button found: ${loginExists}`);
        
        if (!emailExists || !passwordExists || !loginExists) {
            console.log('❌ Login form not found! Let me check what\'s on the page...');
            const pageText = await page.textContent('body');
            console.log('Page contains:', pageText.substring(0, 200) + '...');
            
            // Wait longer to see what's happening
            console.log('Waiting 10 seconds for you to see the page...');
            await page.waitForTimeout(10000);
            return;
        }
        
        console.log('\n=== STEP 3: Testing with valid@test.com ===');
        
        // Clear any existing text and type slowly
        await emailInput.clear();
        await emailInput.type('valid@test.com', { delay: 100 });
        console.log('✅ Typed email');
        
        await passwordInput.clear(); 
        await passwordInput.type('Test123!', { delay: 100 });
        console.log('✅ Typed password');
        
        // Wait so you can see the filled form
        await page.waitForTimeout(2000);
        
        console.log('🖱️ Clicking login button...');
        await loginButton.click();
        
        // Wait to see what happens
        console.log('⏳ Waiting for response...');
        await page.waitForTimeout(5000);
        
        const newURL = page.url();
        console.log(`After login URL: ${newURL}`);
        
        // Check for any error messages
        const errorElements = await page.locator('.error, .alert-danger, [role="alert"]').count();
        if (errorElements > 0) {
            const errorText = await page.locator('.error, .alert-danger, [role="alert"]').allTextContents();
            console.log('❌ Error messages found:', errorText);
        }
        
        // Check for success
        const successElements = await page.locator('.success, .alert-success').count();
        if (successElements > 0) {
            const successText = await page.locator('.success, .alert-success').allTextContents();
            console.log('✅ Success messages:', successText);
        }
        
        // Check if we have a token
        const token = await page.evaluate(() => {
            return localStorage.getItem('token') || sessionStorage.getItem('token');
        });
        
        console.log(`Token in storage: ${token ? 'YES (length: ' + token.length + ')' : 'NO'}`);
        
        // Look for onboarding screen
        const onboardingText = await page.locator('text=Welcome to VeoGen!').count();
        console.log(`Onboarding screen: ${onboardingText > 0 ? 'FOUND' : 'NOT FOUND'}`);
        
        console.log('\n🎭 Test complete! Browser will stay open for 30 seconds so you can explore...');
        await page.waitForTimeout(30000);
        
    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        console.log('Browser will stay open for 30 seconds so you can see the error...');
        await page.waitForTimeout(30000);
    } finally {
        await browser.close();
        console.log('🎬 Browser closed. Test complete!');
    }
}

console.log('🚀 VeoGen Visible Login Test');
console.log('This will open a browser window and show you the automation process!');
console.log('Watch the browser as it navigates and tries to log in...');
console.log('');

testLoginVisually().catch(console.error);