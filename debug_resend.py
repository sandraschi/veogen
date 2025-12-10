import time

import requests

# Test the resend verification endpoint with proper authentication
API_BASE = "http://localhost:4700"

timestamp = int(time.time())
test_email = f"debug-resend-{timestamp}@example.com"
register_data = {
    "email": test_email,
    "password": "TestPass123!",
    "username": f"debuguser{timestamp}",
    "full_name": "Debug User"
}

print("1. Registering user...")
response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/register", json=register_data)
print(f"Registration status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data['access_token']
    print(f"Token received: {token[:20]}...")
    
    # Now test the resend verification endpoint
    print("\n2. Testing resend verification...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with POST request (correct method)
    response = requests.post(f"{API_BASE}/api/v1/enhanced-auth/resend-verification", headers=headers)
    print(f"Resend status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Also test the auth debug endpoint
    print("\n3. Testing debug endpoint...")
    response = requests.get(f"{API_BASE}/api/v1/enhanced-auth/debug-auth", headers=headers)
    print(f"Debug status: {response.status_code}")
    if response.status_code == 200:
        print(f"Debug response: {response.json()}")
    else:
        print(f"Debug error: {response.text}")
        
else:
    print(f"Registration failed: {response.text}")
