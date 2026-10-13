const { firefox } = require('playwright');

async function simpleFirefoxTest() {
    console.log('🔥 Simple Firefox Launch Test');
    
    try {
        console.log('Launching Firefox...');
        const browser = await firefox.launch({ 
            headless: false,
            slowMo: 2000
        });
        
        console.log('✅ Firefox launched successfully!');
        
        const page = await browser.newPage();
        console.log('✅ New page created');
        
        console.log('Navigating to VeoGen...');
        await page.goto('http://localhost:4710');
        
        console.log('✅ Navigation complete');
        
        const title = await page.title();
        console.log(`Page title: ${title}`);
        
        // Take screenshot
        await page.screenshot({ path: 'simple-firefox-test.png' });
        console.log('✅ Screenshot saved: simple-firefox-test.png');
        
        console.log('Keeping Firefox open for 10 seconds...');
        await page.waitForTimeout(10000);
        
        await browser.close();
        console.log('✅ Firefox closed');
        
    } catch (error) {
        console.error('❌ Firefox test failed:', error.message);
        console.error('Error details:', error);
    }
}

simpleFirefoxTest();