const { chromium } = require('playwright');

async function debugOnboardingFlow() {
    console.log('🔍 Debug: Onboarding Flow Analysis...');
    
    const browser = await chromium.launch({ 
        headless: false, 
        slowMo: 1000 
    });
    const page = await browser.newPage();
    
    // Capture all console logs
    page.on('console', msg => {
        console.log(`[BROWSER ${msg.type().toUpperCase()}]: ${msg.text()}`);
    });
    
    // Capture navigation events
    page.on('framenavigated', frame => {
        console.log(`[NAVIGATION]: ${frame.url()}`);
    });
    
    try {
        // 1. Load app
        console.log('\n=== STEP 1: Loading App ===');
        await page.goto('http://localhost:4710', { waitUntil: 'networkidle' });
        console.log(`Initial URL: ${page.url()}`);
        
        // 2. Login
        console.log('\n=== STEP 2: Logging In ===');
        await page.fill('input[type="email"]', 'valid@test.com');
        await page.fill('input[type="password"]', 'Test123!');
        await page.click('button:has-text("Login"), button:has-text("Sign In")');
        
        await page.waitForTimeout(3000);
        console.log(`After login URL: ${page.url()}`);
        
        // 3. Check onboarding screen state
        console.log('\n=== STEP 3: Onboarding State ===');
        const skipButtonExists = await page.locator('button:has-text("Skip for Now")').count() > 0;
        console.log(`Skip button exists: ${skipButtonExists}`);
        
        if (skipButtonExists) {
            // 4. Click skip and monitor
            console.log('\n=== STEP 4: Clicking Skip Button ===');
            
            // Monitor URL changes
            const urlChanges = [];
            page.on('framenavigated', frame => {
                urlChanges.push(frame.url());
                console.log(`[URL CHANGE]: ${frame.url()}`);
            });
            
            await page.click('button:has-text("Skip for Now")');
            console.log('Skip button clicked');
            
            // Wait and check URL progression
            for (let i = 0; i < 10; i++) {
                await page.waitForTimeout(1000);
                const currentURL = page.url();
                console.log(`T+${i+1}s: ${currentURL}`);
                
                // Check if we can see dashboard content
                const hasHomeContent = await page.locator('text=AI Video Generation').count() > 0;
                console.log(`  - Has home content: ${hasHomeContent}`);
                
                // Check page content
                const pageText = await page.textContent('body').catch(() => '');
                if (pageText.includes('AI Video Generation')) {
                    console.log('  - ✅ Found expected home content!');
                    break;
                } else if (pageText.trim().length < 100) {
                    console.log('  - ⚠️ Page seems empty or minimal content');
                } else {
                    console.log('  - 📄 Page has content but not expected home content');
                }
            }
            
            console.log('\n=== URL CHANGE SUMMARY ===');
            urlChanges.forEach((url, i) => {
                console.log(`${i + 1}. ${url}`);
            });
        }
        
    } catch (error) {
        console.error(`❌ Debug failed: ${error.message}`);
    } finally {
        await browser.close();
    }
}

debugOnboardingFlow();