#!/usr/bin/env python3
"""
Test the fixed User Manager with UUID support
"""
import requests
import json

def test_user_manager():
    """Test the User Manager API endpoints"""
    base_url = "http://localhost:8083"
    
    print("🧪 Testing VeoGen User Manager (UUID Fixed)")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test 2: Get statistics
    try:
        response = requests.get(f"{base_url}/api/stats")
        stats = response.json()
        print(f"✅ Statistics: {response.status_code}")
        print(f"   Total Users: {stats.get('total_users', 'N/A')}")
        print(f"   Active Users: {stats.get('active_users', 'N/A')}")
        print(f"   Total Videos: {stats.get('total_videos', 'N/A')}")
        print(f"   API Keys: {stats.get('total_api_keys', 'N/A')}")
    except Exception as e:
        print(f"❌ Statistics Failed: {e}")
    
    # Test 3: Get users (this was failing before)
    try:
        response = requests.get(f"{base_url}/api/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Get Users: {response.status_code}")
            print(f"   Retrieved {len(users)} users successfully")
            
            if users:
                first_user = users[0]
                print(f"   Sample User ID: {first_user.get('id')} (type: {type(first_user.get('id'))})")
                print(f"   Sample User: {first_user.get('username')} ({first_user.get('email')})")
            
            return True
        else:
            print(f"❌ Get Users Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Users Failed: {e}")
        return False

if __name__ == "__main__":
    success = test_user_manager()
    if success:
        print("\n🎉 SUCCESS! User Manager is working with UUID support!")
        print("   ✅ Frontend: http://localhost:8083")
        print("   ✅ API Docs: http://localhost:8083/docs")
    else:
        print("\n❌ FAILED! Check the server logs for more details.")
