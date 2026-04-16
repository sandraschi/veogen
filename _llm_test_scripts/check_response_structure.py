import requests
import json

def check_login_response_structure():
    print("=== Checking Backend Response Structure ===")
    
    url = "http://localhost:4700/api/v1/enhanced-auth/login"
    data = {
        "email": "valid@test.com", 
        "password": "Test123!"
    }
    
    try:
        print("Sending login request...")
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nRAW Response Text:")
            print(response.text)
            print("\n" + "="*50)
            
            try:
                json_data = response.json()
                print("\nParsed JSON Response:")
                print(json.dumps(json_data, indent=2))
                
                print("\n" + "="*50)
                print("FRONTEND EXPECTS:")
                print("- response.data.access_token")
                print("- response.data.user")  
                print("- response.data.onboarding")
                
                print("\nBACKEND ACTUALLY RETURNS:")
                if 'access_token' in json_data:
                    print(f"✅ access_token: {json_data['access_token'][:20]}...")
                else:
                    print("❌ access_token: MISSING")
                    
                if 'user' in json_data:
                    print(f"✅ user: {json_data['user']}")
                else:
                    print("❌ user: MISSING")
                    
                if 'onboarding' in json_data:
                    print(f"✅ onboarding: {json_data['onboarding']}")
                else:
                    print("❌ onboarding: MISSING")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON Decode Error: {e}")
                
        else:
            print(f"❌ Request failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    check_login_response_structure()
