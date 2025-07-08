#!/usr/bin/env python3
"""
Clear browser storage for VeoGen and test the login flow
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def clear_browser_storage_and_test():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        print("=== Browser Storage Clear & Login Test ===")
        
        # Navigate to the app
        print("1. Navigating to VeoGen...")
        driver.get("http://localhost:4710")
        time.sleep(3)
        
        # Clear all storage
        print("2. Clearing browser storage...")
        driver.execute_script("localStorage.clear();")
        driver.execute_script("sessionStorage.clear();")
        driver.delete_all_cookies()
        print("   Storage cleared!")
        
        # Refresh to start clean
        driver.refresh()
        time.sleep(5)
        
        print(f"3. Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")
        
        # Wait for React to load and show login form
        print("4. Waiting for login form to appear...")
        try:
            # Try multiple selectors for email input
            email_input = None
            selectors_to_try = [
                'input[name="email"]',
                'input[type="email"]', 
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]'
            ]
            
            for selector in selectors_to_try:
                try:
                    email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"   Email input found with selector: {selector}")
                    break
                except:
                    continue
            
            if not email_input:
                # If no email input found, check what's on the page
                print("   No email input found. Page content:")
                body_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"   Body text: {body_text[:200]}...")
                
                # Check for any form fields
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"   Found {len(inputs)} input fields")
                for i, inp in enumerate(inputs):
                    try:
                        print(f"   Input {i}: name='{inp.get_attribute('name')}', type='{inp.get_attribute('type')}', placeholder='{inp.get_attribute('placeholder')}'")
                    except:
                        pass
                        
                return False
            
            # Find password input
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"], input[type="password"]')
            print("   Password input found!")
            
            # Fill in the form
            print("5. Filling login form...")
            email_input.clear()
            email_input.send_keys("valid@test.com")
            
            password_input.clear()
            password_input.send_keys("Test123!")
            
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:contains("Sign In")',
                'button:contains("Login")',
                'input[type="submit"]'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if 'contains' in selector:
                        # Use XPath for text-based search - check for common login button text
                        xpaths_to_try = [
                            "//button[contains(text(), 'Sign In')]",
                            "//button[contains(text(), 'Login')]", 
                            "//button[contains(text(), 'Submit')]"
                        ]
                        for xpath in xpaths_to_try:
                            try:
                                submit_button = driver.find_element(By.XPATH, xpath)
                                break
                            except:
                                continue
                        if submit_button:
                            break
                    else:
                        submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                except:
                    continue
            
            if not submit_button:
                # Look for any button
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"   Found {len(buttons)} buttons on page")
                for i, btn in enumerate(buttons):
                    try:
                        print(f"   Button {i}: text='{btn.text}', type='{btn.get_attribute('type')}'")
                    except:
                        pass
                return False
            
            print("   Submit button found!")
            
            # Take screenshot before submit
            driver.save_screenshot("before_login.png")
            print("   Screenshot saved: before_login.png")
            
            # Submit the form
            print("6. Submitting login...")
            submit_button.click()
            
            # Wait for response
            time.sleep(5)
            
            # Check what happened
            current_url = driver.current_url
            print(f"7. After login - URL: {current_url}")
            
            # Check for token in localStorage
            token = driver.execute_script("return localStorage.getItem('token')")
            if token:
                print(f"   SUCCESS: Token found in storage: {token[:20]}...")
                print("   Login appears to be working!")
                return True
            else:
                print("   No token found in localStorage")
                
                # Check for error messages
                error_selectors = [
                    '[role="alert"]',
                    '.MuiAlert-root',
                    '.error-message',
                    '[class*="error"]'
                ]
                
                for selector in error_selectors:
                    try:
                        error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for error in error_elements:
                            if error.text.strip():
                                print(f"   Error message: {error.text}")
                    except:
                        pass
                
                # Take screenshot after login attempt
                driver.save_screenshot("after_login_attempt.png")
                print("   Screenshot saved: after_login_attempt.png")
                
                return False
                
        except Exception as e:
            print(f"   Error during login process: {e}")
            
            # Take error screenshot
            driver.save_screenshot("login_error.png")
            print("   Error screenshot saved: login_error.png")
            return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    success = clear_browser_storage_and_test()
    if success:
        print("\n🎉 Login test PASSED! Browser login should work.")
    else:
        print("\n❌ Login test FAILED. Check screenshots for debugging.")
