const { chromium, firefox, webkit } = require('playwright');

async function testBrowsers() {
    console.log('Testing available browsers...');
    
    try {
        console.log('Testing Chromium...');
        const browserChromium = await chromium.launch();
        console.log('✅ Chromium works!');
        await browserChromium.close();
    } catch (error) {
        console.log('❌ Chromium failed:', error.message);
    }
    
    try {
        console.log('Testing Firefox...');
        const browserFirefox = await firefox.launch();
        console.log('✅ Firefox works!');
        await browserFirefox.close();
    } catch (error) {
        console.log('❌ Firefox failed:', error.message);
    }
    
    try {
        console.log('Testing WebKit...');
        const browserWebKit = await webkit.launch();
        console.log('✅ WebKit works!');
        await browserWebKit.close();
    } catch (error) {
        console.log('❌ WebKit failed:', error.message);
    }
}

testBrowsers().catch(console.error);
