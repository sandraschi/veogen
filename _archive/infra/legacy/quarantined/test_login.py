#!/usr/bin/env python3
import requests
import json

def test_login():
    # Test the login endpoint
    url = "http://localhost:4700/api/v1/enhanced-auth/login"
    
    # Test data
    login_data = {
        "email": "test@test.com",
        "password": "test123"
    }
    
    try:
        print(f"Testing login endpoint: {url}")
        print(f"Login data: {login_data}")
        
        response = requests.post(url, json=login_data, headers={"Content-Type": "application/json"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Login successful!")
            print(f"   Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            print(f"   User Email: {data.get('user', {}).get('email', 'N/A')}")
        else:
            print(f"ERROR: Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Error testing login: {e}")

if __name__ == "__main__":
    test_login() 