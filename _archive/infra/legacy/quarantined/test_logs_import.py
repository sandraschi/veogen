#!/usr/bin/env python3
"""
Test importing logs module to check for errors
"""

import sys
import os

# Add the backend directory to the path
backend_path = r"C:\Users\sandr\AppData\Local\AnthropicClaude\app-0.11.6\veogen\backend"
sys.path.insert(0, backend_path)

try:
    print("Testing logs module import...")
    from app.api.api_v1.endpoints import logs
    print("SUCCESS: Successfully imported logs module")
    print(f"Router: {logs.router}")
    print(f"Routes: {[route.path for route in logs.router.routes]}")
    
except Exception as e:
    print(f"FAILED: Failed to import logs module: {e}")
    import traceback
    traceback.print_exc()
