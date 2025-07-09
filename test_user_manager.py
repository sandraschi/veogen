#!/usr/bin/env python3
"""
Quick test of User Manager API endpoints
"""

import requests
import json

def test_user_manager():
    base_url = "http://localhost:8083"
    
    print("Testing VeoGen User Manager API...")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data}")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Stats: {stats_data}")
        else:
            print(f"❌ Stats Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats Error: {e}")
    
    # Test users endpoint
    try:
        response = requests.get(f"{base_url}/api/users", timeout=5)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ Users: Found {len(users_data)} users")
            if users_data:
                print(f"   First user: {users_data[0]['email']} ({users_data[0]['username']})")
        else:
            print(f"❌ Users Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Users Error: {e}")
    
    # Test frontend
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "VeoGen User Manager" in response.text:
            print("✅ Frontend: HTML page loads correctly")
        else:
            print(f"❌ Frontend Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend Error: {e}")
    
    print("\n🎉 User Manager is working!")
    print(f"📊 Dashboard: {base_url}")
    print(f"📚 API Docs: {base_url}/docs")

if __name__ == "__main__":
    test_user_manager()
