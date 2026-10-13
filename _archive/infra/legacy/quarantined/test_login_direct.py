#!/usr/bin/env python3
"""
Direct test of login functionality
"""
import requests
import json

API_BASE_URL = "http://localhost:4700"

def test_login():
    """Test login with known credentials"""
    
    # Test with valid@test.com and Test123!
    login_data = {
        "email": "valid@test.com",
        "password": "Test123!"
    }
    
    print(f"Testing login with: {login_data['email']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/enhanced-auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Login successful!")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {result.get('user_id', 'N/A')}")
            print(f"User Data: {result.get('user', {})}")
            print(f"Onboarding: {result.get('onboarding', {})}")
            return result.get('access_token')
        else:
            print("FAILED: Login failed!")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
        return None

def test_with_token(token):
    """Test accessing protected endpoint with token"""
    if not token:
        print("No token to test with")
        return
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/enhanced-auth/me",
            headers=headers
        )
        
        print(f"\nTesting /me endpoint:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Token validation successful!")
            print(f"User: {result}")
        else:
            print("FAILED: Token validation failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Token test failed: {e}")

def test_create_user():
    """Test creating a new user"""
    user_data = {
        "email": "newuser@test.com",
        "password": "NewUser123!",
        "username": "newuser",
        "full_name": "New Test User"
    }
    
    print(f"\nTesting user creation with: {user_data['email']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/enhanced-auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: User creation successful!")
            print(f"User ID: {result.get('user_id', 'N/A')}")
            print(f"Access Token: {result.get('access_token', 'N/A')[:50]}...")
            return result.get('access_token')
        else:
            print("FAILED: User creation failed!")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"ERROR: User creation request failed: {e}")
        return None

if __name__ == "__main__":
    print("=== VeoGen Authentication Test ===")
    
    # Test login
    token = test_login()
    
    # Test token usage
    test_with_token(token)
    
    # Test user creation
    print("\n" + "="*50)
    new_token = test_create_user()
    test_with_token(new_token)
