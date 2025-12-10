#!/usr/bin/env python3
"""
Debug the authentication state after login
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

def debug_auth_state() -> bool:
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)
        
        print("=== Authentication State Debug ===")
        
        # Navigate and login
        driver.get("http://localhost:4710")
        time.sleep(3)
        
        print("1. Logging in...")
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]')))
        password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        email_input.send_keys("valid@test.com")
        password_input.send_keys("Test123!")
        submit_button.click()
        
        time.sleep(5)
        
        # Debug the authentication state
        print("2. Checking authentication state...")
        
        # Get localStorage data
        token = driver.execute_script("return localStorage.getItem('token')")
        user_data = driver.execute_script("return localStorage.getItem('user')")
        
        print(f"   Token in localStorage: {bool(token)}")
        if token:
            print(f"   Token preview: {token[:50]}...")
        
        print(f"   User data in localStorage: {bool(user_data)}")
        if user_data:
            try:
                user_obj = json.loads(user_data)
                print(f"   User email: {user_obj.get('email', 'Not found')}")
            except json.JSONDecodeError:
                print(f"   User data preview: {user_data[:100]}...")
        
        # Check React auth context state
        print("3. Checking React AuthContext state...")
        auth_context_check = """
        // Try to access the auth context state
        try {
            // Check if there's a global auth state or context
            const rootElement = document.getElementById('root');
            if (rootElement && rootElement._reactInternalInstance) {
                return 'React context found but complex to access';
            }
            
            // Check for any global auth variables
            if (window.authContext) {
                return JSON.stringify(window.authContext);
            }
            
            return 'No direct auth context access';
        } catch (e) {
            return 'Error accessing auth context: ' + e.message;
        }
        """
        
        auth_result = driver.execute_script(auth_context_check)
        print(f"   Auth context result: {auth_result}")
        
        # Test navigation to home
        print("4. Testing manual navigation to home...")
        driver.get("http://localhost:4710/")
        time.sleep(3)
        
        current_url = driver.current_url
        print(f"   After navigating to /: {current_url}")
        
        if "/auth" in current_url:
            print("   ISSUE: Still redirected to /auth - isAuthenticated() returning false")
        else:
            print("   SUCCESS: Stayed on home page - authentication working")
        
        # Check console errors
        print("5. Checking for JavaScript errors...")
        logs = driver.get_log("browser")
        error_count = 0
        for log in logs:
            if log['level'] in ['SEVERE', 'ERROR']:
                print(f"   ERROR: {log['message']}")
                error_count += 1
        
        if error_count == 0:
            print("   No JavaScript errors found")
        
        # Final state check
        print("6. Final authentication state check...")
        final_check = """
        try {
            const token = localStorage.getItem('token');
            const user = localStorage.getItem('user');
            
            return {
                hasToken: !!token,
                hasUser: !!user,
                tokenLength: token ? token.length : 0,
                userParseable: user ? 'yes' : 'no'
            };
        } catch (e) {
            return { error: e.message };
        }
        """
        
        final_result = driver.execute_script(final_check)
        print(f"   Final state: {final_result}")
        
        return "/auth" not in driver.current_url
        
    except Exception as e:
        print(f"ERROR during debug: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    success = debug_auth_state()
    if success:
        print("\nSUCCESS: Authentication appears to be working correctly!")
    else:
        print("\nISSUE: Authentication not fully working - user stays on /auth page")
