#!/usr/bin/env python3
import requests
import json

def test_me_endpoint():
    # First login to get a token
    login_url = "http://localhost:4700/api/v1/enhanced-auth/login"
    login_data = {
        "email": "test@test.com",
        "password": "test123"
    }
    
    try:
        print("1. Logging in to get access token...")
        login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"ERROR: Login failed: {login_response.status_code}")
            return
            
        login_data = login_response.json()
        access_token = login_data['access_token']
        print(f"SUCCESS: Login successful, got token: {access_token[:50]}...")
        
        # Now test the /me endpoint
        me_url = "http://localhost:4700/api/v1/enhanced-auth/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        print("2. Testing /me endpoint...")
        me_response = requests.get(me_url, headers=headers)
        
        print(f"Status Code: {me_response.status_code}")
        print(f"Response: {me_response.text}")
        
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"SUCCESS: /me endpoint working!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Username: {user_data.get('username')}")
        else:
            print(f"ERROR: /me endpoint failed: {me_response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Error: {e}")

if __name__ == "__main__":
    test_me_endpoint() 