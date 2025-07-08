#!/usr/bin/env python3
"""
Test the browser login flow by checking network requests and JavaScript errors
"""
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_browser_login():
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    # Enable logging
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 10)
        
        print("=== Browser Login Test ===")
        
        # Navigate to the login page
        print("1. Navigating to http://localhost:4710...")
        driver.get("http://localhost:4710")
        time.sleep(3)
        
        # Check if page loaded
        print(f"   Page title: {driver.title}")
        print(f"   Current URL: {driver.current_url}")
        
        # Check for JavaScript errors
        logs = driver.get_log('browser')
        if logs:
            print("   JavaScript Console Logs:")
            for log in logs:
                print(f"   {log['level']}: {log['message']}")
        
        # Look for email input field
        print("\n2. Looking for login form...")
        try:
            email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            password_input = driver.find_element(By.NAME, "password")
            print("   ✅ Login form found!")
            
            # Fill in credentials
            print("\n3. Filling in credentials...")
            email_input.clear()
            email_input.send_keys("valid@test.com")
            password_input.clear() 
            password_input.send_keys("Test123!")
            
            # Find submit button
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            print("   ✅ Submit button found")
            
            # Enable network monitoring
            driver.execute_cdp_cmd('Network.enable', {})
            
            # Click submit
            print("\n4. Submitting login form...")
            submit_button.click()
            
            # Wait a moment for network request
            time.sleep(3)
            
            # Check network logs
            network_logs = driver.get_log('performance')
            login_requests = []
            for log in network_logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if 'login' in url or 'auth' in url:
                        login_requests.append({
                            'url': url,
                            'status': message['message']['params']['response']['status'],
                            'statusText': message['message']['params']['response']['statusText']
                        })
            
            print("   Login-related network requests:")
            for req in login_requests:
                print(f"   {req['status']} {req['statusText']}: {req['url']}")
            
            # Check for success/error messages
            print("\n5. Checking for results...")
            try:
                # Look for success message or navigation
                current_url = driver.current_url
                print(f"   Current URL after login: {current_url}")
                
                # Check for error messages
                alerts = driver.find_elements(By.CSS_SELECTOR, "[role='alert'], .MuiAlert-root")
                if alerts:
                    for alert in alerts:
                        print(f"   Alert message: {alert.text}")
                
                # Check localStorage for token
                token = driver.execute_script("return localStorage.getItem('token')")
                if token:
                    print(f"   ✅ Token stored in localStorage: {token[:20]}...")
                else:
                    print("   ❌ No token found in localStorage")
                    
            except Exception as e:
                print(f"   Error checking results: {e}")
                
        except Exception as e:
            print(f"   ❌ Login form not found: {e}")
            
            # Check what's actually on the page
            print("\n   Page source (first 500 chars):")
            print(driver.page_source[:500])
        
        # Final JavaScript console check
        final_logs = driver.get_log('browser')
        if final_logs:
            print("\n6. Final JavaScript console logs:")
            for log in final_logs:
                if log['level'] in ['SEVERE', 'WARNING']:
                    print(f"   {log['level']}: {log['message']}")
        
    except Exception as e:
        print(f"ERROR: Browser test failed: {e}")
        
    finally:
        if 'driver' in locals():
            driver.quit()
        
    print("\n=== Browser Test Complete ===")

if __name__ == "__main__":
    test_browser_login()
