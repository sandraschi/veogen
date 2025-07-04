#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    print("✓ Importing app.config...")
    from app.config import settings
    print(f"  - Project name: {settings.PROJECT_NAME}")
    
    print("✓ Importing app.database...")
    from app.database import get_db, User, UserSettings, APIKey
    print("  - Database models imported successfully")
    
    print("✓ Importing app.services.auth_service...")
    from app.services.auth_service import auth_service
    print("  - Auth service imported successfully")
    
    print("✓ Importing app.services.api_key_service...")
    from app.services.api_key_service import api_key_service
    print("  - API key service imported successfully")
    
    print("✓ Importing app.api.deps...")
    from app.api.deps import get_current_user, get_current_user_optional
    print("  - API dependencies imported successfully")
    
    print("✓ Importing app.api.api_v1.endpoints.auth...")
    from app.api.api_v1.endpoints import auth
    print("  - Auth endpoints imported successfully")
    
    print("✓ Importing app.main...")
    from app.main import app
    print("  - Main app imported successfully")
    
    print("\n🎉 All imports successful! The backend should start correctly.")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 