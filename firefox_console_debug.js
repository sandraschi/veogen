const { firefox } = require('playwright');

async function firefoxConsoleDebug() {
    console.log('🔥 Firefox Console Error Debug');
    console.log('============================');
    
    const browser = await firefox.launch({ 
        headless: false,
        slowMo: 1000
    });
    
    const page = await browser.newPage();
    
    // Capture all console messages
    const consoleMessages = [];
    page.on('console', msg => {
        const message = `[${msg.type()}] ${msg.text()}`;
        console.log(`🖥️ Console: ${message}`);
        consoleMessages.push(message);
    });
    
    // Capture page errors
    const pageErrors = [];
    page.on('pageerror', error => {
        const errorMsg = `Page Error: ${error.message}`;
        console.log(`❌ ${errorMsg}`);
        pageErrors.push(errorMsg);
    });
    
    // Capture failed requests
    const failedRequests = [];
    page.on('response', response => {
        if (!response.ok()) {
            const failedReq = `Failed Request: ${response.status()} ${response.url()}`;
            console.log(`📥 ${failedReq}`);
            failedRequests.push(failedReq);
        }
    });
    
    try {
        console.log('\n📍 Loading VeoGen in Firefox...');
        await page.goto('http://localhost:4710', { 
            waitUntil: 'networkidle',
            timeout: 30000 
        });
        
        console.log('\n📍 Waiting for React to mount...');
        await page.waitForTimeout(10000);
        
        // Check if React actually mounted
        const reactStatus = await page.evaluate(() => {
            return {
                rootElement: document.getElementById('root'),
                rootInnerHTML: document.getElementById('root')?.innerHTML || '',
                hasReactRoot: !!document.getElementById('root')?._reactInternalInstance,
                hasReactDevTools: !!window.__REACT_DEVTOOLS_GLOBAL_HOOK__,
                windowReact: !!window.React,
                documentReadyState: document.readyState,
                bodyClasses: document.body.className,
                scriptTags: Array.from(document.querySelectorAll('script')).map(s => ({
                    src: s.src,
                    type: s.type,
                    hasContent: s.innerHTML.length > 0
                }))
            };
        });
        
        console.log('\n🔍 React Mount Status:');
        console.log(`  Root element exists: ${!!reactStatus.rootElement}`);
        console.log(`  Root has content: ${reactStatus.rootInnerHTML.length > 0}`);
        console.log(`  Root content preview: ${reactStatus.rootInnerHTML.substring(0, 200)}`);
        console.log(`  Has React dev tools: ${reactStatus.hasReactDevTools}`);
        console.log(`  Window.React exists: ${reactStatus.windowReact}`);
        console.log(`  Document ready state: ${reactStatus.documentReadyState}`);
        console.log(`  Body classes: ${reactStatus.bodyClasses}`);
        console.log(`  Script tags: ${reactStatus.scriptTags.length}`);
        
        reactStatus.scriptTags.forEach((script, i) => {
            if (script.src) {
                console.log(`    Script ${i}: ${script.src}`);
            }
        });
        
        // Try to manually check for JavaScript errors
        const jsErrors = await page.evaluate(() => {
            const errors = [];
            
            // Check if there's an error loading the main React bundle
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            for (const script of scripts) {
                if (script.src.includes('static/js/')) {
                    errors.push(`React bundle: ${script.src}`);
                }
            }
            
            return errors;
        });
        
        console.log('\n📦 JavaScript Bundles:');
        jsErrors.forEach(bundle => {
            console.log(`  ${bundle}`);
        });
        
        // Take a screenshot
        await page.screenshot({ path: 'firefox-console-debug.png' });
        
        console.log('\n📊 Summary:');
        console.log(`  Console messages: ${consoleMessages.length}`);
        console.log(`  Page errors: ${pageErrors.length}`);
        console.log(`  Failed requests: ${failedRequests.length}`);
        
        if (consoleMessages.length > 0) {
            console.log('\n💬 All Console Messages:');
            consoleMessages.forEach((msg, i) => {
                console.log(`  ${i + 1}. ${msg}`);
            });
        }
        
        if (pageErrors.length > 0) {
            console.log('\n❌ All Page Errors:');
            pageErrors.forEach((error, i) => {
                console.log(`  ${i + 1}. ${error}`);
            });
        }
        
        if (failedRequests.length > 0) {
            console.log('\n📥 Failed Requests:');
            failedRequests.forEach((req, i) => {
                console.log(`  ${i + 1}. ${req}`);
            });
        }
        
        // Keep browser open for manual inspection
        console.log('\n🔍 Keeping Firefox open for 20 seconds for inspection...');
        await page.waitForTimeout(20000);
        
    } catch (error) {
        console.error('❌ Debug failed:', error.message);
        await page.screenshot({ path: 'firefox-console-debug-error.png' });
    }
    
    await browser.close();
    console.log('\n🎭 Firefox console debug complete!');
}

firefoxConsoleDebug().catch(console.error);