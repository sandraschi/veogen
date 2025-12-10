import requests
import json

API_BASE_URL = 'http://localhost:4700'

def test_connection_endpoints():
    print("=== Testing Settings Page Connection Endpoints ===")
    
    # Test 1: Health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Health endpoint working")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            
            if 'components' in data:
                print(f"   Components:")
                for component, status in data['components'].items():
                    print(f"     - {component}: {status}")
            return True
        else:
            print(f"FAILED: Health endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Health endpoint failed - {e}")
        return False

def test_auth_settings():
    print("\n2. Testing authenticated settings...")
    try:
        # Login first
        login_response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json={
            'email': 'valid@test.com',
            'password': 'Test123!'
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            print(f"SUCCESS: Login successful")
            
            # Test settings endpoint
            settings_response = requests.get(f"{API_BASE_URL}/api/v1/settings", headers=headers)
            
            if settings_response.status_code == 200:
                settings_data = settings_response.json()
                print(f"SUCCESS: Settings endpoint working")
                print(f"   Default style: {settings_data.get('default_style', 'Unknown')}")
                return True
            else:
                print(f"FAILED: Settings endpoint returned {settings_response.status_code}")
                return False
        else:
            print(f"FAILED: Login returned {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Auth test failed - {e}")
        return False

if __name__ == "__main__":
    health_ok = test_connection_endpoints()
    auth_ok = test_auth_settings()
    
    print(f"\n=== RESULTS ===")
    print(f"Health endpoint: {'WORKING' if health_ok else 'FAILED'}")
    print(f"Auth + Settings: {'WORKING' if auth_ok else 'FAILED'}")
    
    if health_ok and auth_ok:
        print(f"\nSUCCESS: Settings page connection button should work!")
    else:
        print(f"\nISSUE: Some endpoints need attention")
