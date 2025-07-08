const { firefox } = require('playwright');

async function debugVeoGenFlow() {
    console.log('🔍 VeoGen Login Flow Debugging');
    console.log('==============================');
    
    const browser = await firefox.launch({ 
        headless: false,
        slowMo: 1000
    });
    
    const page = await browser.newPage();
    
    // Capture console messages
    page.on('console', msg => {
        console.log(`🖥️ Browser Console [${msg.type()}]: ${msg.text()}`);
    });
    
    // Capture errors
    page.on('pageerror', error => {
        console.log(`❌ Page Error: ${error.message}`);
    });
    
    try {
        console.log('\n📍 Step 1: Loading VeoGen...');
        await page.goto('http://localhost:4710');
        await page.waitForTimeout(5000);
        
        // Take initial screenshot
        await page.screenshot({ path: 'debug-01-initial.png' });
        console.log('📸 Screenshot saved: debug-01-initial.png');
        
        console.log('\n📍 Step 2: Checking current state...');
        const initialState = await page.evaluate(() => {
            return {
                url: window.location.href,
                title: document.title,
                bodyContent: document.body.textContent.substring(0, 300),
                hasLoginForm: !!document.querySelector('input[type="email"]'),
                hasLoadingSpinner: !!document.querySelector('[role="progressbar"]') || 
                                  document.body.textContent.includes('Loading'),
                localStorage: Object.keys(localStorage).reduce((acc, key) => {
                    acc[key] = localStorage.getItem(key);
                    return acc;
                }, {})
            };
        });
        
        console.log('Current State:', initialState);
        
        // If already on auth page, login
        if (initialState.hasLoginForm) {
            console.log('\n📍 Step 3: Logging in...');
            
            await page.fill('input[type="email"]', 'valid@test.com');
            await page.fill('input[type="password"]', 'Test123!');
            
            await page.screenshot({ path: 'debug-02-before-login.png' });
            console.log('📸 Screenshot saved: debug-02-before-login.png');
            
            await page.click('button[type="submit"]');
            console.log('✅ Login form submitted');
            
            // Wait for navigation/response
            await page.waitForTimeout(8000);
            
            await page.screenshot({ path: 'debug-03-after-login.png' });
            console.log('📸 Screenshot saved: debug-03-after-login.png');
        }
        
        console.log('\n📍 Step 4: Analyzing post-login state...');
        const postLoginState = await page.evaluate(() => {
            return {
                url: window.location.href,
                title: document.title,
                bodyContent: document.body.textContent.substring(0, 500),
                hasMainContent: document.body.textContent.length > 500,
                visibleElements: {
                    headers: Array.from(document.querySelectorAll('h1, h2, h3')).map(h => ({
                        tag: h.tagName,
                        text: h.textContent.trim(),
                        visible: window.getComputedStyle(h).display !== 'none'
                    })),
                    buttons: Array.from(document.querySelectorAll('button')).map(b => ({
                        text: b.textContent.trim(),
                        visible: window.getComputedStyle(b).display !== 'none'
                    })),
                    links: Array.from(document.querySelectorAll('a')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href,
                        visible: window.getComputedStyle(a).display !== 'none'
                    })).slice(0, 10) // First 10 links
                },
                backgroundColor: window.getComputedStyle(document.body).backgroundColor,
                hasMainLayout: !!document.querySelector('main') || !!document.querySelector('[role="main"]'),
                hasNavigation: !!document.querySelector('nav') || !!document.querySelector('[role="navigation"]'),
                hasErrorMessage: document.body.textContent.includes('error') || 
                                document.body.textContent.includes('Error'),
                localStorage: Object.keys(localStorage).reduce((acc, key) => {
                    acc[key] = localStorage.getItem(key);
                    return acc;
                }, {})
            };
        });
        
        console.log('\n📊 Post-Login Analysis:');
        console.log(`  URL: ${postLoginState.url}`);
        console.log(`  Title: ${postLoginState.title}`);
        console.log(`  Has Main Content: ${postLoginState.hasMainContent}`);
        console.log(`  Background Color: ${postLoginState.backgroundColor}`);
        console.log(`  Has Main Layout: ${postLoginState.hasMainLayout}`);
        console.log(`  Has Navigation: ${postLoginState.hasNavigation}`);
        console.log(`  Has Error Message: ${postLoginState.hasErrorMessage}`);
        console.log(`  LocalStorage keys: ${Object.keys(postLoginState.localStorage).join(', ')}`);
        
        if (postLoginState.visibleElements.headers.length > 0) {
            console.log('\n📄 Visible Headers:');
            postLoginState.visibleElements.headers.forEach((header, i) => {
                if (header.visible && header.text) {
                    console.log(`  ${i + 1}. ${header.tag}: ${header.text}`);
                }
            });
        }
        
        if (postLoginState.visibleElements.buttons.length > 0) {
            console.log('\n🔘 Visible Buttons:');
            postLoginState.visibleElements.buttons.slice(0, 5).forEach((button, i) => {
                if (button.visible && button.text) {
                    console.log(`  ${i + 1}. ${button.text}`);
                }
            });
        }
        
        console.log('\n📝 Page Content Preview:');
        console.log(postLoginState.bodyContent);
        
        // Check if we can navigate to generate page
        console.log('\n📍 Step 5: Testing navigation...');
        
        // Try to navigate to /generate
        await page.goto('http://localhost:4710/generate');
        await page.waitForTimeout(5000);
        
        await page.screenshot({ path: 'debug-04-generate-page.png' });
        console.log('📸 Screenshot saved: debug-04-generate-page.png');
        
        const generatePageState = await page.evaluate(() => {
            return {
                url: window.location.href,
                title: document.title,
                bodyContent: document.body.textContent.substring(0, 300),
                hasContent: document.body.textContent.length > 100
            };
        });
        
        console.log('\n📊 Generate Page State:');
        console.log(`  URL: ${generatePageState.url}`);
        console.log(`  Has Content: ${generatePageState.hasContent}`);
        console.log(`  Content Preview: ${generatePageState.bodyContent}`);
        
        // Keep browser open for manual inspection
        console.log('\n🔍 Keeping browser open for 30 seconds for manual inspection...');
        await page.waitForTimeout(30000);
        
    } catch (error) {
        console.error('❌ Debug failed:', error.message);
        await page.screenshot({ path: 'debug-error.png' });
    }
    
    await browser.close();
    console.log('\n🎭 Debug session complete!');
}

debugVeoGenFlow().catch(console.error);