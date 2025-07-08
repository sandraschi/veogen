#!/usr/bin/env python3
"""
Final comprehensive test of the VeoGen authentication system
"""
import requests
import json
import time

BACKEND_URL = "http://localhost:4700"
FRONTEND_URL = "http://localhost:4710"

def test_auth_workflow():
    """Test the complete authentication workflow"""
    print("=== VeoGen Authentication System Test ===")
    
    # Test 1: Backend Health
    print("\n1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   SUCCESS: Backend healthy - {health.get('status')}")
            components = health.get('components', {})
            for comp, status in components.items():
                print(f"   - {comp}: {status}")
        else:
            print(f"   ERROR: Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ERROR: Cannot connect to backend: {e}")
        return False
    
    # Test 2: Login Test
    print("\n2. Testing Login...")
    login_data = {"email": "valid@test.com", "password": "Test123!"}
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/enhanced-auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            user_data = result.get('user')
            print(f"   SUCCESS: Login successful")
            print(f"   - User: {user_data.get('email')} ({user_data.get('id')})")
            print(f"   - Token length: {len(token) if token else 0} chars")
            print(f"   - Token type: {result.get('token_type')}")
        else:
            print(f"   ERROR: Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ERROR: Login request failed: {e}")
        return False
    
    # Test 3: /me endpoint
    print("\n3. Testing /me endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/enhanced-auth/me", headers=headers)
        if response.status_code == 200:
            me_data = response.json()
            print(f"   SUCCESS: /me endpoint working")
            print(f"   - User: {me_data.get('email')} ({me_data.get('id')})")
            print(f"   - Has settings: {bool(me_data.get('settings'))}")
            print(f"   - Onboarding complete: {me_data.get('onboarding', {}).get('is_complete')}")
            
            # Check consistency
            if me_data.get('id') == user_data.get('id'):
                print("   SUCCESS: User data consistent between login and /me")
            else:
                print("   WARNING: User data inconsistent!")
        else:
            print(f"   ERROR: /me failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ERROR: /me request failed: {e}")
        return False
    
    # Test 4: Frontend Accessibility
    print("\n4. Testing Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"   SUCCESS: Frontend accessible")
            # Check for key indicators
            content = response.text.lower()
            if "veogen" in content:
                print("   SUCCESS: Contains VeoGen branding")
            if "react" in content or "javascript" in content:
                print("   SUCCESS: React app detected")
        else:
            print(f"   WARNING: Frontend returned {response.status_code}")
    except Exception as e:
        print(f"   WARNING: Frontend test failed: {e}")
    
    # Test 5: API Proxy Test (through frontend)
    print("\n5. Testing Frontend API Proxy...")
    try:
        # Test if frontend can proxy to backend API
        response = requests.get(f"{FRONTEND_URL}/api/v1/auth/debug-auth", 
                              headers=headers, timeout=5)
        if response.status_code == 200:
            print("   SUCCESS: Frontend API proxy working")
        elif response.status_code == 404:
            print("   INFO: Direct proxy not available (normal)")
        else:
            print(f"   INFO: Proxy test returned {response.status_code}")
    except Exception as e:
        print(f"   INFO: Proxy test failed: {e}")
    
    return True

def main():
    success = test_auth_workflow()
    
    print("\n" + "="*50)
    print("AUTHENTICATION SYSTEM STATUS")
    print("="*50)
    
    if success:
        print("SUCCESS: Backend authentication is fully functional")
        print("")
        print("NEXT STEPS:")
        print("1. Open http://localhost:4710 in your browser")
        print("2. Try logging in with: valid@test.com / Test123!")
        print("3. Check browser console for any JavaScript errors")
        print("4. If login doesn't work, clear browser cache/localStorage")
        print("")
        print("TROUBLESHOOTING:")
        print("- If frontend shows errors, check browser developer console")
        print("- If login fails in browser, check Network tab for failed requests")
        print("- Backend is confirmed working, so issues are likely frontend")
    else:
        print("ERROR: Backend authentication has issues")
        print("Check the error messages above and fix backend issues first")
    
    print(f"\nURLs:")
    print(f"- Frontend: {FRONTEND_URL}")
    print(f"- Backend API: {BACKEND_URL}")
    print(f"- API Docs: {BACKEND_URL}/docs")

if __name__ == "__main__":
    main()
