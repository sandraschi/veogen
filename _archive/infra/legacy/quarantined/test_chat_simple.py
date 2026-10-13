#!/usr/bin/env python3
"""
Test chat persona system directly
"""

import requests
import json

def test_chat_simple():
    try:
        # Get auth token
        login_response = requests.post("http://localhost:4700/api/v1/auth/login", json={
            'email': 'valid@test.com',
            'password': 'Test123!'
        })
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test personas
        personas_response = requests.get("http://localhost:4700/api/v1/chat/personas", headers=headers)
        print(f"Personas status: {personas_response.status_code}")
        
        if personas_response.status_code == 200:
            personas = personas_response.json()
            print(f"Found {len(personas)} personas")
        else:
            print(f"Personas error: {personas_response.text}")
            return False
        
        # Test start chat
        start_response = requests.post("http://localhost:4700/api/v1/chat/start", 
            headers=headers, 
            json={'persona_id': 'creative_assistant', 'initial_message': 'Test message'},
            timeout=30
        )
        
        print(f"Start chat status: {start_response.status_code}")
        if start_response.status_code != 200:
            print(f"Start chat error: {start_response.text}")
            return False
        
        result = start_response.json()
        print(f"Chat result keys: {list(result.keys())}")
        
        if 'response' in result:
            print(f"Response received: {str(result['response'])[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_chat_simple()
