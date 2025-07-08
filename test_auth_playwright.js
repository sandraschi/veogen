const { chromium } = require('playwright');

async function testVeoGenAuthentication() {
    console.log('🎬 Starting VeoGen Authentication Test Suite...');
    
    const browser = await chromium.launch({ 
        headless: false,  // Set to true for headless testing
        slowMo: 1000     // Slow down for better visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Test results tracker
    const results = {
        pageLoad: false,
        loginFormExists: false,
        existingUserLogin: false,
        newUserRegistration: false,
        passwordReset: false,
        errors: []
    };
    
    try {
        // Test 1: Page Load and Navigation
        console.log('\n📍 Test 1: Loading VeoGen...');
        await page.goto('http://localhost:4710');
        await page.waitForTimeout(3000);
        
        console.log(`Page title: ${await page.title()}`);
        console.log(`Current URL: ${page.url()}`);
        results.pageLoad = true;
        
        // Take screenshot of initial state
        await page.screenshot({ path: 'veogen-initial.png' });
        console.log('✅ Initial page screenshot saved: veogen-initial.png');
        
        // Test 2: Check for Login Form
        console.log('\n📍 Test 2: Checking for login form...');
        
        // Wait for React to load
        await page.waitForTimeout(5000);
        
        // Look for email input field
        const emailSelectors = [
            'input[name="email"]',
            'input[type="email"]',
            'input[placeholder*="email" i]',
            'input[placeholder*="Email" i]',
            '[data-testid="email"]',
            '#email'
        ];
        
        let emailInput = null;
        for (const selector of emailSelectors) {
            try {
                emailInput = await page.waitForSelector(selector, { timeout: 2000 });
                if (emailInput) {
                    console.log(`✅ Email input found with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                console.log(`❌ Email input not found with selector: ${selector}`);
            }
        }
        
        if (!emailInput) {
            console.log('🔍 No email input found. Checking page content...');
            const bodyText = await page.textContent('body');
            console.log('Page text content:', bodyText.substring(0, 500));
            
            // Try to find any form elements
            const forms = await page.$$('form');
            console.log(`Found ${forms.length} form(s) on page`);
            
            const inputs = await page.$$('input');
            console.log(`Found ${inputs.length} input(s) on page`);
            
            for (let i = 0; i < Math.min(inputs.length, 5); i++) {
                const input = inputs[i];
                const type = await input.getAttribute('type');
                const name = await input.getAttribute('name');
                const placeholder = await input.getAttribute('placeholder');
                console.log(`Input ${i}: type="${type}", name="${name}", placeholder="${placeholder}"`);
            }
            
            throw new Error('Login form not found');
        }
        
        results.loginFormExists = true;
        
        // Test 3: Existing User Login
        console.log('\n📍 Test 3: Testing existing user login...');
        
        // Find password input
        const passwordInput = await page.waitForSelector('input[type="password"], input[name="password"]');
        console.log('✅ Password input found');
        
        // Clear and fill email
        await emailInput.click();
        await emailInput.fill('');
        await emailInput.type('sandraschipal@hotmail.com');
        console.log('✅ Email entered: sandraschipal@hotmail.com');
        
        // Clear and fill password
        await passwordInput.click();
        await passwordInput.fill('');
        await passwordInput.type('S3c1000vg#');
        console.log('✅ Password entered');
        
        // Take screenshot before login
        await page.screenshot({ path: 'veogen-before-login.png' });
        console.log('✅ Pre-login screenshot saved: veogen-before-login.png');
        
        // Find and click submit button
        const submitSelectors = [
            'button[type="submit"]',
            'button:has-text("Sign In")',
            'button:has-text("Login")',
            'input[type="submit"]',
            'button:has-text("Sign in")'
        ];
        
        let submitButton = null;
        for (const selector of submitSelectors) {
            try {
                submitButton = await page.waitForSelector(selector, { timeout: 1000 });
                if (submitButton) {
                    console.log(`✅ Submit button found with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                console.log(`❌ Submit button not found with selector: ${selector}`);
            }
        }
        
        if (!submitButton) {
            // Look for any buttons
            const buttons = await page.$$('button');
            console.log(`Found ${buttons.length} button(s) on page`);
            
            for (let i = 0; i < Math.min(buttons.length, 5); i++) {
                const button = buttons[i];
                const text = await button.textContent();
                const type = await button.getAttribute('type');
                console.log(`Button ${i}: text="${text}", type="${type}"`);
            }
            
            if (buttons.length > 0) {
                submitButton = buttons[0]; // Try the first button
                console.log('🔧 Using first available button as submit');
            }
        }
        
        if (submitButton) {
            await submitButton.click();
            console.log('✅ Submit button clicked');
            
            // Wait for response
            await page.waitForTimeout(5000);
            
            // Take screenshot after login attempt
            await page.screenshot({ path: 'veogen-after-login.png' });
            console.log('✅ Post-login screenshot saved: veogen-after-login.png');
            
            // Check current URL
            const currentUrl = page.url();
            console.log(`Current URL after login: ${currentUrl}`);
            
            // Check for success indicators
            const isLoggedIn = !currentUrl.includes('/auth') || 
                              await page.$('text=Dashboard') !== null ||
                              await page.$('text=Welcome') !== null ||
                              await page.$('[data-testid="user-menu"]') !== null;
            
            if (isLoggedIn) {
                console.log('✅ Login appears successful!');
                results.existingUserLogin = true;
            } else {
                console.log('❌ Login may have failed - still on auth page');
                
                // Check for error messages
                const errorSelectors = [
                    '[role="alert"]',
                    '.error',
                    '.alert-error',
                    '[class*="error"]',
                    'text=Invalid',
                    'text=Error'
                ];
                
                for (const selector of errorSelectors) {
                    try {
                        const errorElement = await page.$(selector);
                        if (errorElement) {
                            const errorText = await errorElement.textContent();
                            console.log(`❌ Error found: ${errorText}`);
                            results.errors.push(`Login error: ${errorText}`);
                        }
                    } catch (e) {
                        // Ignore selector errors
                    }
                }
            }
        } else {
            throw new Error('No submit button found');
        }
        
        // Test 4: New User Registration
        console.log('\n📍 Test 4: Testing new user registration...');
        
        // Navigate back to auth page
        await page.goto('http://localhost:4710/auth');
        await page.waitForTimeout(3000);
        
        // Look for "Sign up" or "Register" link
        const signupSelectors = [
            'text=Sign up',
            'text=Register',
            'text=Create account',
            'button:has-text("Sign up")',
            'a:has-text("Sign up")',
            'text=Don\\'t have an account'
        ];
        
        let signupLink = null;
        for (const selector of signupSelectors) {
            try {
                signupLink = await page.$(selector);
                if (signupLink) {
                    console.log(`✅ Signup link found with selector: ${selector}`);
                    await signupLink.click();
                    await page.waitForTimeout(2000);
                    break;
                }
            } catch (e) {
                console.log(`❌ Signup link not found with selector: ${selector}`);
            }
        }
        
        if (signupLink) {
            // Fill registration form
            const testUser = {
                email: `test-${Date.now()}@example.com`,
                password: 'TestPass123!',
                username: `testuser${Date.now()}`,
                fullName: 'Test User'
            };
            
            console.log(`Testing registration with email: ${testUser.email}`);
            
            // Fill email
            const regEmailInput = await page.$('input[name="email"], input[type="email"]');
            if (regEmailInput) {
                await regEmailInput.fill(testUser.email);
                console.log('✅ Registration email filled');
            }
            
            // Fill password
            const regPasswordInput = await page.$('input[name="password"], input[type="password"]');
            if (regPasswordInput) {
                await regPasswordInput.fill(testUser.password);
                console.log('✅ Registration password filled');
            }
            
            // Fill username if present
            const usernameInput = await page.$('input[name="username"]');
            if (usernameInput) {
                await usernameInput.fill(testUser.username);
                console.log('✅ Username filled');
            }
            
            // Fill full name if present
            const fullNameInput = await page.$('input[name="full_name"], input[name="fullName"]');
            if (fullNameInput) {
                await fullNameInput.fill(testUser.fullName);
                console.log('✅ Full name filled');
            }
            
            // Take screenshot before registration
            await page.screenshot({ path: 'veogen-before-registration.png' });
            
            // Submit registration
            const regSubmitButton = await page.$('button[type="submit"]');
            if (regSubmitButton) {
                await regSubmitButton.click();
                console.log('✅ Registration form submitted');
                
                await page.waitForTimeout(5000);
                await page.screenshot({ path: 'veogen-after-registration.png' });
                
                const regCurrentUrl = page.url();
                console.log(`URL after registration: ${regCurrentUrl}`);
                
                // Check for success
                if (!regCurrentUrl.includes('/auth') || await page.$('text=Welcome') !== null) {
                    console.log('✅ Registration appears successful!');
                    results.newUserRegistration = true;
                } else {
                    console.log('❌ Registration may have failed');
                }
            }
        } else {
            console.log('❌ No registration link found');
        }
        
        // Test 5: Password Reset
        console.log('\n📍 Test 5: Testing password reset...');
        
        // Navigate back to auth page
        await page.goto('http://localhost:4710/auth');
        await page.waitForTimeout(3000);
        
        // Look for "Forgot password" link
        const forgotSelectors = [
            'text=Forgot password',
            'text=Forgot Password',
            'text=Reset password',
            'a:has-text("Forgot")',
            'button:has-text("Forgot")'
        ];
        
        let forgotLink = null;
        for (const selector of forgotSelectors) {
            try {
                forgotLink = await page.$(selector);
                if (forgotLink) {
                    console.log(`✅ Forgot password link found with selector: ${selector}`);
                    await forgotLink.click();
                    await page.waitForTimeout(2000);
                    break;
                }
            } catch (e) {
                console.log(`❌ Forgot password link not found with selector: ${selector}`);
            }
        }
        
        if (forgotLink) {
            // Fill email for reset
            const resetEmailInput = await page.$('input[name="email"], input[type="email"]');
            if (resetEmailInput) {
                await resetEmailInput.fill('sandraschipal@hotmail.com');
                console.log('✅ Reset email filled');
                
                const resetSubmitButton = await page.$('button[type="submit"]');
                if (resetSubmitButton) {
                    await resetSubmitButton.click();
                    console.log('✅ Password reset form submitted');
                    
                    await page.waitForTimeout(3000);
                    await page.screenshot({ path: 'veogen-password-reset.png' });
                    
                    // Check for success message
                    const successSelectors = [
                        'text=sent',
                        'text=check your email',
                        'text=reset link',
                        '[class*="success"]'
                    ];
                    
                    for (const selector of successSelectors) {
                        try {
                            const successElement = await page.$(selector);
                            if (successElement) {
                                console.log('✅ Password reset appears successful!');
                                results.passwordReset = true;
                                break;
                            }
                        } catch (e) {
                            // Ignore
                        }
                    }
                }
            }
        } else {
            console.log('❌ No forgot password link found');
        }
        
    } catch (error) {
        console.error('❌ Test error:', error.message);
        results.errors.push(error.message);
        
        // Take error screenshot
        await page.screenshot({ path: 'veogen-error.png' });
        console.log('📸 Error screenshot saved: veogen-error.png');
    }
    
    await browser.close();
    
    // Print results summary
    console.log('\n📊 TEST RESULTS SUMMARY');
    console.log('========================');
    console.log(`Page Load: ${results.pageLoad ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Login Form Exists: ${results.loginFormExists ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Existing User Login: ${results.existingUserLogin ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`New User Registration: ${results.newUserRegistration ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Password Reset: ${results.passwordReset ? '✅ PASS' : '❌ FAIL'}`);
    
    if (results.errors.length > 0) {
        console.log('\n❌ ERRORS FOUND:');
        results.errors.forEach((error, index) => {
            console.log(`${index + 1}. ${error}`);
        });
    }
    
    console.log('\n📸 Screenshots saved:');
    console.log('- veogen-initial.png');
    console.log('- veogen-before-login.png');
    console.log('- veogen-after-login.png');
    console.log('- veogen-before-registration.png');
    console.log('- veogen-after-registration.png');
    console.log('- veogen-password-reset.png');
    if (results.errors.length > 0) {
        console.log('- veogen-error.png');
    }
    
    return results;
}

// Run the test
if (require.main === module) {
    testVeoGenAuthentication()
        .then(results => {
            console.log('\n🎭 VeoGen Authentication Test Complete!');
            process.exit(0);
        })
        .catch(error => {
            console.error('💥 Test suite failed:', error);
            process.exit(1);
        });
}

module.exports = { testVeoGenAuthentication };
