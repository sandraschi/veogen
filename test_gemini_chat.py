#!/usr/bin/env python3
"""
Test Gemini Chat Integration for VeoGen
"""
import requests
import json

def test_gemini_health():
    """Test if Gemini is configured"""
    print("=== TESTING GEMINI CONFIGURATION ===")
    
    try:
        response = requests.get('http://localhost:4700/health')
        health_data = response.json()
        
        print(f"Backend Health: {health_data.get('status', 'Unknown')}")
        
        if 'gemini_cli' in health_data:
            print(f"Gemini CLI: {health_data['gemini_cli']}")
        
        if health_data.get('status') == 'healthy':
            print("SUCCESS: Backend is healthy!")
        else:
            print("ERROR: Backend health issues")
            
    except Exception as e:
        print(f"ERROR checking health: {e}")

def test_personas():
    """Test available personas"""
    print("\n=== TESTING PERSONAS ===")
    
    try:
        # Get auth token first
        login_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/login',
            json={
                'email': 'sandraschipal@hotmail.com',
                'password': 'S3c1000vg#'
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Try to get personas
            personas_response = requests.get(
                'http://localhost:4700/api/v1/chat/personas',
                headers=headers
            )
            
            print(f"Personas endpoint status: {personas_response.status_code}")
            
            if personas_response.status_code == 200:
                personas = personas_response.json()
                print(f"SUCCESS: Found {len(personas)} personas!")
                
                for persona in personas[:3]:  # Show first 3
                    print(f"  - {persona.get('name', 'Unknown')}: {persona.get('type', 'Unknown')}")
            else:
                print(f"ERROR: Personas error: {personas_response.text}")
                
        else:
            print(f"ERROR: Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"ERROR testing personas: {e}")

def test_simple_chat():
    """Test a simple chat if API key is configured"""
    print("\n=== TESTING SIMPLE CHAT ===")
    
    try:
        # Get auth token
        login_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/login',
            json={
                'email': 'sandraschipal@hotmail.com',
                'password': 'S3c1000vg#'
            }
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Try to start a chat
            chat_request = {
                'persona_id': 'storyteller',
                'initial_message': 'Hello! Tell me a very short story about AI.',
                'context': {}
            }
            
            chat_response = requests.post(
                'http://localhost:4700/api/v1/chat/start',
                headers=headers,
                json=chat_request
            )
            
            print(f"Chat start status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                print("SUCCESS: Chat started successfully!")
                print(f"Conversation ID: {result.get('conversation_id')}")
                print(f"AI Response: {result.get('response', {}).get('message', 'No message')[:100]}...")
            else:
                print(f"ERROR: Chat failed: {chat_response.text}")
                
        else:
            print(f"ERROR: Login failed for chat test")
            
    except Exception as e:
        print(f"ERROR testing chat: {e}")

if __name__ == "__main__":
    print("GEMINI CHAT INTEGRATION TEST")
    print("=" * 50)
    
    test_gemini_health()
    test_personas()
    test_simple_chat()
    
    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("1. Get Gemini API key from: https://aistudio.google.com/app/apikey")
    print("2. Update docker-compose.yml with: GEMINI_API_KEY=your-key-here")
    print("3. Restart backend: docker-compose restart backend")
    print("4. Run this test again!")
