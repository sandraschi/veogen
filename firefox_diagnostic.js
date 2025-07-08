const { firefox } = require('playwright');

async function firefoxDiagnostic() {
    console.log('🔥 Firefox-Specific VeoGen Login Diagnostic');
    console.log('==========================================');
    
    const browser = await firefox.launch({ 
        headless: false,
        slowMo: 1000,
        args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Enable console logging
    page.on('console', msg => {
        console.log(`🖥️ Firefox Console [${msg.type()}]:`, msg.text());
    });
    
    // Enable error logging
    page.on('pageerror', error => {
        console.log(`❌ Firefox Page Error:`, error.message);
    });
    
    // Enable request/response logging
    page.on('request', request => {
        if (request.url().includes('4700') || request.url().includes('auth')) {
            console.log(`📤 Firefox Request: ${request.method()} ${request.url()}`);
        }
    });
    
    page.on('response', response => {
        if (response.url().includes('4700') || response.url().includes('auth')) {
            console.log(`📥 Firefox Response: ${response.status()} ${response.url()}`);
        }
    });
    
    try {
        console.log('\n📍 Step 1: Loading VeoGen in Firefox...');
        await page.goto('http://localhost:4710', { waitUntil: 'networkidle' });
        await page.waitForTimeout(5000);
        
        console.log('📍 Step 2: Taking initial screenshot...');
        await page.screenshot({ path: 'firefox-diagnostic-initial.png' });
        
        const title = await page.title();
        const url = page.url();
        console.log(`Page title: ${title}`);
        console.log(`Current URL: ${url}`);
        
        console.log('\n📍 Step 3: Checking browser environment...');
        const browserInfo = await page.evaluate(() => {
            return {
                userAgent: navigator.userAgent,
                localStorage: typeof Storage !== 'undefined' && typeof localStorage !== 'undefined',
                sessionStorage: typeof Storage !== 'undefined' && typeof sessionStorage !== 'undefined',
                fetch: typeof fetch !== 'undefined',
                cookies: document.cookie,
                location: window.location.href,
                reactDetected: !!window.React || !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                localStorageKeys: Object.keys(localStorage || {}),
                sessionStorageKeys: Object.keys(sessionStorage || {})
            };
        });
        
        console.log('🔍 Firefox Browser Environment:');
        console.log(`  User Agent: ${browserInfo.userAgent}`);
        console.log(`  LocalStorage available: ${browserInfo.localStorage}`);
        console.log(`  SessionStorage available: ${browserInfo.sessionStorage}`);
        console.log(`  Fetch API available: ${browserInfo.fetch}`);
        console.log(`  React detected: ${browserInfo.reactDetected}`);
        console.log(`  Existing localStorage keys: ${browserInfo.localStorageKeys.join(', ')}`);
        console.log(`  Existing sessionStorage keys: ${browserInfo.sessionStorageKeys.join(', ')}`);
        console.log(`  Cookies: ${browserInfo.cookies || 'None'}`);
        
        console.log('\n📍 Step 4: Looking for React app loading...');
        await page.waitForTimeout(3000);
        
        // Check if we're on auth page or need to navigate
        if (!url.includes('/auth')) {
            console.log('Navigating to auth page...');
            await page.goto('http://localhost:4710/auth');
            await page.waitForTimeout(3000);
        }
        
        console.log('\n📍 Step 5: Analyzing login form...');
        const formAnalysis = await page.evaluate(() => {
            const forms = Array.from(document.querySelectorAll('form'));
            const inputs = Array.from(document.querySelectorAll('input'));
            const buttons = Array.from(document.querySelectorAll('button'));
            
            return {
                forms: forms.length,
                inputs: inputs.map(input => ({
                    type: input.type,
                    name: input.name,
                    placeholder: input.placeholder,
                    id: input.id,
                    className: input.className
                })),
                buttons: buttons.map(button => ({
                    type: button.type,
                    textContent: button.textContent.trim(),
                    className: button.className
                })),
                bodyText: document.body.textContent.substring(0, 500)
            };
        });
        
        console.log(`Found ${formAnalysis.forms} form(s)`);
        console.log(`Found ${formAnalysis.inputs.length} input(s):`);
        formAnalysis.inputs.forEach((input, i) => {
            console.log(`  Input ${i}: type="${input.type}", name="${input.name}", placeholder="${input.placeholder}"`);
        });
        console.log(`Found ${formAnalysis.buttons.length} button(s):`);
        formAnalysis.buttons.forEach((button, i) => {
            console.log(`  Button ${i}: type="${button.type}", text="${button.textContent}"`);
        });
        
        console.log('\nPage content preview:');
        console.log(formAnalysis.bodyText);
        
        console.log('\n📍 Step 6: Attempting login...');
        
        const emailInput = await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 10000 });
        const passwordInput = await page.waitForSelector('input[type="password"]', { timeout: 5000 });
        
        if (emailInput && passwordInput) {
            console.log('✅ Login form found, filling credentials...');
            
            await emailInput.fill('valid@test.com');
            await passwordInput.fill('Test123!');
            
            await page.screenshot({ path: 'firefox-diagnostic-before-login.png' });
            
            const submitButton = await page.waitForSelector('button[type="submit"]');
            
            console.log('🔄 Submitting login form...');
            await submitButton.click();
            
            // Wait for potential redirect/response
            await page.waitForTimeout(8000);
            
            await page.screenshot({ path: 'firefox-diagnostic-after-login.png' });
            
            const postLoginUrl = page.url();
            console.log(`URL after login: ${postLoginUrl}`);
            
            // Check what happened
            const postLoginAnalysis = await page.evaluate(() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    bodyText: document.body.textContent.substring(0, 500),
                    localStorageKeys: Object.keys(localStorage || {}),
                    sessionStorageKeys: Object.keys(sessionStorage || {}),
                    hasErrorMessage: document.querySelector('[role="alert"], .error, .alert-error') !== null,
                    hasWelcomeMessage: document.body.textContent.includes('Welcome'),
                    hasOnboardingContent: document.body.textContent.includes('onboarding') || document.body.textContent.includes('API'),
                    isDashboard: window.location.pathname.includes('dashboard'),
                    isAuth: window.location.pathname.includes('auth')
                };
            });
            
            console.log('\n📊 Post-Login Analysis:');
            console.log(`  URL: ${postLoginAnalysis.url}`);
            console.log(`  Title: ${postLoginAnalysis.title}`);
            console.log(`  Is on auth page: ${postLoginAnalysis.isAuth}`);
            console.log(`  Is on dashboard: ${postLoginAnalysis.isDashboard}`);
            console.log(`  Has error message: ${postLoginAnalysis.hasErrorMessage}`);
            console.log(`  Has welcome message: ${postLoginAnalysis.hasWelcomeMessage}`);
            console.log(`  Has onboarding content: ${postLoginAnalysis.hasOnboardingContent}`);
            console.log(`  LocalStorage keys: ${postLoginAnalysis.localStorageKeys.join(', ')}`);
            console.log(`  SessionStorage keys: ${postLoginAnalysis.sessionStorageKeys.join(', ')}`);
            
            console.log('\nPage content after login:');
            console.log(postLoginAnalysis.bodyText);
            
            // Try direct dashboard access
            console.log('\n📍 Step 7: Testing direct dashboard access...');
            await page.goto('http://localhost:4710/dashboard');
            await page.waitForTimeout(5000);
            
            await page.screenshot({ path: 'firefox-diagnostic-dashboard.png' });
            
            const dashboardAnalysis = await page.evaluate(() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    bodyText: document.body.textContent.substring(0, 300),
                    hasContent: document.body.textContent.length > 100,
                    backgroundColor: window.getComputedStyle(document.body).backgroundColor
                };
            });
            
            console.log('\n📊 Dashboard Analysis:');
            console.log(`  URL: ${dashboardAnalysis.url}`);
            console.log(`  Title: ${dashboardAnalysis.title}`);
            console.log(`  Has meaningful content: ${dashboardAnalysis.hasContent}`);
            console.log(`  Background color: ${dashboardAnalysis.backgroundColor}`);
            console.log(`  Content preview: ${dashboardAnalysis.bodyText}`);
            
        } else {
            console.log('❌ Login form not found in Firefox');
        }
        
    } catch (error) {
        console.error('❌ Firefox diagnostic error:', error.message);
        await page.screenshot({ path: 'firefox-diagnostic-error.png' });
    }
    
    console.log('\n📸 Firefox diagnostic screenshots saved:');
    console.log('- firefox-diagnostic-initial.png');
    console.log('- firefox-diagnostic-before-login.png'); 
    console.log('- firefox-diagnostic-after-login.png');
    console.log('- firefox-diagnostic-dashboard.png');
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser will stay open for 30 seconds for manual inspection...');
    await page.waitForTimeout(30000);
    
    await browser.close();
    console.log('\n🎭 Firefox diagnostic complete!');
}

// Run the diagnostic
firefoxDiagnostic().catch(console.error);