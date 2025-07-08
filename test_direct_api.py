import requests
import json

def test_all_login_scenarios():
    print("=== VeoGen Login API Direct Test ===")
    print("Testing all possible credential combinations...")
    
    base_url = "http://localhost:4700/api/v1/enhanced-auth"
    
    # All credential combinations to test
    test_accounts = [
        {"email": "valid@test.com", "password": "Test123!", "name": "Primary"},
        {"email": "sandraschipal@hotmail.com", "password": "S3c1000vg#", "name": "Sandra"},
        {"email": "test@test.com", "password": "test123", "name": "Alternative"},
        # Try variations in case of case sensitivity
        {"email": "Valid@Test.Com", "password": "Test123!", "name": "Primary (caps)"},
        {"email": "VALID@TEST.COM", "password": "Test123!", "name": "Primary (all caps)"},
        {"email": "valid@test.com", "password": "test123!", "name": "Primary (lowercase pass)"},
    ]
    
    print(f"\nTesting against: {base_url}/login")
    print("-" * 60)
    
    for account in test_accounts:
        print(f"\nTesting {account['name']}: {account['email']}")
        
        try:
            response = requests.post(
                f"{base_url}/login",
                json={
                    "email": account["email"],
                    "password": account["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   SUCCESS!")
                print(f"   User: {data.get('user', {}).get('email', 'N/A')}")
                print(f"   Token Length: {len(data.get('access_token', ''))}")
                print(f"   Onboarding Complete: {data.get('onboarding', {}).get('is_complete', 'N/A')}")
            else:
                print(f"   FAILED")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error Text: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"   REQUEST ERROR: {e}")
        except Exception as e:
            print(f"   UNKNOWN ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Checking backend health...")
    
    try:
        health_response = requests.get(f"http://localhost:4700/health", timeout=5)
        print(f"Backend Health: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Backend Status: {health_data}")
    except Exception as e:
        print(f"Backend Health Check Failed: {e}")

if __name__ == "__main__":
    test_all_login_scenarios()
