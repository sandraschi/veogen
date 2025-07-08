const { firefox, chromium } = require('playwright');

async function testBrowserComparison() {
    console.log('🔥 Starting Firefox vs Chromium Authentication Comparison...');
    
    const browsers = [
        { name: 'Firefox', engine: firefox },
        { name: 'Chromium', engine: chromium }
    ];
    
    const results = {};
    
    for (const browserConfig of browsers) {
        console.log(`\n🎯 Testing with ${browserConfig.name}...`);
        results[browserConfig.name] = {};
        
        const browser = await browserConfig.engine.launch({ 
            headless: false,
            slowMo: 1000
        });
        
        const context = await browser.newContext();
        const page = await context.newPage();
        
        try {
            // Step 1: Navigate to VeoGen
            console.log(`📍 ${browserConfig.name}: Loading VeoGen...`);
            await page.goto('http://localhost:4710');
            await page.waitForTimeout(5000); // Wait for React to load
            
            const title = await page.title();
            console.log(`${browserConfig.name} page title: ${title}`);
            results[browserConfig.name].pageTitle = title;
            
            // Take initial screenshot
            await page.screenshot({ path: `veogen-${browserConfig.name.toLowerCase()}-initial.png` });
            
            // Step 2: Check if already on auth page or need to navigate
            const currentUrl = page.url();
            console.log(`${browserConfig.name} current URL: ${currentUrl}`);
            results[browserConfig.name].initialUrl = currentUrl;
            
            // If not on auth page, try to navigate there
            if (!currentUrl.includes('/auth')) {
                console.log(`${browserConfig.name}: Navigating to auth page...`);
                await page.goto('http://localhost:4710/auth');
                await page.waitForTimeout(3000);
            }
            
            // Step 3: Find and fill login form
            console.log(`📍 ${browserConfig.name}: Looking for login form...`);
            
            // Wait for React to render
            await page.waitForTimeout(3000);
            
            // Check for email input
            const emailInput = await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 10000 });
            const passwordInput = await page.waitForSelector('input[type="password"], input[name="password"]', { timeout: 5000 });
            
            if (emailInput && passwordInput) {
                console.log(`✅ ${browserConfig.name}: Login form found`);
                results[browserConfig.name].loginFormFound = true;
                
                // Clear and fill email
                await emailInput.click();
                await emailInput.fill('');
                await emailInput.type('valid@test.com', { delay: 100 });
                console.log(`${browserConfig.name}: Email entered`);
                
                // Clear and fill password  
                await passwordInput.click();
                await passwordInput.fill('');
                await passwordInput.type('Test123!', { delay: 100 });
                console.log(`${browserConfig.name}: Password entered`);
                
                // Take screenshot before login
                await page.screenshot({ path: `veogen-${browserConfig.name.toLowerCase()}-before-login.png` });
                
                // Find submit button
                const submitButton = await page.waitForSelector('button[type="submit"]', { timeout: 5000 });
                
                if (submitButton) {
                    console.log(`${browserConfig.name}: Clicking login button...`);
                    
                    // Listen for network requests
                    const loginRequests = [];
                    page.on('response', response => {
                        if (response.url().includes('/auth/') || response.url().includes('/login')) {
                            loginRequests.push({
                                url: response.url(),
                                status: response.status(),
                                statusText: response.statusText()
                            });
                        }
                    });
                    
                    await submitButton.click();
                    
                    // Wait for login response
                    await page.waitForTimeout(8000);
                    
                    // Take screenshot after login
                    await page.screenshot({ path: `veogen-${browserConfig.name.toLowerCase()}-after-login.png` });
                    
                    const postLoginUrl = page.url();
                    console.log(`${browserConfig.name} URL after login: ${postLoginUrl}`);
                    results[browserConfig.name].postLoginUrl = postLoginUrl;
                    results[browserConfig.name].loginRequests = loginRequests;
                    
                    // Check for success indicators
                    const hasUserMenu = await page.$('[data-testid="user-menu"]') !== null;
                    const hasWelcome = await page.$('text=Welcome') !== null;
                    const hasOnboarding = await page.$('text=onboarding') !== null || await page.$('text=API') !== null;
                    const hasDashboard = await page.$('text=Dashboard') !== null;
                    const isStillOnAuth = postLoginUrl.includes('/auth');
                    
                    results[browserConfig.name].indicators = {
                        hasUserMenu,
                        hasWelcome,
                        hasOnboarding,
                        hasDashboard,
                        isStillOnAuth
                    };
                    
                    console.log(`${browserConfig.name} login indicators:`, results[browserConfig.name].indicators);
                    
                    // Check localStorage for tokens
                    const localStorage = await page.evaluate(() => {
                        return {
                            token: window.localStorage.getItem('token') || window.localStorage.getItem('authToken'),
                            user: window.localStorage.getItem('user'),
                            keys: Object.keys(window.localStorage)
                        };
                    });
                    
                    results[browserConfig.name].localStorage = localStorage;
                    console.log(`${browserConfig.name} localStorage:`, localStorage.keys);
                    
                    // Check sessionStorage too
                    const sessionStorage = await page.evaluate(() => {
                        return {
                            keys: Object.keys(window.sessionStorage),
                            values: Object.keys(window.sessionStorage).reduce((acc, key) => {
                                acc[key] = window.sessionStorage.getItem(key);
                                return acc;
                            }, {})
                        };
                    });
                    
                    results[browserConfig.name].sessionStorage = sessionStorage;
                    
                    // Try to access dashboard directly
                    console.log(`${browserConfig.name}: Trying direct dashboard access...`);
                    await page.goto('http://localhost:4710/dashboard');
                    await page.waitForTimeout(5000);
                    
                    await page.screenshot({ path: `veogen-${browserConfig.name.toLowerCase()}-dashboard.png` });
                    
                    const dashboardUrl = page.url();
                    const dashboardTitle = await page.title();
                    const dashboardContent = await page.textContent('body');
                    
                    results[browserConfig.name].dashboard = {
                        url: dashboardUrl,
                        title: dashboardTitle,
                        hasContent: dashboardContent.length > 100,
                        contentPreview: dashboardContent.substring(0, 200)
                    };
                    
                    console.log(`${browserConfig.name} dashboard access:`, results[browserConfig.name].dashboard);
                    
                } else {
                    console.log(`❌ ${browserConfig.name}: Submit button not found`);
                    results[browserConfig.name].loginFormFound = false;
                }
                
            } else {
                console.log(`❌ ${browserConfig.name}: Login form not found`);
                results[browserConfig.name].loginFormFound = false;
            }
            
        } catch (error) {
            console.error(`❌ ${browserConfig.name} error:`, error.message);
            results[browserConfig.name].error = error.message;
            
            // Take error screenshot
            await page.screenshot({ path: `veogen-${browserConfig.name.toLowerCase()}-error.png` });
        }
        
        await browser.close();
    }
    
    // Compare results
    console.log('\n📊 BROWSER COMPARISON RESULTS');
    console.log('===============================');
    
    for (const browserName of Object.keys(results)) {
        console.log(`\n🔸 ${browserName.toUpperCase()}:`);
        const result = results[browserName];
        
        console.log(`  Page Title: ${result.pageTitle || 'N/A'}`);
        console.log(`  Initial URL: ${result.initialUrl || 'N/A'}`);
        console.log(`  Login Form Found: ${result.loginFormFound ? '✅ YES' : '❌ NO'}`);
        console.log(`  Post-Login URL: ${result.postLoginUrl || 'N/A'}`);
        
        if (result.indicators) {
            console.log(`  Success Indicators:`);
            console.log(`    - Still on Auth: ${result.indicators.isStillOnAuth ? '❌ YES' : '✅ NO'}`);
            console.log(`    - Has Welcome: ${result.indicators.hasWelcome ? '✅ YES' : '❌ NO'}`);
            console.log(`    - Has User Menu: ${result.indicators.hasUserMenu ? '✅ YES' : '❌ NO'}`);
            console.log(`    - Has Onboarding: ${result.indicators.hasOnboarding ? '⚠️ YES' : '✅ NO'}`);
        }
        
        if (result.localStorage) {
            console.log(`  LocalStorage Keys: ${result.localStorage.keys.join(', ')}`);
            console.log(`  Has Token: ${result.localStorage.token ? '✅ YES' : '❌ NO'}`);
        }
        
        if (result.dashboard) {
            console.log(`  Dashboard Access:`);
            console.log(`    - URL: ${result.dashboard.url}`);
            console.log(`    - Has Content: ${result.dashboard.hasContent ? '✅ YES' : '❌ NO'}`);
            console.log(`    - Content Preview: ${result.dashboard.contentPreview.substring(0, 100)}...`);
        }
        
        if (result.error) {
            console.log(`  ❌ ERROR: ${result.error}`);
        }
    }
    
    // Find differences
    console.log('\n🔍 KEY DIFFERENCES:');
    console.log('====================');
    
    if (results.Firefox && results.Chromium) {
        const firefox = results.Firefox;
        const chromium = results.Chromium;
        
        if (firefox.postLoginUrl !== chromium.postLoginUrl) {
            console.log(`🔸 Post-Login URL Difference:`);
            console.log(`  Firefox: ${firefox.postLoginUrl}`);
            console.log(`  Chromium: ${chromium.postLoginUrl}`);
        }
        
        if (firefox.localStorage?.keys?.length !== chromium.localStorage?.keys?.length) {
            console.log(`🔸 LocalStorage Difference:`);
            console.log(`  Firefox: ${firefox.localStorage?.keys || []}`);
            console.log(`  Chromium: ${chromium.localStorage?.keys || []}`);
        }
        
        if (firefox.dashboard?.hasContent !== chromium.dashboard?.hasContent) {
            console.log(`🔸 Dashboard Content Difference:`);
            console.log(`  Firefox has content: ${firefox.dashboard?.hasContent}`);
            console.log(`  Chromium has content: ${chromium.dashboard?.hasContent}`);
        }
    }
    
    console.log('\n📸 Screenshots saved:');
    console.log('- veogen-firefox-initial.png');
    console.log('- veogen-firefox-before-login.png');
    console.log('- veogen-firefox-after-login.png');
    console.log('- veogen-firefox-dashboard.png');
    console.log('- veogen-chromium-initial.png');
    console.log('- veogen-chromium-before-login.png');
    console.log('- veogen-chromium-after-login.png');
    console.log('- veogen-chromium-dashboard.png');
    
    return results;
}

// Run the comparison test
if (require.main === module) {
    testBrowserComparison()
        .then(results => {
            console.log('\n🎭 Firefox vs Chromium Test Complete!');
            process.exit(0);
        })
        .catch(error => {
            console.error('💥 Browser comparison failed:', error);
            process.exit(1);
        });
}

module.exports = { testBrowserComparison };