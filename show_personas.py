#!/usr/bin/env python3
"""
Show available personas and their IDs
"""
import requests
import json

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
        
        # Get all personas
        personas_response = requests.get(
            'http://localhost:4700/api/v1/chat/personas',
            headers=headers
        )
        
        if personas_response.status_code == 200:
            personas = personas_response.json()
            print("AVAILABLE PERSONAS:")
            print("=" * 50)
            
            for i, persona in enumerate(personas):
                print(f"{i+1}. ID: {persona.get('id', 'Unknown')}")
                print(f"   Name: {persona.get('name', 'Unknown')}")
                print(f"   Type: {persona.get('type', 'Unknown')}")
                print(f"   Description: {persona.get('description', 'No description')[:100]}...")
                print()
        else:
            print(f"Error getting personas: {personas_response.text}")
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
