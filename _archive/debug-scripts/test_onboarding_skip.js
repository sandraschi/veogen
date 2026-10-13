const { chromium } = require('playwright');

/**
 * Test the specific onboarding completion flow
 */

async function testOnboardingCompletion() {
    console.log('🚀 Testing Onboarding Skip Flow...');
    
    const browser = await chromium.launch({ 
        headless: false, 
        slowMo: 2000 
    });
    const page = await browser.newPage();
    
    // Enable console logging
    page.on('console', msg => {
        console.log(`🌐 Browser: ${msg.type()}: ${msg.text()}`);
    });
    
    // Enable request/response logging
    page.on('request', request => {
        if (request.url().includes('localhost:4700')) {
            console.log(`📤 API: ${request.method()} ${request.url()}`);
        }
    });
    
    page.on('response', response => {
        if (response.url().includes('localhost:4700')) {
            console.log(`📥 API: ${response.status()} ${response.url()}`);
        }
    });
    
    try {
        // 1. Navigate to the app
        console.log('1. Loading VeoGen...');
        await page.goto('http://localhost:4710', { waitUntil: 'networkidle' });
        await page.screenshot({ path: 'test_1_loaded.png' });
        
        // 2. Login
        console.log('2. Logging in...');
        await page.fill('input[type="email"]', 'valid@test.com');
        await page.fill('input[type="password"]', 'Test123!');
        await page.screenshot({ path: 'test_2_filled_form.png' });
        
        await page.click('button:has-text("Login"), button:has-text("Sign In")');
        console.log('   Clicked login button');
        
        // Wait for response
        await page.waitForTimeout(3000);
        await page.screenshot({ path: 'test_3_after_login.png' });
        
        // 3. Look for onboarding screen
        console.log('3. Checking for onboarding screen...');
        const onboardingTitle = await page.locator('text=Welcome to VeoGen!').count();
        const skipButton = await page.locator('button:has-text("Skip for Now")').count();
        
        console.log(`   Onboarding title found: ${onboardingTitle > 0}`);
        console.log(`   Skip button found: ${skipButton > 0}`);
        
        if (skipButton > 0) {
            console.log('4. Clicking "Skip for Now" button...');
            await page.click('button:has-text("Skip for Now")');
            console.log('   Clicked skip button');
            
            // Wait for API call and response
            await page.waitForTimeout(5000);
            await page.screenshot({ path: 'test_4_after_skip.png' });
            
            // Check current URL
            const currentURL = page.url();
            console.log(`   Current URL after skip: ${currentURL}`);
            
            // Check page content
            const pageTitle = await page.title();
            console.log(`   Page title: ${pageTitle}`);
            
            // Look for dashboard/home content
            const homeContent = await page.locator('text=AI Video Generation, text=Generate stunning videos').count();
            console.log(`   Home content found: ${homeContent > 0}`);
            
            // Wait a bit more and check again
            console.log('5. Waiting 5 more seconds for any redirects...');
            await page.waitForTimeout(5000);
            
            const finalURL = page.url();
            console.log(`   Final URL: ${finalURL}`);
            await page.screenshot({ path: 'test_5_final_state.png' });
            
            // Try manually navigating to home
            console.log('6. Manually navigating to home...');
            await page.goto('http://localhost:4710/', { waitUntil: 'networkidle' });
            await page.waitForTimeout(3000);
            await page.screenshot({ path: 'test_6_manual_home.png' });
            
            const homePageContent = await page.locator('text=AI Video Generation').count();
            console.log(`   Home page content after manual nav: ${homePageContent > 0}`);
            
        } else {
            console.log('❌ No skip button found - onboarding screen issue');
        }
        
    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        await page.screenshot({ path: 'test_error.png' });
    } finally {
        await browser.close();
    }
    
    console.log('🎯 Test completed! Check screenshots for details.');
}

// Run the test
testOnboardingCompletion();
