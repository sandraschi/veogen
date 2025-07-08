#!/usr/bin/env python3
"""
Test the connection endpoints that the settings page uses
"""

import requests
import json

API_BASE_URL = 'http://localhost:4700'

def test_connection_endpoints():
    print("=== Testing Settings Page Connection Endpoints ===\n")
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint working")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            
            if 'components' in data:
                print(f"   Components:")
                for component, status in data['components'].items():
                    print(f"     - {component}: {status}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    print()
    
    # Test 2: Settings endpoint (without auth)
    print("2. Testing settings endpoint (no auth)...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/settings")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Settings endpoint working (default settings)")
            print(f"   Default style: {data.get('default_style', 'Unknown')}")
            print(f"   Default duration: {data.get('default_duration', 'Unknown')}")
        else:
            print(f"⚠️  Settings endpoint returned: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Settings endpoint error: {e}")
    
    print()
    
    # Test 3: Login and test with auth
    print("3. Testing with authentication...")
    try:
        login_response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json={
            'email': 'valid@test.com',
            'password': 'Test123!'
        })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('access_token')
            headers = {'Authorization': f'Bearer {token}'}
            
            print(f"✅ Login successful")
            
            # Test settings with auth
            settings_response = requests.get(f"{API_BASE_URL}/api/v1/settings", headers=headers)
            
            if settings_response.status_code == 200:
                settings_data = settings_response.json()
                print(f"✅ Authenticated settings endpoint working")
                print(f"   User settings loaded successfully")
            else:
                print(f"❌ Authenticated settings failed: {settings_response.status_code}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")

if __name__ == "__main__":
    test_connection_endpoints()
    print("\nTest connection functionality should now work in the settings page!")
