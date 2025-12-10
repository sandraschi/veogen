#!/usr/bin/env python3
"""
Test Gemini API Key Directly
"""
import requests

def test_gemini_api_key():
    """Test the Gemini API key directly"""
    api_key = "AIzaSyC_LBvMeiRdQ8GVhcYt1egAruaGXSYx2oY"
    
    print("=== TESTING GEMINI API KEY DIRECTLY ===")
    
    # Test the Gemini API directly
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Hello! Say hi back in one sentence."
            }]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: API key is working!")
            result = response.json()
            if 'candidates' in result:
                message = result['candidates'][0]['content']['parts'][0]['text']
                print(f"Gemini Response: {message}")
        else:
            print("ERROR: API key validation failed")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_gemini_api_key()
