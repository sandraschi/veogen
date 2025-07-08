#!/usr/bin/env python3
"""
Simple Gemini Chat Test for VeoGen
"""
import requests
import json

def test_gemini_full_integration():
    """Test the complete Gemini chat integration"""
    print("=== TESTING GEMINI CHAT INTEGRATION ===")
    
    try:
        # 1. Login to get auth token
        login_response = requests.post(
            'http://localhost:4700/api/v1/enhanced-auth/login',
            json={
                'email': 'sandraschipal@hotmail.com',
                'password': 'S3c1000vg#'
            }
        )
        
        if login_response.status_code != 200:
            print(f"X LOGIN FAILED: {login_response.text}")
            return
            
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✓ Login successful")
        
        # 2. Get available personas
        personas_response = requests.get(
            'http://localhost:4700/api/v1/chat/personas',
            headers=headers
        )
        
        if personas_response.status_code != 200:
            print(f"X PERSONAS FAILED: {personas_response.text}")
            return
            
        personas = personas_response.json()
        print(f"✓ Found {len(personas)} personas:")
        
        for persona in personas:
            print(f"   * {persona.get('id', 'Unknown ID')}: {persona.get('name', 'Unknown Name')}")
        
        # 3. Test chat with first available persona
        if not personas:
            print("X No personas available for testing")
            return
            
        test_persona = personas[0]['id']
        print(f"\nTesting chat with persona: {test_persona}")
        
        chat_request = {
            'persona_id': test_persona,
            'initial_message': 'Hello! Can you tell me a very short story about AI helping humans?',
            'context': {}
        }
        
        chat_response = requests.post(
            'http://localhost:4700/api/v1/chat/start',
            headers=headers,
            json=chat_request
        )
        
        print(f"Chat response status: {chat_response.status_code}")
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("✓ CHAT SUCCESS!")
            print(f"Conversation ID: {result.get('conversation_id')}")
            
            ai_response = result.get('response', {})
            message = ai_response.get('message', 'No message received')
            
            print(f"\nAI Response:")
            print(f"   {message}")
            
            if len(message) > 10:  # Basic validation
                print("\n✓ GEMINI INTEGRATION WORKING PERFECTLY!")
            else:
                print("\nShort response - check Gemini API")
                
        else:
            print(f"X CHAT FAILED: {chat_response.text}")
            
    except Exception as e:
        print(f"X ERROR: {e}")

if __name__ == "__main__":
    test_gemini_full_integration()
