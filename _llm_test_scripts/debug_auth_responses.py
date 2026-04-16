#!/usr/bin/env python3
import requests
import json

# Test login response structure
login_data = {'email': 'valid@test.com', 'password': 'Test123!'}
login_response = requests.post('http://localhost:4700/api/v1/enhanced-auth/login', json=login_data)

if login_response.status_code == 200:
    login_result = login_response.json()
    print('LOGIN RESPONSE STRUCTURE:')
    print(json.dumps(login_result, indent=2))
    
    token = login_result.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test /me response structure
    me_response = requests.get('http://localhost:4700/api/v1/enhanced-auth/me', headers=headers)
    if me_response.status_code == 200:
        me_result = me_response.json()
        print('\n/ME RESPONSE STRUCTURE:')
        print(json.dumps(me_result, indent=2))
        
        print('\nCOMPARISON:')
        print('Login user field:')
        print(json.dumps(login_result.get('user'), indent=2))
        print('\n/me response:')
        print(json.dumps(me_result, indent=2))
    else:
        print(f'/me failed: {me_response.text}')
else:
    print(f'Login failed: {login_response.text}')
