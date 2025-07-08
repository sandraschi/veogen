const { chromium } = require('playwright');

/**
 * VeoGen Authentication & Onboarding Test Suite
 * Tests the complete user flow from login to onboarding completion
 */

class VeoGenAuthTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.baseURL = 'http://localhost:4710';
        this.testCredentials = {
            working: { email: 'valid@test.com', password: 'Test123!' },
            sandra: { email: 'sandraschipal@hotmail.com', password: 'S3c1000vg#' },
            alt: { email: 'test@test.com', password: 'test123' }
        };
    }

    async init() {
        console.log('🚀 Initializing VeoGen Auth Tester...');
        this.browser = await chromium.launch({ 
            headless: false, // Show browser for debugging
            slowMo: 1000     // Slow down actions for visibility
        });
        this.page = await this.browser.newPage();
        
        // Enable console logging from the page
        this.page.on('console', msg => {
            console.log(`🌐 Browser: ${msg.type()}: ${msg.text()}`);
        });
        
        // Enable request/response logging
        this.page.on('request', request => {
            if (request.url().includes('localhost:4700')) {
                console.log(`📤 API Request: ${request.method()} ${request.url()}`);
            }
        });
        
        this.page.on('response', response => {
            if (response.url().includes('localhost:4700')) {
                console.log(`📥 API Response: ${response.status()} ${response.url()}`);
            }
        });
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async takeScreenshot(name) {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `screenshot_${name}_${timestamp}.png`;
        await this.page.screenshot({ 
            path: filename, 
            fullPage: true 
        });
        console.log(`📸 Screenshot saved: ${filename}`);
        return filename;
    }

    async testPageLoad() {
        console.log('\n=== Testing Page Load ===');
        
        try {
            console.log(`🔗 Navigating to ${this.baseURL}`);
            await this.page.goto(this.baseURL, { waitUntil: 'networkidle' });
            
            const title = await this.page.title();
            console.log(`📄 Page title: ${title}`);
            
            // Check if React app loaded
            const reactRoot = await this.page.locator('#root').count();
            console.log(`⚛️  React root found: ${reactRoot > 0 ? 'YES' : 'NO'}`);
            
            // Check for VeoGen branding
            const veogenText = await this.page.locator('text=VeoGen').count();
            console.log(`🎬 VeoGen branding found: ${veogenText > 0 ? 'YES' : 'NO'}`);
            
            await this.takeScreenshot('page_load');
            
            return true;
        } catch (error) {
            console.error(`❌ Page load failed: ${error.message}`);
            return false;
        }
    }

    async testAuthenticationUI() {
        console.log('\n=== Testing Authentication UI ===');
        
        try {
            // Look for login form elements
            const emailInput = await this.page.locator('input[type="email"]').count();
            const passwordInput = await this.page.locator('input[type="password"]').count();
            const loginButton = await this.page.locator('button:has-text("Login"), button:has-text("Sign In")').count();
            
            console.log(`📧 Email input found: ${emailInput > 0 ? 'YES' : 'NO'}`);
            console.log(`🔐 Password input found: ${passwordInput > 0 ? 'YES' : 'NO'}`);
            console.log(`🔘 Login button found: ${loginButton > 0 ? 'YES' : 'NO'}`);
            
            // Check for registration/signup options
            const signupButton = await this.page.locator('button:has-text("Sign Up"), button:has-text("Register")').count();
            const signupLink = await this.page.locator('a:has-text("Sign Up"), a:has-text("Register")').count();
            
            console.log(`📝 Signup button/link found: ${(signupButton + signupLink) > 0 ? 'YES' : 'NO'}`);
            
            await this.takeScreenshot('auth_ui');
            
            return emailInput > 0 && passwordInput > 0 && loginButton > 0;
        } catch (error) {
            console.error(`❌ Auth UI test failed: ${error.message}`);
            return false;
        }
    }

    async testLogin(credentials) {
        console.log(`\n=== Testing Login (${credentials.email}) ===`);
        
        try {
            // Fill login form
            await this.page.fill('input[type="email"]', credentials.email);
            await this.page.fill('input[type="password"]', credentials.password);
            
            console.log(`📧 Filled email: ${credentials.email}`);
            console.log(`🔐 Filled password: ${'*'.repeat(credentials.password.length)}`);
            
            await this.takeScreenshot('before_login');
            
            // Click login button
            await this.page.click('button:has-text("Login"), button:has-text("Sign In")');
            console.log(`🔘 Clicked login button`);
            
            // Wait for response/navigation
            await this.page.waitForTimeout(3000);
            
            // Check current URL
            const currentURL = this.page.url();
            console.log(`🔗 Current URL: ${currentURL}`);
            
            // Check for error messages
            const errorMessages = await this.page.locator('.error, .alert-danger, [role="alert"]').allTextContents();
            if (errorMessages.length > 0) {
                console.log(`❌ Error messages found: ${errorMessages.join(', ')}`);
            }
            
            // Check for success indicators
            const successIndicators = await this.page.locator('.success, .alert-success').allTextContents();
            if (successIndicators.length > 0) {
                console.log(`✅ Success messages: ${successIndicators.join(', ')}`);
            }
            
            // Check localStorage for token
            const token = await this.page.evaluate(() => localStorage.getItem('token') || sessionStorage.getItem('token'));
            console.log(`🎫 Token in storage: ${token ? 'YES (length: ' + token.length + ')' : 'NO'}`);
            
            await this.takeScreenshot('after_login');
            
            return {
                success: token !== null,
                url: currentURL,
                errors: errorMessages,
                token: token
            };
            
        } catch (error) {
            console.error(`❌ Login test failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }

    async testOnboardingFlow() {
        console.log('\n=== Testing Onboarding Flow ===');
        
        try {
            // Look for onboarding indicators
            const onboardingElements = await this.page.locator(
                'text=onboard, text=welcome, text=getting started, text=setup, .onboarding, .welcome'
            ).count();
            
            console.log(`🎯 Onboarding elements found: ${onboardingElements}`);
            
            // Check for common onboarding UI patterns
            const progressBar = await this.page.locator('.progress, .stepper, .steps').count();
            const nextButton = await this.page.locator('button:has-text("Next"), button:has-text("Continue")').count();
            const skipButton = await this.page.locator('button:has-text("Skip"), a:has-text("Skip")').count();
            
            console.log(`📊 Progress indicator: ${progressBar > 0 ? 'YES' : 'NO'}`);
            console.log(`➡️  Next/Continue button: ${nextButton > 0 ? 'YES' : 'NO'}`);
            console.log(`⏭️  Skip option: ${skipButton > 0 ? 'YES' : 'NO'}`);
            
            // Check for specific onboarding content
            const pageText = await this.page.textContent('body');
            const hasOnboardingContent = pageText.toLowerCase().includes('onboard') || 
                                       pageText.toLowerCase().includes('welcome') ||
                                       pageText.toLowerCase().includes('getting started');
            
            console.log(`📖 Onboarding content detected: ${hasOnboardingContent ? 'YES' : 'NO'}`);
            
            await this.takeScreenshot('onboarding_check');
            
            return {
                hasOnboarding: onboardingElements > 0 || hasOnboardingContent,
                hasProgress: progressBar > 0,
                hasNavigation: nextButton > 0 || skipButton > 0
            };
            
        } catch (error) {
            console.error(`❌ Onboarding test failed: ${error.message}`);
            return { hasOnboarding: false, error: error.message };
        }
    }

    async testDashboardAccess() {
        console.log('\n=== Testing Dashboard Access ===');
        
        try {
            // Try to navigate to dashboard
            await this.page.goto(`${this.baseURL}/dashboard`, { waitUntil: 'networkidle' });
            
            const currentURL = this.page.url();
            console.log(`🔗 Dashboard URL: ${currentURL}`);
            
            // Check if we were redirected back to login
            const redirectedToLogin = currentURL.includes('login') || currentURL.includes('auth');
            console.log(`🔒 Redirected to login: ${redirectedToLogin ? 'YES' : 'NO'}`);
            
            // Check for dashboard content
            const dashboardElements = await this.page.locator(
                'text=dashboard, .dashboard, text=overview, text=projects'
            ).count();
            console.log(`📊 Dashboard elements: ${dashboardElements}`);
            
            await this.takeScreenshot('dashboard_access');
            
            return {
                accessible: !redirectedToLogin && dashboardElements > 0,
                url: currentURL,
                redirected: redirectedToLogin
            };
            
        } catch (error) {
            console.error(`❌ Dashboard test failed: ${error.message}`);
            return { accessible: false, error: error.message };
        }
    }

    async checkNetworkRequests() {
        console.log('\n=== Checking Network Requests ===');
        
        const requests = [];
        
        this.page.on('request', request => {
            if (request.url().includes('localhost:4700')) {
                requests.push({
                    method: request.method(),
                    url: request.url(),
                    headers: request.headers()
                });
            }
        });
        
        const responses = [];
        
        this.page.on('response', response => {
            if (response.url().includes('localhost:4700')) {
                responses.push({
                    status: response.status(),
                    url: response.url(),
                    headers: response.headers()
                });
            }
        });
        
        return { requests, responses };
    }

    async runFullTest() {
        console.log('🎬 Starting VeoGen Authentication & Onboarding Test Suite');
        console.log('=' * 60);
        
        const results = {
            pageLoad: false,
            authUI: false,
            logins: {},
            onboarding: {},
            dashboard: {}
        };
        
        try {
            await this.init();
            
            // Test 1: Page Load
            results.pageLoad = await this.testPageLoad();
            
            // Test 2: Authentication UI
            results.authUI = await this.testAuthenticationUI();
            
            // Test 3: Login with different credentials
            for (const [name, creds] of Object.entries(this.testCredentials)) {
                console.log(`\n--- Testing ${name} credentials ---`);
                
                // Navigate back to home page for fresh start
                await this.page.goto(this.baseURL, { waitUntil: 'networkidle' });
                
                results.logins[name] = await this.testLogin(creds);
                
                if (results.logins[name].success) {
                    // Test onboarding flow after successful login
                    results.onboarding[name] = await this.testOnboardingFlow();
                    
                    // Test dashboard access
                    results.dashboard[name] = await this.testDashboardAccess();
                }
                
                // Clear storage for next test
                await this.page.evaluate(() => {
                    localStorage.clear();
                    sessionStorage.clear();
                });
            }
            
        } catch (error) {
            console.error(`💥 Test suite failed: ${error.message}`);
        } finally {
            await this.cleanup();
        }
        
        // Print summary
        console.log('\n' + '=' * 60);
        console.log('🎬 VeoGen Test Results Summary');
        console.log('=' * 60);
        
        console.log(`📄 Page Load: ${results.pageLoad ? '✅ PASS' : '❌ FAIL'}`);
        console.log(`🔐 Auth UI: ${results.authUI ? '✅ PASS' : '❌ FAIL'}`);
        
        for (const [name, result] of Object.entries(results.logins)) {
            console.log(`🔑 Login (${name}): ${result.success ? '✅ PASS' : '❌ FAIL'}`);
            if (result.success && results.onboarding[name]) {
                console.log(`  └─ Onboarding: ${results.onboarding[name].hasOnboarding ? '✅ DETECTED' : '❌ NOT FOUND'}`);
            }
            if (result.success && results.dashboard[name]) {
                console.log(`  └─ Dashboard: ${results.dashboard[name].accessible ? '✅ ACCESSIBLE' : '❌ BLOCKED'}`);
            }
        }
        
        return results;
    }
}

// Run the test if called directly
if (require.main === module) {
    const tester = new VeoGenAuthTester();
    tester.runFullTest().then(results => {
        console.log('\n🎯 Test completed! Check screenshots for visual evidence.');
        process.exit(0);
    }).catch(error => {
        console.error('💥 Test failed:', error);
        process.exit(1);
    });
}

module.exports = VeoGenAuthTester;
