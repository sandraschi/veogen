#!/usr/bin/env python3
"""
Test user registration endpoints
"""
import requests
import json

def test_registration():
    print("=== Testing Registration Endpoints ===")
    
    # Test registration with new user
    new_user_data = {
        'email': 'newuser@test.com',
        'password': 'Test123!',
        'username': 'newuser',
        'full_name': 'New Test User'
    }
    
    print("1. Testing enhanced-auth registration...")
    try:
        response = requests.post('http://localhost:4700/api/v1/enhanced-auth/register', 
                               json=new_user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   SUCCESS: Registration worked!")
            user_email = data.get("user", {}).get("email", "unknown")
            token = data.get("access_token", "none")
            print(f"   User: {user_email}")
            print(f"   Token: {token[:20] if token != 'none' else 'none'}...")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n2. Testing regular auth registration...")  
    try:
        # Try different email to avoid conflicts
        new_user_data['email'] = 'newuser2@test.com'
        new_user_data['username'] = 'newuser2'
        
        response = requests.post('http://localhost:4700/api/v1/auth/register', 
                               json=new_user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS: Regular registration worked!")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n3. Testing password reset request...")
    try:
        reset_data = {'email': 'valid@test.com'}
        response = requests.post('http://localhost:4700/api/v1/enhanced-auth/request-password-reset', 
                               json=reset_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   SUCCESS: Password reset request worked!")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

if __name__ == "__main__":
    test_registration()
