const { chromium } = require('playwright');

/**
 * Complete VeoGen Login + Onboarding Flow (Visible)
 * This shows the FULL user journey from login to main app
 */

async function testCompleteFlow() {
    console.log('🎬 Testing COMPLETE login + onboarding flow...');
    console.log('This will show you the full user journey!');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 2000,
        devtools: false
    });
    
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1280, height: 720 });
    
    try {
        console.log('\n=== STEP 1: Navigate to VeoGen ===');
        await page.goto('http://localhost:4710');
        await page.waitForTimeout(2000);
        
        console.log('\n=== STEP 2: Login ===');
        await page.fill('input[type="email"]', 'valid@test.com');
        await page.fill('input[type="password"]', 'Test123!');
        console.log('✅ Filled login form');
        
        await page.waitForTimeout(1000);
        await page.click('button:has-text("Login"), button:has-text("Sign In"), button:has-text("SIGN IN")');
        console.log('🖱️ Clicked login button');
        
        await page.waitForTimeout(3000);
        
        console.log('\n=== STEP 3: Check Login Result ===');
        const currentURL = page.url();
        console.log(`Current URL: ${currentURL}`);
        
        const token = await page.evaluate(() => localStorage.getItem('token'));
        console.log(`Token: ${token ? 'FOUND (' + token.length + ' chars)' : 'NOT FOUND'}`);
        
        // Look for onboarding
        const onboardingTitle = await page.locator('text=Welcome to VeoGen!').count();
        console.log(`Onboarding screen: ${onboardingTitle > 0 ? 'FOUND' : 'NOT FOUND'}`);
        
        if (onboardingTitle > 0) {
            console.log('\n=== STEP 4: Complete Onboarding ===');
            
            // Look for skip button
            const skipButton = await page.locator('button:has-text("Skip for Now")');
            const skipExists = await skipButton.count() > 0;
            console.log(`Skip button found: ${skipExists}`);
            
            if (skipExists) {
                console.log('🖱️ Clicking "Skip for Now"...');
                await skipButton.click();
                
                console.log('⏳ Waiting for onboarding completion...');
                await page.waitForTimeout(5000);
                
                const finalURL = page.url();
                console.log(`Final URL: ${finalURL}`);
                
                // Check if we reached the main app
                const homeContent = await page.locator('text=AI Video Generation').count();
                console.log(`Main app content: ${homeContent > 0 ? 'FOUND' : 'NOT FOUND'}`);
                
                if (homeContent === 0) {
                    console.log('🔄 Trying manual navigation to home...');
                    await page.goto('http://localhost:4710/');
                    await page.waitForTimeout(3000);
                    
                    const homeContent2 = await page.locator('text=AI Video Generation').count();
                    console.log(`Home content after manual nav: ${homeContent2 > 0 ? 'FOUND' : 'NOT FOUND'}`);
                }
                
            } else {
                console.log('❌ Skip button not found');
            }
        } else {
            console.log('❌ No onboarding screen - something unexpected happened');
        }
        
        console.log('\n=== FINAL STATUS ===');
        const finalToken = await page.evaluate(() => localStorage.getItem('token'));
        const finalURL = page.url();
        const hasAppContent = await page.locator('text=AI Video Generation').count() > 0;
        
        console.log(`✅ Authentication: ${finalToken ? 'SUCCESS' : 'FAILED'}`);
        console.log(`📍 Final URL: ${finalURL}`);
        console.log(`🎯 Main App Access: ${hasAppContent ? 'SUCCESS' : 'FAILED'}`);
        
        if (finalToken && hasAppContent) {
            console.log('🎉 COMPLETE SUCCESS! Login and onboarding working perfectly!');
        } else if (finalToken && !hasAppContent) {
            console.log('⚠️ Login works but main app access issue');
        } else {
            console.log('❌ Login failed');
        }
        
        console.log('\n🎭 Browser will stay open for 20 seconds for you to explore...');
        await page.waitForTimeout(20000);
        
    } catch (error) {
        console.error(`❌ Test failed: ${error.message}`);
        await page.waitForTimeout(10000);
    } finally {
        await browser.close();
        console.log('🎬 Test complete!');
    }
}

console.log('🚀 VeoGen Complete Flow Test');
console.log('Watch as the browser goes through: Login → Onboarding → Main App');
console.log('');

testCompleteFlow().catch(console.error);