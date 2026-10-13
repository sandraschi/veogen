#!/usr/bin/env python3
"""
Direct test of the authentication flow to debug the issue
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.api.deps import get_current_user
from app.services.auth_service import AuthService
from app.database import SessionLocal
from fastapi.security import HTTPAuthorizationCredentials
from app.models.user import User

async def test_auth_dependency():
    """Test the auth dependency directly"""
    # Create a test JWT token
    auth_service = AuthService()
    
    # Create a token for user 'valid_user'
    token = auth_service.create_access_token(data={"sub": "valid_user"})
    print(f"Generated token: {token[:50]}...")
    
    # Test token verification
    payload = auth_service.verify_token(token)
    print(f"Token payload: {payload}")
    
    # Now test the dependency manually
    db = SessionLocal()
    try:
        # Create mock credentials
        class MockCredentials:
            def __init__(self, token):
                self.credentials = token
        
        credentials = MockCredentials(token)
        
        # Test the dependency
        user = await get_current_user(credentials, db)
        print(f"Dependency returned user: {user.email} (id: {user.id})")
        
    except Exception as e:
        print(f"Dependency test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_auth_dependency())
