#!/usr/bin/env python3
"""
Quick test of VeoGen chat functionality
"""

import requests
import json

API_BASE_URL = 'http://localhost:4700'

def test_chat():
    print("=== VeoGen Chat Test ===\n")
    
    try:
        # 1. Login first
        print("1. Logging in...")
        login_response = requests.post(f"{API_BASE_URL}/api/v1/auth/login", json={
            'email': 'valid@test.com',
            'password': 'Test123!'
        })
        
        if login_response.status_code != 200:
            print(f"X Login failed: {login_response.status_code}")
            print(f"Error: {login_response.text}")
            return False
        
        login_data = login_response.json()
        print(f"Login response: {json.dumps(login_data, indent=2)}")
        
        # Handle different response structures
        if 'user' in login_data:
            email = login_data['user']['email']
        elif 'email' in login_data:
            email = login_data['email']
        else:
            email = "unknown"
        
        print(f"+ Login successful: {email}")
        
        if 'access_token' in login_data:
            token = login_data['access_token']
        elif 'token' in login_data:
            token = login_data['token']
        else:
            print("No access token found in response")
            return False
            
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Test personas endpoint
        print("\n2. Getting personas...")
        personas_response = requests.get(f"{API_BASE_URL}/api/v1/chat/personas", headers=headers)
        
        if personas_response.status_code != 200:
            print(f"X Personas failed: {personas_response.status_code}")
            print(f"Error: {personas_response.text}")
            return False
        
        personas = personas_response.json()
        print(f"+ Found {len(personas)} personas")
        for persona in personas:
            print(f"   - {persona['name']}: {persona['description'][:50]}...")
        
        # 3. Start a chat
        print("\n3. Starting chat...")
        start_chat_response = requests.post(f"{API_BASE_URL}/api/v1/chat/start", 
            headers=headers, 
            json={
                'persona_id': 'creative_assistant',
                'initial_message': 'Hello! Can you help me with video ideas?'
            }
        )
        
        if start_chat_response.status_code != 200:
            print(f"X Start chat failed: {start_chat_response.status_code}")
            print(f"Error: {start_chat_response.text}")
            return False
        
        chat_result = start_chat_response.json()
        print(f"+ Chat started: {chat_result['conversation_id']}")
        print(f"Chat result: {json.dumps(chat_result, indent=2)}")
        
        # Try to get the response content safely
        if 'response' in chat_result:
            response = chat_result['response']
            if 'content' in response:
                print(f"Response: {response['content'][:100]}...")
            else:
                print(f"Response structure: {json.dumps(response, indent=2)}")
        else:
            print("No response field found")
        
        return True
        
    except Exception as e:
        print(f"X Error: {e}")
        return False

if __name__ == "__main__":
    success = test_chat()
    if success:
        print("\nChat system is working!")
    else:
        print("\nChat system has issues")
