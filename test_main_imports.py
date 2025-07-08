#!/usr/bin/env python3
"""
Test main.py imports and router registration
"""

import sys
import os

# Add the backend directory to the path
backend_path = r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\backend"
sys.path.insert(0, backend_path)

try:
    print("Testing imports from main.py...")
    
    # Test all imports from main
    from app.config import settings
    print("OK settings imported")
    
    from app.routers import video, movie
    print("OK video, movie imported")
    
    from app.api.api_v1.endpoints import music, image, book, code, translation, auth
    print("OK music, image, book, code, translation, auth imported")
    
    from app.api.api_v1.endpoints import settings as settings_endpoints
    print("OK settings_endpoints imported")
    
    from app.api.api_v1.endpoints import system
    print("OK system imported")
    
    from app.api.api_v1.endpoints import chat
    print("OK chat imported")
    
    from app.api.api_v1.endpoints import enhanced_auth
    print("OK enhanced_auth imported")
    
    from app.api.api_v1.endpoints import logs
    print("OK logs imported")
    
    print("\nAll imports successful!")
    
    # Check logs router specifically
    print(f"\nLogs router: {logs.router}")
    print(f"Logs router routes: {[route.path for route in logs.router.routes]}")
    
    # Test creating FastAPI app and registering the router
    from fastapi import FastAPI
    
    test_app = FastAPI()
    test_app.include_router(
        logs.router,
        prefix=f"{settings.API_V1_STR}/logs",
        tags=["logs"]
    )
    
    print(f"\nTest app routes: {[route.path for route in test_app.routes]}")
    
    logs_routes = [route for route in test_app.routes if "/logs" in str(route.path)]
    print(f"Logs routes in test app: {[str(route.path) for route in logs_routes]}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
