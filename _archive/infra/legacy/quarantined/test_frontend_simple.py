#!/usr/bin/env python3
"""
Simple frontend connectivity test
"""
import requests

def test_frontend():
    print("=== Frontend Connectivity Test ===")
    
    # Test main page
    print("1. Testing main page...")
    try:
        response = requests.get('http://localhost:4710/', timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)} chars")
        
        # Check for key indicators
        content_lower = response.text.lower()
        
        if 'veogen' in content_lower:
            print("   SUCCESS: VeoGen branding found")
        
        if 'email' in content_lower and 'password' in content_lower:
            print("   SUCCESS: Login form elements found")
        elif 'auth' in content_lower:
            print("   INFO: Auth-related content found, may need to navigate to /auth")
            
        # Check for React app
        if 'react' in content_lower or 'root' in content_lower:
            print("   SUCCESS: React app detected")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test auth page
    print("\n2. Testing auth page...")
    try:
        response = requests.get('http://localhost:4710/auth', timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content length: {len(response.text)} chars")
        
        content_lower = response.text.lower()
        
        if 'email' in content_lower:
            print("   SUCCESS: Email field found")
        if 'password' in content_lower:
            print("   SUCCESS: Password field found")
        if 'login' in content_lower or 'sign in' in content_lower:
            print("   SUCCESS: Login text found")
            
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_frontend()
