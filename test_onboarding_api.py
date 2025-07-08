import requests
import json

# Test the onboarding completion endpoint
def test_onboarding_completion():
    print("=== Testing Onboarding Completion ===")
    
    # First, login to get a token
    login_url = "http://localhost:4700/api/v1/enhanced-auth/login"
    login_data = {
        "email": "valid@test.com",
        "password": "Test123!"
    }
    
    try:
        print("1. Logging in...")
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            user = login_result.get('user')
            onboarding = login_result.get('onboarding')
            
            print(f"User: {user.get('email')}")
            print(f"Onboarding complete: {onboarding.get('is_complete')}")
            print(f"Token: {token[:20]}...")
            
            # Now test onboarding completion
            print("\n2. Testing onboarding completion...")
            onboarding_url = "http://localhost:4700/api/v1/enhanced-auth/complete-onboarding"
            onboarding_data = {
                "api_keys": {},  # Empty API keys (skipping)
                "preferences": {
                    "theme": "dark",
                    "notifications": True
                },
                "skip_tutorial": True
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            
            onboarding_response = requests.post(
                onboarding_url, 
                json=onboarding_data, 
                headers=headers
            )
            
            print(f"Onboarding completion status: {onboarding_response.status_code}")
            
            if onboarding_response.status_code == 200:
                result = onboarding_response.json()
                print("SUCCESS: Onboarding completion successful!")
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Now check if user shows onboarding as complete
                print("\n3. Checking updated user status...")
                me_url = "http://localhost:4700/api/v1/enhanced-auth/me"
                me_response = requests.get(me_url, headers=headers)
                
                if me_response.status_code == 200:
                    updated_user = me_response.json()
                    print(f"Updated onboarding status: {updated_user.get('settings', {}).get('onboarding_complete')}")
                    print("SUCCESS: Test completed successfully!")
                else:
                    print(f"FAILED: Failed to get updated user: {me_response.status_code}")
                    print(me_response.text)
                    
            else:
                print(f"FAILED: Onboarding completion failed: {onboarding_response.status_code}")
                print(onboarding_response.text)
                
        else:
            print(f"FAILED: Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except Exception as e:
        print(f"FAILED: Test failed with error: {e}")

if __name__ == "__main__":
    test_onboarding_completion()
